"""BOT95 — H1056 : stratégies qui vivent seulement des renversements (Pitch, 13.10.2026 09:55 « Il faut aussi des stratégies qui vivent que
de renversement. Cherchons cela aussi »). PROTOCOLE PRÉ-ENREGISTRÉ avant le calcul de la validation et du test. Hors ligne ; aucun ordre ;
aucun fantôme ni stratégie modifié.

DONNÉES : cycles Dublin (carnet rejoué), exécution preneur à 164 ms, 10 $ par achat, prix limite = meilleur vendeur + 1 c, frais 0,07·p·(1−p).
PÉRIODES : apprentissage = 2/3 des cycles avant le 12.10 12:00 UTC (seule période explorée) ; validation = dernier tiers ; test = 12.10
  12:00–24:00 UTC ; confirmation (option --confirmation) = cycles à partir du 13.10 00:00 UTC, lancée une seule fois plus tard.
EXPLORATION (apprentissage seulement, déjà vue) :
  - billets ≤ 0,05 : gagnent ~0,7 % pour un prix de 1,3–3,5 % (biais du billet de loterie) ; 0,10–0,30 : à peu près au juste prix ;
  - variables Chainlink, Binance, perp, flux, carnet, vitesse : aucune séparation monotone ;
  - flux des portefeuilles (09–12.10, prix des transactions) : acheter l'outsider quand le favori passe 0,80 perd chaque jour
    (−415 à −910 $ / jour) ; avec l'alerte H1055, résultats +19 / −34 / −83 / +71 $ : rien d'exploitable, l'outsider est déjà plus cher ;
  - « rejoindre le renversement » (passé ≤ 0,20, remonte à 0,35) : 88 cas, ROI +13 % ;
  - outsider sous-évalué selon Binance (écart 0,05–0,20) : 121 cas, ROI +8,5 %.
RÈGLES FIGÉES (une entrée au plus par cycle et par côté) :
  T  témoin : premier instant où le côté X a un meilleur vendeur entre 0,03 et 0,30, avec 20 à 200 s restantes ;
  RA rejoindre le renversement : le milieu de X est passé ≤ 0,20 plus tôt dans le cycle, puis repasse au-dessus de 0,35, au moins 15 s restantes ;
  RB outsider sous-évalué : comme T, mais la probabilité projetée depuis Binance (base Binance − Chainlink des 60 s précédentes, même formule
     de moyenne 60 s que M0) dépasse le prix payé de 0,05 à 0,20.
CRITÈRE : ROI > 0 en validation ET sur le test, et IC 90 % par cycles de la somme des P&L, corrigé pour 2 règles, > 0 sur le test. Sinon abandon.
  Le résultat est rapporté par période, séparément. Aucune proposition de fantôme sans accord de Pitch.
Usage : python3 etude/bot5min/renversement_h1056.py dossier_cycles_dublin [--confirmation]"""
import os, sys, math, time
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
import liquidite_h833 as L, latence_h766 as LH, dpe_h841 as DP
import reversal_h1003 as RV
CONF = "--confirmation" in sys.argv
if CONF: L.RESERVE = 10 ** 12
SORTIE = os.path.join(ICI, "resultat_renversement_h1056" + ("_confirmation" if CONF else "") + ".md")
TEST0, TEST1 = 1791806400, 1791849600
fee = lambda p: 0.07 * p * (1 - p)
RNG = np.random.default_rng(1056)


def achat(Lc, X, lim, dollars=10.0):
    q = c = 0.0
    for px, sz in DP.vend(Lc, X):
        if px > lim: break
        if px <= 0: continue
        pp = px / 1000; u = pp + fee(pp); k = min(sz, (dollars - c) / u)
        if k <= 1e-9: break
        q += k; c += k * u
    return q, c


def main():
    t_go = time.time()
    G, cyc = L.grille(sys.argv[1]); P = L.preparer(G); L.P_sd1 = P["sd1"]; Y = L.resultats_officiels(cyc)

    def pbn(st, rest):
        i = st + 300 - rest - G["t0"]; cl = G["cl"]; K = cyc[st]["strike"]
        if K is None or not np.isfinite(cl[i]) or not np.isfinite(G["bn"][i]): return None
        b = G["bn"][i - 60:i - 4] - cl[i - 60:i - 4]; b = b[np.isfinite(b)]
        if len(b) < 20: return None
        x = G["bn"][i] - np.median(b)
        sig = P["sd1"][i] if np.isfinite(P["sd1"][i]) and P["sd1"][i] > 0 else None
        if sig is None: return None
        a = st + 240 - G["t0"]
        if i <= a: mu = x; sd = sig * math.sqrt(a - i + 20)
        else:
            obs = cl[a:i]; obs = obs[np.isfinite(obs)]; Lf = 60 - len(obs)
            mu = (obs.sum() + Lf * x) / 60.0; sd = sig * (Lf / 60.0) * math.sqrt(max(Lf, 1) / 3.0)
        return L.Phi((mu - K) / max(sd, 1e-6))

    cycles = sorted(s for s in cyc if s in Y)
    if CONF: cycles = [s for s in cycles if s >= TEST1]; part = lambda s: "confirmation"
    else:
        dev = [s for s in cycles if s < RV.DEV_FIN]; tr = set(dev[:len(dev) * 2 // 3]); va = set(dev[len(dev) * 2 // 3:])
        cycles = [s for s in cycles if s < TEST1]
        part = lambda s: "apprentissage" if s in tr else ("validation" if s in va else "test")
    R = {k: [] for k in ("T", "RA", "RB")}
    for st in cycles:
        T = [st * 1000 + s * 1000 for s in range(300)]
        try: E = {k: DP.compact(v) for k, v in LH.Cycle(cyc[st]["f"]).etats(T + [t + 164 for t in T]).items()}
        except Exception: continue
        mid = {"Up": [None] * 300, "Down": [None] * 300}
        for s in range(300):
            Lc = E.get(T[s])
            for X in mid:
                a, b = DP.meilleur(Lc, X, "a"), DP.meilleur(Lc, X, "b")
                mid[X][s] = (a + b) / 2000 if a and b and 0 < a - b <= 100 else (mid[X][s - 1] if s else None)
        for X in ("Up", "Down"):
            win = (Y[st] == 1.0) == (X == "Up"); fait = set(); bas = False
            for s in range(5, 286):
                a = DP.meilleur(E.get(T[s]), X, "a"); rest = 300 - s; m = mid[X][s]
                if m is not None and m <= 0.20: bas = True
                cand = []
                if "T" not in fait and a and 30 <= a <= 300 and 20 <= rest <= 200: cand.append("T")
                if "RB" not in fait and a and 30 <= a <= 300 and 20 <= rest <= 200: cand.append("RB")
                if "RA" not in fait and bas and m is not None and m >= 0.35 and mid[X][s - 1] is not None and mid[X][s - 1] < 0.35 and rest >= 15: cand.append("RA")
                for k in cand:
                    if not a: continue
                    q, c = achat(E.get(T[s] + 164), X, a + 10)
                    if q <= 0 or c < 5: continue
                    if k == "RB":
                        p = pbn(st, rest)
                        if p is None: continue
                        p = p if X == "Up" else 1 - p
                        if not (0.05 <= p - c / q < 0.20): continue
                    fait.add(k); R[k].append((part(st), st, c, q * win - c, int(win), c / q))
    parts = ["confirmation"] if CONF else ["apprentissage", "validation", "test"]
    o = [f"# Bot95 — H1056 : stratégies de renversement{' — CONFIRMATION (≥ 13.10)' if CONF else ''}\n",
         f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. 10 $ par achat, preneur 164 ms. Aucun ordre.\n",
         "| Règle | Période | Cycles | Achats | Gagnants | Prix moyen payé | Taux de gain | P&L ($) | ROI | IC 90 % (corrigé, 2 règles) |", "|---|---|---|---|---|---|---|---|---|---|"]
    verdict = {}
    for k in ("T", "RA", "RB"):
        for pa in parts:
            x = [r for r in R[k] if r[0] == pa]; ncy = len({st for _, st, *_ in [(r[0], r[1]) for r in R[k] if r[0] == pa]})
            allcy = sorted({r[1] for r in x}); g = {}
            for r in x: g[r[1]] = g.get(r[1], 0) + r[3]
            v = np.array(list(g.values())) if g else np.zeros(1)
            nc = len([s for s in cycles if part(s) == pa]); vv = np.concatenate([v, np.zeros(max(nc - len(v), 0))])
            bs = vv[RNG.integers(0, len(vv), (4000, len(vv)))].sum(1)
            lo, hi = np.percentile(bs, [2.5, 97.5])
            pnl = sum(r[3] for r in x); cost = sum(r[2] for r in x) or 1
            o.append(f"| {k} | {pa} | {nc} | {len(x)} | {sum(r[4] for r in x)} | {np.mean([r[5] for r in x]) if x else 0:.3f} | "
                     f"{100 * np.mean([r[4] for r in x]) if x else 0:.0f} % | {pnl:+.0f} | {100 * pnl / cost:+.0f} % | [{lo:+.0f} ; {hi:+.0f}] |")
            verdict[(k, pa)] = (pnl, lo)
    if not CONF:
        o.append("\n**Verdict (critère figé)**\n")
        for k in ("RA", "RB"):
            ok = verdict[(k, "validation")][0] > 0 and verdict[(k, "test")][0] > 0 and verdict[(k, "test")][1] > 0
            o.append(f"- {k} : {'candidat (proposition à Pitch, confirmation ≥ 13.10)' if ok else 'abandon'}")
    o.append(f"\n_Calcul : {time.time() - t_go:.0f} s._\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
