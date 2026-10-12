"""BOT95 — H986 à H993, première priorité (Pitch, 12.10.2026 15:59) : H993 flux forcé contre flux volontaire, H990 cascade de liquidations,
H988/H989 sur les données déjà enregistrées. PROTOCOLE PRÉ-ENREGISTRÉ (ce fichier tel que committé avant tout calcul). Hors ligne ; aucun ordre ;
aucun bot, H816, H821, R4 ni fantôme modifié ; période réservée (≥ 13.10.2026) jamais lue.

DONNÉES (Dublin, heures de réception) : liquidations Bybit BTCUSDT (flux public allLiquidation, agrégé par 100 ms, en $, côté de l'ordre forcé :
  « ventes forcées » = positions longues liquidées, « achats forcés » = courtes liquidées), transactions agressives Binance spot et Bybit perp,
  carnets, Chainlink, carnet Polymarket, résultat officiel. Open interest Binance toutes les 5 minutes (contexte). Mark price, index price, open interest
  Bybit à haute fréquence : NON enregistrés (H988 et H989 non testables finement ; déclaré).
ÉCHANTILLONS : apprentissage / validation / test (12.10 06:00–12:00 UTC) / nouveau (≥ 12.10 12:00 UTC), comme H977.
H993 : vague = z(pression nette 5 s) ≥ 1,5 (définition H933/H941), au plus une par 5 s et par sens. Vague « contrainte » si des liquidations Bybit du
  même sens (ventes forcées pour une vague vendeuse, achats forcés pour une vague acheteuse) totalisent ≥ 10 000 $ dans les 5 s qui précèdent
  (jusqu'à t compris) ; sinon « volontaire ». Appariement : pour chaque vague contrainte, les vagues volontaires du même échantillon avec |pression|
  à ± 30 %, même tiers de volatilité 60 s et même tranche de temps restant (30–120 / 120–200 / 200–280 s) ; écart = contrainte − moyenne appariée.
  Mesures : continuation BTC signée à 5/15/30/60/120 s ; résultat officiel − M0 (signé) ; achat de 20 $ du jeton dans le sens à 164 ms au prix vu
  (frais compris), conservé ; réévaluation Polymarket (+1 c en 5 s). IC 90 % par cycles.
H990 : salve de liquidations = ≥ 50 000 $ de liquidations d'un même côté en 5 s (au plus une par 10 s). Probabilité d'une nouvelle salve du même
  côté dans 1/3/5/10/30 s après la fin de la fenêtre, comparée à des instants témoins appariés (même |variation du prix sur 5 s| à ± 30 %, sans salve)
  ; continuation du prix à 5/30/60 s ; amplitude.
H988 (partiel) : sans mark/index Bybit, seul l'écart perp Bybit − spot Binance (base) est testé : base extrême (|z| ≥ 2 sur 600 s) avant les salves de
  liquidations ? Fréquence des salves dans les 30 s qui suivent une base extrême, contre le taux de base.
H992 : appliqué à toute piste dont la continuation contrainte − volontaire a un IC > 0 sur la validation ET le test.
Usage : python3 etude/bot5min/liq_h993.py dossier_cycles_dublin"""
import os, sys, math, time, json, gzip, collections
import numpy as np, pandas as pd

ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
import latence_h766 as LH, liquidite_h833 as L, dpe_h841 as DP, pression_h971 as PR
RESERVE = 1791849600; TEST_DEB = 1791784800; NOUV_DEB = 1791806400; MISE = 20.0; RNG = np.random.default_rng(993)
SORTIE = os.path.join(ICI, "resultat_liq_h993.md"); fee = lambda p: 0.07 * p * (1 - p)


def cell(v, g):
    v = np.asarray(v, float); g = np.asarray(g); m = np.isfinite(v)
    if m.sum() < 5: return f"— (n={int(m.sum())})"
    c = L.ic_g(g[m], v[m]); return f"{v[m].mean():+.2f} [{c[0]:+.2f} ; {c[1]:+.2f}] (n={int(m.sum())})"


def main():
    t_go = time.time(); o = []; w = o.append
    G, cyc = L.grille(sys.argv[1]); P = L.preparer(G); L.P_sd1 = P["sd1"]; Y = L.resultats_officiels(cyc); V = PR.grandeurs(G, P)
    cycles = sorted(s for s in cyc if s < RESERVE); avant = [s for s in cycles if s < TEST_DEB]; n_tr = len(avant) * 2 // 3
    part = {s: ("apprentissage" if k < n_tr else "validation") for k, s in enumerate(avant)}
    part.update({s: ("test" if s < NOUV_DEB else "nouveau") for s in cycles if s >= TEST_DEB})
    PARTS = ["apprentissage", "validation", "test", "nouveau"]; nb = collections.Counter(part.values())
    stof = lambda i: (G["t0"] + i) - (G["t0"] + i) % 300; bn = G["bn"]
    # liquidations par seconde
    lv = np.zeros(G["n"]); la = np.zeros(G["n"])
    for st in cycles:
        try: R = json.load(gzip.open(cyc[st]["f"]))
        except Exception: continue
        for r in R.get("fx", []):
            x = r[1].get("liq_bybit")
            if not x: continue
            i = int(math.ceil(r[0] / 1000)) - G["t0"]
            if 0 <= i < G["n"]: la[i] += x[0]; lv[i] += x[1]
    cs = lambda x: np.concatenate([[0], np.cumsum(x)]); CLa, CLv = cs(la), cs(lv)
    win = lambda C, i, k: C[i + 1] - C[max(i + 1 - k, 0)]
    w("# Bot95 — H986 à H993 (première priorité) : flux forcé contre flux volontaire, cascades de liquidations, base perp/spot\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. Cycles Dublin : " + ", ".join(f"{k} {nb[k]}" for k in PARTS) + ". Aucun ordre ; période réservée non lue.\n")
    w("## 0. Audit des données Dublin pour cette série\n")
    w("| Donnée | Enregistrée ? | Depuis | Remarque |\n|---|---|---|---|\n"
      f"| Liquidations Bybit BTCUSDT (agrégées, ~500 ms) | oui | 11.10 | {int((la > 0).sum() + (lv > 0).sum())} secondes avec liquidation ; {lv.sum() / 1e6:.1f} M$ de ventes forcées, {la.sum() / 1e6:.1f} M$ d'achats forcés |\n"
      "| Transactions agressives Binance spot / Bybit perp | oui | 11.10 | |\n| Carnets Binance / Bybit (50 $) | oui | 11.10 | |\n"
      "| Mark price, index price, open interest, funding Bybit (ticker 100 ms) | **non** | — | à enregistrer (gratuit) pour H988/H989 |\n"
      "| Mark price, liquidations, transactions Binance perp | **non** | — | à enregistrer (gratuit) |\n"
      "| Open interest Binance | 5 min seulement (archive) | 12.09 | trop grossier pour 5–120 s |\n"
      "| Deribit : indice, perpétuel (avec OI), DVOL, transactions d'options, OI par prix d'exercice | indice/perp/DVOL depuis 12.10 11:55 ; OI par strike et transactions d'options depuis le déploiement de 14:03 UTC | — | trop récent |\n"
      "| Coinbase L2, ETH / SOL | depuis le déploiement de 14:03 UTC | — | trop récent |\n"
      "| IBIT (OPRA), CME, ETF | **non** | — | payant (non acheté) |\n")

    # ---------- vagues H993
    vol60 = pd.Series(P["sd1"]).values
    vag = []; last = {1: -99, -1: -99}
    for i in range(700, G["n"] - 121):
        st = stof(i)
        if st not in part or not (G["ok"][i] and G["ok"][i + 120]) or not np.isfinite(V["zPn5"][i]) or not np.isfinite(bn[i + 120]): continue
        z = V["zPn5"][i]
        if abs(z) < 1.5: continue
        s = 1 if z > 0 else -1
        if i - last[s] < 5: continue
        last[s] = i
        liq = win(CLa, i, 5) if s > 0 else win(CLv, i, 5)
        rest = st + 300 - (G["t0"] + i)
        vag.append(dict(i=i, st=st, s=s, part=part[st], pn=abs(V["Pn5"][i]), vol=vol60[i], rest=rest, force=liq >= 10000, liq=liq,
                        y={h: (bn[i + h] - bn[i]) * s for h in (5, 15, 30, 60, 120)}))
    for pt in PARTS:
        Z = [v for v in vag if v["part"] == pt]
        if not Z: continue
        q = np.nanpercentile([v["vol"] for v in Z], [33.3, 66.7])
        for v in Z: v["vt"] = int(np.searchsorted(q, v["vol"])); v["rt"] = 0 if v["rest"] < 120 else (1 if v["rest"] < 200 else 2)
    def m0s(v):
        if not (30 <= v["rest"] <= 280) or v["st"] not in Y: return np.nan
        m = L.m0(G, cyc, v["st"], v["rest"]); return ((Y[v["st"]] - m[0]) * v["s"]) if m else np.nan
    w("\n## 1. H993 — Flux contraint (liquidations du même sens) contre flux volontaire, appariés\n")
    w("Écart de continuation BTC (contraint − moyenne des volontaires appariés), en $, signé dans le sens de la vague ; et effet sur le règlement officiel.\n")
    w("| Échantillon | Vagues contraintes appariées | 5 s | 15 s | 30 s | 60 s | 120 s | Règlement : contraint − volontaire (résultat − M0) |\n|---|---|---|---|---|---|---|---|")
    appar = {}
    for pt in PARTS:
        F = [v for v in vag if v["part"] == pt and v["force"]]; Vo = [v for v in vag if v["part"] == pt and not v["force"]]
        rows = []
        for f in F:
            M = [v for v in Vo if abs(v["pn"] - f["pn"]) <= 0.3 * f["pn"] and v["vt"] == f["vt"] and v["rt"] == f["rt"]]
            if len(M) < 3: continue
            d = {h: f["y"][h] - np.mean([m["y"][h] for m in M]) for h in (5, 15, 30, 60, 120)}
            ms = [m0s(m) for m in M]; fr = m0s(f)
            d["r"] = fr - np.nanmean(ms) if (np.isfinite(fr) and np.isfinite(ms).any()) else np.nan
            rows.append((f, d))
        appar[pt] = rows
        if not rows: w(f"| {pt} | 0 | — | — | — | — | — | — |"); continue
        g = [f["st"] for f, _ in rows]
        w(f"| {pt} | {len(rows)} | " + " | ".join(cell([d[h] for _, d in rows], g) for h in (5, 15, 30, 60, 120)) + f" | {cell([d['r'] for _, d in rows], g)} |")
    w("\nContinuation brute (non appariée), même définition :\n")
    w("| Échantillon | Type | Vagues | 30 s | 120 s | Résultat − M0 |\n|---|---|---|---|---|---|")
    for pt in PARTS:
        for ty, f_ in (("contrainte", True), ("volontaire", False)):
            Z = [v for v in vag if v["part"] == pt and v["force"] == f_]
            if not Z: continue
            g = [v["st"] for v in Z]
            w(f"| {pt} | {ty} | {len(Z)} | {cell([v['y'][30] for v in Z], g)} | {cell([v['y'][120] for v in Z], g)} | {cell([m0s(v) for v in Z], g)} |")
    # H992 sur les vagues contraintes : prix Polymarket exécutable
    w("\n**H992 — Achat de 20 $ du jeton dans le sens de la vague contrainte, à 164 ms au prix vu, conservé (frais compris)**\n")
    w("| Échantillon | Achats | Victoire | Prix payé moyen | Avantage par achat (résultat − prix − frais) | P&L ($) | IC 90 % |\n|---|---|---|---|---|---|---|")
    for pt in PARTS:
        Z = [v for v in vag if v["part"] == pt and v["force"] and v["rest"] >= 35 and v["st"] in Y]
        res = []
        for v in Z:
            cy = LH.Cycle(cyc[v["st"]]["f"]); t = (G["t0"] + v["i"]) * 1000; E = {k: DP.compact(x) for k, x in cy.etats([t, t + 164]).items()}
            X = "Up" if v["s"] > 0 else "Down"; vv = DP.vend(E[t], X)
            if not vv: continue
            q = cc = 0.0
            for px, sz in DP.vend(E[t + 164], X):
                if px > vv[0][0]: break
                if px <= 0 or px >= 1000: continue
                pp = px / 1000; u = pp + fee(pp); k = min(sz, (MISE - cc) / u)
                if k <= 1e-9: break
                q += k; cc += k * u
            if q > 0:
                yX = Y[v["st"]] if X == "Up" else 1 - Y[v["st"]]; res.append((v["st"], yX, cc / q, q * yX - cc))
        if not res: w(f"| {pt} | 0 | — | — | — | — | — |"); continue
        g = np.array([r_[0] for r_ in res]); pn = np.array([r_[3] for r_ in res]); ci = L.ic_tot(g, pn) if len(res) >= 3 else (np.nan, np.nan)
        w(f"| {pt} | {len(res)} | {100 * np.mean([r_[1] for r_ in res]):.0f} % | {np.mean([r_[2] for r_ in res]):.2f} | {cell([r_[1] - r_[2] for r_ in res], g)} | {pn.sum():+.0f} | [{ci[0]:+.0f} ; {ci[1]:+.0f}] |")

    # ---------- H990 cascades
    w("\n## 2. H990 — Une salve de liquidations en déclenche-t-elle une autre ?\n")
    sal = []; lastS = {1: -99, -1: -99}
    for i in range(700, G["n"] - 61):
        st = stof(i)
        if st not in part or not G["ok"][i]: continue
        for s, C in ((1, CLa), (-1, CLv)):
            if win(C, i, 5) >= 50000 and i - lastS[s] >= 10: lastS[s] = i; sal.append(dict(i=i, st=st, s=s, part=part[st], amp=win(C, i, 5)))
    nb_s = len(sal)
    w(f"{nb_s} salves (≥ 50 000 $ du même côté en 5 s). Témoins : instants sans salve, |variation du prix sur 5 s| à ± 30 % de celle de la salve, même échantillon.\n")
    w("| Échantillon | Salves | Nouvelle salve du même côté dans 1 / 3 / 5 / 10 / 30 s | Témoins : même probabilité | Prix à 5 / 30 / 60 s (sens de la vente ou de l'achat forcé) |\n|---|---|---|---|---|")
    d5 = P["d5"]
    for pt in PARTS:
        Z = [s_ for s_ in sal if s_["part"] == pt]
        if not Z: continue
        def nouvelle(i, s, k):
            C = CLa if s > 0 else CLv; return float((C[min(i + 1 + k, G["n"])] - C[i + 1]) >= 50000)
        pr = " / ".join(f"{100 * np.mean([nouvelle(z['i'], z['s'], k) for z in Z]):.0f} %" for k in (1, 3, 5, 10, 30))
        cand = np.array([i for i in range(700, G["n"] - 61, 7) if part.get(stof(i)) == pt and win(CLa, i, 5) + win(CLv, i, 5) < 1000 and np.isfinite(d5[i])])
        tem = []
        for z in Z:
            a = abs(d5[z["i"]]) if np.isfinite(d5[z["i"]]) else 0
            mm = cand[np.abs(np.abs(d5[cand]) - a) <= 0.3 * max(a, 1)]
            if len(mm): tem.append(RNG.choice(mm, min(5, len(mm)), replace=False))
        tem = np.concatenate(tem) if tem else np.array([], int)
        prt = " / ".join(f"{100 * np.mean([max(nouvelle(i, 1, k), nouvelle(i, -1, k)) for i in tem]):.0f} %" if len(tem) else "—" for k in (1, 3, 5, 10, 30))
        g = [z["st"] for z in Z]; sg = lambda z: -1 if z["s"] < 0 else 1   # ventes forcées → baisse attendue
        mv = " / ".join(cell([(bn[min(z['i'] + h, G['n'] - 1)] - bn[z['i']]) * sg(z) for z in Z], g) for h in (5, 30, 60))
        w(f"| {pt} | {len(Z)} | {pr} | {prt} | {mv} |")

    # ---------- H988 partiel : base perp/spot
    w("\n## 3. H988 (partiel) — Une base perp/spot extrême précède-t-elle les liquidations ?\n")
    base = G["perp"] - bn; zb = pd.Series(base); zb = ((zb - zb.rolling(600, min_periods=200).mean().shift(1)) / zb.rolling(600, min_periods=200).std().shift(1)).values
    w("| Échantillon | Instants (base |z| ≥ 2) | Salve dans les 30 s après | Taux de base (tous instants) |\n|---|---|---|---|")
    for pt in PARTS:
        I = np.array([i for i in range(700, G["n"] - 31, 3) if part.get(stof(i)) == pt and G["ok"][i] and np.isfinite(zb[i])])
        if not len(I): continue
        s30 = np.array([(CLa[i + 31] - CLa[i + 1]) >= 50000 or (CLv[i + 31] - CLv[i + 1]) >= 50000 for i in I], float)
        ext = np.abs(zb[I]) >= 2
        w(f"| {pt} | {int(ext.sum())} | {100 * s30[ext].mean() if ext.any() else float('nan'):.1f} % | {100 * s30.mean():.1f} % |")
    w("\n## 4. Non testables aujourd'hui (données absentes)\n- **H986** options IBIT (OPRA payant), **H991** IBIT/CME/Deribit, **H987** gamma (OI par strike enregistré seulement depuis 14:03 UTC aujourd'hui).\n"
      "- **H988 complet / H989** : mark price, index price et open interest Bybit/Binance à haute fréquence non enregistrés.\n")
    w(f"_Calcul : {time.time() - t_go:.0f} s._\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
