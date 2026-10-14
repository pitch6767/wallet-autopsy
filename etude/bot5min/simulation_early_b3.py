"""BOT95 — simulation « achat early peu cher » + B3, demandée par Pitch le 14.10.2026 13:10
(« fais une simulation avec 10 $ early achat peu chère et B3 combiné »).
Hors ligne, aucun ordre. Simulation DESCRIPTIVE : B3 a été figée avant la validation (H1084) ; les règles early sont NOUVELLES et
n'ont PAS été pré-enregistrées. Seuls les chiffres de validation avec leur IC comptent ; aucun avantage annoncé si l'IC contient 0.
Données et conventions identiques à H1084 (etude/bot5min/biais_fin_cycle_h1084.py) : transactions publiques Polymarket BTC 5 min
(achats seulement), Binance BTCUSDT 1 s. Marchés ≥ 09.10 00:00 UTC écartés. Exploration 12.09–30.09, validation 01.10–08.10.
  Prix du marché à t = médiane des achats (en prix Up) dans (t−6, t], au moins 2 achats. Prix PAYÉ = médiane des achats du côté acheté
  dans (t, t+6] (secondes entières, donc t+1 à t+6) ; frais 0,07·p·(1−p) ; prix payé gardé seulement dans ]0,01 ; 0,99[ ; gardé jusqu'au
  règlement ; un achat par cycle et par règle (premier instant qui déclenche ET est servi) ; 10 $ par achat.
RÈGLES :
  B3   : 20–60 s restantes (t = 240…280), favori 0,90–0,98 au signal et zf ≥ 3 → acheter le favori (identique à H1084).
  E1   : t = 10, 15, …, 60 s après l'ouverture, côté le moins cher au signal ≤ 0,45 → acheter ce côté.
  E2   : idem avec ≤ 0,40.
  E3   : E1 ; puis, seulement dans les cycles où E1 a acheté, si B3 déclenche : même côté → renfort ; autre côté → couverture.
  E1+B3: E1 et B3 indépendants dans tous les cycles.
P&L par cycle ; cycles sans achat = 0 $ ; IC 90 % bootstrap par cycles (10 000 tirages, percentiles 5 / 95). Un prix PESSIMISTE
= max(prix du signal, prix payé) est rejoué à côté.
Usage : python3 etude/bot5min/simulation_early_b3.py btc1s.npz polytrades_*.json.gz"""
import sys, json, gzip, os, numpy as np, pandas as pd
ICI = os.path.dirname(os.path.abspath(__file__)); FIN_EXPLO = 1790812800; FIN_VALID = 1791504000   # 01.10 / 09.10 00:00 UTC
fee = lambda p: 0.07 * p * (1 - p); TT_B = list(range(240, 295, 5)); TT_E = list(range(10, 65, 5)); MISE = 10.0

def med(a):
    return float(np.median(a)) if len(a) else np.nan

def construire(npz, fichiers):
    z = np.load(npz); t0 = int(z["t"][0]); c = z["c"].astype(float)
    Cc = np.concatenate([[0], np.cumsum(c)]); Cd2 = np.concatenate([[0], np.cumsum(np.diff(c, prepend=c[0]) ** 2)])
    sd = lambda i, w: np.sqrt((Cd2[i + 1] - Cd2[i + 1 - w]) / w)
    rows, cyc = [], []
    for f in sorted(fichiers):
        for st_, m in json.load(gzip.open(f))["marches"].items():
            st = int(st_); r = m.get("resultat") or {}
            if r.get("Up") not in (0.0, 1.0) or st >= FIN_VALID: continue
            s0 = st - t0
            if s0 < 3700 or s0 + 300 >= len(c): continue
            upw = int(r["Up"] == 1.0); K = (Cc[s0] - Cc[s0 - 60]) / 60; cyc.append((st, upw))
            T = np.array([(x[0] - st, x[4] if x[3] == "Up" else 1 - x[4], 1 if x[3] == "Up" else 0, x[4]) for x in m["trades"]
                          if x[0] is not None and x[4] and 0 < x[4] < 1 and x[2] == "BUY" and 0 <= x[0] - st < 300], float).reshape(-1, 4)
            for tt in TT_E + TT_B:
                if tt >= 240:
                    i = s0 + tt; s1 = sd(i, 3600); n = 300 - tt - 1
                    EA = (Cc[i + 1] - Cc[s0 + 240] + n * c[i]) / 60; zz = (EA - K) / (s1 * np.sqrt(n * (n + 1) * (2 * n + 1) / 6) / 60)
                else:
                    zz = np.nan
                w = T[(T[:, 0] > tt - 6) & (T[:, 0] <= tt)]; nx = T[(T[:, 0] > tt) & (T[:, 0] <= tt + 6)]
                rows.append(dict(st=st, t=tt, upw=upw, pu=np.median(w[:, 1]) if len(w) >= 2 else np.nan,
                                 pUp=med(nx[nx[:, 2] == 1][:, 3]), pDown=med(nx[nx[:, 2] == 0][:, 3]), z=zz))
    D = pd.DataFrame(rows); D = D[D.pu.notna()].copy()
    D["fav_up"] = D.pu >= .5; D["fp"] = np.where(D.fav_up, D.pu, 1 - D.pu)
    D["zf"] = np.where(D.fav_up, D.z, -D.z); D["left"] = 300 - D.t
    C = pd.DataFrame(cyc, columns=["st", "upw"]).drop_duplicates("st").sort_values("st").reset_index(drop=True)
    C["part"] = np.where(C.st < FIN_EXPLO, "exploration", "validation")
    return D, C

def achats(D, regle):
    """Un achat par cycle : premier instant qui déclenche et est servi. Colonnes : st, up (côté acheté), px, sig (prix du signal), w."""
    if regle == "B3":
        x = D[D.fp.between(.90, .98) & D.left.between(20, 60) & (D.zf >= 3)].copy(); x["up"] = x.fav_up; x["sig"] = x.fp
    else:
        lim = .45 if regle == "E1" else .40
        x = D[(D.t <= 60) & ((1 - D.fp) <= lim)].copy(); x["up"] = ~x.fav_up; x["sig"] = 1 - x.fp
    x["px"] = np.where(x.up, x.pUp, x.pDown); x["w"] = np.where(x.up, x.upw, 1 - x.upw)
    x = x[np.isfinite(x.px) & (x.px > 0.01) & (x.px < 0.99)].sort_values(["st", "t"]).groupby("st").head(1)
    return x[["st", "t", "up", "px", "sig", "w"]].reset_index(drop=True)

def pnl(x, pessimiste):
    p = np.maximum(x.px, x.sig) if pessimiste else x.px
    return (x.w / (p + fee(p)) - 1) * MISE

def stats(C, buys, rng):
    """buys : DataFrame (st, pnl, w, px). C : cycles de la période (ordre chronologique)."""
    per = buys.groupby("st").pnl.sum(); v = C.st.map(per).fillna(0.0).values
    bs = v[rng.integers(0, len(v), (10000, len(v)))].sum(1)
    cum = np.cumsum(v); dd = float((np.maximum.accumulate(np.concatenate([[0], cum]))[1:] - cum).max()) if len(v) else 0.0
    serie = best = 0
    for p in per.reindex(C.st[C.st.isin(per.index)]).values:     # cycles avec achat, dans l'ordre
        serie = serie + 1 if p < 0 else 0; best = max(best, serie)
    nb = len(buys); mx = int(buys.groupby("st").size().max()) if nb else 0
    return dict(cycles=int(len(C)), cycles_actifs=int(len(per)), achats=int(nb), gagnants=int(buys.w.sum()),
                taux=float(buys.w.mean()) if nb else np.nan, prix=float(buys.px.mean()) if nb else np.nan,
                mise=float(nb * MISE), mise_max_cycle=float(mx * MISE), pnl=float(v.sum()),
                roi=float(v.sum() / (nb * MISE)) if nb else np.nan, ic90=np.percentile(bs, [5, 95]).round(1).tolist(),
                ic90_roi=(np.percentile(bs, [5, 95]) / (nb * MISE)).round(4).tolist() if nb else [np.nan, np.nan],
                dd_max=dd, serie_pertes=int(best))

if __name__ == "__main__":
    D, C = construire(sys.argv[1], sys.argv[2:]); rng = np.random.default_rng(14102026)
    A = {r: achats(D, r) for r in ("E1", "E2", "B3")}
    out = {"cycles": C.groupby("part").size().to_dict(), "strategies": {}, "e3": {}}
    parts = {"exploration": C[C.part == "exploration"], "validation": C[C.part == "validation"], "total": C}
    for prix in ("observe", "pessimiste"):
        L = {r: A[r].assign(pnl=pnl(A[r], prix == "pessimiste"), regle=r) for r in A}
        e1, b3 = L["E1"], L["B3"]
        b3_e3 = b3[b3.st.isin(e1.st)]
        strat = {"E1": e1, "E2": L["E2"], "E3": pd.concat([e1, b3_e3]), "B3": b3, "E1+B3": pd.concat([e1, b3])}
        for nom, b in strat.items():
            for pa, Cp in parts.items():
                out["strategies"][f"{nom}|{pa}|{prix}"] = stats(Cp, b[b.st.isin(Cp.st)], rng)
        # E3 : renfort / couverture
        m = e1.merge(b3, on="st", suffixes=("_e", "_b"))
        for pa, Cp in parts.items():
            mm = m[m.st.isin(Cp.st)]; same = mm[mm.up_e == mm.up_b]; oth = mm[mm.up_e != mm.up_b]
            tot = oth.pnl_e + oth.pnl_b
            out["e3"][f"{pa}|{prix}"] = dict(
                achats_e1=int(e1.st.isin(Cp.st).sum()), b3_dans_cycles_e1=int(len(mm)),
                renforts=int(len(same)), renforts_gagnes=int(same.w_b.sum()), pnl_renforts=float(same.pnl_b.sum()),
                couvertures=int(len(oth)), couvertures_gagnees=int(oth.w_b.sum()), pnl_couvertures=float(oth.pnl_b.sum()),
                pertes_e1_couvertes=int((oth.w_e == 0).sum()),
                perte_e1_moyenne_couverte=float(oth[oth.w_e == 0].pnl_e.mean()) if len(oth) else np.nan,
                perte_cycle_moyenne_apres_couverture=float(tot[oth.w_e == 0].mean()) if len(oth) else np.nan,
                couvertures_qui_annulent_la_perte=int(((oth.w_e == 0) & (tot >= 0)).sum()),
                couvertures_perdues=int((oth.w_b == 0).sum()),
                prix_moyen_couverture=float(oth.px_b.mean()) if len(oth) else np.nan)
    # contrôle : B3 doit reproduire H1084 (validation : 169 achats, 168 gagnés, +42 $)
    out["controle_B3_validation"] = {k: out["strategies"]["B3|validation|observe"][k] for k in ("achats", "gagnants", "pnl")}
    out["e1_par_instant"] = {pa: A["E1"][A["E1"].st.isin(Cp.st)].groupby("t").agg(n=("w", "size"), taux=("w", "mean"), prix=("px", "mean")).round(3).reset_index().to_dict("records")
                             for pa, Cp in parts.items()}
    s = json.dumps(out, ensure_ascii=False, indent=1, default=float); print(s)
    open(os.path.join(ICI, "simulation_early_b3.json"), "w").write(s)
