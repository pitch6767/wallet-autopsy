"""BOT95 — FUSION ENGINE F1, priorités 2 à 5 (Pitch, 12.10.2026 14:13) : H933/H954 fatigue de l'absorption et transition vers la cassure ;
H937/H956 perp → spot et retraits synchronisés ; H941 traduction d'un mouvement BTC en règlement ; H965/H969 avance exploitable après latence.
PROTOCOLE PRÉ-ENREGISTRÉ (ce fichier tel que committé avant le calcul de validation et de test). Hors ligne ; aucun ordre ; aucun bot, H816, H821,
R4 ni fantôme modifié ; période réservée (≥ 13.10.2026) jamais lue. Découpage identique à H971 : test INÉDIT ≥ 12.10 06:00 UTC ; avant :
apprentissage 2/3, validation 1/3. IC 90 % par cycles.

H933 FATIGUE : vague = seconde où z(pression nette 5 s) ≥ 1,5 (au plus une par 5 s) ; rang = nombre de vagues de même sens dans les 60 s
  précédentes + 1. Vague « absorbée » si le prix Binance bouge de moins de 0,5 σ5 dans son sens sur les 5 s. Efficacité = mouvement de prix sur
  5 s ($) / pression nette 5 s (BTC). Hypothèse : l'efficacité augmente avec le rang (l'absorption s'épuise).
H954 TRANSITION : après au moins une vague absorbée dans les 60 s, une nouvelle vague de même sens annonce-t-elle une cassure (mouvement
  > 1,5 σ30 dans le sens de la vague sur 30 s) plus souvent qu'une première vague ? Taux comparés, IC par cycles.
H937 PERP → SPOT (grille 50 ms, heures de réception Dublin) : choc perp = variation du perp Bybit sur 500 ms ≥ 3 écarts-types (100 dernières s)
  alors que Binance spot a bougé de moins d'un tiers de ce choc ; au plus un par 5 s. Mesures : part du choc reproduite par le spot après
  100 / 250 / 500 / 1 000 / 2 000 ms ; délai jusqu'à 50 % (H965, distribution) ; délai de réévaluation Polymarket (milieu du jeton dans le sens du choc
  ≥ +1 c) ; avance restante après notre latence de 164 ms.
H969 ALPHA EXÉCUTABLE : à chaque choc, achat 20 $ du jeton dans le sens du choc à détection + 164 ms au prix vendeur vu à la détection ;
  (a) revente au meilleur acheteur 10 s après ; (b) revente 30 s après ; (c) conservation jusqu'au règlement officiel. Frais compris.
H956 RETRAITS SYNCHRONISÉS : retrait = baisse de profondeur non expliquée par les transactions sur 1 s ; « fort » = au-dessus du 95e centile
  (apprentissage) pour la place. Synchronisé = Binance spot et Bybit perp forts du même côté dans la même seconde. Mouvement BTC à 5/10/30 s
  signé (retrait vendeur → hausse), comparé aux retraits forts sur une seule place.
H941 RÈGLEMENT : pour chaque vague forte (H933) avec 30 à 240 s restantes, déplacement de la probabilité de règlement M0 entre t et t + 10 s
  (signé dans le sens de la vague), part des cas où ce déplacement dépasse 0,03 (ordre de grandeur écart + frais), et écart résultat officiel − M0(t).
Usage : python3 etude/bot5min/transmission_h933.py dossier_cycles_dublin [--controle]"""
import os, sys, math, time, json, gzip, collections
import numpy as np, pandas as pd

ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
import latence_h766 as LH, liquidite_h833 as L, dpe_h841 as DP, pression_h971 as PR
CONTROLE = "--controle" in sys.argv; RESERVE = 1791849600; TEST_DEB = 1791784800
SORTIE = os.path.join(ICI, "resultat_transmission_h933" + ("_controle" if CONTROLE else "") + ".md")
EXEC = 164; MISE = 20.0; RNG = np.random.default_rng(933)
fee = lambda p: 0.07 * p * (1 - p)


def cell(v, g):
    v = np.asarray(v, float); g = np.asarray(g); m = np.isfinite(v)
    if m.sum() < 5: return f"— (n={int(m.sum())})"
    c = L.ic_g(g[m], v[m]); return f"{v[m].mean():+.2f} [{c[0]:+.2f} ; {c[1]:+.2f}]"


def main():
    t_go = time.time(); o = []; w = o.append
    G, cyc = L.grille(sys.argv[1]); P = L.preparer(G); L.P_sd1 = P["sd1"]; Y = L.resultats_officiels(cyc); V = PR.grandeurs(G, P)
    cycles = sorted(s for s in cyc if s < RESERVE); avant = [s for s in cycles if s < TEST_DEB]; n_tr = len(avant) * 2 // 3
    part = {s: ("apprentissage" if k < n_tr else "validation") for k, s in enumerate(avant)}
    if not CONTROLE: part.update({s: "test" for s in cycles if s >= TEST_DEB})
    PARTS = ["apprentissage", "validation"] + ([] if CONTROLE else ["test"])
    stof = lambda i: (G["t0"] + i) - (G["t0"] + i) % 300; bn = G["bn"]; sd5 = P["sd5"]
    w(f"# Bot95 — F1 priorités 2 à 5 : fatigue de l'absorption, perp → spot, retraits synchronisés, règlement, avance exploitable "
      f"({'CONTRÔLE' if CONTROLE else 'apprentissage / validation / test inédit'})\n")
    nb = collections.Counter(part.values())
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. Cycles : " + ", ".join(f"{k} {nb[k]}" for k in PARTS) + ". Aucun ordre ; période réservée non lue.\n")

    # ---------------- H933 / H954 / H941
    vagues = []; last = {1: -99, -1: -99}
    for i in range(700, G["n"] - 31):
        st = stof(i)
        if st not in part or not (G["ok"][i] and G["ok"][i + 30]) or not np.isfinite(V["zPn5"][i]) or not np.isfinite(sd5[i]) or sd5[i] <= 0: continue
        z = V["zPn5"][i]
        if abs(z) < 1.5: continue
        s = 1 if z > 0 else -1
        if i - last[s] < 5: continue
        last[s] = i
        vagues.append(dict(i=i, st=st, s=s, part=part[st], mv=P["d5"][i] * s, pn=abs(V["Pn5"][i]), sd5=sd5[i], sd30=P["sd1"][i] * math.sqrt(30)))
    for k, v in enumerate(vagues):
        prev = [u for u in vagues[max(0, k - 30):k] if u["s"] == v["s"] and v["i"] - u["i"] <= 60]
        v["rang"] = len(prev) + 1; v["absorbee"] = v["mv"] < 0.5 * v["sd5"]; v["apres_abs"] = any(u["absorbee"] for u in prev)
        v["eff"] = v["mv"] / max(v["pn"], 1e-6)
        v["casse"] = float((bn[v["i"] + 30] - bn[v["i"]]) * v["s"] > 1.5 * v["sd30"])
        v["y10"] = (bn[v["i"] + 10] - bn[v["i"]]) * v["s"]
    w("## 1. H933 — Fatigue de l'absorption\n")
    w("Efficacité = mouvement du prix sur 5 s ($) par BTC de pression nette ; part de vagues absorbées ; mouvement à 10 s (signé).\n")
    w("| Échantillon | Rang de la vague | Vagues | Absorbées | Efficacité ($/BTC) | Mouvement à 10 s ($) |\n|---|---|---|---|---|---|")
    for pt in PARTS:
        for rg, f in (("1re", lambda v: v["rang"] == 1), ("2e", lambda v: v["rang"] == 2), ("3e et plus", lambda v: v["rang"] >= 3)):
            Z = [v for v in vagues if v["part"] == pt and f(v)]
            if not Z: continue
            g = [v["st"] for v in Z]
            w(f"| {pt} | {rg} | {len(Z)} | {100 * np.mean([v['absorbee'] for v in Z]):.0f} % | {cell([v['eff'] for v in Z], g)} | {cell([v['y10'] for v in Z], g)} |")
    w("\n## 2. H954 — Après une absorption, la vague suivante casse-t-elle plus souvent ?\n")
    w("Cassure = mouvement > 1,5 σ30 dans le sens de la vague sur 30 s.\n")
    w("| Échantillon | Vague | Vagues | Taux de cassure (IC 90 %) | Écart avec une 1re vague (IC 90 %) |\n|---|---|---|---|---|")
    for pt in PARTS:
        A = [v for v in vagues if v["part"] == pt and v["rang"] == 1]; B = [v for v in vagues if v["part"] == pt and v["rang"] >= 2 and v["apres_abs"]]
        for lab, Z in (("1re vague", A), ("après absorption", B)):
            if len(Z) < 5: continue
            ref = np.mean([v["casse"] for v in A]) if A else np.nan
            d = [v["casse"] - ref for v in Z]
            w(f"| {pt} | {lab} | {len(Z)} | {cell([100 * v['casse'] for v in Z], [v['st'] for v in Z])} % | " + ("—" if lab == "1re vague" else cell([100 * x for x in d], [v["st"] for v in Z]) + " pts") + " |")
    w("\n## 3. H941 — Un mouvement BTC déplace-t-il assez la probabilité de règlement ?\n")
    w("Pour chaque vague forte avec 30 à 240 s restantes : déplacement de M0 entre t et t + 10 s (signé), part des cas où il dépasse 0,03, et résultat officiel − M0(t).\n")
    w("| Échantillon | Temps restant | Vagues | Δ M0 à 10 s | Part > 0,03 | Résultat − M0(t) |\n|---|---|---|---|---|---|")
    for pt in PARTS:
        for lo, hi in ((30, 90), (90, 150), (150, 241)):
            rows = []
            for v in vagues:
                if v["part"] != pt: continue
                rest = v["st"] + 300 - (G["t0"] + v["i"])
                if not (lo <= rest < hi) or rest - 10 < 1: continue
                a = L.m0(G, cyc, v["st"], rest); b = L.m0(G, cyc, v["st"], rest - 10)
                if a and b: rows.append(((b[0] - a[0]) * v["s"], ((Y[v["st"]] - a[0]) * v["s"]) if v["st"] in Y else np.nan, v["st"]))
            if len(rows) < 5: continue
            R_ = np.array([(x[0], x[1]) for x in rows], float); g = [x[2] for x in rows]
            w(f"| {pt} | {lo}–{hi - 1} s | {len(rows)} | {cell(R_[:, 0], g)} | {100 * np.mean(R_[:, 0] > 0.03):.0f} % | {cell(R_[:, 1], g)} |")

    # ---------------- H937 / H965 / H969 : grille 50 ms
    w("\n## 4. H937 / H965 / H969 — Chocs du perp Bybit : transmission au spot, à Polymarket, et avance exploitable\n")
    chocs = []
    for st in cycles:
        if st not in part: continue
        try: R = json.load(gzip.open(cyc[st]["f"]))
        except Exception: continue
        rows = [(r[0], (r[1][0] if r[1] else np.nan), (r[3][0] if r[3] else np.nan)) for r in R.get("ex", []) if r[1] and r[3]]
        if len(rows) < 200: continue
        D = pd.DataFrame(rows, columns=["t", "perp", "bn"]).sort_values("t"); D["t"] = (D["t"] // 50) * 50
        D = D.groupby("t").last().reindex(np.arange(D.t.min(), D.t.max() + 50, 50)).ffill(limit=40)
        tt = D.index.values; pe = D["perp"].values; sp = D["bn"].values
        d10 = np.full(len(pe), np.nan); d10[10:] = pe[10:] - pe[:-10]; s10 = np.full(len(sp), np.nan); s10[10:] = sp[10:] - sp[:-10]
        sdv = pd.Series(d10).rolling(2000, min_periods=400).std().shift(1).values
        cy = None; lastk = -999
        for k in np.flatnonzero(np.isfinite(d10) & np.isfinite(sdv) & (np.abs(d10) >= 3 * np.nan_to_num(sdv, nan=1e9))):
            if k - lastk < 100 or k + 40 >= len(pe): continue
            s = 1 if d10[k] > 0 else -1
            if abs(s10[k]) >= abs(d10[k]) / 3 or s10[k] * s >= abs(d10[k]) / 3: continue
            lastk = k; t = int(tt[k]); rest = st + 300 - t / 1000
            if rest < 35: continue
            frac = {ms: ((sp[k + ms // 50] - sp[k]) * s / abs(d10[k])) if k + ms // 50 < len(sp) else np.nan for ms in (100, 250, 500, 1000, 2000)}
            mi = [j for j in range(1, 41) if k + j < len(sp) and (sp[k + j] - sp[k]) * s >= 0.5 * abs(d10[k])]
            chocs.append(dict(st=st, t=t, s=s, part=part[st], frac=frac, t50=(mi[0] * 50 if mi else np.nan), rest=rest))
    # Polymarket : réévaluation et exécution
    par_cy = collections.defaultdict(list)
    for c in chocs: par_cy[c["st"]].append(c)
    for st, Cs in par_cy.items():
        cy = LH.Cycle(cyc[st]["f"]); T = []
        for c in Cs: T += [c["t"], c["t"] + EXEC] + [c["t"] + d for d in range(250, 10001, 250)] + [c["t"] + 30000, c["t"] + 30000 + EXEC]
        E = {k: DP.compact(v) for k, v in cy.etats(T).items()}
        for c in Cs:
            X = "Up" if c["s"] > 0 else "Down"; t = c["t"]
            def mid(L_):
                if not L_ or not L_[0] or not L_[1]: return np.nan
                m = (L_[0][0][0] + L_[1][0][0]) / 2000; return m if X == "Up" else 1 - m
            m0 = mid(E.get(t)); c["tpoly"] = np.nan
            for d in range(250, 10001, 250):
                if (mid(E.get(t + d)) - m0) >= 0.01: c["tpoly"] = d; break
            c["pa"] = c["pb"] = c["pc"] = np.nan
            Lo, Lx = E.get(t), E.get(t + EXEC); v = DP.vend(Lo, X)
            if not v or not Lx: continue
            lim = v[0][0]; q = cc = 0.0
            for px, sz in DP.vend(Lx, X):
                if px > lim: break
                if px <= 0 or px >= 1000: continue
                pp = px / 1000; u = pp + fee(pp); kq = min(sz, (MISE - cc) / u)
                if kq <= 1e-9: break
                q += kq; cc += kq * u
            if q <= 0: continue
            def revente(L_):
                if not L_: return np.nan
                r = 0.0; rq = q
                for px, sz in DP.ach(L_, X):
                    kk = min(sz, rq); pp = px / 1000; r += kk * (pp - fee(pp)); rq -= kk
                    if rq <= 1e-9: break
                return r - cc if rq <= 1e-9 else np.nan
            c["pa"] = revente(E.get(t + 10000)); c["pb"] = revente(E.get(t + 30000 + EXEC) or E.get(t + 30000))
            if st in Y: c["pc"] = q * (1.0 if ((Y[st] == 1.0) == (X == "Up")) else 0.0) - cc
    w(f"{len(chocs)} chocs du perp (≥ 3 écarts-types en 500 ms, spot encore immobile).\n")
    w("| Échantillon | Chocs | Part reproduite par le spot à 100 / 250 / 500 / 1 000 / 2 000 ms | Délai spot à 50 % (médiane, ms) | Polymarket +1 c : part et délai médian (ms) | Avance restante après 164 ms (médiane, ms) |\n|---|---|---|---|---|---|")
    for pt in PARTS:
        Z = [c for c in chocs if c["part"] == pt]
        if not Z: continue
        fr = " / ".join(f"{np.nanmean([c['frac'][ms] for c in Z]):+.2f}" for ms in (100, 250, 500, 1000, 2000))
        tp = np.array([c["tpoly"] for c in Z], float); t5 = np.array([c["t50"] for c in Z], float)
        w(f"| {pt} | {len(Z)} | {fr} | {np.nanmedian(t5) if np.isfinite(t5).any() else float('nan'):.0f} ({100 * np.isfinite(t5).mean():.0f} % atteignent 50 %) | "
          f"{100 * np.isfinite(tp).mean():.0f} %, {np.nanmedian(tp) if np.isfinite(tp).any() else float('nan'):.0f} | {np.nanmedian(tp - EXEC) if np.isfinite(tp).any() else float('nan'):.0f} |")
    w("\n**H969 — Achat de 20 $ du jeton dans le sens du choc à 164 ms, au prix vu (frais compris)**\n")
    w("| Échantillon | Achats | (a) revente à 10 s ($, IC 90 % total) | (b) revente à 30 s | (c) règlement |\n|---|---|---|---|---|")
    for pt in PARTS:
        Z = [c for c in chocs if c["part"] == pt and np.isfinite(c.get("pa", np.nan)) | np.isfinite(c.get("pc", np.nan))]
        if not Z: continue
        row = f"| {pt} | {len(Z)} |"
        for k in ("pa", "pb", "pc"):
            v = np.array([c.get(k, np.nan) for c in Z], float); g = np.array([c["st"] for c in Z]); m = np.isfinite(v)
            if m.sum() < 3: row += " — |"; continue
            ci = L.ic_tot(g[m], v[m]); row += f" {v[m].sum():+.0f} [{ci[0]:+.0f} ; {ci[1]:+.0f}] (n={m.sum()}) |"
        w(row)

    # ---------------- H956 retraits synchronisés
    w("\n## 5. H956 — Retraits synchronisés Binance spot / Bybit perp\n")
    by_dec = {"a": np.zeros(G["n"]), "b": np.zeros(G["n"])}
    for st in cycles:
        if st not in part: continue
        try: R = json.load(gzip.open(cyc[st]["f"]))
        except Exception: continue
        for r in (R.get("ob") or {}).get("by", []):
            i = int(math.ceil(r[0] / 1000)) - G["t0"]
            if 0 <= i < G["n"] and len(r) > 15: by_dec["b"][i] += r[14]; by_dec["a"][i] += r[15]
    Wbn = {"a": np.nan_to_num(G["dec_a"]) - np.nan_to_num(G["agb"]), "b": np.nan_to_num(G["dec_b"]) - np.nan_to_num(G["ags"])}
    Wby = {"a": by_dec["a"] - np.nan_to_num(G["agb_by"]), "b": by_dec["b"] - np.nan_to_num(G["ags_by"])}
    trI = np.array([part.get(stof(i)) == "apprentissage" and G["ok"][i] for i in range(G["n"])])
    seuil = {(pl, sd): np.percentile(W[sd][trI], 95) for pl, W in (("bn", Wbn), ("by", Wby)) for sd in ("a", "b")}
    ev = []
    for i in range(700, G["n"] - 31):
        st = stof(i)
        if st not in part or not (G["ok"][i] and G["ok"][i + 30]): continue
        for sd, s in (("a", 1), ("b", -1)):
            f1 = Wbn[sd][i] > seuil[("bn", sd)]; f2 = Wby[sd][i] > seuil[("by", sd)]
            if f1 or f2: ev.append(dict(st=st, part=part[st], typ="synchronisé" if (f1 and f2) else ("Binance seul" if f1 else "Bybit seul"), y={h: (bn[i + h] - bn[i]) * s for h in (5, 10, 30)}))
    w("Mouvement BTC signé (retrait d'offres vendeuses → hausse attendue), en $.\n")
    w("| Échantillon | Type | Secondes | 5 s | 10 s | 30 s |\n|---|---|---|---|---|---|")
    for pt in PARTS:
        for ty in ("synchronisé", "Binance seul", "Bybit seul"):
            Z = [e for e in ev if e["part"] == pt and e["typ"] == ty]
            if not Z: continue
            g = [e["st"] for e in Z]
            w(f"| {pt} | {ty} | {len(Z)} | " + " | ".join(cell([e["y"][h] for e in Z], g) for h in (5, 10, 30)) + " |")
    w("\n## Limites\n- Carnets limités à 50 $ du meilleur prix ; perp Binance non enregistré ; quelques dizaines d'heures.\n"
      "- Les délais sont des heures de réception à Dublin ; notre latence de 164 ms est appliquée en plus.\n")
    w(f"_Calcul : {time.time() - t_go:.0f} s._\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
