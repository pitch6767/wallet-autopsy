"""Erreur du prix a battre affiche contre l'officiel (BTC), 07.10 -> 09.10.2026.
Affiche = valeur du site (API crypto-price) enregistree par le bot (dernier prix a battre du cycle dans les carnets enregistres).
Officiel = priceToBeat / finalPrice de la fiche du marche (gamma), publies 3-7 min apres la fin."""
import json, gzip, glob, time, math, statistics as stt, collections
import numpy as np
O = json.load(open("bot95/officiels.json"))
rows = {}
for f in sorted(glob.glob("bot95/donnees/*/rec_BTC.json.gz")):
    for doc in json.load(gzip.open(f, "rt")).values():
        for r in doc["lignes"]: rows[r[0]] = r
rows = sorted(rows.values(), key=lambda r: r[0])
K = {}; P1 = {}
for r in rows:
    if r[16]: K[r[1]] = r[16]
    p = r[11] or r[12]
    if p: P1[int(r[0])] = p
def px(s):
    for i in range(5):
        if s - i in P1: return P1[s - i]
hs = lambda t: time.strftime("%d.%m %H:%M", time.gmtime(t + 7200))
out = ["# L'erreur du prix à battre affiché — BTC, " + hs(min(K)) + " → " + hs(max(K)), ""]
# 1. continuite
c = [(st, O[f"BTC:{st}"]["final"], O[f"BTC:{st + 300}"]["ptb"]) for st in K if O.get(f"BTC:{st}", {}).get("final") and O.get(f"BTC:{st + 300}", {}).get("ptb")]
eg = sum(1 for _, a, b in c if abs(a - b) < 0.01)
out += ["## 1. Continuité officielle", "", f"Prix final officiel d'un cycle = prix à battre officiel du suivant : **{eg} sur {len(c)}** paires de cycles consécutifs (à 1 centime près).", ""]
# 2. erreurs debut / fin
D = []
for st in sorted(K):
    o = O.get(f"BTC:{st}", {})
    if not (o.get("ptb") and o.get("gagnant") and st + 300 in K): continue
    off_fin = o.get("final") or O.get(f"BTC:{st + 300}", {}).get("ptb")
    if not off_fin: continue
    eK = K[st] - o["ptb"]; eF = K[st + 300] - off_fin          # cloture affichee = prix a battre affiche du cycle suivant
    p0 = px(st)
    mom = {w: (p0 - px(st - w)) if p0 and px(st - w) else None for w in (5, 15, 30, 60)}
    D.append(dict(st=st, eK=eK, eF=eF, g=o["gagnant"], dAff=K[st + 300] - K[st], dOff=off_fin - o["ptb"], mom=mom))
eK = np.array([d["eK"] for d in D]); eF = np.array([d["eF"] for d in D])
q = lambda v, p: float(np.percentile(np.abs(v), p))
out += ["## 2. Taille de l'erreur", "", f"{len(D)} cycles avec valeurs officielles.", "",
        "| Erreur | Moyenne (biais) | Médiane absolue | 75 % | 90 % | 95 % | max |", "|---|---|---|---|---|---|---|",
        f"| début (prix à battre affiché − officiel) | {eK.mean():+.2f} $ | {q(eK,50):.1f} $ | {q(eK,75):.1f} $ | {q(eK,90):.1f} $ | {q(eK,95):.1f} $ | {q(eK,100):.1f} $ |",
        f"| fin (clôture affichée − officielle) | {eF.mean():+.2f} $ | {q(eF,50):.1f} $ | {q(eF,75):.1f} $ | {q(eF,90):.1f} $ | {q(eF,95):.1f} $ | {q(eF,100):.1f} $ |",
        f"| sur la différence fin − début (ce qui décide le gagnant) | {(eF - eK).mean():+.2f} $ | {q(eF-eK,50):.1f} $ | {q(eF-eK,75):.1f} $ | {q(eF-eK,90):.1f} $ | {q(eF-eK,95):.1f} $ | {q(eF-eK,100):.1f} $ |", "",
        f"Corrélation erreur de début / erreur de fin : **{np.corrcoef(eK, eF)[0, 1]:+.2f}** (les erreurs de bord se compensent si elle est proche de +1).", ""]
# 3. inversions
inv = [d for d in D if (d["dAff"] >= 0) != (d["g"] == "Up")]
out += ["## 3. Gagnant faux avec les chiffres affichés", "", f"**{len(inv)} cycles sur {len(D)}** ({100 * len(inv) / len(D):.1f} %).", "",
        "| Écart final affiché (|clôture − prix à battre|) | Cycles | Gagnant faux | % |", "|---|---|---|---|"]
for a, b in ((0, 5), (5, 10), (10, 20), (20, 30), (30, 50), (50, 1e9)):
    X = [d for d in D if a <= abs(d["dAff"]) < b]
    if X: out.append(f"| {a:.0f}-{b:.0f} $ | {len(X)} | {sum(1 for d in X if d in inv)} | {100 * sum(1 for d in X if d in inv) / len(X):.0f} % |".replace("-1000000000 $", " $ et plus"))
# 4. biais directionnel
out += ["", "## 4. L'erreur de début est-elle prévisible par le mouvement du BTC juste avant ?", "",
        "| Mouvement du BTC (perp) avant le début | Corrélation avec l'erreur de début | Pente ($ d'erreur par $ de mouvement) |", "|---|---|---|"]
for w in (5, 15, 30, 60):
    X = [(d["mom"][w], d["eK"]) for d in D if d["mom"][w] is not None]
    if len(X) > 20:
        a = np.array(X); cc = np.corrcoef(a[:, 0], a[:, 1])[0, 1]; sl = np.polyfit(a[:, 0], a[:, 1], 1)[0]
        out.append(f"| {w} s | {cc:+.2f} | {sl:+.2f} |")
# validation chronologique simple : pente apprise sur la 1re moitie, testee sur la 2e
X = [(d["mom"][15], d["eK"]) for d in D if d["mom"][15] is not None]
m = len(X) // 2; A = np.array(X[:m]); B = np.array(X[m:])
if len(A) > 20:
    co = np.polyfit(A[:, 0], A[:, 1], 1); pred = np.polyval(co, B[:, 0])
    out += ["", f"Test sur cycles futurs (appris sur la 1re moitié, testé sur la 2e, mouvement 15 s) : erreur absolue moyenne {np.mean(np.abs(B[:, 1])):.1f} $ sans correction → {np.mean(np.abs(B[:, 1] - pred)):.1f} $ avec correction."]
open("etude/bot5min/resultat_oracle.md", "w").write("\n".join(out)); print("\n".join(out))
