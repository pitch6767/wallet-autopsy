"""BOT95 — QUEUE RACE ENGINE, PHASES 0, 1 et 2 relancées sur TOUS les cycles enregistrés (14.10.2026). Copie de queue_race_phase12.py
(laissé intact) avec : prix en millièmes (format ≥ 11.10 ~12:30), traitement parallèle cycle par cycle, flux agressifs `fx` en phase 2,
et sauvegarde d'un résumé compact par cycle pour les phases 3 à 6 (queue_race_phases36.py). Hors ligne, aucun bot modifié.
Hypothèses H491–H510 et H523–H558 : qui fait disparaître la meilleure offre (transaction ou retrait), dans quel ordre
(nouvelle information → réaction des acheteurs → retrait des vendeurs → première transaction), et un ordre envoyé depuis Dublin
arriverait-il avant la disparition ?
Données : enregistreur du VPS de Dublin (bot95/rapide/rapide.js), branche git « donnees-rapide », un fichier gzip par cycle 5 min.
Usage (depuis la racine du dépôt) : QR_CACHE=<dossier> python3 etude/bot5min/queue_race_phases.py → etude/bot5min/resultat_queue_race_phases.md"""
import gzip, json, os, subprocess, collections, math, random, bisect, time, sys
import numpy as np

T0 = time.time()
RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SORTIE = os.path.join(RACINE, "etude", "bot5min", "resultat_queue_race_phases.md")
REF = "origin/donnees-rapide"
CACHE = os.environ.get("QR_CACHE") or os.path.join("/tmp", "queue_race_cycles")
FEAT = os.environ.get("QR_FEAT") or os.path.join(CACHE, "..", "feat")      # résumés compacts par cycle (pour les phases 3–6)

# ---------------------------------------------------------------- paramètres FIXÉS À L'AVANCE (pas d'optimisation sur les résultats)
X_INFO = 5.0              # $ : saut d'une source (perp, okx, bn, cb) entre deux échantillons 50 ms = « nouvelle information »
FEN_INFO = 1000           # ms : on cherche l'information qui précède une disparition dans cette fenêtre
PRES = 30                 # millièmes (= 3 c) : filtre de l'enregistreur (±3 c du meilleur prix)
POLY_VERS_DUBLIN = 8.6    # ms médian (mesuré par le bot)
RTT_CLOB = 28.0           # ms médian aller-retour Dublin → Polymarket (mesuré par le bot)
CALCUL = 0.1              # ms
SRCS = ["perp", "okx", "bn", "cb", "cl"]
random.seed(7); np.random.seed(7)


def git(*a):
    return subprocess.run(["git", "-C", RACINE, *a], capture_output=True, check=True).stdout


def charger_fichiers():
    try:
        git("rev-parse", "--verify", REF)
    except subprocess.CalledProcessError:
        git("fetch", "origin", "donnees-rapide:refs/remotes/origin/donnees-rapide")
    noms = [l for l in git("ls-tree", "-r", "--name-only", REF).decode().split("\n") if l.endswith(".json.gz")]
    os.makedirs(CACHE, exist_ok=True)
    out = []
    for n in sorted(noms):
        loc = os.path.join(CACHE, os.path.basename(n))
        if not os.path.exists(loc):
            with open(loc, "wb") as fh:
                fh.write(git("show", f"{REF}:{n}"))
        out.append(loc)
    return out


# ---------------------------------------------------------------- carnet Up (cents → taille)
class Livre:
    __slots__ = ("b", "a", "bb", "ba", "npurge")

    def __init__(self):
        self.b = {}; self.a = {}; self.bb = None; self.ba = None; self.npurge = 0

    def copie(self):
        L = Livre(); L.b = dict(self.b); L.a = dict(self.a); L.bb = self.bb; L.ba = self.ba; return L

    def charger(self, bids, asks):
        self.b = {c: s for c, s in bids if s > 0}; self.a = {c: s for c, s in asks if s > 0}
        self.bb = max(self.b) if self.b else None; self.ba = min(self.a) if self.a else None

    def maj(self, side, c, s, purge=True):
        """applique un changement ; renvoie l'ancienne taille. purge : un niveau qui croise le carnet efface les niveaux
        opposés périmés (le filtre ±3 c de l'enregistreur peut perdre des retraits lors d'un balayage)"""
        if purge and s > 0:
            if side == 0 and self.ba is not None and c >= self.ba:
                for k in [k for k in self.a if k <= c]: del self.a[k]
                self.ba = min(self.a) if self.a else None; self.npurge = getattr(self, "npurge", 0) + 1
            elif side == 1 and self.bb is not None and c <= self.bb:
                for k in [k for k in self.b if k >= c]: del self.b[k]
                self.bb = max(self.b) if self.b else None; self.npurge = getattr(self, "npurge", 0) + 1
        if side == 0:
            old = self.b.get(c, 0.0)
            if s > 0:
                self.b[c] = s
                if self.bb is None or c > self.bb: self.bb = c
            else:
                self.b.pop(c, None)
                if c == self.bb: self.bb = max(self.b) if self.b else None
        else:
            old = self.a.get(c, 0.0)
            if s > 0:
                self.a[c] = s
                if self.ba is None or c < self.ba: self.ba = c
            else:
                self.a.pop(c, None)
                if c == self.ba: self.ba = min(self.a) if self.a else None
        return old

    def top(self, side, n=5):
        if side == 0: return sorted(self.b.items(), key=lambda x: -x[0])[:n]
        return sorted(self.a.items(), key=lambda x: x[0])[:n]


mil = lambda p: int(round(p * 1000))      # prix en millièmes (pas de 0,001 près des extrêmes)


# ---------------------------------------------------------------- lecture d'un cycle → format normalisé
# flux : liste ordonnée d'événements (tR_ms, tsPoly_ms, genre, données)
#   ("P", side, c, size) Up seulement ; ("B", bids, asks) Up ; ("T", tok, side, c, size)
def normaliser(path):
    R = json.load(gzip.open(path))
    st = R["start"]; ver = R.get("version"); m = R.get("marche") or {}
    C = dict(start=st, version=ver, coupe=bool(R.get("coupe")), nEv=R.get("nEv"), strike=m.get("strike"),
             ex=R.get("ex", []), snap=R.get("snap", []), sig=R.get("sig", []), fx=R.get("fx"))
    flux = []
    if "p" not in R:                                   # format brut (premières versions) : tout, les 2 jetons
        C["format"] = "brut"
        for e in R["ev"]:
            if e[0] == "T": flux.append((e[1], e[2], "T", e[3], e[4], mil(e[5]), e[6]))
            elif e[3] != 0: continue
            elif e[0] == "B": flux.append((e[1], e[2], "B", [(mil(p), s) for p, s in e[4]], [(mil(p), s) for p, s in e[5]]))
            else: flux.append((e[1], e[2], "P", e[4], mil(e[5]), e[6]))
    else:                                              # format compact
        C["format"] = "compact"
        fm = R.get("format", ""); mult = 1 if "millieme" in fm else 10          # ≥ 11.10 ~12:30 : prix en millièmes ; avant : en cents
        C["cents"] = mult == 10
        t = 0; P = []
        for dt, ret, side, c, sz in R["p"]:
            t += dt; P.append((float(t), (t - ret) if ret is not None else None, "P", side, c * mult, sz / 100.0))
        A = []
        for e in R["ev"]:
            if e[0] == "T": A.append((e[1], e[2], "T", e[3], e[4], mil(e[5]), e[6]))
            elif e[0] == "B" and e[3] == 0: A.append((e[1], e[2], "B", [(mil(p), s) for p, s in e[4]], [(mil(p), s) for p, s in e[5]]))
        # fusion par heure de réception (stable : à égalité, l'ordre d'origine de chaque liste)
        flux = sorted(P + A, key=lambda x: x[0])
    C.setdefault("cents", False)
    C["flux"] = flux
    C["t_fin_flux"] = flux[-1][0] if flux else None
    return C


def simuler_filtre(C):
    """format brut → ce que l'enregistreur compact aurait gardé (±3 c du meilleur, B toutes les 10 s, T toutes)"""
    L = Livre(); dernierB = None; out = []
    for e in C["flux"]:
        g = e[2]
        if g == "T": out.append(e); continue
        if g == "B":
            if dernierB is None or e[0] - dernierB >= 10000: out.append(e); dernierB = e[0]
            L.charger(e[3], e[4]); continue
        side, c, s = e[3], e[4], e[5]
        best = (L.bb if L.bb is not None else 0) if side == 0 else (L.ba if L.ba is not None else 1000)
        garde = (best - c if side == 0 else c - best) <= PRES
        if garde: out.append((round(e[0]), e[1], "P", side, int(round(c / 10)) * 10, round(s * 100) / 100.0))
        L.maj(side, c, s, purge=False)
    D = dict(C); D["flux"] = out; D["format"] = "brut→filtré"
    return D


# ---------------------------------------------------------------- PHASE 0 : reconstruction contre les photos 5 niveaux (1 s)
def controle_photos(C):
    """rejoue le flux et compare au carnet 5 niveaux enregistré chaque seconde (jeton Up)"""
    L = Livre(); fl = C["flux"]; i = 0; n = len(fl); res = collections.Counter(); vu_B = False
    t_fin = C["t_fin_flux"] if C["coupe"] else None
    mauvais = []                                     # (t, ok_bid_L1, ok_ask_L1) pour marquer les périodes douteuses
    for sn in C["snap"]:
        t = sn[0]
        if t_fin is not None and t > t_fin: res["apres_coupure"] += 1; continue
        while i < n and fl[i][0] < t:
            e = fl[i]; i += 1
            if e[2] == "B": L.charger(e[3], e[4]); vu_B = True
            elif e[2] == "P" and vu_B: L.maj(e[3], e[4], e[5])
        if not vu_B: res["avant_carnet"] += 1; continue
        res["n"] += 1
        ok = {}
        for side, ref in ((0, sn[1]), (1, sn[2])):
            arr = 10 if C.get("cents") else 1                      # compact au cent : photo arrondie au cent
            r = [(int(round(mil(p) / arr)) * arr, s) for p, s in ref]
            if arr > 1:                                             # deux niveaux 0,991 et 0,99 fusionnent au cent
                agg = collections.OrderedDict()
                for c, z in r: agg[c] = agg.get(c, 0) + z
                r = list(agg.items())
                if any(mil(p) % 10 for p, _ in ref[:1]): res["L1_sous_cent_" + ("bid" if side == 0 else "ask")] += 1
            m = L.top(side, 5)
            if arr > 1: r = r[:len(m)] if len(r) > len(m) else r
            px = [c for c, _ in r] == [c for c, _ in m]
            ex = px and all(abs(a[1] - b[1]) <= 0.011 for a, b in zip(r, m))
            l1p = (r[0][0] if r else None) == (m[0][0] if m else None)          # côté vide des deux côtés = accord
            l1 = l1p and (not r or abs(r[0][1] - m[0][1]) <= 0.011)
            nom = "bid" if side == 0 else "ask"
            res[nom + "_L1_prix"] += l1p; res[nom + "_L1"] += l1; res[nom + "_top5_prix"] += px; res[nom + "_top5"] += ex
            ok[side] = l1
        # miroir : le carnet Down enregistré doit être le miroir exact du carnet Up enregistré
        mir = [(1000 - mil(p), round(s, 4)) for p, s in sn[3]] == [(mil(p), round(s, 4)) for p, s in sn[2]] and \
              [(1000 - mil(p), round(s, 4)) for p, s in sn[4]] == [(mil(p), round(s, 4)) for p, s in sn[1]]
        res["miroir"] += mir
        mauvais.append((t, ok[0], ok[1]))
    return res, mauvais


# ---------------------------------------------------------------- REJEU : baisses au meilleur prix, transactions, série L1
def cible_trade(tok, side, m):
    """transaction → (côté du carnet Up consommé, prix Up) en supposant side = côté du PRENEUR (vérifié en phase 0)"""
    if tok == 0: return (1, m) if side == 1 else (0, m)            # achat Up → offre Up ; vente Up → demande Up
    return (0, 1000 - m) if side == 1 else (1, 1000 - m)          # achat Down → offre Down = demande Up ; vente Down → demande Down = offre Up


def rejouer(C):
    """un passage sur le flux : baisses de quantité au meilleur niveau Up (offre et demande), transactions, série L1, positions des niveaux"""
    L = Livre(); fl = C["flux"]; vu_B = False
    snaps = C["snap"]; js = 0; fiable = {0: True, 1: True}; souscent = {0: False, 1: False}
    t_fin = C["t_fin_flux"] if C["coupe"] else None
    compact = C.get("cents", False)                    # seulement le format au cent (pas de 0,001 perdu)
    baisses = []; trades = []; serie = []; poses = collections.defaultdict(list)   # (side, prix) → heures où une quantité > 0 est posée/augmentée
    best_depuis = {0: None, 1: None}; cree = {0: {}, 1: {}}
    hausses = []                                                                   # augmentations au même côté (pour « déplacé »)
    last = None
    for e in fl:
        t = e[0]
        while js < len(snaps) and snaps[js][0] <= t:                              # contrôle de fiabilité avec les photos 1 s
            sn = snaps[js]; js += 1
            if not vu_B: continue
            for side in (0, 1):
                ref = sn[1 + side]
                r0 = mil(ref[0][0]) if ref else None
                if compact and r0 is not None: r0 = int(round(r0 / 10)) * 10
                m0 = L.bb if side == 0 else L.ba
                fiable[side] = (r0 == m0)
                souscent[side] = any(mil(p) % 10 for p, _ in ref)
        g = e[2]
        if g == "B":
            L.charger(e[3], e[4]); vu_B = True; best_depuis = {0: t, 1: t}
            for side, lv in ((0, e[3]), (1, e[4])):
                for c, z in lv: cree[side].setdefault(c, t)
            fiable = {0: True, 1: True}
        elif g == "T":
            cs, cm = cible_trade(e[3], e[4], e[5])
            trades.append((t, e[1], e[3], e[4], e[5], e[6], cs, cm, L.ba, L.bb))
        elif g == "P" and vu_B:
            side, c, z = e[3], e[4], e[5]
            best = L.bb if side == 0 else L.ba
            old = L.b.get(c, 0.0) if side == 0 else L.a.get(c, 0.0)
            if z < old - 1e-9 and c == best:
                indet = (not fiable[side]) or (compact and (souscent[side] or c <= 40 or c >= 960)) or (t_fin is not None and t > t_fin)
                baisses.append(dict(t=t, ts=e[1], side=side, c=c, old=old, new=z, d=old - z, full=z <= 1e-9, indet=indet,
                                    age_best=(t - best_depuis[side]) if best_depuis[side] else None,
                                    age_niv=(t - cree[side][c]) if c in cree[side] else None, spread=(L.ba - L.bb) if L.ba and L.bb else None))
            if z > old + 1e-9:
                poses[(side, c)].append(t); hausses.append((t, side, c, z - old))
                if old <= 1e-9: cree[side][c] = t
            if z <= 1e-9: cree[side].pop(c, None)
            L.maj(side, c, z)
            nb = L.bb if side == 0 else L.ba
            if nb != best: best_depuis[side] = t
        cur = (L.bb, L.b.get(L.bb, 0.0) if L.bb else 0.0, L.ba, L.a.get(L.ba, 0.0) if L.ba else 0.0)
        if vu_B and cur != last:
            serie.append((t,) + tuple(np.nan if x is None else x for x in cur)); last = cur
    S = np.array(serie, dtype=float) if serie else np.zeros((0, 5))
    return dict(baisses=baisses, trades=trades, serie=S, poses={k: np.array(v) for k, v in poses.items()}, hausses=hausses, npurge=L.npurge)


# ---------------------------------------------------------------- PHASE 1 : cause de chaque baisse au meilleur niveau
FEN_TRADE = (14, 40)      # ms (heure Polymarket) : le message de transaction suit la baisse du carnet ; fenêtre FIXÉE depuis l'histogramme (pic à +21 ms)
tol = lambda d: 0.02 + 0.01 * d


def index_trades(trades):
    idx = collections.defaultdict(list)
    for k, tt in enumerate(trades):
        if tt[1] is not None: idx[(tt[6], tt[7])].append((tt[1], tt[5], k))
    for v in idx.values(): v.sort()
    return idx


def trades_fenetre(idx, side, c, ts, lo=FEN_TRADE[0], hi=FEN_TRADE[1]):
    L = idx.get((side, c), [])
    i = bisect.bisect_left(L, (ts + lo, -1, -1)); out = []
    while i < len(L) and L[i][0] <= ts + hi: out.append(L[i]); i += 1
    return out


def classer(C, Rj):
    idx = index_trades(Rj["trades"]); utilises = set()
    H = {0: [], 1: []}
    for t, side, c, inc in Rj["hausses"]: H[side].append((t, c, inc))
    Ht = {s: [x[0] for x in H[s]] for s in (0, 1)}
    for x in Rj["baisses"]:
        if x["indet"] or x["ts"] is None: x["cause"] = "indéterminé"; x["vol_trade"] = None; continue
        cand = [u for u in trades_fenetre(idx, x["side"], x["c"], x["ts"]) if u[2] not in utilises]
        d = x["d"]; tot = sum(u[1] for u in cand); pris = []
        if cand:
            if abs(tot - d) <= tol(d) or tot < d: pris = cand
            else:
                un = [u for u in cand if abs(u[1] - d) <= tol(d)]
                pris = un[:1] if un else cand
        vt = sum(u[1] for u in pris)
        for u in pris: utilises.add(u[2])
        x["vol_trade"] = vt; x["t_trade"] = min((u[0] for u in pris), default=None)
        if vt >= d - tol(d): x["cause"] = "consommé"
        elif vt > 0: x["cause"] = "mixte"
        else:
            # déplacé : la même quantité réapparaît à un autre prix du même côté dans [−5 ; +50] ms
            i = bisect.bisect_left(Ht[x["side"]], x["t"] - 5); dep = False
            while i < len(H[x["side"]]) and H[x["side"]][i][0] <= x["t"] + 50:
                tt, cc, inc = H[x["side"]][i]; i += 1
                if cc != x["c"] and abs(inc - d) <= tol(d): dep = True; break
            x["cause"] = "déplacé" if dep else "retiré"
    return idx


def remplissage(Rj, x, fen):
    """H499 : après la disparition complète du niveau p, un vendeur revient-il à p (ou mieux) ?"""
    S = Rj["serie"]; t = x["t"]
    P = Rj["poses"].get((x["side"], x["c"]))
    out = {}
    for w in fen:
        meme = bool(P is not None and np.any((P > t) & (P <= t + w)))
        i0 = np.searchsorted(S[:, 0], t, "right"); i1 = np.searchsorted(S[:, 0], t + w, "right")
        seg = S[i0:i1]
        retour = bool(len(seg) and (np.any(seg[:, 3] <= x["c"]) if x["side"] == 1 else np.any(seg[:, 1] >= x["c"])))
        out[w] = (meme, retour)
    return out


# ---------------------------------------------------------------- PHASE 1b : offres visées par les signaux du bot
def etats_aux_instants(C, instants):
    """copie du carnet reconstruit à chaque instant demandé (heure de réception), et index du prochain événement"""
    L = Livre(); fl = C["flux"]; vu = False; out = {}; i = 0
    for t in sorted(instants):
        while i < len(fl) and fl[i][0] <= t:
            e = fl[i]; i += 1
            if e[2] == "B": L.charger(e[3], e[4]); vu = True
            elif e[2] == "P" and vu: L.maj(e[3], e[4], e[5])
        out[t] = (L.copie() if vu else None, i)
    return out


def suivre_signal(C, idx, L0, i0, sg, horizon=2000):
    up = sg["cote"] == "Up"; side = 1 if up else 0; a0 = mil(sg["a0"]); lim = a0 if up else 1000 - a0
    ok = (lambda c: c <= lim) if up else (lambda c: c >= lim)
    L = L0.copie(); cote = L.a if up else L.b
    q = lambda: sum(z for c, z in cote.items() if ok(c))
    q0 = q(); fl = C["flux"]; i = i0; t0 = sg["tDecision"]; dec = []; disp = None; prem = None
    while i < len(fl) and fl[i][0] <= t0 + horizon:
        e = fl[i]; i += 1
        if e[2] == "B": L.charger(e[3], e[4]); cote = L.a if up else L.b; continue
        if e[2] != "P": continue
        if e[3] == side and ok(e[4]):
            old = cote.get(e[4], 0.0)
            if e[5] < old - 1e-9: dec.append((e[0], e[1], e[4], old - e[5]))
        L.maj(e[3], e[4], e[5]); cote = L.a if up else L.b
        qq = q()
        if prem is None and qq < q0 - 1e-6: prem = e[0] - t0
        if qq < 1: disp = e[0] - t0; break
    vt = vd = 0.0
    for t, ts, c, d in dec:
        vd += d
        if ts is None: continue
        tr = trades_fenetre(idx, side, c, ts); s = sum(u[1] for u in tr); vt += min(d, s)
    part = vt / vd if vd > 0 else None
    if disp is None: cat = "encore là à 2 s"
    elif part is None: cat = "indéterminé"
    elif part >= 0.8: cat = "consommée"
    elif part <= 0.2: cat = "retirée"
    else: cat = "mixte"
    return dict(q0=q0, disp=disp, prem=prem, part=part, cat=cat, vd=vd)


# ---------------------------------------------------------------- PHASE 2 : chronologie information → réaction → retrait → transaction
def infos(C, X=X_INFO):
    """sauts ≥ X $ d'une bourse entre deux échantillons 50 ms consécutifs ; nouvelles valeurs Chainlink.
    Heure = heure de RÉCEPTION à Dublin du dernier prix de la source (connu à cet instant)."""
    out = []; prev = {}
    for r in C["ex"]:
        for k, nm in enumerate(SRCS):
            v = r[1 + k]
            if not v: continue
            p, tss, trs = v
            if nm in prev:
                pp, ptss = prev[nm]
                if nm == "cl":
                    if tss != ptss and p != pp: out.append((trs * 1000, nm, 1 if p > pp else -1, p - pp))
                elif abs(p - pp) >= X: out.append((trs * 1000, nm, 1 if p > pp else -1, p - pp))
            prev[nm] = (p, tss)
    out.sort()
    return out


def placebo(C, INF, src_ok, rng):
    """même nombre d'« informations » que le réel, mais à des instants et dans des sens tirés au hasard (témoin)"""
    st = C["start"] * 1000; n = sum(1 for x in INF if x[1] in src_ok)
    return sorted((st + rng.random() * 300000, "perp", rng.choice((1, -1)), 0.0) for _ in range(n))


def chronologie(C, Rj, INF, src_ok):
    """pour chaque disparition complète du meilleur niveau (hors indéterminé), dans la fenêtre du cycle"""
    st = C["start"] * 1000
    I = [x for x in INF if x[1] in src_ok]; It = [x[0] for x in I]
    B = sorted([x for x in Rj["baisses"] if x["cause"] != "indéterminé"], key=lambda x: x["t"]); Bt = [x["t"] for x in B]
    S = Rj["serie"]; res = []
    for x in B:
        if not x["full"] or not (st <= x["t"] <= st + 300000): continue
        sens = 1 if x["side"] == 1 else -1        # offre Up disparaît ← BTC monte ; demande Up (= offre Down) disparaît ← BTC baisse
        j = bisect.bisect_right(It, x["t"]) - 1; info = None
        while j >= 0 and It[j] >= x["t"] - FEN_INFO:
            if I[j][2] == sens: info = I[j]; break
            j -= 1
        r = dict(side=x["side"], cause=x["cause"], t=x["t"], ts=x["ts"], info=info)
        if info is not None:
            t0 = info[0]
            # 1re réaction de l'autre côté (renforcement : prix meilleur ou taille plus grande au meilleur) après l'information
            i0 = np.searchsorted(S[:, 0], t0, "right"); i1 = np.searchsorted(S[:, 0], x["t"], "right")
            seg = S[max(0, i0 - 1):i1]; react = None
            for a in range(1, len(seg)):
                p0, z0 = (seg[a - 1, 1], seg[a - 1, 2]) if x["side"] == 1 else (seg[a - 1, 3], seg[a - 1, 4])
                p1, z1 = (seg[a, 1], seg[a, 2]) if x["side"] == 1 else (seg[a, 3], seg[a, 4])
                mieux = (p1 > p0 or (p1 == p0 and z1 > z0)) if x["side"] == 1 else (p1 < p0 or (p1 == p0 and z1 > z0))
                if mieux and seg[a, 0] > t0: react = seg[a, 0] - t0; break
            # 1er retrait et 1re consommation au meilleur niveau du côté qui disparaît, après l'information
            ret = cons = None; ts1 = None
            k0 = bisect.bisect_right(Bt, t0)
            for y in B[k0:]:
                if y["t"] > x["t"]: break
                if y["side"] != x["side"]: continue
                if ret is None and y["cause"] in ("retiré", "déplacé"): ret = y["t"] - t0
                if cons is None and y["cause"] in ("consommé", "mixte"): cons = y["t"] - t0
                if ts1 is None and y["c"] == x["c"]: ts1 = y["ts"]             # 1re baisse du niveau qui va disparaître, après l'information
            arrivee = t0 + CALCUL + RTT_CLOB / 2
            r.update(dt_info=x["t"] - t0, react=react, ret=ret, cons=cons,
                     course_demi=(x["ts"] is not None and arrivee < x["ts"]), course_rtt=(x["ts"] is not None and t0 + CALCUL + RTT_CLOB < x["ts"]),
                     avant_1re=(ts1 is not None and arrivee < ts1))
        res.append(r)
    return res


# ---------------------------------------------------------------- précurseurs (H497, H541, H543) : 100/200/500 ms avant une consommation
def etat(S, t):
    i = np.searchsorted(S[:, 0], t, "right") - 1
    return S[i] if i >= 0 else None


def variables(S, t, side, h, fin=1):
    """état à t−fin et variations depuis t−fin−h (fin = 1 ms : tout ce qui est visible juste avant ; fin = h : arrêté h ms avant)"""
    a = etat(S, t - fin); b = etat(S, t - fin - h)
    if a is None or b is None or np.isnan(a[1:]).any() or np.isnan(b[1:]).any(): return None
    def vue(r):                       # perspective du côté consommé : « propre » = l'offre consommée, « face » = l'autre côté
        bb, bz, ba, az = r[1:]
        spread = ba - bb; micro = (bb * az + ba * bz) / (bz + az) if bz + az > 0 else (bb + ba) / 2
        tilt = (micro - (bb + ba) / 2) / (spread / 2) if spread > 0 else 0.0
        if side == 1: return spread, tilt, bz, az, bb
        return spread, -tilt, az, bz, -ba
    sa, ta, fa, pa, xa = vue(a); sb, tb, fb, pb, xb = vue(b)
    return [ta, sa - sb, math.log1p(fa) - math.log1p(fb), xa - xb, math.log1p(pa) - math.log1p(pb), sa]


NOMS_VAR = ["déséquilibre du microprix vers l'offre consommée (en fin de fenêtre)", "variation de l'écart (compression < 0)",
            "variation log taille du meilleur acheteur d'en face (renforcement > 0)", "variation du prix d'en face (millièmes, vers l'offre > 0)",
            "variation log taille de l'offre consommée", "écart en fin de fenêtre (millièmes)"]


# ================================================================ AJOUTS 14.10 : flux agressifs (fx) comme « information »
FX_SRCS = ("perp", "okx", "bn", "cb")
FX_SEUIL = 250000.0       # $ : flux net agressif (achats − ventes preneurs, 4 bourses) dans une tranche de 50 ms — FIXÉ À L'AVANCE (ordre de grandeur d'un gros ordre)


def infos_fx(C, X=FX_SEUIL):
    out = []
    for t, d in (C.get("fx") or []):
        net = sum((d[k][0] - d[k][1]) for k in FX_SRCS if k in d)
        if abs(net) >= X: out.append((t, "fx", 1 if net > 0 else -1, net))
    return out


def resume_chrono(L):
    """réduit une liste de chronologie : nombre total + seulement les disparitions précédées d'une information (champs utiles)"""
    keep = ("side", "cause", "dt_info", "react", "ret", "cons", "course_demi", "course_rtt", "avant_1re", "ts")
    return len(L), [{k: r.get(k) for k in keep} for r in L if r["info"] is not None]


GAGN = {}; RAP = {}


def init_worker():
    rap = json.load(open(os.path.join(RACINE, "bot95", "rapide.json")))["signaux"]
    for s in rap:
        if s.get("gagnant"): GAGN[s["start"]] = s["gagnant"]
        RAP.setdefault(s["start"], []).append(s)


def traiter(path):
    """tout le travail d'un cycle → agrégats compacts (permet le parallélisme et une mémoire bornée)"""
    rng = random.Random(int(os.path.basename(path).split(".")[0]))
    C = normaliser(path); Rj = rejouer(C); idx = classer(C, Rj)
    st = C["start"] * 1000
    o = dict(start=C["start"], version=C["version"], format=C["format"], cents=C.get("cents"), coupe=C["coupe"], fx=bool(C.get("fx")))
    r, _ = controle_photos(C); o["photos"] = r
    o["filtre"] = controle_photos(simuler_filtre(C))[0] if C["format"] == "brut" else None
    o["nP"] = sum(1 for e in C["flux"] if e[2] == "P"); o["nB"] = sum(1 for e in C["flux"] if e[2] == "B"); o["ntr"] = len(Rj["trades"])
    o["t0"] = C["flux"][0][0] / 1000 - C["start"] if C["flux"] else None; o["t1"] = C["flux"][-1][0] / 1000 - C["start"] if C["flux"] else None
    o["npurge"] = Rj["npurge"]
    # sens du champ side
    sens = collections.Counter(); hist = {0: [], 1: []}
    for x in Rj["baisses"]:
        if x["full"] and x["ts"] is not None: hist[x["side"]].append((x["ts"], x["c"]))
    for s in (0, 1): hist[s].sort()
    for tt in Rj["trades"]:
        t, ts, tok, sd, m, z, cs, cm, ba, bb = tt
        if ba is None or bb is None or ts is None: continue
        pu = m if tok == 0 else 1000 - m
        def recent(s):
            L = hist[s]; i = bisect.bisect_left(L, (ts - 60, -1))
            return any(c == pu for tt_, c in L[i:i + 50] if tt_ <= ts)
        ou = "offre" if (pu == ba or recent(1)) else "demande" if (pu == bb or recent(0)) else "ailleurs"
        sens[((tok == 0 and sd == 1) or (tok == 1 and sd == 0), ou)] += 1
    o["sens"] = sens
    # phase 1
    cnt = collections.Counter(); vol = collections.Counter()
    for x in Rj["baisses"]:
        cnt[(x["side"], x["cause"], x["full"])] += 1
        if x["cause"] != "indéterminé": vol[(x["side"], "t")] += min(x["vol_trade"] or 0, x["d"]); vol[(x["side"], "d")] += x["d"]
    o["cnt"] = cnt; o["vol"] = vol
    o["full"] = [(x["side"], x["cause"], x["age_best"], x["age_niv"], x["old"], x["t"], x["ts"], x["c"]) for x in Rj["baisses"] if x["full"]]
    fond = collections.Counter()
    for x in Rj["baisses"]:
        if x["cause"] == "indéterminé": continue
        fond["n"] += 1; fond["nf"] += x["full"]
        s_ = sum(u[1] for u in trades_fenetre(idx, x["side"], x["c"], x["ts"], -200, -174))
        if s_ >= x["d"] - tol(x["d"]): fond["f"] += 1; fond["ff"] += x["full"]
    o["fond"] = fond
    FEN = (100, 500, 1000); rempl = collections.defaultdict(collections.Counter)
    for x in Rj["baisses"]:
        if not x["full"] or x["cause"] == "indéterminé": continue
        R_ = remplissage(Rj, x, FEN); k = (x["side"], "consommé" if x["cause"] in ("consommé", "mixte") else "retiré/déplacé")
        rempl[k]["n"] += 1
        for wv, (meme, ret) in R_.items(): rempl[k][("meme", wv)] += meme; rempl[k][("retour", wv)] += ret
    o["rempl"] = dict(rempl)
    # phase 1b
    SG = []
    if C["sig"]:
        E = etats_aux_instants(C, [s["tDecision"] + 0.5 for s in C["sig"]])
        g = GAGN.get(C["start"])
        for s in C["sig"]:
            L0, i0 = E[s["tDecision"] + 0.5]
            if L0 is None: continue
            r_ = suivre_signal(C, idx, L0, i0, s)
            bot = [y for y in RAP.get(C["start"], []) if y["nom"] == s["nom"] and abs(y["tDecision"] - s["tDecision"]) < 1]
            r_.update(nom=s["nom"], start=C["start"], cote=s["cote"], a0=s["a0"], gagne=(g == s["cote"]) if g else None, bot=bool(bot),
                      bot_disp=bot[0].get("disparu_ms") if bot else None, tD=s["tDecision"], tronque=C["coupe"] and s["tDecision"] > C["t_fin_flux"])
            SG.append(r_)
    o["sig"] = SG
    # phase 2
    nINF = collections.Counter(); CH = {}
    if C["ex"]:
        INF = infos(C); I2 = infos(C, 2.0); IFX = infos_fx(C)
        for x in INF: nINF[x[1]] += 1
        nINF["fx"] += len(IFX)
        B4 = {"perp", "okx", "bn", "cb"}
        CH["bourses"] = resume_chrono(chronologie(C, Rj, INF, B4))
        CH["cl"] = resume_chrono(chronologie(C, Rj, INF, {"cl"}))
        CH["b2"] = resume_chrono(chronologie(C, Rj, I2, B4))
        if C.get("fx"): CH["fx"] = resume_chrono(chronologie(C, Rj, IFX, {"fx"}))
        P = {"bourses": [0, []], "cl": [0, []], "fx": [0, []]}
        for rep in range(20):
            for k, src in (("bourses", B4), ("cl", {"cl"})) + ((("fx", {"fx"}),) if C.get("fx") else ()):
                II = IFX if k == "fx" else INF
                n_, L_ = resume_chrono(chronologie(C, Rj, placebo(C, II, src, rng), {"perp"}))
                P[k][0] += n_; P[k][1].extend(L_)
        CH["placebo"] = P
    o["nINF"] = nINF; o["CH"] = CH
    # précurseurs
    S = Rj["serie"]; PRE = {}
    evt = {s: np.array(sorted(x["t"] for x in Rj["baisses"] if x["full"] and x["side"] == s and x["cause"] in ("consommé", "mixte"))) for s in (0, 1)}
    ev = [x for x in Rj["baisses"] if x["full"] and x["cause"] == "consommé" and st <= x["t"] <= st + 300000]
    for h, mode in [(h, m) for m in ("t-1", "t-h") for h in (100, 200, 500)]:
        fin = 1 if mode == "t-1" else h; Xp, Xn = [], []
        for x in ev:
            v = variables(S, x["t"], x["side"], h, fin)
            if v is None: continue
            Xp.append(v); k = 0; essais = 0
            while k < 3 and essais < 50:
                essais += 1; tr = st + rng.random() * 300000; E_ = evt[x["side"]]
                if len(E_) and np.min(np.abs(E_ - tr)) < 1000: continue
                v2 = variables(S, tr, x["side"], h, fin)
                if v2 is None: continue
                Xn.append(v2); k += 1
        PRE[(h, mode)] = (Xp, Xn)
    o["PRE"] = PRE
    # résumé compact pour les phases 3–6
    os.makedirs(FEAT, exist_ok=True)
    B = [x for x in Rj["baisses"]]
    cause_code = {"consommé": 1, "mixte": 2, "retiré": 3, "déplacé": 4, "indéterminé": 0}
    bar = np.array([(x["t"], x["ts"] if x["ts"] is not None else np.nan, x["side"], x["c"], x["old"], x["new"], x["full"], cause_code[x["cause"]]) for x in B], dtype=float).reshape(-1, 8)
    trd = np.array([(tt[0], tt[1] if tt[1] is not None else np.nan, tt[6], tt[7], tt[5]) for tt in Rj["trades"]], dtype=float).reshape(-1, 5)
    perp = np.array([(r[0], r[1][0]) for r in C["ex"] if r[1]], dtype=float).reshape(-1, 2)
    fxa = np.array([(t, sum((d[k][0] - d[k][1]) for k in FX_SRCS if k in d)) for t, d in (C.get("fx") or [])], dtype=float).reshape(-1, 2)
    np.savez_compressed(os.path.join(FEAT, f"{C['start']}.npz"), serie=S, baisses=bar, trades=trd, perp=perp, fx=fxa,
                        meta=np.array([C["start"], 1.0 if C["coupe"] else 0.0, C["t_fin_flux"] or np.nan, 1.0 if C.get("cents") else 0.0, 1.0 if C.get("fx") else 0.0]))
    return o


# ================================================================ PROGRAMME
fr = lambda x, d=1: "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:,.{d}f}".replace(",", " ").replace(".", ",")
pc = lambda a, b: "—" if not b else f"{100 * a / b:.1f} %".replace(".", ",")
def q3(v, d=1):
    v = [x for x in v if x is not None]
    if not v: return "—"
    a = np.percentile(v, [10, 50, 90]); return " · ".join(fr(float(x), d) for x in a)
NOM_SIDE = {1: "offre Up (vendeur Up)", 0: "demande Up = offre Down"}
JOUR = lambda st: time.strftime("%d.%m", time.gmtime(st + 7200))      # heure suisse (UTC+2)


def main():
    from multiprocessing import Pool
    fichiers = charger_fichiers()
    lim = int(os.environ.get("QR_MAX", "0"))
    if lim: fichiers = fichiers[:lim]
    with Pool(int(os.environ.get("QR_PROC", "2")), initializer=init_worker) as P:
        CY = []
        for k, o in enumerate(P.imap(traiter, fichiers, chunksize=2)):
            CY.append(o)
            if k % 50 == 0: print(k, f"{time.time() - T0:.0f} s", flush=True)
    CY.sort(key=lambda o: o["start"])
    nc = len(CY); jours = collections.Counter(JOUR(o["start"]) for o in CY)
    md = []; w = md.append
    # ------------------------------------------------ agrégats
    tot = collections.Counter(); totf = collections.Counter(); sens = collections.Counter(); cnt = collections.Counter(); vol = collections.Counter(); fond = collections.Counter()
    rempl = collections.defaultdict(collections.Counter); FULL = []; SG = []; nINF = collections.Counter()
    CH = collections.defaultdict(lambda: [0, []]); CHP = collections.defaultdict(lambda: [0, []])
    PRE = collections.defaultdict(lambda: ([], [], [], []))
    for ci, o in enumerate(CY):
        tot.update(o["photos"]); sens.update(o["sens"]); cnt.update(o["cnt"]); vol.update(o["vol"]); fond.update(o["fond"]); nINF.update(o["nINF"])
        if o["filtre"]: totf.update(o["filtre"])
        for k, v in o["rempl"].items(): rempl[k].update(v)
        FULL.extend((o["start"],) + x for x in o["full"]); SG.extend(o["sig"])
        for k, v in o["CH"].items():
            if k == "placebo":
                for k2, (n_, L_) in v.items(): CHP[k2][0] += n_; CHP[k2][1].extend(L_)
            else: CH[k][0] += v[0]; CH[k][1].extend(v[1])
        for k, (Xp, Xn) in o["PRE"].items():
            A = PRE[k]; A[0].extend(Xp); A[1].extend(Xn); A[2].extend([ci] * len(Xp)); A[3].extend([ci] * len(Xn))
    couvert = sum(max(0.0, min(300.0, o["t1"]) - max(0.0, o["t0"])) for o in CY if o["t0"] is not None)
    # FULL : (start, side, cause, age_best, age_niv, old, t, ts, c)
    Fok = [x for x in FULL if x[2] != "indéterminé"]
    cF = collections.Counter(x[2] for x in FULL)
    ncons = cF["consommé"] + cF["mixte"]; nret = cF["retiré"] + cF["déplacé"]; nfull = len(Fok)
    allc = collections.Counter(); 
    for (s, c_, f_), v in cnt.items(): allc[c_] += v
    nbaisses_ok = sum(v for k, v in allc.items() if k != "indéterminé")
    delai_msg = POLY_VERS_DUBLIN + CALCUL + RTT_CLOB / 2
    vies = [x[3] for x in Fok if x[3] is not None]
    # précurseurs
    from sklearn.metrics import roc_auc_score
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import GroupKFold
    PR = {}
    for key in [(h, m) for m in ("t-1", "t-h") for h in (100, 200, 500)]:
        Xp, Xn, gp, gn = PRE[key]
        X = np.array(Xp + Xn); y = np.array([1] * len(Xp) + [0] * len(Xn)); g = np.array(gp + gn)
        aucs = [roc_auc_score(y, X[:, j]) for j in range(X.shape[1])]
        pred = np.zeros(len(y))
        for a, b in GroupKFold(n_splits=5).split(X, y, g):
            m = LogisticRegression(max_iter=1000).fit(X[a], y[a]); pred[b] = m.predict_proba(X[b])[:, 1]
        PR[key] = dict(n1=len(Xp), n0=len(Xn), aucs=aucs, auc_cv=roc_auc_score(y, pred), med1=np.median(np.array(Xp), 0), med0=np.median(np.array(Xn), 0))
    # ================================================= RAPPORT
    w("# BOT95 — QUEUE RACE ENGINE · phases 0, 1 et 2 relancées sur toutes les données")
    w("")
    w(f"Étude hors ligne du 14.10.2026 (aucun bot, aucun workflow modifié). Données : enregistreur du VPS de Dublin, branche `donnees-rapide` : **{nc} cycles BTC 5 min** "
      f"({', '.join(f'{j} : {v}' for j, v in sorted(jours.items()))}), soit ≈ {fr(nc * 5 / 60, 1)} h d'horloge. Même méthode que `resultat_queue_race_phase12.md` (15 cycles du 11.10), "
      "avec trois changements : prix en millièmes pris tels quels quand l'enregistreur les fournit, flux agressifs `fx` ajoutés comme source d'information en phase 2, tableaux par jour au lieu de par cycle. "
      "Script : `etude/bot5min/queue_race_phases.py`. Les phases 3 à 6 sont dans `resultat_queue_race_phases36.md`.")
    w("")
    avec = CH["bourses"][1]; nb_ = CH["bourses"][0]; PBa = CHP["bourses"][1]; nPB = CHP["bourses"][0]
    def premier(L):
        c = collections.Counter()
        for r in L:
            a, b = r.get("ret"), r.get("cons")
            c["REQ" if a is not None and (b is None or a < b) else "SW" if b is not None and (a is None or b < a) else "SIM" if a is not None else "AUC"] += 1
        return c
    med = lambda L, k: fr(float(np.median([r[k] for r in L if r.get(k) is not None])) if any(r.get(k) is not None for r in L) else None, 0)
    pr, pp = premier(avec), premier(PBa)
    race = [r for r in avec if r.get("ts") is not None]; PBr = [r for r in PBa if r.get("ts") is not None]
    w("## Verdict (en tête)")
    w("")
    w(f"- **Qui fait disparaître la meilleure offre ?** Sur {fr(nfull, 0)} disparitions complètes du meilleur niveau (hors indéterminé), **{pc(nret, nfull)} sont des retraits** "
      f"(dont {pc(cF['déplacé'], nfull)} « déplacés ») et **{pc(ncons, nfull)} des consommations** par une transaction ({pc(cF['mixte'], nfull)} mixtes). "
      f"{fr(cF['indéterminé'], 0)} disparitions indéterminées exclues. Toutes baisses confondues : {fr(nbaisses_ok, 0)} baisses, {pc(allc['consommé'], nbaisses_ok)} consommées. "
      f"Sur 15 cycles (11.10) : 77,4 % / 22,6 % — **le résultat tient sur {nc} cycles**.")
    w(f"- **Chronologie** : {fr(len(avec), 0)} des {fr(nb_, 0)} disparitions ({pc(len(avec), nb_)}) sont précédées dans la seconde d'un saut de bourse ≥ {fr(X_INFO, 0)} $ dans le bon sens, "
      f"contre {pc(len(PBa), nPB)} avec des informations placées au hasard → l'information de bourse explique ≈ **{fr(100 * (len(avec) / max(1, nb_) - len(PBa) / max(1, nPB)), 1)} points** des disparitions. "
      f"Médianes après l'information (témoin) : réaction de l'autre côté {med(avec, 'react')} ms ({med(PBa, 'react')}), 1er retrait {med(avec, 'ret')} ms ({med(PBa, 'ret')}), "
      f"1re consommation {med(avec, 'cons')} ms ({med(PBa, 'cons')}), disparition {med(avec, 'dt_info')} ms ({med(PBa, 'dt_info')}). "
      f"Retrait d'abord {pc(pr['REQ'], len(avec))}, consommation d'abord {pc(pr['SW'], len(avec))} (témoin {pc(pp['REQ'], len(PBa))} / {pc(pp['SW'], len(PBa))}).")
    if race:
        w(f"- **Course** (ordre parti à la réception de l'information, +{fr(CALCUL, 1)} ms de calcul, +{fr(RTT_CLOB / 2, 0)} ms aller simple) : avant la disparition complète {pc(sum(r['course_demi'] for r in race), len(race))}, "
          f"**avant la 1re baisse du niveau visé {pc(sum(r['avant_1re'] for r in race), len(race))}** contre {pc(sum(r['avant_1re'] for r in PBr), len(PBr))} à des instants au hasard.")
    nv = len(vies); ok_v = sum(1 for v in vies if v > delai_msg)
    w(f"- **Course déclenchée par le carnet lui-même** : un niveau devenu meilleur prix vit en médiane {fr(float(np.median(vies)), 0)} ms à ce rang avant de disparaître ; "
      f"{pc(ok_v, nv)} vivent plus que notre délai ≈ {fr(delai_msg, 1)} ms (borne de faisabilité, pas un gain).")
    sg_ok = [s for s in SG if not s["tronque"]]; cs_ = collections.Counter(x["cat"] for x in sg_ok)
    nd = sum(v for k, v in cs_.items() if k not in ("encore là à 2 s", "indéterminé"))
    w(f"- **Signaux du bot ({fr(len(sg_ok), 0)})** : offre visée disparue dans les 2 s pour {fr(nd, 0)} — **retirée {cs_['retirée']}** ({pc(cs_['retirée'], nd)}), consommée {cs_['consommée']}, mixte {cs_['mixte']} ; "
      f"encore là à 2 s {cs_['encore là à 2 s']} ; indéterminé {cs_['indéterminé']}.")
    pk = PR[(500, "t-h")]; pk1 = PR[(100, "t-1")]
    w(f"- **Précurseurs d'une consommation** : déséquilibre du microprix AUC {fr(pk1['aucs'][0], 3)} juste avant (t−1 ms), {fr(pk['aucs'][0], 3)} arrêté à t−500 ms ; modèle combiné {fr(pk1['auc_cv'], 3)} / {fr(pk['auc_cv'], 3)}.")
    w("")
    # ---------- phase 0
    w("## Phase 0 — audit des données")
    w("")
    w("| Jour (heure suisse) | Cycles | Versions | Format des prix | Avec `fx` | Coupés | Changements P (Up) | Transactions | Photos 1 s comparées | Meilleur acheteur : prix · prix+taille | Meilleur vendeur : prix · prix+taille | 5 niveaux : prix acheteur · vendeur | Miroir |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for j in sorted(jours):
        L = [o for o in CY if JOUR(o["start"]) == j]; r = collections.Counter()
        for o in L: r.update(o["photos"])
        n = r["n"]; fm = collections.Counter("brut" if o["format"] == "brut" else ("cents" if o["cents"] else "millièmes") for o in L)
        w(f"| {j} | {len(L)} | {len(set(o['version'] for o in L))} | {', '.join(f'{k} {v}' for k, v in fm.items())} | {sum(o['fx'] for o in L)} | {sum(o['coupe'] for o in L)} | {fr(sum(o['nP'] for o in L), 0)} | {fr(sum(o['ntr'] for o in L), 0)} | {fr(n, 0)} | "
          f"{pc(r['bid_L1_prix'], n)} · {pc(r['bid_L1'], n)} | {pc(r['ask_L1_prix'], n)} · {pc(r['ask_L1'], n)} | {pc(r['bid_top5_prix'], n)} · {pc(r['ask_top5_prix'], n)} | {pc(r['miroir'], n)} |")
    n = tot["n"]
    w(f"| **total** | {nc} | {len(set(o['version'] for o in CY))} | | {sum(o['fx'] for o in CY)} | {sum(o['coupe'] for o in CY)} | {fr(sum(o['nP'] for o in CY), 0)} | {fr(sum(o['ntr'] for o in CY), 0)} | {fr(n, 0)} | "
      f"{pc(tot['bid_L1_prix'], n)} · {pc(tot['bid_L1'], n)} | {pc(tot['ask_L1_prix'], n)} · {pc(tot['ask_L1'], n)} | {pc(tot['bid_top5_prix'], n)} · {pc(tot['ask_top5_prix'], n)} | {pc(tot['miroir'], n)} |")
    w("")
    vides = [o for o in CY if o["nP"] < 5000]
    w(f"- **Couverture** : {nc} cycles, du {time.strftime('%d.%m %H:%M', time.gmtime(CY[0]['start'] + 7200))} au {time.strftime('%d.%m %H:%M', time.gmtime(CY[-1]['start'] + 7200))} (heure suisse). "
      f"Temps de cycle couvert par le flux : **{fr(couvert / 3600, 1)} h sur {fr(nc * 5 / 60, 1)} h**. Cycles presque vides (< 5 000 changements, redémarrages) : {len(vides)}. "
      f"Cycles sans flux de prix des bourses : {sum(1 for o in CY if not o['nINF'])}. Cycles avec flux agressifs `fx` : {sum(o['fx'] for o in CY)}.")
    w(f"- **Format des prix** : {sum(1 for o in CY if o['format'] == 'brut')} cycles bruts, {sum(1 for o in CY if o['cents'])} au cent, {sum(1 for o in CY if o['format'] == 'compact' and not o['cents'])} en millièmes "
      "(le défaut « pas de 0,001 » signalé le 11.10 est corrigé dans l'enregistreur depuis ~12:30 le 11.10 ; les baisses près de 0/1 ne sont plus classées indéterminées pour ces cycles).")
    nf = totf["n"]
    if nf:
        w(f"- **Perte due au filtre ±3 c** (simulée sur les cycles bruts) : meilleur prix+taille {pc(totf['bid_L1'], nf)} / {pc(totf['ask_L1'], nf)} ; 5 niveaux prix+taille {pc(totf['bid_top5'], nf)} / {pc(totf['ask_top5'], nf)}. Le meilleur niveau reste fiable.")
    tA = sum(v for (a, o_), v in sens.items() if a); tV = sum(v for (a, o_), v in sens.items() if not a)
    w(f"- **Sens du champ `side`** : transactions dites acheteuses tombant sur l'offre Up {pc(sens[(True, 'offre')], tA)} ; dites vendeuses tombant sur la demande Up {pc(sens[(False, 'demande')], tV)} → `side` = côté du preneur (confirmé).")
    w(f"- **Faux appariement** (fenêtre témoin décalée à −200 ms) : {pc(fond['f'], fond['n'])} des baisses, {pc(fond['ff'], fond['nf'])} des disparitions complètes (à comparer à {pc(allc['consommé'], nbaisses_ok)} de baisses consommées).")
    w("")
    # ---------- phase 1
    w("## Phase 1 — pourquoi la meilleure offre disparaît (toutes les données)")
    w("")
    w("Définitions identiques au 11.10 : *consommé* = transaction(s) au même prix dans [+14 ; +40] ms (heure Polymarket) couvrant la baisse ; *mixte* = couverture partielle ; *retiré* = aucune transaction ; "
      "*déplacé* = retiré et même quantité reposée à un autre prix dans [−5 ; +50] ms ; *indéterminé* = reconstruction non confirmée, pas de 0,001 (cycles au cent), ou après coupure.")
    w("")
    w("| Côté | Toutes baisses | consommé | mixte | retiré | déplacé | indéterminé | Volume consommé / volume des baisses |")
    w("|---|---|---|---|---|---|---|---|")
    for s in (1, 0):
        c = collections.Counter()
        for (s_, c_, f_), v in cnt.items():
            if s_ == s: c[c_] += v
        w(f"| {NOM_SIDE[s]} | {fr(sum(c.values()), 0)} | {fr(c['consommé'], 0)} | {fr(c['mixte'], 0)} | {fr(c['retiré'], 0)} | {fr(c['déplacé'], 0)} | {fr(c['indéterminé'], 0)} | {pc(vol[(s, 't')], vol[(s, 'd')])} |")
    w("")
    w("**Disparitions complètes du meilleur niveau, par cause**")
    w("")
    w("| Côté | Disparitions | consommé | mixte | retiré | déplacé | indéterminé | Durée au meilleur rang (ms) 10 % · méd. · 90 % — consommé | — retiré/déplacé | Taille méd. (parts) consommé · retiré |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    for s in (1, 0):
        L = [x for x in FULL if x[1] == s]; c = collections.Counter(x[2] for x in L)
        ac = [x[3] for x in L if x[2] in ("consommé", "mixte")]; ar = [x[3] for x in L if x[2] in ("retiré", "déplacé")]
        zc = [x[5] for x in L if x[2] in ("consommé", "mixte")]; zr = [x[5] for x in L if x[2] in ("retiré", "déplacé")]
        w(f"| {NOM_SIDE[s]} | {fr(len(L), 0)} | {fr(c['consommé'], 0)} | {fr(c['mixte'], 0)} | {fr(c['retiré'], 0)} | {fr(c['déplacé'], 0)} | {fr(c['indéterminé'], 0)} | {q3(ac, 0)} | {q3(ar, 0)} | {fr(float(np.median(zc)), 1)} · {fr(float(np.median(zr)), 1)} |")
    w(f"| **total** | {fr(len(FULL), 0)} | {fr(cF['consommé'], 0)} | {fr(cF['mixte'], 0)} | {fr(cF['retiré'], 0)} | {fr(cF['déplacé'], 0)} | {fr(cF['indéterminé'], 0)} | | | |")
    w("")
    w("**Stabilité par jour** (disparitions complètes hors indéterminé)")
    w("")
    w("| Jour | Disparitions | retrait (retiré + déplacé) | consommation (consommé + mixte) |")
    w("|---|---|---|---|")
    for j in sorted(jours):
        L = [x for x in Fok if JOUR(x[0]) == j]; r_ = sum(1 for x in L if x[2] in ("retiré", "déplacé"))
        w(f"| {j} | {fr(len(L), 0)} | {pc(r_, len(L))} | {pc(len(L) - r_, len(L))} |")
    w("")
    w("**Remplissage après disparition complète (H499)**")
    w("")
    w("| Côté | Cause | n | Nouvelle quantité au même prix dans 100 · 500 · 1000 ms | Meilleur prix revenu à ce prix ou mieux dans 100 · 500 · 1000 ms |")
    w("|---|---|---|---|---|")
    for s in (1, 0):
        for k in ("consommé", "retiré/déplacé"):
            R_ = rempl[(s, k)]; n_ = R_["n"]
            w(f"| {NOM_SIDE[s]} | {k} | {fr(n_, 0)} | " + " · ".join(pc(R_[('meme', x)], n_) for x in (100, 500, 1000)) + " | " + " · ".join(pc(R_[('retour', x)], n_) for x in (100, 500, 1000)) + " |")
    w("")
    # ---------- 1b
    w("### Phase 1b — offres visées par les signaux réels du bot")
    w("")
    w("Pour chaque signal enregistré, quantité disponible au prix du signal ou mieux suivie 2 s ; *disparue* = moins d'une part. Cause = part du volume disparu expliquée par des transactions appariées (≥ 80 % consommée, ≤ 20 % retirée, sinon mixte). Gagnant : `rapide.json`.")
    w("")
    w("| Catégorie | Signaux | dont gagnants (réglés) | Taux de gain | Disparition (ms) méd. |")
    w("|---|---|---|---|---|")
    for cat in ("consommée", "mixte", "retirée", "encore là à 2 s", "indéterminé"):
        L = [s for s in sg_ok if s["cat"] == cat]
        if not L: continue
        reg = [s for s in L if s["gagne"] is not None]; dd = [s["disp"] for s in L if s["disp"] is not None]
        w(f"| {cat} | {len(L)} | {sum(s['gagne'] for s in reg)}/{len(reg)} | {pc(sum(s['gagne'] for s in reg), len(reg))} | {fr(float(np.median(dd)) if dd else None, 0)} |")
    w("")
    w("Par règle (offre disparue dans 2 s : retirée / consommée+mixte / encore là) :")
    w("")
    w("| Règle | Signaux | retirée | consommée + mixte | encore là à 2 s | gain si retirée | gain si encore là |")
    w("|---|---|---|---|---|---|---|")
    for nom in sorted(set(s["nom"] for s in sg_ok)):
        L = [s for s in sg_ok if s["nom"] == nom]
        f_ = lambda cat: [s for s in L if s["cat"] in cat]
        gr = [s for s in f_(("retirée",)) if s["gagne"] is not None]; ge = [s for s in f_(("encore là à 2 s",)) if s["gagne"] is not None]
        w(f"| {nom} | {len(L)} | {len(f_(('retirée',)))} | {len(f_(('consommée', 'mixte')))} | {len(f_(('encore là à 2 s',)))} | {pc(sum(s['gagne'] for s in gr), len(gr))} ({len(gr)}) | {pc(sum(s['gagne'] for s in ge), len(ge))} ({len(ge)}) |")
    w("")
    sb = [s for s in sg_ok if s["bot"]]; acc = [s for s in sb if (s["disp"] is None) == (s["bot_disp"] is None)]
    acc5 = [s for s in acc if s["disp"] is None or abs(s["disp"] - s["bot_disp"]) <= 5]
    w(f"Contrôle de la reconstruction contre la mesure en direct du bot ({len(sb)} signaux retrouvés dans `rapide.json`) : même verdict disparue / pas disparue pour {len(acc)}/{len(sb)} ({pc(len(acc), len(sb))}), même instant à 5 ms près pour {len(acc5)}/{len(sb)}.")
    w("")
    # ---------- phase 2
    w("## Phase 2 — chronologie : information → réaction → retrait → transaction")
    w("")
    w(f"*Information* (fixée à l'avance, comme le 11.10) : saut ≥ {fr(X_INFO, 0)} $ d'une bourse (Bybit perp, OKX perp, Binance, Coinbase) entre deux échantillons 50 ms, dans le sens qui rend l'offre trop bon marché ; "
      f"heure = réception à Dublin. **Nouveau** : flux net agressif (achats − ventes preneurs des 4 bourses) ≥ {fr(FX_SEUIL / 1000, 0)} k$ dans une tranche de 50 ms (seuil fixé à l'avance, cycles avec `fx` seulement).")
    w("")
    w("Informations détectées : " + ", ".join(f"{k} {fr(nINF[k], 0)}" for k in SRCS + ["fx"]) + ".")
    w("")
    def bloc(nom, n_, A, P=None):
        nP_, AP = (P if P else (0, []))
        w(f"**{nom}** — disparitions complètes (hors indét., dans le cycle) : {fr(n_, 0)} ; précédées d'une information : **{fr(len(A), 0)}** ({pc(len(A), n_)})"
          + (f" — témoin au hasard (20 tirages) : {pc(len(AP), nP_)}." if P else "."))
        w("")
        if not A: return
        w("| Mesure (ms après l'information) | n | 10 % · médiane · 90 % | témoin : médiane |")
        w("|---|---|---|---|")
        for k, lab in (("react", "1re réaction de l'autre côté"), ("ret", "1er retrait au meilleur niveau"), ("cons", "1re consommation au meilleur niveau"), ("dt_info", "disparition complète")):
            v = [r[k] for r in A if r.get(k) is not None]; vp = [r[k] for r in AP if r.get(k) is not None]
            w(f"| {lab} | {fr(len(v), 0)} | {q3(v, 0)} | {fr(float(np.median(vp)) if vp else None, 0)} |")
        w("")
        pr_, pp_ = premier(A), premier(AP)
        lab = {"REQ": "retrait d'abord", "SW": "consommation d'abord", "SIM": "même ms", "AUC": "aucun avant la disparition"}
        w("Premier après l'information : " + " ; ".join(f"{lab[k]} {pc(v, len(A))}" + (f" (témoin {pc(pp_[k], len(AP))})" if P else "") for k, v in pr_.most_common()) + ".")
        w("")
        R_ = [r for r in A if r.get("ts") is not None]; RP = [r for r in AP if r.get("ts") is not None]
        w(f"Course : avant la disparition complète {pc(sum(r['course_demi'] for r in R_), len(R_))} (aller simple 14 ms), {pc(sum(r['course_rtt'] for r in R_), len(R_))} (aller-retour 28 ms) ; "
          f"**avant la 1re baisse du niveau : {pc(sum(r['avant_1re'] for r in R_), len(R_))}**" + (f" — témoin {pc(sum(r['course_demi'] for r in RP), len(RP))} et {pc(sum(r['avant_1re'] for r in RP), len(RP))}." if P else "."))
        w("")
    bloc(f"Bourses, saut ≥ {fr(X_INFO, 0)} $ (critère principal)", CH["bourses"][0], CH["bourses"][1], CHP["bourses"])
    bloc("Sensibilité : bourses, saut ≥ 2 $", CH["b2"][0], CH["b2"][1])
    bloc("Chainlink (nouvelle valeur dans le bon sens)", CH["cl"][0], CH["cl"][1], CHP["cl"])
    if CH["fx"][0]: bloc(f"Flux agressifs ≥ {fr(FX_SEUIL / 1000, 0)} k$ en 50 ms (nouveau)", CH["fx"][0], CH["fx"][1], CHP["fx"])
    w(f"**Course déclenchée par le carnet lui-même** : délai ≈ {fr(delai_msg, 1)} ms ; durée au meilleur rang des niveaux qui disparaissent {q3(vies, 0)} ms ; plus longue que notre délai pour **{pc(ok_v, nv)}**.")
    w("")
    w("### Précurseurs d'une consommation complète (contre 3 instants témoins au hasard par événement)")
    w("")
    w("| Fenêtre | Consommations · témoins | " + " | ".join(NOMS_VAR) + " | Modèle combiné (AUC, validation croisée par cycle) |")
    w("|---|---|" + "---|" * len(NOMS_VAR) + "---|")
    for (h, mode), P_ in PR.items():
        lab = f"{h} ms, jusqu'à t−1 ms" if mode == "t-1" else f"{h} ms, arrêté à t−{h} ms"
        w(f"| {lab} | {fr(P_['n1'], 0)} · {fr(P_['n0'], 0)} | " + " | ".join(f"{fr(a, 3)}" for a in P_["aucs"]) + f" | {fr(P_['auc_cv'], 3)} |")
    w("")
    w("Lecture : « jusqu'à t−1 ms » = en grande partie mécanique (la file fond déjà) ; « arrêté à t−h » = seulement ce qui était connu h ms avant (utilisable). Témoins non appariés sur prix ni taille.")
    w("")
    w("## Limites")
    w("")
    w("- 3 jours et demi (11.10 → 14.10), un seul actif (BTC 5 min). Les bourses arrivent à Dublin avec ~45 ms (Coinbase) à ~100–130 ms (Bybit, OKX, Binance) de retard ; échantillon 50 ms.")
    w("- Profondeur au-delà de ±3 c périmée entre deux carnets complets (10 s). Horloges Dublin (NTP) / Polymarket comparées directement (décalage inclus dans les 8,6 ms).")
    w(f"- Durée d'exécution : {time.time() - T0:.0f} s.")
    open(SORTIE, "w").write("\n".join(md) + "\n")
    print("écrit", SORTIE, f"{time.time() - T0:.1f} s")


if __name__ == "__main__":
    main()
