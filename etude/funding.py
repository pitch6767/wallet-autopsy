"""Etude n°3 : arbitrage de financement Hyperliquid (30 jours, lecture seule).

Strategie testee, sans regarder le futur :
  - toutes les heures, on regarde la moyenne du financement des 8 dernieres heures ;
  - si elle depasse le seuil d'entree, on vend le perpetuel Hyperliquid et on achete
    la meme quantite au comptant ailleurs (couverture) ;
  - on encaisse le financement horaire tant que la moyenne 8 h reste au-dessus du seuil de sortie ;
  - frais : perp Hyperliquid 0,045 % x2 + comptant 0,10 % x2 (+ 0,10 % de glissement) par aller-retour.
"""
import json, time, urllib.request, statistics
from concurrent.futures import ThreadPoolExecutor

HL = "https://api.hyperliquid.xyz/info"
NOW = int(time.time() * 1000)
JOURS = 30
DEBUT = NOW - JOURS * 86400 * 1000
FRAIS = 2 * 0.00045 + 2 * 0.0010 + 0.0010   # 0,39 % par aller-retour


def post(body, tries=8):
    for k in range(tries):
        try:
            req = urllib.request.Request(HL, data=json.dumps(body).encode(),
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read())
        except Exception as e:
            err = e
            time.sleep(15 if "429" in str(e) else 3)
    raise err


def historique(coin):
    out, t = [], DEBUT
    for _ in range(10):
        lot = post({"type": "fundingHistory", "coin": coin, "startTime": t})
        if not lot:
            break
        out += lot
        dernier = lot[-1]["time"]
        if dernier <= t or len(lot) < 400:
            break
        t = dernier + 1
        time.sleep(1.2)
    vu, propre = set(), []
    for x in out:
        if x["time"] not in vu:
            vu.add(x["time"]); propre.append((x["time"], float(x["fundingRate"])))
    return sorted(propre)


def simuler(h, entree, sortie):
    """Renvoie (gain en % du notionnel sur la periode, nb d'episodes, heures en position)."""
    gain, ep, heures, pos = 0.0, 0, 0, False
    for i in range(8, len(h)):
        moy = sum(r for _, r in h[i - 8:i]) / 8 * 24 * 365   # annualise, connu a l'heure i
        if not pos and moy > entree:
            pos, ep = True, ep + 1
            gain -= FRAIS
        elif pos and moy < sortie:
            pos = False
        if pos:
            gain += h[i][1]      # financement encaisse par le vendeur du perp
            heures += 1
    return gain, ep, heures


def main():
    meta, ctx = post({"type": "metaAndAssetCtxs"})
    lignes = []
    for a, c in zip(meta["universe"], ctx):
        if a.get("isDelisted"):
            continue
        lignes.append({"coin": a["name"], "oi_usd": float(c.get("openInterest") or 0) * float(c.get("markPx") or 0),
                       "vol24h": float(c.get("dayNtlVlm") or 0), "fund_now": float(c.get("funding") or 0) * 24 * 365})
    print("perpetuels actifs :", len(lignes))
    lignes = [l for l in lignes if l["vol24h"] > 300000]
    print("perpetuels avec > 0,3 M$ de volume/jour :", len(lignes))
    H = {}
    for l in lignes:
        try:
            H[l["coin"]] = historique(l["coin"])
        except Exception as e:
            print("  echec", l["coin"], str(e)[:60])
        time.sleep(1.2)
    regles = [(0.30, 0.10), (0.50, 0.20), (1.00, 0.30), (2.00, 0.50)]
    print("frais par aller-retour : %.2f %%" % (FRAIS * 100))
    print("\n=== Resultat global par regle (30 jours, notionnel egal sur chaque episode) ===")
    meilleure = None
    for e, s in regles:
        res = []
        for l in lignes:
            h = H.get(l["coin"]) or []
            if len(h) < 100:
                continue
            g, ep, hr = simuler(h, e, s)
            if ep:
                res.append((l["coin"], g, ep, hr, l["vol24h"], l["oi_usd"]))
        if not res:
            continue
        gagnants = [r for r in res if r[1] > 0]
        tot_h = sum(r[3] for r in res)
        rend_annuel = (sum(r[1] for r in res) / max(tot_h, 1)) * 24 * 365 * 100
        print("entree > %3.0f %%/an, sortie < %3.0f %% : %3d cryptos tradees, %3d gagnantes, %4d episodes, "
              "rendement annualise du capital EN POSITION : %6.1f %%" % (
                  e * 100, s * 100, len(res), len(gagnants), sum(r[2] for r in res), rend_annuel))
        if meilleure is None or rend_annuel > meilleure[0]:
            meilleure = (rend_annuel, e, s, res)
    _, e, s, res = meilleure
    print("\n=== Detail de la meilleure regle (entree %.0f %%, sortie %.0f %%) - 25 premieres ===" % (e * 100, s * 100))
    print("crypto | gain 30j %% notionnel | episodes | heures | volume 24h M$ | OI M$")
    for r in sorted(res, key=lambda r: -r[1])[:25]:
        print("%-10s | %7.2f | %3d | %4d | %8.2f | %7.2f" % (r[0], r[1] * 100, r[2], r[3], r[4] / 1e6, r[5] / 1e6))
    print("\n=== Les 10 pires ===")
    for r in sorted(res, key=lambda r: r[1])[:10]:
        print("%-10s | %7.2f | %3d | %4d | %8.2f | %7.2f" % (r[0], r[1] * 100, r[2], r[3], r[4] / 1e6, r[5] / 1e6))
    # profil des taux
    tous = [r for h in H.values() for _, r in h]
    an = [r * 24 * 365 for r in tous]
    print("\n=== Profil des taux horaires (annualises), toutes cryptos ===")
    print("observations :", len(an))
    for q in (0.5, 0.75, 0.9, 0.95, 0.99):
        print("  centile %2d : %7.1f %%" % (q * 100, sorted(an)[int(q * len(an)) - 1] * 100))
    print("  part des heures > 50 %%/an : %.1f %%" % (100 * sum(1 for x in an if x > 0.5) / len(an)))
    print("  part des heures negatives : %.1f %%" % (100 * sum(1 for x in an if x < 0) / len(an)))
    # capacite : cryptos liquides
    liq = [l for l in lignes if l["vol24h"] > 5e6]
    print("\ncryptos avec > 5 M$ de volume/jour :", len(liq))
    print("taux actuels les plus eleves (annualises) :")
    for l in sorted(lignes, key=lambda l: -l["fund_now"])[:10]:
        print("  %-10s %7.1f %%  vol24h %6.2f M$  OI %6.2f M$" % (l["coin"], l["fund_now"] * 100, l["vol24h"] / 1e6, l["oi_usd"] / 1e6))


if __name__ == "__main__":
    main()
