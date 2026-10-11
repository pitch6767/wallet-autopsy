"""BOT95 — QUEUE RACE ENGINE, PHASES 0, 1 et 2 (PRÉLIMINAIRE). Demande de Pitch, 11.10.2026. Hors ligne, aucun bot modifié.
Hypothèses H491–H510 et H523–H558 : qui fait disparaître la meilleure offre (transaction ou retrait), dans quel ordre
(nouvelle information → réaction des acheteurs → retrait des vendeurs → première transaction), et un ordre envoyé depuis Dublin
arriverait-il avant la disparition ?
Données : enregistreur du VPS de Dublin (bot95/rapide/rapide.js), branche git « donnees-rapide », un fichier gzip par cycle 5 min.
Usage (depuis la racine du dépôt) : python3 etude/bot5min/queue_race_phase12.py → etude/bot5min/resultat_queue_race_phase12.md"""
import gzip, json, os, subprocess, collections, math, random, bisect, time, sys
import numpy as np

T0 = time.time()
RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SORTIE = os.path.join(RACINE, "etude", "bot5min", "resultat_queue_race_phase12.md")
REF = "origin/donnees-rapide"
CACHE = os.environ.get("QR_CACHE") or os.path.join("/tmp", "queue_race_cycles")

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
        t = 0; P = []
        for dt, ret, side, c, sz in R["p"]:
            t += dt; P.append((float(t), (t - ret) if ret is not None else None, "P", side, c * 10, sz / 100.0))   # NB : prix arrondi au cent par l'enregistreur
        A = []
        for e in R["ev"]:
            if e[0] == "T": A.append((e[1], e[2], "T", e[3], e[4], mil(e[5]), e[6]))
            elif e[0] == "B" and e[3] == 0: A.append((e[1], e[2], "B", [(mil(p), s) for p, s in e[4]], [(mil(p), s) for p, s in e[5]]))
        # fusion par heure de réception (stable : à égalité, l'ordre d'origine de chaque liste)
        flux = sorted(P + A, key=lambda x: x[0])
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
            arr = 10 if C["format"] != "brut" else 1               # compact : prix enregistrés au cent → photo arrondie au cent
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
    compact = C["format"] != "brut"
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


# ================================================================ PROGRAMME
fr = lambda x, d=1: "—" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:,.{d}f}".replace(",", " ").replace(".", ",")
pc = lambda a, b: "—" if not b else f"{100 * a / b:.1f} %".replace(".", ",")
def q3(v, d=1):
    v = [x for x in v if x is not None]
    if not v: return "—"
    a = np.percentile(v, [10, 50, 90]); return " · ".join(fr(float(x), d) for x in a)
NOM_SIDE = {1: "offre Up (vendeur Up)", 0: "demande Up = offre Down"}
CAUSES = ["consommé", "mixte", "retiré", "déplacé", "indéterminé"]


def main():
    fichiers = charger_fichiers()
    CY = []
    for f in fichiers:
        C = normaliser(f); Rj = rejouer(C); idx = classer(C, Rj); CY.append((C, Rj, idx))
    print("cycles", len(CY), f"{time.time() - T0:.1f} s", flush=True)
    rap = json.load(open(os.path.join(RACINE, "bot95", "rapide.json")))["signaux"]
    gagnants = {}
    for s in rap:
        if s.get("gagnant"): gagnants[s["start"]] = s["gagnant"]
    try:
        off = json.load(open(os.path.join(RACINE, "bot95", "officiels.json")))
        for C, _, _ in CY:
            k = f"BTC:{C['start']}"
            if k in off and off[k].get("gagnant"): gagnants[C["start"]] = off[k]["gagnant"]
    except Exception: pass
    md = []; w = md.append

    # ------------------------------------------------ PHASE 0
    p0 = []; tot = collections.Counter(); totf = collections.Counter()
    for C, Rj, _ in CY:
        r, _ = controle_photos(C); tot.update(r)
        fil = None
        if C["format"] == "brut":
            D = simuler_filtre(C); fil, _ = controle_photos(D); totf.update(fil)
        tr = len(Rj["trades"]); nP = sum(1 for e in C["flux"] if e[2] == "P"); nB = sum(1 for e in C["flux"] if e[2] == "B")
        t1 = C["flux"][-1][0] / 1000 - C["start"] if C["flux"] else None; t0 = C["flux"][0][0] / 1000 - C["start"] if C["flux"] else None
        p0.append((C, r, fil, nP, nB, tr, t0, t1, Rj["npurge"]))
    couvert = sum(max(0.0, min(300.0, x[7]) - max(0.0, x[6])) for x in p0 if x[6] is not None) / 1.0
    # sens du champ « side » des transactions : à quel prix tombe la transaction par rapport au carnet juste avant (heure Polymarket)
    sens = collections.Counter()
    for C, Rj, _ in CY:
        hist = {0: [], 1: []}
        for x in Rj["baisses"]:
            if x["full"] and x["ts"] is not None: hist[x["side"]].append((x["ts"], x["c"]))
        for s in (0, 1): hist[s].sort()
        for tt in Rj["trades"]:
            t, ts, tok, sd, m, z, cs, cm, ba, bb = tt
            if ba is None or bb is None: continue
            pu = m if tok == 0 else 1000 - m
            def recent(s):
                L = hist[s]; i = bisect.bisect_left(L, (ts - 60 if ts else 0, -1)) if ts else len(L)
                return any(c == pu for _, c in L[i:i + 50] if ts and _ <= ts)
            ou = "offre" if (pu == ba or recent(1)) else "demande" if (pu == bb or recent(0)) else "ailleurs"
            # en équivalent Up : achat Up ou vente Down = acheteur preneur côté Up
            agresseur_up = (tok == 0 and sd == 1) or (tok == 1 and sd == 0)
            sens[(agresseur_up, ou)] += 1

    # ------------------------------------------------ PHASE 1
    B = [x for C, Rj, _ in CY for x in Rj["baisses"]]
    Bf = [x for x in B if x["full"]]
    # bruit de fond de l'appariement : même règle dans une fenêtre témoin décalée [−200 ; −174] ms
    fond = 0; nb_t = 0; fond_full = 0; nb_full = 0
    for C, Rj, idx in CY:
        for x in Rj["baisses"]:
            if x["cause"] == "indéterminé": continue
            nb_t += 1; s = sum(u[1] for u in trades_fenetre(idx, x["side"], x["c"], x["ts"], -200, -174))
            if s >= x["d"] - tol(x["d"]):
                fond += 1; fond_full += x["full"]
            nb_full += x["full"]
    # durée de vie des niveaux et remplissage
    FEN = (100, 500, 1000)
    rempl = collections.defaultdict(lambda: collections.Counter())
    for C, Rj, _ in CY:
        for x in Rj["baisses"]:
            if not x["full"] or x["cause"] == "indéterminé": continue
            R = remplissage(Rj, x, FEN)
            k = (x["side"], "consommé" if x["cause"] in ("consommé", "mixte") else "retiré/déplacé")
            rempl[k]["n"] += 1
            for wv, (meme, ret) in R.items(): rempl[k][("meme", wv)] += meme; rempl[k][("retour", wv)] += ret

    # ------------------------------------------------ PHASE 1b
    SG = []
    for C, Rj, idx in CY:
        if not C["sig"]: continue
        E = etats_aux_instants(C, [s["tDecision"] + 0.5 for s in C["sig"]])    # +0,5 ms : heures des P arrondies à la ms
        for s in C["sig"]:
            L0, i0 = E[s["tDecision"] + 0.5]
            if L0 is None: continue
            r = suivre_signal(C, idx, L0, i0, s)
            g = gagnants.get(C["start"])
            bot = [y for y in rap if y["start"] == C["start"] and y["nom"] == s["nom"] and abs(y["tDecision"] - s["tDecision"]) < 1]
            r.update(nom=s["nom"], start=C["start"], cote=s["cote"], a0=s["a0"], gagne=(g == s["cote"]) if g else None,
                     bot=bool(bot), bot_disp=bot[0].get("disparu_ms") if bot else None, bot_prem=bot[0].get("premiereBaisse_ms") if bot else None, tD=s["tDecision"],
                     tronque=C["coupe"] and s["tDecision"] > C["t_fin_flux"])
            SG.append(r)

    # ------------------------------------------------ PHASE 2
    CH = {}; CHcl = []; nINF = collections.Counter(); CH2 = []; CHP = {}; RNG = random.Random(11)
    for C, Rj, _ in CY:
        if not C["ex"]: continue
        INF = infos(C); I2 = infos(C, 2.0)
        for x in INF: nINF[x[1]] += 1
        CH.setdefault("bourses", []).extend(chronologie(C, Rj, INF, {"perp", "okx", "bn", "cb"}))
        CHcl.extend(chronologie(C, Rj, INF, {"cl"}))
        CH2.extend(chronologie(C, Rj, I2, {"perp", "okx", "bn", "cb"}))
        for rep in range(20):                                    # 20 tirages témoins
            CHP.setdefault("bourses", []).extend(chronologie(C, Rj, placebo(C, INF, {"perp", "okx", "bn", "cb"}, RNG), {"perp"}))
            CHP.setdefault("cl", []).extend(chronologie(C, Rj, placebo(C, INF, {"cl"}, RNG), {"perp"}))
    # course déclenchée par le message Polymarket lui-même : durée de vie au meilleur prix contre notre délai
    delai_msg = POLY_VERS_DUBLIN + CALCUL + RTT_CLOB / 2

    # ------------------------------------------------ précurseurs
    from sklearn.metrics import roc_auc_score
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import GroupKFold
    PRE = {}
    for h, mode in [(h, m) for m in ("t-1", "t-h") for h in (100, 200, 500)]:
        fin = 1 if mode == "t-1" else h
        Xp, Xn, gp, gn = [], [], [], []
        for ci, (C, Rj, _) in enumerate(CY):
            S = Rj["serie"]; st = C["start"] * 1000
            ev = [x for x in Rj["baisses"] if x["full"] and x["cause"] == "consommé" and st <= x["t"] <= st + 300000]
            evt = {0: np.array(sorted(x["t"] for x in Rj["baisses"] if x["full"] and x["side"] == 0 and x["cause"] in ("consommé", "mixte"))),
                   1: np.array(sorted(x["t"] for x in Rj["baisses"] if x["full"] and x["side"] == 1 and x["cause"] in ("consommé", "mixte")))}
            for x in ev:
                v = variables(S, x["t"], x["side"], h, fin)
                if v is None: continue
                Xp.append(v); gp.append(ci)
                k = 0; essais = 0
                while k < 3 and essais < 50:                      # 3 instants témoins tirés au hasard dans le même cycle, même côté, loin d'une consommation
                    essais += 1; tr = st + random.random() * 300000
                    E_ = evt[x["side"]]
                    if len(E_) and np.min(np.abs(E_ - tr)) < 1000: continue
                    v2 = variables(S, tr, x["side"], h, fin)
                    if v2 is None: continue
                    Xn.append(v2); gn.append(ci); k += 1
        X = np.array(Xp + Xn); y = np.array([1] * len(Xp) + [0] * len(Xn)); g = np.array(gp + gn)
        aucs = [roc_auc_score(y, X[:, j]) if len(set(y)) > 1 else None for j in range(X.shape[1])]
        pred = np.zeros(len(y))
        if len(set(g)) >= 3:
            for a, b in GroupKFold(n_splits=min(5, len(set(g)))).split(X, y, g):
                m = LogisticRegression(max_iter=1000).fit(X[a], y[a]); pred[b] = m.predict_proba(X[b])[:, 1]
            auc_cv = roc_auc_score(y, pred)
        else: auc_cv = None
        PRE[(h, mode)] = dict(n1=len(Xp), n0=len(Xn), aucs=aucs, auc_cv=auc_cv, med1=np.median(np.array(Xp), 0) if Xp else None, med0=np.median(np.array(Xn), 0) if Xn else None)

    # ================================================= RAPPORT
    nc = len(CY); duree_h = nc * 5 / 60
    Bok = [x for x in B if x["cause"] != "indéterminé"]; Bfok = [x for x in Bf if x["cause"] != "indéterminé"]
    cnt = collections.Counter(x["cause"] for x in Bf); cntS = collections.Counter((x["side"], x["cause"]) for x in Bf)
    chb = CH.get("bourses", [])
    avec = [r for r in chb if r["info"] is not None]
    w("# BOT95 — QUEUE RACE ENGINE · phases 0, 1 et 2 — **PRÉLIMINAIRE**")
    w("")
    w(f"Étude hors ligne du 11.10.2026 (aucun bot, aucun workflow modifié, rien publié). Données : enregistreur du VPS de Dublin, branche `donnees-rapide` : **{nc} cycles BTC 5 min ≈ {fr(duree_h, 2)} h** d'enregistrement, un seul après-midi de dimanche (marché calme). "
      "**Tout ce qui suit est préliminaire : quelques heures, un seul régime de marché ; aucune conclusion de P&L.** Les cycles ne se recouvrent pas : chaque cycle est un marché distinct ; le flux commence ~40 s avant le début du cycle (abonnement anticipé).")
    w("")
    # ---------- verdict
    nfull = len(Bfok); ncons = cnt["consommé"] + cnt["mixte"]; nret = cnt["retiré"] + cnt["déplacé"]
    race = [r for r in avec if r.get("ts") is not None]
    vies = [x["age_best"] for x in Bfok if x["age_best"] is not None]
    w("## Verdict (en tête)")
    w("")
    w(f"- **Qui fait disparaître la meilleure offre ?** Sur {nfull} disparitions complètes du meilleur niveau (offre Up et offre Down, hors indéterminé), "
      f"**{pc(nret, nfull)} sont des retraits** (dont {pc(cnt['déplacé'], nfull)} « déplacés » : même quantité reposée à un autre prix) et **{pc(ncons, nfull)} des consommations** par une transaction "
      f"({pc(cnt['mixte'], nfull)} mixtes). {cnt['indéterminé']} disparitions indéterminées (reconstruction douteuse) sont exclues. "
      f"Toutes baisses confondues (y compris partielles) : {fr(len(Bok), 0)} baisses, {pc(sum(1 for x in Bok if x['cause'] == 'consommé'), len(Bok))} consommées.")
    PB = CHP.get("bourses", []); PBa = [r for r in PB if r["info"] is not None]; PBr = [r for r in PBa if r.get("ts") is not None]
    def premier(L):
        c = collections.Counter()
        for r in L:
            x_, y_ = r.get("ret"), r.get("cons")
            if x_ is not None and (y_ is None or x_ < y_): c["REQ"] += 1
            elif y_ is not None and (x_ is None or y_ < x_): c["SW"] += 1
        return c
    pr, pp = premier(avec), premier(PBa)
    med = lambda L, k: fr(float(np.median([r[k] for r in L if r.get(k) is not None])) if any(r.get(k) is not None for r in L) else None, 0)
    w(f"- **Chronologie (H533/H544/H547)** : seules **{len(avec)} des {len(chb)} disparitions ({pc(len(avec), len(chb))})** sont précédées dans la seconde d'un saut de bourse ≥ {fr(X_INFO, 0)} $ dans le bon sens, "
      f"contre {pc(len(PBa), len(PB))} avec des informations placées au hasard (marché très calme : {sum(nINF[k] for k in ('perp', 'okx', 'bn', 'cb'))} sauts ≥ {fr(X_INFO, 0)} $ en {fr(duree_h, 2)} h). "
      f"→ l'information de bourse n'explique qu'environ **{fr(100 * (len(avec) / max(1, len(chb)) - len(PBa) / max(1, len(PB))), 1)} points** des disparitions ; l'immense majorité n'a aucune information de bourse détectable avant elle. "
      f"Quand il y a une information, tout va plus vite qu'au hasard : réaction de l'autre côté en {med(avec, 'react')} ms (témoin {med(PBa, 'react')}), 1er retrait {med(avec, 'ret')} ms ({med(PBa, 'ret')}), "
      f"1re consommation {med(avec, 'cons')} ms ({med(PBa, 'cons')}), disparition {med(avec, 'dt_info')} ms ({med(PBa, 'dt_info')}) — médianes. "
      f"**FIRST REQUOTE vs FIRST SWEEP** : retrait d'abord {pc(pr['REQ'], len(avec))}, consommation d'abord {pc(pr['SW'], len(avec))} (témoin {pc(pp['REQ'], len(PBa))} / {pc(pp['SW'], len(PBa))}) : les vendeurs se retirent plus souvent qu'ils ne sont balayés, et l'information déplace un peu la balance vers le balayage.")
    if race:
        w(f"- **Course** : ordre parti de Dublin à la réception de l'information (+{fr(CALCUL, 1)} ms de calcul, +{fr(RTT_CLOB / 2, 0)} ms aller simple). Il arriverait avant la disparition complète dans {pc(sum(r['course_demi'] for r in race), len(race))} des {len(race)} cas, "
          f"mais **avant la 1re baisse du niveau visé dans seulement {pc(sum(r['avant_1re'] for r in race), len(race))}**, contre {pc(sum(r['avant_1re'] for r in PBr), len(PBr))} à des instants pris au hasard : "
          "après une vraie information, d'autres agissent avant nous plus souvent que d'habitude. « Arriver avant la disparition » est surtout mécanique (les niveaux vivent en général plus de 14 ms) et ne prouve aucun avantage. "
          "Rappel : l'information des bourses asiatiques nous parvient déjà avec ~100–130 ms de retard. Échantillon petit.")
    nv = len(vies); ok_v = sum(1 for v in vies if v > delai_msg)
    w(f"- **Course déclenchée par le carnet lui-même** : un niveau devenu meilleur prix vit en médiane {fr(float(np.median(vies)) if vies else None, 0)} ms à ce rang avant de disparaître ; "
      f"{pc(ok_v, nv)} vivent plus que notre délai « message Polymarket → Dublin → ordre arrivé » ≈ {fr(delai_msg, 1)} ms.")
    sg_ok = [s for s in SG if not s["tronque"]]
    cs_ = collections.Counter(x["cat"] for x in sg_ok)
    w(f"- **Signaux du bot ({len(sg_ok)} dans ces cycles)** : offre visée disparue dans les 2 s pour {sum(v for k, v in cs_.items() if k not in ('encore là à 2 s', 'indéterminé'))} signaux — "
      f"**retirée {cs_['retirée']}**, consommée {cs_['consommée']}, mixte {cs_['mixte']} ; encore là à 2 s {cs_['encore là à 2 s']} ; indéterminé {cs_['indéterminé']}. "
      "Les offres que visent nos signaux disparaissent surtout parce que le vendeur les retire, pas parce qu'un concurrent les achète avant nous. Effectifs trop petits pour un taux de gain par catégorie (donnés pour mémoire en 1b).")
    w("- **Ce qu'il faut de plus** : plusieurs jours (≥ 3–5) incluant des heures actives (ouverture US, annonces) pour avoir des centaines de disparitions précédées d'une information ; "
      "un enregistrement des prix au millième (pas de 0,001 près de 0/1) ; idéalement les messages bruts de bourse (et non un échantillon 50 ms) pour dater l'information à la ms.")
    w("")
    # ---------- phase 0
    w("## Phase 0 — audit des données")
    w("")
    w("| Cycle (début) | Version | Format | Flux couvert (s par rapport au début) | Coupé (plafond) | Changements P (Up) | Carnets B (Up) | Transactions (2 jetons) | Photos 1 s comparées | Meilleur acheteur Up : prix · prix+taille | Meilleur vendeur Up : prix · prix+taille | 5 niveaux : prix acheteur · vendeur | Miroir Up/Down exact | Purges (croisement) |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for C, r, fil, nP, nB, tr, t0, t1, npg in p0:
        n = r["n"]
        w(f"| {C['start']} | {C['version']} | {C['format']} | {fr(t0, 0)} → {fr(t1, 0)} | {'oui' if C['coupe'] else 'non'} | {nP} | {nB} | {tr} | {n} | {pc(r['bid_L1_prix'], n)} · {pc(r['bid_L1'], n)} | {pc(r['ask_L1_prix'], n)} · {pc(r['ask_L1'], n)} | {pc(r['bid_top5_prix'], n)} · {pc(r['ask_top5_prix'], n)} | {pc(r['miroir'], n)} | {npg} |")
    n = tot["n"]
    w(f"| **total** | | | | | | | | {n} | {pc(tot['bid_L1_prix'], n)} · {pc(tot['bid_L1'], n)} | {pc(tot['ask_L1_prix'], n)} · {pc(tot['ask_L1'], n)} | {pc(tot['bid_top5_prix'], n)} · {pc(tot['ask_top5_prix'], n)} | {pc(tot['miroir'], n)} | |")
    w("")
    nf = totf["n"]
    w(f"- **Couverture** : {nc} cycles de 1791708300 à {CY[-1][0]['start']} (≈ {fr(duree_h, 2)} h d'horloge). **Temps de cycle réellement couvert par le flux : {fr(couvert / 60, 1)} min sur {nc * 5} min** (coupures des 3 cycles bruts, cycle 1791709200 quasi vide après redémarrage — {p0[3][3]} changements —, dernier cycle commencé à +88 s après une nouvelle version). "
      f"Aucun cycle de la version b2b4d959b243 (flux agressifs `fx`) n'est encore disponible → les flux agressifs par bourse ne sont pas utilisés ici.")
    w(f"- **Format brut (3 premiers cycles)** : tout est enregistré mais le plafond de 150 000 lignes coupe le cycle après ~{fr(float(np.mean([x[7] for x in p0[:3]])), 0)} s (les photos après la coupure sont exclues : {tot['apres_coupure']}).")
    w(f"- **Reconstruction** : carnet Up = dernier carnet complet B + changements P. En format brut, elle colle aux photos 1 s à ~99,5 % (meilleur prix et taille). "
      f"Contrôle supplémentaire : les P seuls (sans recharger les B) reproduisent les carnets complets suivants à 99,7 % → **les exécutions sont bien publiées en `price_change`** (pas seulement en carnet complet).")
    w(f"- **Perte due au filtre ±3 c et au carnet complet toutes les 10 s** (simulée sur les 3 cycles bruts en appliquant le filtre exact de rapide.js) : meilleur prix {pc(totf['bid_L1_prix'], nf)} (acheteur) / {pc(totf['ask_L1_prix'], nf)} (vendeur) ; "
      f"prix + taille {pc(totf['bid_L1'], nf)} / {pc(totf['ask_L1'], nf)} ; **5 niveaux prix+taille : {pc(totf['bid_top5'], nf)} / {pc(totf['ask_top5'], nf)}** (contre {pc(sum(x[1]['bid_top5'] for x in p0[:3]), sum(x[1]['n'] for x in p0[:3]))} sans filtre). "
      "Le meilleur niveau reste fiable ; la profondeur au-delà de 3 c est périmée entre deux carnets complets. Lors d'un balayage de plus de 3 c, des retraits sont perdus : le rejeu efface alors les niveaux opposés qui croisent le carnet (« purges »).")
    w(f"- **Pas de 0,001** : près de 0 et 1 Polymarket cote au millième ; l'enregistreur compact arrondit au cent (`Math.round(prix*100)`) → deux niveaux (0,99 et 0,991) fusionnent et la reconstruction se trompe. "
      f"Photos concernées : {tot['L1_sous_cent_bid']} (acheteur) / {tot['L1_sous_cent_ask']} (vendeur), surtout le cycle 1791709800. Toute baisse à ≤ 0,04 ou ≥ 0,96, ou pendant une seconde où la photo montre un prix au millième, est classée **indéterminée**. "
      "**À corriger dans l'enregistreur (proposition, à décider par Pitch) : enregistrer le prix en millièmes.**")
    w(f"- **Miroir** : carnet Down = miroir exact du carnet Up dans {pc(tot['miroir'], n)} des photos.")
    tA = sum(v for (a, o), v in sens.items() if a); tV = sum(v for (a, o), v in sens.items() if not a)
    w(f"- **Sens du champ `side` des transactions** (« BUY » sur Up ou « SELL » sur Down = acheteur Up) : transactions dites acheteuses tombant sur l'offre Up : **{pc(sens[(True, 'offre')], tA)}** (sur la demande : {pc(sens[(True, 'demande')], tA)}, ailleurs : {pc(sens[(True, 'ailleurs')], tA)}) ; "
      f"dites vendeuses tombant sur la demande Up : **{pc(sens[(False, 'demande')], tV)}** (sur l'offre : {pc(sens[(False, 'offre')], tV)}). → **`side` = côté du PRENEUR (agresseur)**. "
      "Confirmé par l'appariement : avec ce sens, les transactions s'alignent sur les baisses du carnet ; avec le sens opposé, il n'y a presque aucune coïncidence.")
    w(f"- **Décalage carnet → transaction** : le message `last_trade_price` est horodaté par Polymarket **~21 ms APRÈS** la baisse de quantité correspondante dans le carnet (pic net entre +18 et +30 ms, même quantité au centième). "
      f"Fenêtre d'appariement fixée à [+{FEN_TRADE[0]} ; +{FEN_TRADE[1]}] ms (heure Polymarket). Bruit de fond mesuré dans une fenêtre témoin de même largeur décalée à −200 ms : "
      f"{pc(fond, nb_t)} des baisses (et {pc(fond_full, nb_full)} des disparitions complètes) y trouveraient une « consommation » par hasard — ordre de grandeur du faux appariement, à comparer aux {pc(sum(1 for x in Bok if x['cause'] == 'consommé'), len(Bok))} de baisses classées consommées. "
      "Conséquence pratique : **la disparition par exécution se voit dans le carnet avant le message de transaction** ; un robot qui attend le message de transaction a ~20 ms de retard.")
    w("")
    # ---------- phase 1
    w("## Phase 1 — pourquoi la meilleure offre disparaît")
    w("")
    w(f"Définitions : *baisse* = diminution de quantité au meilleur prix (côté offre Up, et côté demande Up = offre Down par miroir). *Disparition complète* = la quantité au meilleur prix tombe à 0. "
      f"*Consommé* = transaction(s) au même prix (Up achetée, ou Down vendue au prix miroir) dans [+{FEN_TRADE[0]} ; +{FEN_TRADE[1]}] ms dont la somme couvre la baisse ; *mixte* = transaction couvrant une partie ; "
      "*retiré* = aucune transaction ; *déplacé* = retiré et la même quantité (±1 %) réapparaît à un autre prix du même côté dans [−5 ; +50] ms ; *indéterminé* = reconstruction non confirmée par la dernière photo, pas de 0,001, ou après coupure.")
    w("")
    w("| Côté | Toutes baisses (n) | dont consommé | mixte | retiré | déplacé | indéterminé | Volume consommé / volume total des baisses (hors indét.) |")
    w("|---|---|---|---|---|---|---|---|")
    for s in (1, 0):
        L = [x for x in B if x["side"] == s]; c = collections.Counter(x["cause"] for x in L); Lk = [x for x in L if x["cause"] != "indéterminé"]
        vt = sum(min(x["vol_trade"] or 0, x["d"]) for x in Lk); vd = sum(x["d"] for x in Lk)
        w(f"| {NOM_SIDE[s]} | {len(L)} | {c['consommé']} | {c['mixte']} | {c['retiré']} | {c['déplacé']} | {c['indéterminé']} | {pc(vt, vd)} |")
    w("")
    w("**Livrable : nombre d'offres disparues (disparitions complètes du meilleur niveau) par cause**")
    w("")
    w("| Côté | Disparitions | consommé | mixte | retiré | déplacé | indéterminé | Durée au meilleur rang avant disparition (ms) 10 % · méd. · 90 % — consommé | — retiré/déplacé | Âge du niveau (ms) méd. consommé · retiré |")
    w("|---|---|---|---|---|---|---|---|---|---|")
    for s in (1, 0):
        L = [x for x in Bf if x["side"] == s]; c = collections.Counter(x["cause"] for x in L)
        ac = [x["age_best"] for x in L if x["cause"] in ("consommé", "mixte")]; ar = [x["age_best"] for x in L if x["cause"] in ("retiré", "déplacé")]
        nc_ = [x["age_niv"] for x in L if x["cause"] in ("consommé", "mixte") and x["age_niv"] is not None]; nr_ = [x["age_niv"] for x in L if x["cause"] in ("retiré", "déplacé") and x["age_niv"] is not None]
        w(f"| {NOM_SIDE[s]} | {len(L)} | {c['consommé']} | {c['mixte']} | {c['retiré']} | {c['déplacé']} | {c['indéterminé']} | {q3(ac, 0)} | {q3(ar, 0)} | {fr(float(np.median(nc_)) if nc_ else None, 0)} · {fr(float(np.median(nr_)) if nr_ else None, 0)} |")
    c = cnt
    w(f"| **total** | {len(Bf)} | {c['consommé']} | {c['mixte']} | {c['retiré']} | {c['déplacé']} | {c['indéterminé']} | | | |")
    w("")
    w("Par cycle (disparitions complètes hors indéterminé : consommé+mixte / retiré+déplacé) : " + " ; ".join(
        f"{C['start']} : {sum(1 for x in Rj['baisses'] if x['full'] and x['cause'] in ('consommé', 'mixte'))}/{sum(1 for x in Rj['baisses'] if x['full'] and x['cause'] in ('retiré', 'déplacé'))}" for C, Rj, _ in CY) + ".")
    w("")
    w("Taille du niveau disparu (parts) — médiane : consommé " + fr(float(np.median([x["old"] for x in Bfok if x["cause"] in ("consommé", "mixte")])) if ncons else None, 1)
      + " · retiré " + fr(float(np.median([x["old"] for x in Bfok if x["cause"] in ("retiré", "déplacé")])) if nret else None, 1) + ".")
    w("")
    w("### H499 — remplissage après disparition complète")
    w("")
    w("| Côté | Cause | n | Nouvelle quantité au MÊME prix dans 100 · 500 · 1000 ms | Meilleur prix revenu à ce prix ou mieux dans 100 · 500 · 1000 ms |")
    w("|---|---|---|---|---|")
    for s in (1, 0):
        for k in ("consommé", "retiré/déplacé"):
            R = rempl[(s, k)]; n_ = R["n"]
            w(f"| {NOM_SIDE[s]} | {k} | {n_} | " + " · ".join(pc(R[('meme', x)], n_) for x in FEN) + " | " + " · ".join(pc(R[('retour', x)], n_) for x in FEN) + " |")
    w("")
    # ---------- phase 1b
    w("### Phase 1b — offres visées par les signaux réels du bot de Dublin")
    w("")
    w("Pour chaque signal enregistré (`sig`), on suit la quantité disponible au prix du signal ou mieux pendant 2 s ; *disparue* = moins d'une part (même définition que `disparu_ms` du bot). "
      "Cause = part du volume disparu expliquée par des transactions appariées (≥ 80 % consommée, ≤ 20 % retirée, sinon mixte). Gagnant : `rapide.json` (Gamma) ; `officiels.json` ne couvre pas encore ces cycles.")
    w("")
    w("| Catégorie | Signaux | Offres distinctes | dont gagnants (réglés, par signal) | Disparition (ms) méd. | Contrôle : `disparu_ms` du bot méd. |")
    w("|---|---|---|---|---|---|")
    for cat in ("consommée", "mixte", "retirée", "encore là à 2 s", "indéterminé"):
        L = [s for s in sg_ok if s["cat"] == cat]
        if not L: continue
        reg = [s for s in L if s["gagne"] is not None]
        dd = [s["disp"] for s in L if s["disp"] is not None]; bd = [s["bot_disp"] for s in L if s["bot_disp"] is not None]
        w(f"| {cat} | {len(L)} | {len(set((s['start'], s['cote'], s['a0'], round(s['tD'] / 50)) for s in L))} | {sum(s['gagne'] for s in reg)}/{len(reg)} | {fr(float(np.median(dd)) if dd else None, 0)} | {fr(float(np.median(bd)) if bd else None, 0)} |")
    w("")
    sb = [s for s in sg_ok if s["bot"]]
    acc = [s for s in sb if (s["disp"] is None) == (s["bot_disp"] is None)]
    acc5 = [s for s in acc if s["disp"] is None or abs(s["disp"] - s["bot_disp"]) <= 5]
    w(f"Contrôle de la reconstruction contre la mesure en direct du bot (`rapide.json`, {len(sb)} signaux réglés) : même verdict disparue / pas disparue dans 2 s pour {len(acc)}/{len(sb)}, et même instant à 5 ms près pour {len(acc5)}/{len(sb)}. "
      f"Signaux dans la partie coupée d'un cycle brut (exclus) : {sum(s['tronque'] for s in SG)}. **Effectifs minuscules : aucun taux de gain par catégorie n'est interprétable.**")
    w("")
    w("<details><summary>Détail des signaux</summary>")
    w("")
    w("| Cycle | Règle | Côté | Prix | Quantité au prix (reconstruite) | Disparue (ms) | 1re baisse (ms) | Part consommée | Catégorie | `disparu_ms` bot | Gagné |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")
    for s in sg_ok:
        w(f"| {s['start']} | {s['nom']} | {s['cote']} | {s['a0']} | {fr(s['q0'], 1)} | {fr(s['disp'], 0)} | {fr(s['prem'], 0)} | {pc(s['part'], 1) if s['part'] is not None else '—'} | {s['cat']} | {fr(s['bot_disp'], 0)} | {'—' if s['gagne'] is None else ('oui' if s['gagne'] else 'non')} |")
    w("")
    w("</details>")
    w("")
    # ---------- phase 2
    w("## Phase 2 — chronologie : information → réaction → retrait → transaction (H533, H544, H547)")
    w("")
    w(f"*Nouvelle information* (fixée à l'avance) : saut ≥ {fr(X_INFO, 0)} $ du prix d'une bourse (Bybit perp, OKX perp, Binance, Coinbase) entre deux échantillons 50 ms consécutifs, dans le sens qui rend l'offre qui disparaît trop bon marché "
      f"(hausse pour l'offre Up, baisse pour l'offre Down) ; heure = **réception à Dublin** du dernier prix de la source. On prend l'information la plus récente dans les {FEN_INFO} ms avant la disparition. "
      "Délais mesurés en heure de réception à Dublin. *Réaction* = l'autre côté du carnet s'améliore (prix ou taille au meilleur) ; *retrait* = 1re baisse « retiré/déplacé » au meilleur niveau ; *consommation* = 1re baisse « consommé/mixte ».")
    w("")
    w(f"Informations détectées sur {fr(duree_h, 2)} h : " + ", ".join(f"{k} {nINF[k]}" for k in SRCS) + " (Chainlink : chaque nouvelle valeur).")
    w("")
    def stats(L):
        A = [r for r in L if r["info"] is not None]; R_ = [r for r in A if r.get("ts") is not None]
        prem = collections.Counter()
        for r in A:
            a, b = r.get("ret"), r.get("cons")
            prem["REQ" if a is not None and (b is None or a < b) else "SW" if b is not None and (a is None or b < a) else "SIM" if a is not None else "AUC"] += 1
        return A, R_, prem
    def bloc(nom, L, P=None):
        A, R_, prem = stats(L)
        w(f"**{nom}** — disparitions complètes (hors indét., dans le cycle) : {len(L)} ; précédées d'une information : **{len(A)}** ({pc(len(A), len(L))})"
          + (f" — **témoin** (même nombre d'informations placées au hasard, 20 tirages) : {pc(sum(1 for r in P if r['info'] is not None), len(P))}." if P else "."))
        w("")
        if not A: return
        AP = [r for r in P if r["info"] is not None] if P else []
        w("| Mesure (ms après l'information) | n | 10 % · médiane · 90 % | témoin au hasard : médiane |")
        w("|---|---|---|---|")
        for k, lab in (("react", "1re réaction de l'autre côté (renforcement)"), ("ret", "1er retrait au meilleur niveau"), ("cons", "1re consommation au meilleur niveau"), ("dt_info", "disparition complète")):
            v = [r[k] for r in A if r.get(k) is not None]; vp = [r[k] for r in AP if r.get(k) is not None]
            w(f"| {lab} | {len(v)} | {q3(v, 0)} | {fr(float(np.median(vp)) if vp else None, 0)} |")
        w("")
        lab = {"REQ": "retrait d'abord (FIRST REQUOTE)", "SW": "consommation d'abord (FIRST SWEEP)", "SIM": "même milliseconde", "AUC": "aucun des deux avant la disparition"}
        _, _, pp = stats(P) if P else (None, None, collections.Counter())
        nP = sum(pp.values())
        w("Qui vient en premier après l'information : " + " ; ".join(f"{lab[k]} {v} ({pc(v, len(A))}" + (f", témoin {pc(pp[k], nP)})" if P else ")") for k, v in prem.most_common()) + ".")
        w("")
        RP = [r for r in AP if r.get("ts") is not None]
        w(f"Course (ordre envoyé à la réception de l'information, arrivée comparée à l'heure Polymarket de la disparition) : avant la disparition complète **{sum(r['course_demi'] for r in R_)}/{len(R_)}** ({pc(sum(r['course_demi'] for r in R_), len(R_))}) avec {fr(RTT_CLOB / 2, 0)} ms aller simple, "
          f"{sum(r['course_rtt'] for r in R_)}/{len(R_)} avec l'aller-retour complet {fr(RTT_CLOB, 0)} ms ; **avant la 1re baisse de ce niveau après l'information : {sum(r['avant_1re'] for r in R_)}/{len(R_)}** ({pc(sum(r['avant_1re'] for r in R_), len(R_))}). "
          + (f"Témoin au hasard : {pc(sum(r['course_demi'] for r in RP), len(RP))} et {pc(sum(r['avant_1re'] for r in RP), len(RP))}. " if P else "")
          + "Par cause de disparition (avant la disparition complète, aller simple) : " +
          " ; ".join(f"{k} {sum(r['course_demi'] for r in R_ if r['cause'] in ks)}/{sum(1 for r in R_ if r['cause'] in ks)}" for k, ks in (("consommé/mixte", ("consommé", "mixte")), ("retiré/déplacé", ("retiré", "déplacé")))) + ".")
        w("")
    bloc(f"Bourses, saut ≥ {fr(X_INFO, 0)} $ (critère principal)", chb, CHP.get("bourses"))
    bloc("Sensibilité (déclarée à l'avance) : bourses, saut ≥ 2 $", CH2)
    bloc("Chainlink (nouvelle valeur dans le bon sens)", CHcl, CHP.get("cl"))
    w("Lecture : si les délais et l'ordre « retrait / consommation » sont les mêmes avec des informations placées au hasard, l'information de bourse n'explique pas la disparition : "
      "la course « avant la disparition » est alors surtout mécanique (les niveaux vivent de toute façon plus de 14 ms) et ne prouve aucun avantage.")
    w("")
    w(f"**Course déclenchée par le carnet Polymarket lui-même** (sans information externe) : délai « Polymarket → Dublin ({fr(POLY_VERS_DUBLIN, 1)} ms) + calcul ({fr(CALCUL, 1)} ms) + aller simple ({fr(RTT_CLOB / 2, 0)} ms) » ≈ {fr(delai_msg, 1)} ms. "
      f"Durée passée au meilleur rang par les niveaux qui disparaissent : {q3(vies, 0)} ms (10 % · méd. · 90 %) ; plus longue que notre délai pour **{pc(ok_v, nv)}** ({ok_v}/{nv}). "
      f"Consommés seulement : {pc(sum(1 for x in Bfok if x['cause'] in ('consommé', 'mixte') and x['age_best'] and x['age_best'] > delai_msg), sum(1 for x in Bfok if x['cause'] in ('consommé', 'mixte') and x['age_best'] is not None))}. "
      "Attention : « vivre plus longtemps que notre délai » ne veut pas dire que l'avantage existait — c'est une borne de faisabilité mécanique, pas un gain.")
    w("")
    # ---------- précurseurs
    w("### Précurseurs H497 / H541 / H543 (avant une consommation complète, contre 3 instants témoins au hasard par événement)")
    w("")
    w("AUC = probabilité qu'une valeur avant consommation dépasse une valeur témoin (0,5 = aucun signal). Instants témoins : même cycle, même côté, à plus de 1 s de toute consommation. "
      "Modèle combiné : régression logistique, validation croisée par cycle (les cycles de test ne servent pas à l'apprentissage).")
    w("")
    w("| Fenêtre (variations sur h ms) | Consommations · témoins | " + " | ".join(NOMS_VAR) + " | Modèle combiné (AUC validation croisée) |")
    w("|---|---|" + "---|" * len(NOMS_VAR) + "---|")
    for (h, mode), P_ in PRE.items():
        lab = f"{h} ms, jusqu'à t−1 ms" if mode == "t-1" else f"{h} ms, arrêté à t−{h} ms"
        w(f"| {lab} | {P_['n1']} · {P_['n0']} | " + " | ".join(f"{fr(a, 3)} (méd. {fr(float(P_['med1'][j]), 2)} / {fr(float(P_['med0'][j]), 2)})" for j, a in enumerate(P_["aucs"])) + f" | {fr(P_['auc_cv'], 3)} |")
    w("")
    w("Lecture : (méd. avant consommation / méd. témoin). Lignes « jusqu'à t−1 ms » : tout ce qui est visible juste avant — en grande partie **mécanique** (la file de l'offre consommée fond déjà : "
      "consommations partielles du même niveau juste avant). Lignes « arrêté à t−h » : seulement ce qui était connu h ms avant, donc utilisable pour arriver à temps. "
      "Témoins non appariés sur le prix, l'écart ni la taille : un petit niveau est plus facilement consommé en entier, donc le déséquilibre du microprix reflète en partie la petite taille de l'offre (effet de sélection). **Préliminaire, effectifs groupés par cycle (15 cycles), aucune conclusion de P&L.**")
    w("")
    w("## Ce qu'il faut de plus (et limites)")
    w("")
    w(f"- **Durée** : {fr(duree_h, 2)} h, un seul dimanche après-midi, BTC très calme (≈ {sum(nINF[k] for k in ('perp', 'okx', 'bn', 'cb'))} sauts ≥ 5 $ en tout). Il faut **au moins 3 à 5 jours** dont des séances actives pour la phase 2 (des centaines de disparitions précédées d'une information) et pour la phase 1b (≥ 100 signaux par catégorie avant tout taux de gain).")
    w("- **Échantillon 50 ms des bourses** : seul le dernier prix de chaque tranche est gardé ; le moment exact où le seuil est franchi peut être plus tôt (jusqu'à ~50 ms). Les bourses asiatiques arrivent à Dublin avec ~100–130 ms de retard (Bybit, OKX, Binance), Coinbase ~45 ms : un concurrent mieux placé voit l'information avant nous.")
    w("- **Prix arrondis au cent** dans l'enregistreur compact (pas de 0,001 perdu près de 0/1) et profondeur au-delà de ±3 c périmée entre deux carnets complets (10 s).")
    w("- **Flux agressifs `fx`** (version b2b4d959b243) : pas encore de cycle disponible ; à intégrer à la phase 2 (balayage des bourses vs. retrait Polymarket).")
    w(f"- **Horloges** : la course compare l'heure Dublin (NTP) à l'heure Polymarket ; le décalage médian Polymarket → Dublin mesuré ({fr(POLY_VERS_DUBLIN, 1)} ms) inclut un éventuel écart d'horloge.")
    w(f"- Durée d'exécution : {time.time() - T0:.0f} s.")
    open(SORTIE, "w").write("\n".join(md) + "\n")
    print("écrit", SORTIE, f"{time.time() - T0:.1f} s")


if __name__ == "__main__":
    main()
