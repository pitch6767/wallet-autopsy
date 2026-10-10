"""Fiabilité du moteur TWAP fin (demande ChatGPT 10.10.2026 08:37) — erreurs de prévision, quantiles, incertitude après saut, certitudes extrêmes,
mémoire des erreurs, prix Chainlink fantôme, santé du modèle. Mêmes données et mêmes périodes que oracle_tournoi.py. Diagnostic : aucune stratégie modifiée."""
import sys
sys.path.insert(0, "etude/bot5min")
_T = open("etude/bot5min/oracle_tournoi.py").read()
exec(_T.split("# ---------------- Q1 transmission")[0])
exec(_T.split("# ---------------- tournoi : construction des mesures")[1].split("# apprentissage des coefficients")[0])
out = [f"# Fiabilité du moteur TWAP fin — BTC, {len(valides)} cycles ({hs(valides[0])} → {hs(valides[-1] + 300)})", "",
       f"Apprentissage avant le {hs(CUT)} ; validation {hs(CUT)} → {hs(NUIT0)} ; nuit du 10.10 à part. Tout ce qui est appris l'est sur l'apprentissage seulement.", ""]
# ---- enrichissement des mesures
for m in M:
    m["E"] = E_(m, m["Lp"]); m["u"] = (m["F"] - m["E"]) / m["sd"]; m["p"] = phi((m["E"] - m["K"]) / m["sd"])
    m["kc"] = 60 - m["rem"]
    m["Ecl"] = E_(m, m["cl"])                            # si les prix restants restaient au dernier Chainlink
    lb, lc = lev("bn", m["t"]), lev("cb", m["t"])
    m["spot"] = float(np.median([x for x in (lb, lc) if x is not None])) if (lb is not None or lc is not None) else m["cons"]
    m["reg"] = "calme" if m["sg"] < 2 else "agité"
    m["bk"] = "avant la fenêtre" if m["rem"] == 60 else ("45-60 s restantes" if m["rem"] > 45 else "30-45 s" if m["rem"] > 30 else "15-30 s" if m["rem"] > 15 else "< 15 s")
for st in {m["st"] for m in M}: pass
TR = [m for m in M if per(m["st"]) == "apprentissage"]
def une_par_s(L):
    vu = set(); R_ = []
    for m in L:
        k = (m["st"], int(m["t"]))
        if k not in vu: vu.add(k); R_.append(m)
    return R_
# ---- E : quantiles empiriques des erreurs (par tranche de temps et régime), appris sur l'apprentissage
Q = collections.defaultdict(list)
for m in une_par_s(TR): Q[(m["bk"], m["reg"])].append(m["u"]); Q[(m["bk"], "*")].append(m["u"])
QS = {k: np.sort(np.array(v)) for k, v in Q.items() if len(v) >= 200}
def pE(m):
    a = QS.get((m["bk"], m["reg"])) if (m["bk"], m["reg"]) in QS else QS.get((m["bk"], "*"))
    if a is None: return m["p"]
    x = (m["K"] - m["E"]) / m["sd"]                      # Up gagne si u > x
    k = np.searchsorted(a, x, side="right"); return float(np.clip((len(a) - k + 0.5) / (len(a) + 1), 0.0005, 0.9995))
# ---- G : incertitude élargie après un saut (facteur appris)
uj = [m["u"] for m in une_par_s(TR) if m["saut"]]; un = [m["u"] for m in une_par_s(TR) if not m["saut"]]
KJ = float(np.std(uj) / np.std(un)) if len(uj) > 30 else 1.0
pG = lambda m: phi((m["E"] - m["K"]) / (m["sd"] * (KJ if m["saut"] else 1.0)))
# ---- plancher d'incertitude : écart-type des erreurs normalisées par tranche (appris)
SDU = {k: float(np.std(v)) for k, v in Q.items() if len(v) >= 200}
pF = lambda m: phi((m["E"] - m["K"]) / (m["sd"] * max(1.0, SDU.get((m["bk"], m["reg"]), SDU.get((m["bk"], "*"), 1.0)))))
pD = lambda m: phi((E_(m, m["cl"] + 0.98 * (m["cons"] - m["cl"])) - m["K"]) / m["sd"])
MODS = {"A — moteur actuel": lambda m: m["p"], "D — prévision Chainlink (déjà en fantôme)": pD,
        "E — quantiles empiriques des erreurs (appris)": pE, f"F — incertitude élargie par tranche (appris, × jusqu'à {max(SDU.values()):.1f})": pF,
        f"G — incertitude × {KJ:.2f} juste après un saut (appris)": pG}
out += ["## 1. Les erreurs du moteur sont-elles à la taille annoncée ? (idées 11-13, 17-19, 21)", "",
        "Erreur normalisée = (moyenne finale officielle − moyenne prévue) / écart-type annoncé par le moteur. Si le moteur est juste, son écart-type vaut 1 et 95 % des erreurs sont entre −1,96 et +1,96.", "",
        "| Tranche | Régime | Mesures (appr.) | Écart-type réel des erreurs | Part hors ±1,96 (attendu 5 %) | Quantiles 5 % / 95 % |", "|---|---|---|---|---|---|"]
for bk in ("avant la fenêtre", "45-60 s restantes", "30-45 s", "15-30 s", "< 15 s"):
    for rg in ("agité", "calme"):
        v = Q.get((bk, rg))
        if not v or len(v) < 100: continue
        a = np.array(v); out.append(f"| {bk} | {rg} | {len(a)} | {a.std():.2f} | {100 * np.mean(np.abs(a) > 1.96):.1f} % | {np.quantile(a, 0.05):+.2f} / {np.quantile(a, 0.95):+.2f} |")
out += ["", "### Couverture des intervalles (idée 21) : intervalles appris sur l'apprentissage, vérifiés ensuite", "",
        "| Période | Intervalle 50 % | 80 % | 95 % |", "|---|---|---|---|"]
for g in ("apprentissage", "validation", "nuit 10.10"):
    L = une_par_s([m for m in M if per(m["st"]) == g]); cov = []
    for c in (0.50, 0.80, 0.95):
        ok = 0; n = 0
        for m in L:
            a = QS.get((m["bk"], m["reg"])) if (m["bk"], m["reg"]) in QS else QS.get((m["bk"], "*"))
            if a is None: continue
            lo, hi = np.quantile(a, (1 - c) / 2), np.quantile(a, 1 - (1 - c) / 2); n += 1; ok += lo <= m["u"] <= hi
        cov.append(f"{100 * ok / max(1, n):.0f} %")
    out.append(f"| {g} | " + " | ".join(cov) + " |")
# ---- tournoi de calibration
out += ["", "## 2. Tournoi des probabilités (même moyenne prévue sauf D ; mêmes mesures, une par seconde, 90-20 s)", ""]
def ll(p, y): p = np.clip(p, 1e-4, 1 - 1e-4); return -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))
SIG = collections.defaultdict(dict)
for g in ("apprentissage", "validation", "nuit 10.10"):
    L = une_par_s([m for m in M if per(m["st"]) == g]); y = np.array([m["y"] for m in L], float)
    out += [f"### {g}", "", "| Modèle | Brier | Perte log | Proba > 95 % fausse | Proba > 99 % fausse |", "|---|---|---|---|---|"]
    for nom, f in MODS.items():
        p = np.array([f(m) for m in L]); c95 = np.maximum(p, 1 - p) > 0.95; c99 = np.maximum(p, 1 - p) > 0.99; w = (p > 0.5) != (y > 0.5)
        out.append(f"| {nom} | {np.mean((p - y) ** 2):.4f} | {ll(p, y):.4f} | {(c95 & w).sum()} / {c95.sum()} ({100 * (c95 & w).sum() / max(1, c95.sum()):.1f} %) | {(c99 & w).sum()} / {c99.sum()} ({100 * (c99 & w).sum() / max(1, c99.sum()):.1f} %) |")
    out.append("")
for m in M:
    for nom, f in MODS.items():
        d = SIG[nom]
        if m["st"] in d: continue
        p = f(m)
        for up in (True, False):
            a = m["ua"] if up else m["da"]; z = m["uz"] if up else m["dz"]
            if a is None or not (0.02 <= a <= 0.98) or z <= 0: continue
            if (p if up else 1 - p) - a >= 0.20:
                gm = m["y"] if up else not m["y"]; q = min(50 / a, z); d[m["st"]] = (q * ((1 if gm else 0) - a - FEE(a)), q * a, gm); break
out += ["### Rejeu TWAP fin (premier signal, avantage ≥ 0,20, quantité affichée, frais compris)", "",
        "| Modèle | Apprentissage | Validation | Nuit 10.10 | Jackpots valid. + nuit |", "|---|---|---|---|---|"]
for nom in MODS:
    cel = []
    for g in ("apprentissage", "validation", "nuit 10.10"):
        L = [v for st, v in SIG[nom].items() if per(st) == g]
        cel.append(f"{f0(sum(l[0] for l in L))} ({len(L)}, {100 * sum(l[2] for l in L) / max(1, len(L)):.0f} %)")
    jk = sum(1 for st, l in SIG[nom].items() if per(st) != "apprentissage" and l[0] >= 4 * l[1])
    out.append(f"| {nom} | " + " | ".join(cel) + f" | {jk} |")
# ---- 3. audit des certitudes extremes
out += ["", "## 3. D'où viennent les certitudes ? (idées 6, 22, 23, 43, 46) — moteur actuel, probabilités > 95 %, toutes périodes", "",
        "| Groupe | Mesures | Fausses | Taux faux | Dont nuit 10.10 : taux faux |", "|---|---|---|---|---|"]
EX = collections.defaultdict(list)
byst = collections.defaultdict(list)
for m in M: byst[m["st"]].append(m)
for st, L in byst.items():
    L.sort(key=lambda m: m["t"]); debut = None
    for m in L:
        p = m["p"]
        if max(p, 1 - p) <= 0.95: debut = None; continue
        if debut is None or (debut[1] != (p > 0.5)): debut = (m["t"], p > 0.5)
        age = m["t"] - debut[0]; faux = (p > 0.5) != m["y"]; nuit = per(st) == "nuit 10.10"
        same_cl = (m["Ecl"] > m["K"]) == (p > 0.5)
        groups = ["secondes de la fenêtre déjà connues : " + ("0" if m["kc"] == 0 else "1-20" if m["kc"] <= 20 else "21-40" if m["kc"] <= 40 else "41-60"),
                  "le dernier Chainlink seul donne déjà ce côté" if same_cl else "seule l'extrapolation des exchanges donne ce côté",
                  "saut des exchanges dans les 2 dernières secondes" if m["saut"] else "pas de saut récent",
                  "certitude née il y a " + ("< 0,25 s" if age < 0.25 else "0,25-1 s" if age < 1 else "1-3 s" if age < 3 else "> 3 s")]
        for g in groups: EX[g].append((faux, nuit))
for g in sorted(EX):
    a = np.array(EX[g], float); n_ = a[a[:, 1] == 1]
    out.append(f"| {g} | {len(a)} | {int(a[:, 0].sum())} | {100 * a[:, 0].mean():.2f} % | {100 * n_[:, 0].mean() if len(n_) else float('nan'):.1f} % ({len(n_)}) |")
# ---- 4. memoire des erreurs
out += ["", "## 4. Mémoire des erreurs (idées 14-16, 36-40)", ""]
res = []
for st in valides:
    for s in range(st, st + 300):
        c0, c1 = sec("cl", s), sec("cl", s + 1); t = s + 0.999
        L4 = [lev(x, t) for x in EXCH]; L4 = [x for x in L4 if x is not None]
        if c0 is None or c1 is None or not L4: res.append(None); continue
        res.append((c1 - c0) - 0.24 * (float(np.median(L4)) - c0))
x = np.array([r if r is not None else np.nan for r in res])
out += ["Erreur à 1 s de la prévision Chainlink (variation réelle − 0,24 × écart consensus, la part transmise en 1 s mesurée ce matin) ; autocorrélation :", "",
        "| Décalage | 1 s | 2 s | 5 s | 10 s |", "|---|---|---|---|---|",
        "| Autocorrélation | " + " | ".join(f"{np.corrcoef(x[:-k][~np.isnan(x[:-k]) & ~np.isnan(x[k:])], x[k:][~np.isnan(x[:-k]) & ~np.isnan(x[k:])])[0, 1]:+.2f}" for k in (1, 2, 5, 10)) + " |", ""]
ev = []
for st in valides:
    L = [m for m in M if m["st"] == st and 30 <= m["tl"] <= 40]
    if L: ev.append((st, float(np.mean([m["F"] - m["E"] for m in L]))))
ev.sort(); a = np.array([e for _, e in ev])
out.append(f"Biais d'un cycle à l'autre (idées 16, 39) : corrélation entre l'erreur signée de la moyenne finale d'un cycle et celle du cycle suivant = **{np.corrcoef(a[:-1], a[1:])[0, 1]:+.2f}** ({len(a)} cycles). Erreur signée moyenne : {a.mean():+.2f} $ (apprentissage {np.mean([e for st, e in ev if per(st) == 'apprentissage']):+.2f} $, validation {np.mean([e for st, e in ev if per(st) == 'validation']):+.2f} $, nuit {np.mean([e for st, e in ev if per(st) == 'nuit 10.10']):+.2f} $).")
# ---- 5. prix Chainlink fantome
out += ["", "## 5. Prix Chainlink « fantôme » : quel estimateur prévoit le mieux le Chainlink suivant ? (idées 48-53)", "",
        "| Estimateur | Erreur sur Chainlink dans 1 s (RMSE) | dans 5 s | Erreur sur la moyenne finale si prolongé |", "|---|---|---|---|"]
EST = {"dernier Chainlink": lambda m: m["cl"], "dernier Bybit (moteur actuel)": lambda m: m["Lp"], "consensus spot (Binance, Coinbase)": lambda m: m["spot"],
       "consensus des 4 exchanges": lambda m: m["cons"], "prévision Chainlink D (Chainlink + 0,98 × écart)": lambda m: m["cl"] + 0.98 * (m["cons"] - m["cl"]),
       "Chainlink + 0,24 × écart (part transmise en 1 s)": lambda m: m["cl"] + 0.24 * (m["cons"] - m["cl"])}
LV = une_par_s([m for m in M if per(m["st"]) != "apprentissage"])
for nom, f in EST.items():
    e1, e5, ef = [], [], []
    for m in LV:
        v = f(m); c1, c5 = der("cl", m["t"] + 1), der("cl", m["t"] + 5)
        if c1: e1.append(c1 - v)
        if c5: e5.append(c5 - v)
        ef.append(m["F"] - E_(m, v))
    out.append(f"| {nom} | {np.sqrt(np.mean(np.square(e1))):.2f} $ | {np.sqrt(np.mean(np.square(e5))):.2f} $ | {np.sqrt(np.mean(np.square(ef))):.2f} $ |")
# ---- 6. sante du modele
out += ["", "## 6. Santé du modèle par tranche de 3 heures (idées 31-35) : moteur contre carnet (Brier, mesures où le carnet a un milieu)", "",
        "| Tranche | Mesures | Volatilité médiane ($/s) | Brier moteur | Brier carnet | Écart (moteur − carnet) | CUSUM |", "|---|---|---|---|---|---|---|"]
blocs = collections.defaultdict(list)
for m in une_par_s(M):
    if m["mid"] is None: continue
    blocs[(m["st"] + 7200) // 10800].append(m)
cus = 0.0; ref = None
for b in sorted(blocs):
    L = blocs[b]; y = np.array([m["y"] for m in L], float); pa = np.array([m["p"] for m in L]); pm = np.array([m["mid"] for m in L])
    d = np.mean((pa - y) ** 2) - np.mean((pm - y) ** 2)
    if ref is None: ref = 0.0
    cus = max(0.0, cus + d - 0.005)                      # alerte quand le moteur fait durablement pire que le carnet (+0,005 de tolérance)
    out.append(f"| {time.strftime('%d.%m %H:%M', time.gmtime(b * 10800))} | {len(L)} | {np.median([m['sg'] for m in L]):.1f} | {np.mean((pa - y) ** 2):.4f} | {np.mean((pm - y) ** 2):.4f} | {d:+.4f} | {cus:.3f}{' ⚠' if cus > 0.03 else ''} |")
open("etude/bot5min/resultat_oracle_fiabilite.md", "w").write("\n".join(out)); print("\n".join(out))
