"""BOT95 V3 — expérience 006 : routeur. PAS de grand routeur optimisé (l'étude META-ROUTER a déjà montré que le routage dynamique
sur 3 jours perd contre une stratégie fixe). On teste UNE seule règle simple, pré-enregistrée avant exécution :
  R0 = la stratégie fixe (parmi les 7) au meilleur résultat d'APPRENTISSAGE, exécution délai 0,5 s ;
  R* = R0, mais on n'achète pas dans les cases (volatilité haute/basse × jour/nuit, seuils de l'expérience 005) où R0 avait une espérance
       d'apprentissage < 0 avec au moins 10 achats.
Jugement : différence R* − R0 sur validation et inédit, intervalle à 90 % par blocs d'une heure. Aucun réglage sur validation / inédit."""
exec(open("etude/bot5min/v3_commun.py").read())
DL = 0.5
TRD = {n: {st: exe(st, s, DL) for st, s in STRATS[n].items()} for n in NOMS7}
appres = {n: sum(x["pn"] for st, x in TRD[n].items() if x and PER(st) == "apprentissage") for n in NOMS7}
R0 = max(NOMS7, key=lambda n: appres[n])
VOLS = [vol(int(s["t"])) for n in NOMS7 for st, s in STRATS[n].items() if PER(st) == "apprentissage" and vol(int(s["t"])) is not None]
VOL_MED = float(np.median(VOLS))
def case(s):
    v = vol(int(s["t"])); h = time.gmtime(s["t"] + 7200).tm_hour
    return ("vol. inconnue" if v is None else ("vol. haute" if v >= VOL_MED else "vol. basse"), "nuit" if (h >= 22 or h < 8) else "jour")
TAB = collections.defaultdict(list)
for st, s in STRATS[R0].items():
    if PER(st) == "apprentissage" and TRD[R0][st]: TAB[case(s)].append(TRD[R0][st]["pn"])
INTERDIT = {c for c, L in TAB.items() if len(L) >= 10 and np.mean(L) < 0}
def r0(st): return TRD[R0].get(st)
def rs(st):
    s = STRATS[R0].get(st)
    return None if (s is None or case(s) in INTERDIT) else TRD[R0].get(st)
RNG2 = np.random.default_rng(6)
def diff(S, B=4000):
    H = collections.defaultdict(float)
    for st in S: H[st // 3600] += ((rs(st) or {}).get("pn", 0.0)) - ((r0(st) or {}).get("pn", 0.0))
    hv = np.array(list(H.values())); sims = hv[RNG2.integers(0, len(hv), (B, len(hv)))].sum(axis=1)
    return hv.sum(), np.percentile(sims, 5), np.percentile(sims, 95), float(np.mean(sims <= 0))
out = ["# BOT95 V3 — Expérience 006 : routeur (une seule règle simple, pré-enregistrée)", "", ENTETE, "",
       "Rappel de l'étude précédente (`resultat_meta_router.md`) : hors apprentissage, R1 (choix par volatilité × tendance) − R0 (fixe) = −1 027 $ [−2 658 ; +536], "
       "R2 − R0 = −1 236 $ [−2 712 ; +215] : le routage dynamique perdait contre la meilleure stratégie fixe.", "",
       f"Exécution : délai {str(DL).replace('.', ',')} s demandé (~0,6 s réel), meilleur vendeur seul, quantité affichée, prix ≤ prix de décision, frais, 50 $ max.", "",
       "## Choix de R0 sur l'apprentissage seulement", "", "| Stratégie | Résultat d'apprentissage (délai 0,5 s) |", "|---|---|"]
out += [f"| {n}{' ← R0' if n == R0 else ''} | {f0(appres[n])} |" for n in sorted(NOMS7, key=lambda n: -appres[n])]
out += ["", f"## Cases interdites par la règle (R0 = {R0}, seuil de volatilité = médiane d'apprentissage {str(round(VOL_MED, 2)).replace('.', ',')} $/s)", "",
        "| Case | Achats app. | Espérance app. | Interdite |", "|---|---|---|---|"]
out += [f"| {c[0]} · {c[1]} | {len(L)} | {fe(np.mean(L))} | {'oui' if c in INTERDIT else 'non'} |" for c, L in sorted(TAB.items(), key=lambda x: str(x[0]))]
out += ["", "## Résultats", ""]
for p in PERS:
    out += [f"**{p}**", "", hdr("Politique"), lig(f"R0 fixe : {R0}", bilan([r0(st) for st in CYC[p]], CYC[p])), lig("R* : R0 sauf cases interdites", bilan([rs(st) for st in CYC[p]], CYC[p])), ""]
out += ["## R* bat-il R0 ? (différence, intervalle à 90 % par blocs d'une heure)", "", "| Période | Différence R* − R0 | IC 90 % | Probabilité ≤ 0 |", "|---|---|---|---|"]
for p in ("validation", "inédit"):
    d, lo, hi, pz = diff(CYC[p]); out.append(f"| {p} | {f0(d)} | [{f0(lo)} ; {f0(hi)}] | {100 * pz:.0f} % |")
d, lo, hi, pz = diff(CYC["validation"] + CYC["inédit"]); out.append(f"| validation + inédit | {f0(d)} | [{f0(lo)} ; {f0(hi)}] | {100 * pz:.0f} % |")
out += ["", "Inédit : les 40 cycles inédits sont tous de jour (10.10 10:25 → 13:45) ; aucune case interdite n'y tombe, R* = R0 à l'identique (différence nulle, la « probabilité ≤ 0 » de 100 % n'a pas de sens ici).", "", "Si l'intervalle contient 0, la nouvelle règle ne change pas le verdict de l'étude META-ROUTER : pas de preuve qu'un routage par régime bat une stratégie fixe. "
        "L'expérience 005 (stabilité des régimes) explique pourquoi : les écarts entre régimes ne se répètent pas de l'apprentissage à la validation.", ""]
open("etude/bot5min/resultat_v3_exp006.md", "w").write("\n".join(out)); print("\n".join(out))
