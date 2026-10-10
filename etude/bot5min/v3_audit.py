"""BOT95 V3 — audit des données disponibles hors ligne (couverture exacte, champs manquants) + rejeu contre fantômes réels.
Aucune estimation des données manquantes : on les signale."""
import datetime
exec(open("etude/bot5min/v3_commun.py").read())
out = ["# BOT95 V3 — audit des données (hors ligne)", "", ENTETE, ""]
# ---------- rec_BTC
out += ["## 1. Lignes enregistrées `bot95/donnees/<jour>/rec_BTC.json.gz`", "",
        "| Jour (fichier) | Lignes | Première ligne | Dernière ligne | Intervalle médian | Trous > 5 s (nombre · durée totale) |", "|---|---|---|---|---|---|"]
for f in sorted(glob.glob("bot95/donnees/*/rec_BTC.json.gz")):
    L = sorted({r[0]: r for doc in json.load(gzip.open(f, "rt")).values() for r in doc["lignes"]}.values(), key=lambda r: r[0])
    T = np.array([r[0] for r in L]); d = np.diff(T); g = d[d > 5]
    out.append(f"| {f.split('/')[2]} | {len(L)} | {hsec(T[0])} | {hsec(T[-1])} | {np.median(d):.2f} s | {len(g)} · {g.sum() / 60:.0f} min |")
T = np.array([r[0] for r in rows]); d = np.diff(T)
out += ["", f"Total après dédoublonnage : {len(rows)} lignes, {hsec(T[0])} → {hsec(T[-1])}. Intervalle entre lignes : "
        f"5 % {np.percentile(d, 5):.2f} s · médiane {np.median(d):.2f} s · 95 % {np.percentile(d, 95):.2f} s · 99 % {np.percentile(d, 99):.2f} s. "
        "**La résolution temporelle réelle des carnets est donc d'environ 0,3 s (pas 0,25 s)** : un délai demandé de 0,25 s devient 0,3 s, 0,5 s devient ~0,6 s, 1 s devient ~1,2 s.", "",
        "| Colonne | Champ | Valeurs manquantes |", "|---|---|---|"]
NOMC = ["t", "début du cycle", "proba Up du modèle du bot (0,08 %)", "Up meilleur acheteur", "Up meilleur vendeur", "Down meilleur acheteur", "Down meilleur vendeur",
        "taille Up acheteur", "taille Up vendeur", "taille Down acheteur", "taille Down vendeur", "Bybit perp", "OKX perp", "Coinbase", "Binance spot", "Chainlink", "prix d'exercice"]
for i, n in enumerate(NOMC):
    m = sum(1 for r in rows if r[i] is None); out.append(f"| r[{i}] | {n} | {m} ({100 * m / len(rows):.1f} %) |")
out += ["", "Champs **absents** des lignes : profondeur au-delà du meilleur niveau Polymarket (seul le meilleur prix et sa taille), transactions Polymarket (qui a acheté, à quel prix), "
        "position dans la file d'attente, intérêt ouvert (open interest), horodatage des bourses à la source (seule l'heure de réception par le bot est connue).", ""]
nc = len({r[1] for r in rows}); out += [f"Cycles présents dans les lignes : {nc} ; avec résultat officiel et lignes complètes (modèle + 4 prix Polymarket) : {len(valides)}.", ""]
b = sorted(int(k.split(":")[1]) for k in O if k.startswith("BTC"))
out += [f"Règlements officiels `officiels.json` : {len(b)} cycles BTC, {hs(b[0])} → {hs(b[-1] + 300)}, sans trou. "
        f"Les lignes vont jusqu'à {hsec(T[-1])} : les cycles après {hs(b[-1] + 300)} n'ont pas encore de résultat officiel et sont exclus.", ""]
out += ["| Période | Cycles | De | À |", "|---|---|---|---|"] + [f"| {p} | {len(CYC[p])} | {hs(CYC[p][0])} | {hs(CYC[p][-1] + 300)} |" for p in PERS] + [""]
# ---------- signaux des 7 stratégies
out += ["## 2. Signaux rejoués des 7 stratégies principales (un par cycle au plus)", "", "| Stratégie | app. | valid. | inédit | Définition |", "|---|---|---|---|---|"]
DEF = {"V2-F original (O8)": "écart ≥ 0,20 (modèle du bot 0,08 %) qui a grandi de 3 c en 3 s, vendeur 0,03-0,97",
       "V2-F 0,01 % (H1)": "même règle, modèle du bot ramené à 0,01 % (= fantôme réel « V2-F incertitude 0,01 % »)",
       "V2-D perp 120-269 s": "écart ≥ 0,20, 120-269 s restantes, perp Bybit dans notre sens sur 5 s",
       "V2-G jury des bourses": "écart ≥ 0,20, les 4 bourses dans notre sens sur 3 s, modèle monte plus vite que Polymarket (3 c)",
       "désaccord 30": "premier écart ≥ 0,30 du cycle, vendeur 0,02-0,98",
       "désaccord 20 60-180 s": "premier écart ≥ 0,20 entre 60 et 180 s restantes",
       "désaccord 20 jeton 0,35-0,65": "premier écart ≥ 0,20 avec vendeur 0,35-0,65"}
for n in NOMS7:
    out.append(f"| {n} | " + " | ".join(str(sum(1 for st in STRATS[n] if PER(st) == p)) for p in PERS) + f" | {DEF[n]} |")
out.append("")
# ---------- lead
D = json.load(gzip.open("bot95/lead.json.gz", "rt"))
av = [x for x in D if x["phase"] == "avant"]; ap = [x for x in D if x["phase"] == "apres"]
ust = sorted({x["start"] for x in av}); okO = [s for s in ust if (O.get(f"BTC:{s}") or {}).get("gagnant")]
out += ["## 3. Photos « qui a bougé en premier » `bot95/lead.json.gz`", "",
        f"- {len(D)} photos : {len(av)} « avant » (10 s avant le premier désaccord ≥ 0,20 du cycle vu par le bot en direct) et {len(ap)} « après » (10 s après), "
        f"{hsec(min(x['t'] for x in D))} → {hsec(max(x['t'] for x in D))}.",
        f"- {len(ust)} cycles distincts ; {len(av) - len(ust)} cycles ont deux photos « avant » (on garde la première) ; {len(ust) - len({x['start'] for x in ap})} cycles sans photo « après ».",
        f"- {len(okO)} cycles photographiés ont un résultat officiel ({len(ust) - len(okO)} sans résultat : après {hs(b[-1] + 300)}).",
        "- Échantillonnage : une ligne toutes les 100 ms (intervalle 0,09-0,11 s). **Mais les prix des bourses ne changent pas toutes les 100 ms** : "
        "intervalle médian entre deux changements = Bybit 0,4 s, OKX 0,4 s, Coinbase 0,5 s, Binance 0,4 s, Chainlink 0,9 s ; le carnet Polymarket change à chaque ligne. "
        "La résolution effective de l'ordre « qui bouge en premier » est donc de 100 ms au mieux, souvent 0,4-0,5 s pour les bourses.",
        "- Les horodatages sont l'heure de RÉCEPTION par le bot (Cloudflare), pas l'heure de l'événement à la bourse : la latence réseau propre à chaque source est mélangée à l'avance réelle.",
        "- Colonnes : 5 prix (Bybit perp, OKX perp, Coinbase, Binance spot, Chainlink), carnet Bybit (meilleurs prix, profondeurs 1/3/5/10 pb), flux perp, liquidations, "
        "3 meilleurs niveaux acheteurs/vendeurs Up et Down Polymarket, flux Polymarket agrégés (retraits/ajouts/échanges, sans prix ni position en file).", ""]
for p in PERS:
    out.append(f"  - {p} : {sum(1 for s in ust if PER(s) == p)} cycles photographiés")
out.append("")
# ---------- autres fichiers
tw = json.load(open("bot95/twap_carnets.json")); vi = json.load(open("bot95/vitesse.json"))
out += ["## 4. Autres fichiers", "",
        f"- `twap_carnets.json` : {len(tw)} carnets à 8 niveaux aux signaux TWAP ({hsec(min(x['t0'] for x in tw))} → {hsec(max(x['t0'] for x in tw))}), "
        "aux délais 0 / 0,25 / 1 / 2 / 5 s. Stratégies TWAP seulement : hors du périmètre des 7 stratégies, non utilisé.",
        f"- `vitesse.json` : {len(vi)} signaux ({hsec(min(x['t0'] for x in vi))} → {hsec(max(x['t0'] for x in vi))}) avec carnets à 0,1 / 0,25 / 0,5 / 1 / 2 s : trop peu pour une mesure.",
        "- Intérêt ouvert (open interest) Polymarket : **absent de toutes les données**.", ""]
# ---------- fantômes réels contre rejeu
out += ["## 5. Fantômes réels (`bot95/sauvegarde`) contre rejeu de l'étude — exécution théorique ou simulée ?", "",
        "Le fantôme réel « achète » au meilleur vendeur vu par le bot en direct ; le rejeu achète au meilleur vendeur de la ligne enregistrée au même instant (délai 0). "
        "Comparaison sur les cycles réglés où les deux existent.", "",
        "| Fantôme réel | Rejeu | Trades réels (cycles réglés) | Période couverte | Cycles communs | Même côté | Résultat réel (communs) | Résultat rejeu délai 0 (communs) | Rejeu délai 0,5 s demandé (~0,6 s réel) (communs) |",
        "|---|---|---|---|---|---|---|---|---|"]
MAP = [("V2-F_ecart_qui_grandit_BTC", "V2-F original (O8)"), ("V2-F_incertitude_0,01_BTC", "V2-F 0,01 % (H1)"),
       ("V2-D_perp_120-269_s_BTC", "V2-D perp 120-269 s"), ("V2-G_jury_des_bourses_BTC", "V2-G jury des bourses")]
def iso(s): return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
for fn, n in MAP:
    d = json.load(open(f"bot95/sauvegarde/{fn}.json")); TRr = {}
    for a in d["archive"]: TRr[iso(a[0])] = dict(up=a[1] == "Up", net=a[3])
    for k, v in d["trades"].items():
        if v.get("net") is not None: TRr[iso(v["heure"])] = dict(up=v["cote"] == "Up", net=v["net"])
    par = {}
    for t, v in TRr.items():
        st = int(t // 300 * 300)
        if st in C and (O.get(f"BTC:{st}") or {}).get("gagnant") and st not in par: par[st] = (t, v)
    com = [st for st in par if st in STRATS[n]]; same = [st for st in com if par[st][1]["up"] == STRATS[n][st]["up"]]
    r0 = sum((exe(st, STRATS[n][st]) or {}).get("pn", 0) for st in com); r5 = sum((exe(st, STRATS[n][st], 0.5) or {}).get("pn", 0) for st in com)
    rr = sum(par[st][1]["net"] for st in com); ts = sorted(par)
    out.append(f"| {d['nom']} | {n} | {len(par)} | {hs(ts[0])} → {hs(ts[-1] + 300)} | {len(com)} | {len(same)} | {f0(rr)} | {f0(r0)} | {f0(r5)} |" if ts else f"| {d['nom']} | {n} | 0 | — | — | — | — | — | — |")
out += ["", "**Le rejeu ne reproduit pas le fantôme réel** sur V2-D et V2-G (écarts de 1 000 à 1 800 $ sur les mêmes cycles) : instants et prix de décision différents entre le bot en direct et les lignes enregistrées 0,3 s. Toute conclusion de rejeu est donc une SIMULATION, pas le résultat du bot.", "Les fantômes réels ne couvrent que le 09.10-10.10 (le fichier V2-F 0,01 % seulement le 10.10 de 12:40 à 13:45, 11 trades) : ils servent de contrôle, pas d'échantillon. "
        "Désaccord 30 / désaccord 20 60-180 s / jeton 0,35-0,65 n'ont pas de fantôme réel avec exactement la même règle.", ""]
open("etude/bot5min/resultat_v3_audit.md", "w").write("\n".join(out)); print("\n".join(out))
