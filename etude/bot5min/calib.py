"""Audit du modele (09.10.2026) : la formule du bot ajoute une incertitude fixe SD_ECART_REL = 0,08 % du prix (~66 $ sur BTC) et suppose
un reglement sur la moyenne des 60 dernieres secondes, alors que la regle officielle compare le prix Chainlink de fin a celui du debut.
On recalcule la probabilite Up avec la MEME formule que le bot pour plusieurs valeurs d'incertitude, en version moyenne 60 s et en version prix de fin,
sur tous les cycles enregistres, et on mesure la precision (Brier, log-loss) contre le resultat officiel, comparee au prix Polymarket.
"""
import sys, math, statistics, time, json, glob, gzip
sys.path.insert(0, "etude/bot5min")
from sauvetage import resultat, RES

OUT = "etude/bot5min/"
phi = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))


def charger():
    rows = []
    for f in sorted(glob.glob("bot95/donnees/*/rec_BTC.json.gz")):
        for k, doc in json.load(gzip.open(f, "rt")).items(): rows += doc["lignes"]
    rows.sort(key=lambda r: r[0]); C = {}
    for r in rows: C.setdefault(r[1], []).append(r)
    return C


def main():
    C = charger(); sts = sorted(C)
    for st in sts: resultat("BTC", st)
    # serie seconde par seconde du perp et de Chainlink (toutes cycles confondus)
    sec = {}
    for st in sts:
        for r in C[st]:
            s = int(r[0])
            if r[11]: sec.setdefault(s, [None, None])[0] = r[11]
            if r[15]: sec.setdefault(s, [None, None])[1] = r[15]
    SD = [0.0, 1e-4, 2e-4, 4e-4, 8e-4]
    res = {(m, sd): [] for m in ("moyenne 60 s (bot)", "prix de fin (regle officielle)") for sd in SD}
    poly, bot = [], []
    for st in sts:
        g = RES.get(("BTC", st))
        if g is None: continue
        y = 1 if g else 0; end = st + 300; deb = end - 59
        for tl in (270, 240, 210, 180, 150, 120, 90, 60, 45, 30, 15):
            ts = end - tl
            r = min(C[st], key=lambda x: abs(x[0] - ts))
            if abs(r[0] - ts) > 2 or None in (r[2], r[3], r[4], r[16]): continue
            K = r[16]
            perp = [sec[s][0] for s in range(ts - 300, ts + 1) if s in sec and sec[s][0]]
            if len(perp) < 60: continue
            lr = [math.log(perp[i] / perp[i - 1]) for i in range(1, len(perp))]
            mo = sum(lr) / len(lr); sg = math.sqrt(sum((x - mo) ** 2 for x in lr) / len(lr)) or 1e-6
            bs = [sec[s][0] - sec[s][1] for s in range(ts - 120, ts + 1) if s in sec and sec[s][0] and sec[s][1]]
            if not bs: continue
            S = sec.get(ts, [r[11], None])[0] or r[11]
            if not S: continue
            S = S - statistics.median(bs)
            for sd in SD:
                # version du bot : moyenne des 60 dernieres secondes
                if ts >= deb:
                    connus = [sec[s][1] for s in range(deb, ts + 1) if s in sec and sec[s][1]]; nr = max(1, end - ts)
                    E = (sum(connus) + nr * S) / (len(connus) + nr); v = (sg * S) ** 2 * nr ** 3 / 3 / 3600
                else:
                    E = S; v = (sg * S) ** 2 * ((deb - ts) + 20)
                res[("moyenne 60 s (bot)", sd)].append((phi((E - K) / math.sqrt(v + (sd * S) ** 2)), y, tl))
                # version regle officielle : prix de fin
                v2 = (sg * S) ** 2 * max(1, end - ts)
                res[("prix de fin (regle officielle)", sd)].append((phi((S - K) / math.sqrt(v2 + (sd * S) ** 2)), y, tl))
            poly.append(((r[3] + r[4]) / 2, y, tl)); bot.append((r[2], y, tl))
    def met(L):
        b = statistics.mean((p - y) ** 2 for p, y, _ in L)
        ll = -statistics.mean(y * math.log(min(max(p, 1e-4), 1 - 1e-4)) + (1 - y) * math.log(1 - min(max(p, 1e-4), 1 - 1e-4)) for p, y, _ in L)
        return b, ll
    rap = [f"# Audit de la formule du modele — {len(poly)} points (cycles BTC enregistres, 11 instants par cycle)", "",
           "Brier et log-loss : plus bas = meilleur. Reference : le prix Polymarket (milieu) au meme instant.", "",
           "| Probabilite | Brier | Log-loss |", "|---|---|---|"]
    for nom, L in (("prix Polymarket (milieu)", poly), ("probabilite enregistree du bot", bot)):
        b, ll = met(L); rap.append(f"| **{nom}** | {b:.4f} | {ll:.4f} |")
    for (m, sd), L in res.items():
        b, ll = met(L); rap.append(f"| {m}, incertitude {sd * 100:.2f} % ({sd * 83000:.0f} $) | {b:.4f} | {ll:.4f} |")
    # calibration des « outsiders » : quand la formule dit 25-50 % pour un cote
    rap += ["", "## Calibration quand la formule donne 25-50 % a un cote (la zone ou nos desaccords naissent)", "",
            "| Probabilite | Points | Dit en moyenne | Arrive en vrai |", "|---|---|---|---|"]
    def outs(L):
        X = []
        for p, y, _ in L:
            if 0.25 <= p <= 0.5: X.append((p, y))
            elif 0.5 <= p <= 0.75: X.append((1 - p, 1 - y))
        return X
    for nom, L in [("probabilite enregistree du bot", bot), ("prix Polymarket (milieu)", poly)] + [(f"{m}, {sd * 100:.2f} %", L) for (m, sd), L in res.items() if sd in (8e-4, 1e-4, 0.0)]:
        X = outs(L)
        if X: rap.append(f"| {nom} | {len(X)} | {statistics.mean(p for p, _ in X):.2f} | **{statistics.mean(y for _, y in X):.2f}** |")
    open(OUT + "resultat_calib.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
