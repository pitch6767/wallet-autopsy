"""BOT95 — H1085 « les grosses transactions » : sur les marchés Polymarket BTC 5 min Up/Down, quand un gros ACHAT passe (une transaction
ou une rafale du même portefeuille en quelques secondes), l'issue achetée gagne-t-elle plus souvent que son prix (suivre le gros) ou
moins souvent (le contrer) ? Hors ligne, aucun ordre. Rien après le 08.10.2026 n'est lu (marchés ≥ 09.10 00:00 UTC écartés).
DÉCOUPAGE : exploration 12.09–30.09, validation 01.10–08.10, lue UNE seule fois (option --validation), après commit des règles.
QUI A ACHETÉ ? Chaque transaction (même hash) contient une ligne par participant : la PREMIÈRE ligne est le preneur (l'ordre qui traverse
  le carnet), les suivantes sont les teneurs de marché servis. Vérifié : dans les transactions à ≥ 3 lignes, la taille de la 1re ligne
  = somme des autres dans > 99 % des cas (le reste : un teneur ≈ total, ambigu). Les paires « BUY Up + BUY Down » sont des créations de
  parts (le preneur achète un côté, le teneur l'autre) ; « SELL X + BUY X » un échange direct. On ne garde que la 1re ligne de chaque
  transaction, côté BUY : un achat agressif compté UNE fois (pas de double comptage avec la contrepartie). Les ventes agressives sont ignorées.
GROS ACHAT : achats preneur d'un même portefeuille sur la même issue, regroupés si l'écart entre deux achats ≤ 3 s et la rafale ≤ 5 s ;
  montant = Σ prix × parts. Événement au seuil S (500 / 2 000 / 5 000 $) = seconde te où le cumul de la rafale franchit S ; prix du gros =
  prix moyen de la rafale jusque-là ; te dans [0 ; 300[ s du cycle.
CONVENTIONS (H1067 / H1084) : notre prix = médiane des achats (toutes lignes BUY) de l'issue achetée dans (te+1, te+6] (on réagit après
  avoir vu le gros) ; frais 0,07·p·(1−p) ; prix gardé dans [0,01 ; 0,99] ; gardé jusqu'au règlement ; un seul achat par cycle et par
  règle (premier événement qui déclenche) ; P&L à 10 $ par achat ; bootstrap par cycles (0 $ pour les cycles sans achat), 10 000 tirages.
  Prix PESSIMISTE publié à côté = max(notre prix, médiane du prix de ce côté dans (te−6, te−1], avant le gros) : on ne profite pas de
  l'impact passager du gros. Mouvement BTC (Binance 1 s) : b10 = (c[te−1] − c[te−11]) / (σ1s(1 h)·√10), compté dans le sens du gros.
EXPLORATION (12.09–30.09, 5 459 cycles ; 18 140 événements ≥ 500 $, 2 065 ≥ 2 000 $, 73 ≥ 5 000 $) : 68 % des gros achats ≥ 500 $ se font
  à 0,95–1 (favori quasi sûr). Partout la fréquence de gain ≈ prix du gros (écarts ≤ 1 pt), sauf ≥ 2 000 $ hors zone 0,95 : le gros gagne
  ~6 pts de moins que son prix. Après notre entrée, le prix ne continue pas dans son sens (−0,1 pt à 10 s, −0,5 à −1 pt à 30 s).
  Gros achat contre le mouvement BTC : perd 8 pts sur son prix, mais le prix a déjà corrigé quand on arrive. ~360 cases testées : tout
  ressemble à du bruit ; les règles ci-dessous sont donc des tests, pas des promesses.
RÈGLES FIGÉES (avant toute lecture de la validation) :
  G1 : SUIVRE un gros achat ≥ 2 000 $ à un prix 0,30–0,95, 10–300 s restantes   (expl. ROI −12,8 %, IC 90 % [−526 ; −138] $)
  G2 : CONTRER le même (acheter l'autre issue)                                     (expl. +8,6 %, [−352 ; +858] $ ; pessimiste −7,4 %)
  G3 : CONTRER un gros achat ≥ 500 $ à 0,65–0,95 avec 60–120 s restantes           (expl. +21,9 %, [−32 ; +3 160] $ ; pessimiste −8,4 % ; meilleure case
       après essais : la plus exposée au hasard)
  G4 : SUIVRE un gros achat ≥ 500 $ à 0,95–0,99 avec 10–60 s restantes (baleine qui confirme le favori, cousin de Bot95)
                                                                                   (expl. +0,6 %, [+41 ; +238] $ ; pessimiste +0,1 %)
CRITÈRE : ROI > 0 en exploration ET en validation, et borne basse de l'IC 90 % corrigé Bonferroni (4 règles → percentiles 1,25 / 98,75)
  du P&L de validation > 0. Aucun fantôme sans accord de Pitch.
Usage : python3 etude/bot5min/grosses_transactions_h1085.py btc1s.npz polytrades_*.json.gz [--validation]"""
import sys, json, gzip, os, numpy as np, pandas as pd
from multiprocessing import Pool
ICI = os.path.dirname(os.path.abspath(__file__)); FIN_EXPLO = 1790812800; FIN_VALID = 1791504000   # 01.10 / 09.10 00:00 UTC
fee = lambda p: 0.07 * p * (1 - p); SEUILS = (500, 2000, 5000); GAP = 3; SPAN = 5

def lire(f):
    out = {}
    for st_, m in json.load(gzip.open(f))["marches"].items():
        st = int(st_); r = m.get("resultat") or {}
        if r.get("Up") not in (0.0, 1.0) or st >= FIN_VALID: continue
        vu = set(); wid = {}; rows = []
        for x in m["trades"]:
            if x[0] is None or not x[4] or not (0 < x[4] < 1) or x[5] is None: continue
            premier = x[6] not in vu; vu.add(x[6])
            rows.append((x[0] - st, wid.setdefault(x[1], len(wid)), x[2] == "BUY", x[3] == "Up", x[4], x[5], premier))
        out[st] = (int(r["Up"] == 1.0), np.array(rows, float).reshape(-1, 7))
    return out

def construire(npz, fichiers, avec_validation):
    z = np.load(npz); t0 = int(z["t"][0]); c = z["c"].astype(float)
    Cd2 = np.concatenate([[0], np.cumsum(np.diff(c, prepend=c[0]) ** 2)]); sd = lambda i, w: np.sqrt((Cd2[i + 1] - Cd2[i + 1 - w]) / w)
    with Pool(2) as P: blocs = P.map(lire, sorted(fichiers))
    ev = []; cyc = {}
    for b in blocs:
        for st, (upw, A) in b.items():
            if st >= FIN_EXPLO and not avec_validation: continue
            s0 = st - t0
            if s0 < 3700 or s0 + 300 >= len(c): continue
            cyc[st] = "exploration" if st < FIN_EXPLO else "validation"
            A = A[np.argsort(A[:, 0], kind="stable")]; B = A[A[:, 2] == 1]; tb = B[:, 0]; pu = np.where(B[:, 3] == 1, B[:, 4], 1 - B[:, 4])
            def med(lo, hi, oc=None):
                m = (tb > lo) & (tb <= hi)
                if oc is None: return np.median(pu[m]) if m.any() else np.nan
                m &= B[:, 3] == oc; return np.median(B[m, 4]) if m.any() else np.nan
            K = A[(A[:, 6] == 1) & (A[:, 2] == 1) & (A[:, 0] >= 0) & (A[:, 0] < 300)]          # preneur, achat
            uk, inv = np.unique(K[:, 1] * 2 + K[:, 3], return_inverse=True); tot = np.bincount(inv, weights=K[:, 4] * K[:, 5])
            for kk in np.where(tot >= SEUILS[0])[0]:
                g = K[inv == kk]; X = int(g[0, 3]); tt = g[:, 0]; nn = g[:, 4] * g[:, 5]; ss = g[:, 5]; sg = 1 if X else -1; i = 0
                cote = lambda v: (v if X else 1 - v) if np.isfinite(v) else np.nan
                while i < len(tt):
                    j = i; cum = sh = 0; fait = set()
                    while j < len(tt) and (j == i or (tt[j] - tt[j - 1] <= GAP and tt[j] - tt[i] <= SPAN)):
                        cum += nn[j]; sh += ss[j]
                        for S in SEUILS:
                            if cum >= S and S not in fait:
                                fait.add(S); te = int(tt[j]); i0 = s0 + te; s1 = sd(i0, 3600)
                                ev.append(dict(st=st, part=cyc[st], seuil=S, te=te, left=300 - te, X=X, xwin=upw if X else 1 - upw,
                                    pbig=cum / sh, seul=int(j == i), pav=cote(med(te - 6, te - 1)), p5=cote(med(te + 1, te + 6)),
                                    p10=cote(med(te + 5, te + 10)), p30=cote(med(te + 25, te + 35)), pfol=med(te + 1, te + 6, X),
                                    pfad=med(te + 1, te + 6, 1 - X), b10=sg * (c[i0 - 1] - c[i0 - 11]) / (s1 * np.sqrt(10))))
                        j += 1
                    i = j
    return pd.DataFrame(ev), cyc

REGLES = {"G1 suivre ≥ 2 000 $, prix 0,30–0,95": (lambda x: (x.seuil == 2000) & x.pbig.between(.30, .95) & x.left.between(10, 300), "suivre"),
          "G2 contrer ≥ 2 000 $, prix 0,30–0,95": (lambda x: (x.seuil == 2000) & x.pbig.between(.30, .95) & x.left.between(10, 300), "contrer"),
          "G3 contrer ≥ 500 $, prix 0,65–0,95, 60–120 s": (lambda x: (x.seuil == 500) & x.pbig.between(.65, .95) & x.left.between(60, 120), "contrer"),
          "G4 suivre ≥ 500 $, prix 0,95–0,99, 10–60 s": (lambda x: (x.seuil == 500) & x.pbig.between(.95, .99) & x.left.between(10, 60), "suivre")}

if __name__ == "__main__":
    VALID = "--validation" in sys.argv; args = [a for a in sys.argv[1:] if a != "--validation"]
    E, cyc = construire(args[0], args[1:], VALID); RNG = np.random.default_rng(1085)
    parts = ["exploration"] + (["validation"] if VALID else [])
    NC = {p: sum(v == p for v in cyc.values()) for p in parts}; out = {"cycles": NC, "regles": {}, "descriptif": {}, "derive": {}, "btc": {}}
    for nom, (f, sens) in REGLES.items():
        for pa in parts:
            P = E[E.part == pa]; x = P[f(P)].copy()
            x["px"] = x.pfol if sens == "suivre" else x.pfad; x["w"] = x.xwin if sens == "suivre" else 1 - x.xwin
            x = x[x.px.between(.01, .99)].sort_values(["st", "te"]).groupby("st").head(1)
            avant = x.pav if sens == "suivre" else 1 - x.pav
            for prix in ("observe", "pessimiste"):
                px = x.px if prix == "observe" else np.maximum(x.px, avant.fillna(0))
                pnl = (x.w / (px + fee(px)) - 1).values; vv = np.concatenate([pnl, np.zeros(NC[pa] - len(x))]) * 10
                bs = vv[RNG.integers(0, len(vv), (10000, len(vv)))].sum(1)
                out["regles"][f"{nom}|{pa}|{prix}"] = dict(cycles=NC[pa], achats=int(len(x)), gagnants=int(x.w.sum()), taux=float(x.w.mean()),
                    prix=float(px.mean()), roi=float(pnl.mean()), pnl10=float(vv.sum()), ic90=np.percentile(bs, [5, 95]).tolist(),
                    ic_bonf=np.percentile(bs, [1.25, 98.75]).tolist())
    E["lb"] = pd.cut(E.left, [0, 30, 60, 120, 200, 300]); E["ex_big"] = E.xwin - E.pbig; E["ex_fol"] = E.xwin - E.pfol
    E["d_entree"] = E.p5 - E.pav; E["c10"] = E.p10 - E.p5; E["c30"] = E.p30 - E.p5
    E["bdir"] = pd.cut(E.b10, [-99, -1, 1, 99], labels=["contre", "neutre", "avec"]); E["zone"] = np.where(E.pbig >= .95, "≥ 0,95", "< 0,95")
    def ic(g, col):
        sts = g.st.unique(); idx = {s: k for k, s in enumerate(sts)}; k = g.st.map(idx).values; v = g[col].values; ok = np.isfinite(v)
        sm = np.bincount(k[ok], weights=v[ok], minlength=len(sts)); nb = np.bincount(k[ok], minlength=len(sts))
        dr = RNG.integers(0, len(sts), (2000, len(sts))); r = sm[dr].sum(1) / np.maximum(nb[dr].sum(1), 1)
        return np.percentile(r, [5, 95]).round(4).tolist()
    for pa in parts:
        P = E[E.part == pa]; L = []
        for (S, lb), g in P.groupby(["seuil", "lb"], observed=True):
            L.append(dict(seuil=int(S), reste=str(lb), n=len(g), cycles=int(g.st.nunique()), prix_gros=float(g.pbig.mean()), freq=float(g.xwin.mean()),
                          ecart_gros=float(g.ex_big.mean()), ic90_ecart_gros=ic(g, "ex_big"), prix_nous=float(g.pfol.mean()), ecart_nous=float(g.ex_fol.mean())))
        out["descriptif"][pa] = L; D = []
        for (S, zn), g in P.groupby(["seuil", "zone"]):
            D.append(dict(seuil=int(S), zone=zn, n=len(g), d_entree=float(g.d_entree.mean()), c10=float(g.c10.mean()), ic90_c10=ic(g, "c10"),
                          c30=float(g.c30.mean()), ic90_c30=ic(g, "c30")))
        out["derive"][pa] = D; Bt = []
        for (S, bd), g in P.groupby(["seuil", "bdir"], observed=True):
            Bt.append(dict(seuil=int(S), btc=str(bd), n=len(g), prix_gros=float(g.pbig.mean()), freq=float(g.xwin.mean()), ecart_gros=float(g.ex_big.mean()),
                           ic90_ecart_gros=ic(g, "ex_big"), ecart_nous=float(g.ex_fol.mean()), ic90_ecart_nous=ic(g, "ex_fol")))
        out["btc"][pa] = Bt
        out.setdefault("evenements", {})[pa] = {int(S): int((P.seuil == S).sum()) for S in SEUILS}
        out.setdefault("part_095", {})[pa] = float((P[P.seuil == 500].pbig >= .95).mean())
    s = json.dumps(out, ensure_ascii=False, indent=1, default=str); print(s)
    open(os.path.join(ICI, "grosses_transactions_h1085_" + ("validation" if VALID else "exploration") + ".json"), "w").write(s)
