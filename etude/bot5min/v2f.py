"""V2-F « ecart qui grandit » (BTC) — toutes les trades, 09.10.2026.
1. Trades reels du fantome gardes par le bot (les 60 derniers + archive) via /api/hist.
2. Rejeu complet sur les vrais carnets (48 h) avec la meme regle : ecart (modele - meilleur vendeur) >= 0,20 ET ecart plus grand d'au moins 3 pts
   qu'il y a 3 s, au moins 5 s restantes, 1 achat par cycle, 50 $ (limite a la taille du vendeur), garde jusqu'au resultat.
Sortie : v2f.json
"""
import sys, json, urllib.parse
sys.path.insert(0, "etude/bot5min")
from sauvetage import resultat, RES, FEE, get, U
from proche import charger_brut

OUT = "etude/bot5min/"


def main():
    nom = "V2-F ecart qui grandit BTC"
    live = {}
    for k in range(5):
        try: live = get(f"{U}/api/hist?s=" + urllib.parse.quote(nom)); break
        except Exception as e: print("hist", e); import time; time.sleep(20)
    C = charger_brut("BTC"); sts = sorted(C)
    for st in sts: resultat("BTC", st)
    T = []
    for st in sts:
        R = C[st]; g = RES.get(("BTC", st))
        if g is None: continue
        for i, r in enumerate(R):
            tl = st + 300 - r[0]
            if tl < 5: break
            j = i
            while j > 0 and r[0] - R[j][0] < 3: j -= 1
            h3 = R[j] if r[0] - R[j][0] >= 2.5 else None
            if h3 is None: continue
            fait = False
            for up in (True, False):
                ask = r[4] if up else r[6]; fair = r[2] if up else 1 - r[2]
                a3 = h3[4] if up else h3[6]; f3 = h3[2] if up else 1 - h3[2]
                if ask is None or a3 is None or not (0.03 <= ask <= 0.97): continue
                e, e3 = fair - ask, f3 - a3
                if e >= 0.20 and e - e3 >= 0.03:
                    taille = (r[8] if up else r[10]) or 0
                    parts = min(50 / ask, taille) if taille else 50 / ask
                    if parts < 1: continue
                    gm = g if up else (not g)
                    T.append({"t": r[0], "st": st, "cote": "Up" if up else "Down", "prix": ask, "modele": round(fair, 3), "ecart": round(e, 3), "ecart3": round(e3, 3),
                              "reste": round(tl), "parts": round(parts, 1), "gagne": bool(gm), "pnl": round(parts * ((1 if gm else 0) - ask - FEE(ask)), 2)})
                    fait = True; break
            if fait: break
    json.dump({"live": live, "rejeu": T, "periode": [sts[0], sts[-1] + 300]}, open(OUT + "v2f.json", "w"), ensure_ascii=False)
    print(len(T), sum(t["pnl"] for t in T), live.get("resume"))


if __name__ == "__main__":
    main()
