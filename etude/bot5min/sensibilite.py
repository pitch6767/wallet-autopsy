"""Sensibilite de l'incertitude fixe du modele (V2-F BTC, 09.10.2026) + remplissage limite au vrai carnet + memes cycles.
Rejeu complet de la regle V2-F pour chaque marge ; remplissage : 50 $ au meilleur vendeur, limite a la taille affichee a ce prix."""
import os, sys, json, gzip, glob, math, time, statistics as stt, collections
import numpy as np
sys.path.insert(0, "etude/bot5min")
from sauvetage import FEE
from edge_truth import stats, f0, hs, phi
OUT = "etude/bot5min/"

def preparer(T0):
    L = {}
    for f in sorted(glob.glob("bot95/donnees/*/rec_BTC.json.gz")):
        for k, doc in json.load(gzip.open(f, "rt")).items():
            for r in doc["lignes"]: L[r[0]] = r
    rows = sorted(L.values(), key=lambda r: r[0])
    C = collections.defaultdict(list)
    for r in rows:
        if None in (r[2], r[3], r[4], r[5], r[6]): continue
        C[r[1]].append(r)
    RES = {t["st"]: (t["gagne"] if t["cote"] == "Up" else not t["gagne"]) for t in T0}
    P1, CL1 = {}, {}
    for r in rows:
        s = int(r[0]); p = r[11] or r[12]
        if p: P1[s] = p
        if r[15]: CL1[s] = r[15]
    VC, BC = {}, {}
    def vol(s):
        if s not in VC:
            x = [P1[k] for k in range(s - 300, s + 1) if k in P1]
            VC[s] = (float(np.std(np.diff(np.log(x)))) or 1e-6) if len(x) >= 150 else None
        return VC[s]
    def base(s):
        if s not in BC:
            d = [P1[k] - CL1[k] for k in range(s - 120, s + 1) if k in P1 and k in CL1]
            BC[s] = float(np.median(d)) if d else None
        return BC[s]
    def modele(r, st, sd):
        K = r[16]; p = r[11] or r[12]; s = int(r[0])
        if not K or not p: return None
        sg, b = vol(s), base(s)
        if sg is None or b is None: return None
        S = p - b; end = st + 300; deb = end - 59
        if s >= deb:
            con = [CL1[k] for k in range(deb, s + 1) if k in CL1]; nr = max(1, end - s)
            E = (sum(con) + nr * S) / (len(con) + nr); v = (sg * S) ** 2 * nr ** 3 / 3 / 3600
        else: E = S; v = (sg * S) ** 2 * ((deb - s) + 20)
        return phi((E - K) / math.sqrt(v + (sd * S) ** 2))
    def rejouer(sd):
        out = []
        for st in sorted(C):
            g = RES.get(st)
            if g is None:
                a, b = CL1.get(st), CL1.get(st + 300) or CL1.get(st + 299)
                g = (b >= a) if a and b else None
            if g is None: continue
            R = C[st]; MC = {}
            mo = lambda k: MC.setdefault(k, R[k][2] if sd is None else modele(R[k], st, sd))
            for i, r in enumerate(R):
                tl = st + 300 - r[0]
                if tl < 5: break
                j = i
                while j > 0 and r[0] - R[j][0] < 3: j -= 1
                if r[0] - R[j][0] < 2.5: continue
                pu, p3 = mo(i), mo(j)
                if pu is None or p3 is None: continue
                h3 = R[j]; fait = False
                for up in (True, False):
                    ask = r[4] if up else r[6]; a3 = h3[4] if up else h3[6]
                    fair = pu if up else 1 - pu; f3 = p3 if up else 1 - p3
                    if ask is None or a3 is None or not (0.03 <= ask <= 0.97): continue
                    if fair - ask >= 0.20 and (fair - ask) - (f3 - a3) >= 0.03:
                        gm = g if up else (not g); taille = (r[8] if up else r[10]) or 0
                        parts = min(50 / ask, taille) if taille else 50 / ask
                        out.append({"t": r[0], "st": st, "prix": ask, "p": fair, "gagne": bool(gm), "pnl": (50 / ask) * ((1 if gm else 0) - ask - FEE(ask)),
                                    "pnl_c": parts * ((1 if gm else 0) - ask - FEE(ask)), "mise_c": parts * ask, "reste": round(tl)}); fait = True; break
                if fait: break
        return out
    return rejouer


def main():
    T0 = json.load(open(OUT + "v2f_tous.json"))
    rejouer = preparer(T0)
    V = [("bot enregistré 0,08 % (V2-F)", None), ("reconstruit 0,08 %", 8e-4), ("0,04 %", 4e-4), ("0,03 %", 3e-4), ("0,02 %", 2e-4), ("0,015 % (fantôme « corrigé » en direct)", 1.5e-4),
         ("0,0125 %", 1.25e-4), ("0,01 %", 1e-4), ("0,0075 %", 7.5e-5), ("0,005 %", 5e-5), ("0 % (aucune marge)", 1e-9)]
    R = {nom: rejouer(sd) for nom, sd in V}
    allT = sorted(t["t"] for t in R["reconstruit 0,08 %"]); QQ = [allT[int(len(allT) * k / 4)] for k in (1, 2, 3)]
    rap = ["# Sensibilité de la marge d'incertitude du modèle — V2-F BTC, rejeu complet sur les vrais carnets", "",
           "Pour chaque marge, toute la règle V2-F est rejouée. « Rempli au carnet » = 50 $ au meilleur vendeur mais au plus la quantité affichée à ce prix (pas de remontée dans le carnet) : c'est l'hypothèse prudente.", "",
           "| Marge | Trades | Gagnés | % gagnés | Prix moyen | Résultat (50 $ toujours remplis) | Résultat rempli au carnet | Mise moyenne remplie | Creux (rempli au carnet) | Pertes de suite max | Q1 | Q2 | Q3 | Q4 |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for nom, sd in V:
        X = sorted(R[nom], key=lambda t: t["t"]); s = stats(X)
        cum = pk = cr = 0.0
        for t in X: cum += t["pnl_c"]; pk = max(pk, cum); cr = min(cr, cum - pk)
        Q = [sum(t["pnl_c"] for t in X if sum(t["t"] >= x for x in QQ) == k) for k in range(4)]
        rap.append(f"| {nom} | {s['n']} | {s['g']} | {100 * s['g'] / max(1, s['n']):.0f} % | {stt.mean(t['prix'] for t in X):.2f} | {f0(s['pnl'])} | **{f0(sum(t['pnl_c'] for t in X))}** | "
                   f"{stt.mean(t['mise_c'] for t in X):.0f} $ | {f0(cr)} | {s['smax']} | " + " | ".join(f0(x) for x in Q) + " |")
    # memes cycles
    ref = {t["st"]: t for t in R["reconstruit 0,08 %"]}
    rap += ["", "## Mêmes cycles : d'où vient le gain ?", "", "Comparaison avec le moteur reconstruit à 0,08 % (même moteur de rejeu, seule la marge change). Résultats remplis au carnet.", "",
            "| Marge | Cycles communs | Résultat 0,08 % sur ces cycles | Résultat nouvelle marge sur ces cycles | Cycles abandonnés (que 0,08 % prenait) | Leur résultat à 0,08 % | Cycles nouveaux | Leur résultat |",
            "|---|---|---|---|---|---|---|---|"]
    for nom in ("0,02 %", "0,015 % (fantôme « corrigé » en direct)", "0,01 %"):
        X = {t["st"]: t for t in R[nom]}
        com = set(X) & set(ref); ab = set(ref) - set(X); nv = set(X) - set(ref)
        rap.append(f"| {nom} | {len(com)} | {f0(sum(ref[k]['pnl_c'] for k in com))} | {f0(sum(X[k]['pnl_c'] for k in com))} | {len(ab)} | {f0(sum(ref[k]['pnl_c'] for k in ab))} | {len(nv)} | {f0(sum(X[k]['pnl_c'] for k in nv))} |")
        # sur les cycles communs : meme cote ? plus tard ? prix ?
        same = [k for k in com if (X[k]["p"] >= 0.5) == (ref[k]["p"] >= 0.5) or True]
        dt = [X[k]["t"] - ref[k]["t"] for k in com]
        rap.append(f"| ↳ sur les cycles communs | | prix moyen {stt.mean(ref[k]['prix'] for k in com):.2f} | prix moyen {stt.mean(X[k]['prix'] for k in com):.2f} | achat en moyenne {stt.mean(dt):+.0f} s plus tard (médiane {stt.median(dt):+.0f} s) | | | |")
    open(OUT + "resultat_sensibilite.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
