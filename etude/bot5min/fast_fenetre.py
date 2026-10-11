"""BOT95 — FAST A-T-IL UNE FENÊTRE D'EXÉCUTION ? (H575, H576, H593, H601) + TOURNOI H650 PRÉLIMINAIRE + DIAGNOSTIC MAKER.
Demande de Pitch, 11.10.2026 14:05. Hors ligne, aucun bot modifié, aucun ordre.

Données : cycles enregistrés à Dublin (branche donnees-rapide), signaux réglés (bot95/rapide.json), offres maker réglées
(bot95/rapide_maker.json). PÉRIODE HORS ÉCHANTILLON RÉSERVÉE (fixée le 11.10.2026 avant toute mesure) : cycles commençant à partir du
13.10.2026 00:00 UTC. Ce script ne les lit PAS (sauf option --hors-echantillon, à n'utiliser qu'une fois, pour le verdict).

Usage : python3 etude/bot5min/fast_fenetre.py [dossier_des_cycles] → etude/bot5min/resultat_fast_fenetre.md
"""
import gzip, json, os, sys, glob, bisect, collections, math, random, time
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, ICI)
import queue_race_phase12 as Q   # reconstruction du carnet, classement transaction / retrait (étude du 11.10)

SORTIE = os.path.join(ICI, "resultat_fast_fenetre.md")
HORS_ECH = 1791849600            # 13.10.2026 00:00 UTC — réservé
# ---------------------------------------------------------------- paramètres FIXÉS À L'AVANCE
UN_SENS = 14.0                   # ms : trajet simple Dublin → Polymarket (moitié de l'aller-retour médian mesuré, 28 ms)
CALCUL = 0.2                     # ms : décision (mesuré : < 0,2 ms)
DELAI_PRENEUR = 150.0            # ms : retard des preneurs sur les marchés crypto (changelog Polymarket du 04.09.2026 ; drapeau itode=true sur nos marchés)
AVANCES = [50, 100, 150, 200, 300, 500]
FEE = lambda p: 0.07 * p * (1 - p)   # barème lu sur nos marchés (crypto_fees_v2, rate 0,07, preneur seulement)
MIN_PARTS = 5                    # taille minimale d'un ordre Polymarket
random.seed(11)


def normaliser(path):
    """comme Q.normaliser, mais lit les prix en millièmes pour les versions qui les enregistrent ainsi (depuis le 11.10 ~12:20)"""
    R = json.load(gzip.open(path))
    st = R["start"]; m = R.get("marche") or {}
    C = dict(start=st, version=R.get("version"), coupe=bool(R.get("coupe")), nEv=R.get("nEv"), strike=m.get("strike"), strikeTwap=m.get("strikeTwap"),
             ex=R.get("ex", []), snap=R.get("snap", []), sig=R.get("sig", []), fx=R.get("fx"), mk=R.get("mk", []), tw=R.get("tw", []), cl2=R.get("cl2", []))
    milliemes = "milliemes" in (R.get("format") or "")
    t = 0; P = []
    for dt, ret, side, c, sz in R.get("p", []):
        t += dt; P.append((float(t), (t - ret) if ret is not None else None, "P", side, c if milliemes else c * 10, sz / 100.0))
    A = []
    for e in R["ev"]:
        if e[0] == "T": A.append((e[1], e[2], "T", e[3], e[4], Q.mil(e[5]), e[6]))
        elif e[0] == "B" and e[3] == 0: A.append((e[1], e[2], "B", [(Q.mil(p), s) for p, s in e[4]], [(Q.mil(p), s) for p, s in e[5]]))
    C["format"] = "compact-milliemes" if milliemes else "compact"
    C["flux"] = sorted(P + A, key=lambda x: x[0]); C["t_fin_flux"] = C["flux"][-1][0] if C["flux"] else None
    return C


def qte_niveau(L, side, c):
    return (L.a if side == 1 else L.b).get(c, 0.0)


def survie(C, Rj, disp):
    """pour chaque disparition complète d'un meilleur niveau (côté 1 = offre Up ; côté 0 = demande Up = offre Down) :
    quantité encore présente à ce prix quand notre ordre, décidé `a` ms avant la disparition, serait exécuté
    (arrivée = décision + trajet simple + calcul ; exécution = arrivée + retard preneur)."""
    fl = C["flux"]; out = []
    instants = []
    for x in disp:
        for a in AVANCES: instants.append(x["t"] - a)
        for a in AVANCES:
            for dl in (0.0, 50.0, DELAI_PRENEUR):
                instants.append(x["t"] - a + UN_SENS + CALCUL + dl)
    E = Q.etats_aux_instants(C, set(instants))
    for x in disp:
        r = dict(cause=x["cause"], side=x["side"], c=x["c"], t=x["t"], q_avant={}, exec={})
        for a in AVANCES:
            L0 = E[x["t"] - a][0]; q0 = qte_niveau(L0, x["side"], x["c"]) if L0 else 0.0
            meilleur = L0 is not None and ((L0.ba == x["c"]) if x["side"] == 1 else (L0.bb == x["c"]))
            r["q_avant"][a] = (q0, meilleur)
            for dl in (0.0, 50.0, DELAI_PRENEUR):
                te = x["t"] - a + UN_SENS + CALCUL + dl
                if te >= x["t"]: r["exec"][(a, dl)] = 0.0; continue
                L1 = E[te][0]; q1 = qte_niveau(L1, x["side"], x["c"]) if L1 else 0.0
                r["exec"][(a, dl)] = min(q0, q1)
        out.append(r)
    return out


def lead_info(C, Rj, INF):
    """avance de l'information disponible à Dublin (saut ≥ 5 $ d'une bourse dans le bon sens, ≤ 1 s avant) sur chaque disparition"""
    I = [x for x in INF if x[1] in ("perp", "okx", "bn", "cb")]; It = [x[0] for x in I]
    st = C["start"] * 1000; out = []
    for x in Rj["baisses"]:
        if not x["full"] or x["cause"] == "indéterminé" or not (st <= x["t"] <= st + 300000): continue
        sens = 1 if x["side"] == 1 else -1
        j = bisect.bisect_right(It, x["t"]) - 1; info = None
        while j >= 0 and It[j] >= x["t"] - 1000:
            if I[j][2] == sens: info = I[j]
            j -= 1                                     # on garde la PLUS ANCIENNE information du bon sens dans la seconde (avance maximale)
        out.append(dict(cause=x["cause"], lead=(x["t"] - info[0]) if info else None))
    return out


def trades_apres_info(C, Rj, INF):
    """vérification indirecte du retard preneur : délai entre une information (vue à Dublin) et les transactions qui consomment le côté
    devenu trop bon marché, comparé au délai des retraits"""
    I = [x for x in INF if x[1] in ("perp", "okx", "bn", "cb")]
    tr = Rj["trades"]; Tt = [t[0] for t in tr]
    B = [b for b in Rj["baisses"] if b["cause"] in ("retiré", "déplacé")]; Bt = [b["t"] for b in B]
    dtr, dret = [], []
    for t0, src, sens, d in I:
        side_vise = 1 if sens == 1 else 0              # BTC monte → offres Up consommées (côté 1)
        i = bisect.bisect_right(Tt, t0)
        while i < len(tr) and tr[i][0] <= t0 + 1000:
            if tr[i][6] == side_vise: dtr.append(tr[i][0] - t0); break
            i += 1
        i = bisect.bisect_right(Bt, t0)
        while i < len(B) and B[i]["t"] <= t0 + 1000:
            if B[i]["side"] == side_vise: dret.append(B[i]["t"] - t0); break
            i += 1
    return dtr, dret


def fiabilite(C, Rj, INF, rng):
    """après une information (saut ≥ 5 $), une disparition complète du côté devenu trop bon marché survient-elle entre 164 et 1000 ms ?
    Témoin : mêmes nombres d'instants tirés au hasard dans le cycle."""
    st = C["start"] * 1000; I = [x for x in INF if x[1] in ("perp", "okx", "bn", "cb") and st <= x[0] <= st + 300000]
    D = {0: [], 1: []}
    for b in Rj["baisses"]:
        if b["full"] and b["cause"] != "indéterminé": D[b["side"]].append(b["t"])
    lo = UN_SENS + CALCUL + DELAI_PRENEUR
    def touche(t0, side): L = D[side]; i = bisect.bisect_left(L, t0 + lo); return i < len(L) and L[i] <= t0 + 1000
    vrai = [touche(t0, 1 if sens == 1 else 0) for t0, src, sens, d in I]
    temoin = [touche(st + rng.random() * 300000, rng.choice((0, 1))) for _ in I]
    return vrai, temoin


def tournoi_signaux(C, sigs):
    """FAST : achat preneur décidé au signal, exécuté 164 ms plus tard ; SLOW : 1 s plus tard (offre persistante) ; quantité au prix vu ou mieux, 50 $"""
    lo = UN_SENS + CALCUL + DELAI_PRENEUR; inst = set()
    for S in sigs: inst.add(S["tDecision"] + lo); inst.add(S["tDecision"] + 1000 + lo)
    E = Q.etats_aux_instants(C, inst); out = []
    def dispo(L, up, a0):
        if L is None: return 0.0, 0.0
        lim = Q.mil(a0); q = c = 0.0
        niv = sorted(((k, z) for k, z in L.a.items() if k <= lim)) if up else sorted((((1000 - k), z) for k, z in L.b.items() if 1000 - k <= lim))
        for k, z in niv:
            p = k / 1000; x = min(z, (50 - c) / (p + FEE(p)))
            if x <= 0: break
            q += x; c += x * (p + FEE(p))
        return q, c
    for S in sigs:
        up = S["cote"] == "Up"; g = 1.0 if S.get("gagne") else 0.0
        qf, cf = dispo(E[S["tDecision"] + lo][0], up, S["a0"]); qs, cs = dispo(E[S["tDecision"] + 1000 + lo][0], up, S["a0"])
        f = (qf, cf, qf * g - cf) if qf >= MIN_PARTS else (0, 0, 0); sl = (qs, cs, qs * g - cs) if qs >= MIN_PARTS else (0, 0, 0)
        h = f if f[0] > 0 else sl
        out.append(dict(nom=S["nom"], start=S["start"], FAST=f, SLOW=sl, HYBRID=h))
    return out


def ic_blocs(par_cycle, n=2000, rng=None):
    """intervalle de confiance à 90 % du total, rééchantillonnage par cycles (blocs de 5 min)"""
    v = np.array(list(par_cycle.values()), dtype=float)
    if len(v) < 3: return None
    rng = rng or np.random.default_rng(3); b = [v[rng.integers(0, len(v), len(v))].sum() for _ in range(n)]
    return np.percentile(b, [5, 95])


def pct(x): return "—" if x is None else f"{100 * x:.0f} %"
def q3(v, d=0):
    if not v: return "—"
    a = np.percentile(v, [10, 50, 90]); return " / ".join(f"{x:.{d}f}" for x in a)


def main():
    dossier = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else os.path.join("/tmp", "cycles_rapide")
    hors = "--hors-echantillon" in sys.argv
    fichiers = sorted(glob.glob(os.path.join(dossier, "**", "*.json.gz"), recursive=True))
    fichiers = [f for f in fichiers if (int(os.path.basename(f).split(".")[0]) >= HORS_ECH) == hors]
    L = []; trous = collections.Counter()
    S_all, LEAD, DTR, DRET, CAUSES = [], [], [], [], collections.Counter()
    MK = []; versions = collections.Counter(); ncy = 0; VR, TM = [], []; rng = random.Random(5); TOUR = []; cycles_vus = set()
    SIG = json.load(open(os.path.join(RACINE, "bot95", "rapide.json")))["signaux"] if os.path.exists(os.path.join(RACINE, "bot95", "rapide.json")) else []
    SIGc = collections.defaultdict(list)
    for S in SIG:
        if S.get("gagnant") and S.get("tDecision"): SIGc[S["start"]].append(S)
    for fn in fichiers:
        C = normaliser(fn); ncy += 1; versions[C["version"]] += 1
        if C["coupe"]: trous["cycle coupé (limite d'événements)"] += 1
        Rb = json.load(gzip.open(fn))
        if "obSnap" in Rb:
            trous["cycles avec carnets Binance/Bybit"] += 1
            if Rb.get("obTrous"): trous["cycles avec trou de carnet ou de transactions (exclus des études de carnets)"] += 1
            for k in ("bn", "by"):
                if any(r[-1] == 0 for r in (Rb.get("ob") or {}).get(k, []) if len(r) > 21): trous[f"cycles avec carnet {k} marqué non fiable"] += 1
        if not C["flux"] or not any(e[2] == "B" for e in C["flux"]): trous["sans carnet complet"] += 1; continue
        Rj = Q.rejouer(C); Q.classer(C, Rj)
        for b in Rj["baisses"]:
            if b["full"]: CAUSES[b["cause"]] += 1
        st = C["start"] * 1000
        disp = [b for b in Rj["baisses"] if b["full"] and st <= b["t"] <= st + 300000]
        S_all += survie(C, Rj, disp)
        INF = Q.infos(C); LEAD += lead_info(C, Rj, INF)
        a, b = trades_apres_info(C, Rj, INF); DTR += a; DRET += b
        v, tm = fiabilite(C, Rj, INF, rng); VR += v; TM += tm
        cycles_vus.add(C["start"]); TOUR += tournoi_signaux(C, SIGc.get(C["start"], []))
        for r in C["mk"]: MK.append([C["start"]] + r)
    # ------------------------------------------------ rapport
    o = []
    w = o.append
    w("# Bot95 — FAST a-t-il une fenêtre d'exécution ? (diagnostic PRÉLIMINAIRE, non validé statistiquement)\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. {ncy} cycles de Dublin, {'HORS ÉCHANTILLON' if hors else 'avant la période réservée (13.10.2026 00:00 UTC)'}. "
      f"Paramètres fixés avant mesure : trajet simple {UN_SENS:.0f} ms, calcul {CALCUL} ms, retard preneur {DELAI_PRENEUR:.0f} ms.\n")
    if trous: w("Données exclues ou douteuses : " + ", ".join(f"{k} {v}" for k, v in trous.items()) + "\n")
    tot = sum(CAUSES.values())
    w("## 1. Pourquoi les meilleures offres disparaissent (disparitions complètes du meilleur niveau)\n")
    w("| Cause | Nombre | Part |\n|---|---|---|")
    for k in ("consommé", "mixte", "retiré", "déplacé", "indéterminé"):
        w(f"| {k} | {CAUSES[k]} | {pct(CAUSES[k] / tot if tot else None)} |")
    w("\n« consommé » exige une transaction enregistrée qui correspond (prix, quantité, 14–40 ms après la baisse). Sans preuve : « retiré » ou « indéterminé ». "
      "Une disparition n'est JAMAIS comptée comme une transaction sans cette preuve.\n")
    # survie
    w("## 2. Probabilité que l'offre soit encore exécutable selon notre avance (H575 / H576)\n")
    w("Lecture : notre ordre est décidé `a` ms avant la disparition ; il est exécuté à décision + 14 ms + retard preneur. "
      "« Exécutable » = au moins 5 parts encore à ce prix au moment de l'exécution ; « part » = quantité encore là / quantité vue à la décision.\n")
    for dl, nom in ((0.0, "sans retard preneur (référence théorique)"), (50.0, "retard 50 ms (réglage du 17.08 au 04.09)"), (DELAI_PRENEUR, "retard 150 ms (réglage actuel)")):
        w(f"**{nom}**\n")
        w("| Avance a | Toutes | Consommées | Retirées / déplacées | Mixtes | Part médiane de la quantité |\n|---|---|---|---|---|---|")
        for a in AVANCES:
            row = []
            for grp in (None, ("consommé",), ("retiré", "déplacé"), ("mixte",)):
                sel = [r for r in S_all if r["q_avant"][a][0] >= MIN_PARTS and (grp is None or r["cause"] in grp)]
                ok = [r for r in sel if r["exec"][(a, dl)] >= MIN_PARTS]
                row.append(f"{pct(len(ok) / len(sel)) if sel else '—'} ({len(sel)})")
            sel = [r for r in S_all if r["q_avant"][a][0] >= MIN_PARTS]
            fr = [r["exec"][(a, dl)] / r["q_avant"][a][0] for r in sel]
            w(f"| {a} ms | " + " | ".join(row) + f" | {np.median(fr) * 100:.0f} % |" if fr else f"| {a} ms | " + " | ".join(row) + " | — |")
        w("")
    w(f"Avance MINIMALE pour qu'un ordre arrive avant la disparition : trajet simple {UN_SENS:.0f} ms + calcul + retard preneur {DELAI_PRENEUR:.0f} ms ≈ **{UN_SENS + CALCUL + DELAI_PRENEUR:.0f} ms**.\n")
    # avance de l'information
    w("## 3. Quelle avance l'information nous donne-t-elle réellement ? (H575, H593, H601)\n")
    w("Pour chaque disparition (hors indéterminé), la plus ancienne information du bon sens reçue à Dublin dans la seconde qui précède "
      "(saut ≥ 5 $ entre deux échantillons 50 ms de Bybit, OKX, Binance ou Coinbase).\n")
    w("| Cause | Disparitions | Avec information dans la seconde | Avance médiane (p10 / p50 / p90, ms) | Avance ≥ 164 ms | Avance ≥ 300 ms |\n|---|---|---|---|---|---|")
    for grp, nom in ((None, "toutes"), (("consommé",), "consommées"), (("retiré", "déplacé"), "retirées / déplacées"), (("mixte",), "mixtes")):
        sel = [r for r in LEAD if grp is None or r["cause"] in grp]; li = [r["lead"] for r in sel if r["lead"] is not None]
        g164 = sum(1 for x in li if x >= UN_SENS + CALCUL + DELAI_PRENEUR); g300 = sum(1 for x in li if x >= 300)
        w(f"| {nom} | {len(sel)} | {len(li)} ({pct(len(li) / len(sel) if sel else None)}) | {q3(li)} | {g164} ({pct(g164 / len(sel) if sel else None)}) | {g300} ({pct(g300 / len(sel) if sel else None)}) |")
    w(f"\n**Fiabilité de l'information** : après un saut ≥ 5 $ vu à Dublin ({len(VR)} cas), une disparition complète du côté devenu trop bon marché survient entre 164 et 1000 ms "
      f"dans {pct(sum(VR) / len(VR)) if VR else '—'} des cas ; à des instants tirés au hasard (témoin) : {pct(sum(TM) / len(TM)) if TM else '—'}.\n")
    w("\nC'est un PLAFOND optimiste pour FAST : il suppose un prédicteur parfait qui saurait, dès l'information, quelle offre va disparaître.\n")
    w("## 4. Vérification indirecte du retard preneur sur nos marchés\n")
    w(f"Après une information reçue à Dublin : délai jusqu'à la 1re transaction sur le côté devenu trop bon marché (n = {len(DTR)}) : p10 / p50 / p90 = {q3(DTR)} ms ; "
      f"jusqu'au 1er retrait (n = {len(DRET)}) : {q3(DRET)} ms. "
      f"Transactions moins de 150 ms après NOTRE information : {pct(sum(1 for x in DTR if x < 150) / len(DTR)) if DTR else '—'}. "
      "Avec un retard de 150 ms, ces acheteurs avaient l'information avant nous (ou ont acheté sans elle). Mesure directe : seul un vrai ordre (test de 1 $, en attente de ton accord).\n")
    # maker
    w("## 5. Makers : remplissage, file, sélection adverse, résultat (préliminaire)\n")
    if MK:
        V = collections.defaultdict(list)
        for r in MK: V[r[1]].append(r)
        w("Toutes les offres posées, enregistrées dans les cycles (y compris jamais remplies).\n")
        w("| Variante | Offres | Rejetées (post only) | Remplies prudent | Remplies proportionnel | File devant nous médiane (parts) | Temps jusqu'au 1er remplissage médian (ms) |\n|---|---|---|---|---|---|---|")
        for v in sorted(V):
            R = V[v]; n = len(R); rej = sum(1 for r in R if r[6] == "rejetee"); fp = sum(1 for r in R if r[8] and r[8] > 0); fr = sum(1 for r in R if r[9] and r[9] > 0)
            qd = [r[7] for r in R if r[7] is not None]; tf = [r[10] for r in R if r[10] is not None]
            w(f"| {v} | {n} | {rej} | {fp} ({pct(fp / n)}) | {fr} ({pct(fr / n)}) | {np.median(qd):.0f} | {np.median(tf) if tf else float('nan'):.0f} |")
    else:
        w("Pas encore d'offres enregistrées dans les cycles.\n")
    MKR = json.load(open(os.path.join(RACINE, "bot95", "rapide_maker.json"))) if os.path.exists(os.path.join(RACINE, "bot95", "rapide_maker.json")) else []
    MKR = [x for x in MKR if x.get("type") != "resume" and x.get("resultat") and ((x["start"] >= HORS_ECH) == hors)]
    if MKR:
        w("\nOffres remplies et réglées (fichier bot95/rapide_maker.json) :\n")
        w("| Variante | Offres remplies | Parts (prudent / prop.) | $ exécutés prudent | Résultat prudent | Résultat proportionnel | Résultat par $ exécuté (prudent) | Sélection adverse carnet +1 / +3 / +5 / +10 s (c par part, prudent) |\n|---|---|---|---|---|---|---|---|")
        V = collections.defaultdict(list)
        for x in MKR: V[x["variante"]].append(x)
        for v in sorted(V):
            X = V[v]; pp = sum(x["remplP"] for x in X); pr = sum(x["remplR"] for x in X); usd = sum(x["remplP"] * x["prix"] for x in X)
            rp = sum(x["resultat"]["prudent"] for x in X); rr = sum(x["resultat"]["proportionnel"] for x in X)
            mo = []
            for h in ("1", "3", "5", "10"):
                a = sum((x.get("mo") or {}).get("p", {}).get(h, [0, 0])[0] for x in X); b = sum((x.get("mo") or {}).get("p", {}).get(h, [0, 0])[1] for x in X)
                mo.append(f"{100 * a / b:+.1f}" if b else "—")
            w(f"| {v} | {len(X)} | {pp:.0f} / {pr:.0f} | {usd:.0f} $ | {rp:+.0f} $ | {rr:+.0f} $ | {(rp / usd if usd else float('nan')):+.2f} | {' / '.join(mo)} |")
        w("\n**Par prix d'achat et temps restant (toutes variantes maker, prudent)**\n")
        w("| Prix | Offres remplies | $ exécutés | Résultat | par $ |\n|---|---|---|---|---|")
        for lo, hi in ((0, .2), (.2, .35), (.35, .5), (.5, .65), (.65, 1.01)):
            X = [x for x in MKR if lo <= x["prix"] < hi]; usd = sum(x["remplP"] * x["prix"] for x in X); r = sum(x["resultat"]["prudent"] for x in X)
            w(f"| {lo:.2f}–{min(hi, 1):.2f} | {len(X)} | {usd:.0f} $ | {r:+.0f} $ | {(r / usd if usd else float('nan')):+.2f} |")
        w("\n| Temps restant à la pose | Offres remplies | $ exécutés | Résultat | par $ |\n|---|---|---|---|---|")
        for lo, hi in ((0, 60), (60, 120), (120, 180), (180, 300)):
            X = [x for x in MKR if x.get("restantPose_s") is not None and lo <= x["restantPose_s"] < hi]; usd = sum(x["remplP"] * x["prix"] for x in X); r = sum(x["resultat"]["prudent"] for x in X)
            w(f"| {lo}–{hi} s | {len(X)} | {usd:.0f} $ | {r:+.0f} $ | {(r / usd if usd else float('nan')):+.2f} |")
        w("(temps restant enregistré seulement depuis la version du 11.10 13:55)\n")
        w("\n**Intervalle de confiance à 90 % du résultat prudent (rééchantillonnage par cycles)**\n")
        for v in sorted(V):
            pc = collections.defaultdict(float)
            for x in V[v]: pc[x["start"]] += x["resultat"]["prudent"]
            ic = ic_blocs(pc); w(f"- {v} : {sum(pc.values()):+.0f} $ sur {len(pc)} cycles, IC 90 % " + (f"[{ic[0]:+.0f} ; {ic[1]:+.0f}] $" if ic is not None else "— (trop peu de cycles)"))
        w("\nSélection adverse : milieu du carnet h secondes après chaque remplissage moins notre prix (négatif = le marché est parti contre nous). "
          "Les offres remplies avant la version du 11.10 13:55 n'ont pas cette mesure.\n")
    w("\n## 6. Tournoi H650 préliminaire sur nos signaux (mêmes cycles)\n")
    MKR_all = json.load(open(os.path.join(RACINE, "bot95", "rapide_maker.json"))) if os.path.exists(os.path.join(RACINE, "bot95", "rapide_maker.json")) else []
    debut_maker = min((x["start"] for x in MKR_all if x.get("type") != "resume"), default=None)
    T = [x for x in TOUR if debut_maker and x["start"] >= debut_maker]
    cyc = sorted({x["start"] for x in T})
    w(f"Cycles communs (Dublin enregistré + makers actifs + signaux réglés) : {len(cyc)}. Achat 50 $ au plus, au prix vu au signal ou mieux, frais preneur 0,07·p·(1−p).\n")
    w("| Stratégie | Trades | $ engagés | Résultat | Résultat par $ |\n|---|---|---|---|---|")
    for k, nom in (("FAST", "FAST : preneur exécuté 164 ms après le signal"), ("SLOW", "SLOW : preneur exécuté 1,164 s après (offre persistante)"), ("HYBRID", "HYBRID : FAST sinon SLOW (règle fixée avant)")):
        X = [x[k] for x in T if x[k][0] > 0]; c = sum(x[1] for x in X); r = sum(x[2] for x in X)
        pc = collections.defaultdict(float)
        for x in T:
            if x[k][0] > 0: pc[x["start"]] += x[k][2]
        ic = ic_blocs(pc)
        w(f"| {nom} | {len(X)} | {c:.0f} $ | {r:+.0f} $ {('[IC 90 % ' + f'{ic[0]:+.0f} ; {ic[1]:+.0f}]') if ic is not None else ''} | {(r / c if c else float('nan')):+.2f} |")
    sC = [S for st in cyc for S in SIGc.get(st, []) if S.get("moteurC") and S["moteurC"].get("resultat")]
    rC = 0.0; nC = 0
    for S in sC:
        R = S["moteurC"]["resultat"]; v = R.get("300ms", None)
        if v is not None: rC += v; nC += 1 if v != 0 else 0
    w(f"| C : moteur alpha exécutable (exécution mesurée à 300 ms) | {nC} | — | {rC:+.0f} $ | — |")
    M1 = [x for x in MKR_all if x.get("type") != "resume" and x.get("resultat") and x["start"] in set(cyc)]
    for pre, nom in (("M1", "M1 : offre posée au signal"), ("M2 cotation marge 5 c", "M2 marge 5 c"), ("M2 cotation marge 10 c", "M2 marge 10 c"), ("M0", "M0 témoin aléatoire"),
                     ("M3", "M3 anticipation Chainlink"), ("M4", "M4 retrait toxique"), ("M5", "M5 remplissage attendu")):
        X = [x for x in M1 if x["variante"].startswith(pre)]; c = sum(x["remplP"] * x["prix"] for x in X)
        rp = sum(x["resultat"]["prudent"] for x in X); rr = sum(x["resultat"]["proportionnel"] for x in X)
        w(f"| {nom} (prudent ; proportionnel {rr:+.0f} $) | {len(X)} | {c:.0f} $ | {rp:+.0f} $ | {(rp / c if c else float('nan')):+.2f} |")
    w("\nPériode hors échantillon réservée : cycles à partir du 13.10.2026 00:00 UTC, jamais lus par ce script avant le verdict.\n")
    w("\n## Limites\n- Peu de cycles : chiffres indicatifs, intervalles non calculés à ce stade.\n- Retard preneur de 150 ms : tiré du changelog et du drapeau itode, pas mesuré par un ordre réel.\n"
      "- Le carnet Polymarket enregistré ne garde que ±3 c autour du meilleur prix et un carnet complet toutes les 10 s.\n"
      "- Remplissages maker : estimations prudente et proportionnelle, aucune n'est certaine.\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o)); print("versions", versions)


if __name__ == "__main__":
    main()
