"""BOT95 — H979 à H985 (Pitch, 12.10.2026 15:10) : options Deribit, CME, Coinbase, gamma, fusion, avance exécutable.
PROTOCOLE PRÉ-ENREGISTRÉ (ce fichier tel que committé avant tout calcul). Hors ligne ; aucun ordre ; aucun bot, H816, H821, R4 ni fantôme modifié ;
période réservée (≥ 13.10.2026) jamais lue. Aucun abonnement acheté.

DONNÉES
  Deribit : toutes les transactions d'options BTC (API publique d'historique) du 12.09 au 12.10 13:00 UTC : heure de l'échange, instrument
    (échéance, prix d'exercice, call/put), côté preneur, prix, quantité, volatilité implicite, indice. Pas d'heure de réception historique :
    l'information est supposée disponible 100 ms après l'heure de l'échange (sensibilité 500 ms), arrondie à la seconde suivante sur les données 1 s.
    Open interest par prix d'exercice : non disponible en historique (H981 non testable, déclaré).
  BTC Binance spot 1 s (12.09 → 11.10) ; laboratoire de Dublin (11.10 → 12.10 13:00 UTC : perp, spot, Coinbase prix et flux agressifs,
    Chainlink, carnet Polymarket, résultat officiel).
  CME, Nasdaq, taux, dollar, or : aucune donnée à la seconde (H982 non testable ; coûts relevés dans le rapport).
DÉLTA : Black-Scholes, taux nul, volatilité implicite de la transaction, échéance Deribit à 08:00 UTC.
  Sens d'une transaction : + si achat de call ou vente de put par le preneur, − si achat de put ou vente de call.
  Flux delta DF(w) = somme sur w s de (sens preneur × delta × quantité), en BTC équivalent.
H979 ÉVÉNEMENTS : grosse transaction = notionnel (quantité × indice) au-dessus du 95e centile de l'apprentissage ; catégories : toutes ;
  courtes (échéance < 2 jours) proches de la monnaie (|ln(K/S)| < 1 %) ; blocs. Mouvement BTC signé (sens delta) à 1/2/5/10/30/60 s après
  l'heure de disponibilité, et sur les 10 s AVANT (réaction ou avance ?). Placebo : mêmes instants décalés de ± 120 à 600 s, même signe.
  Dublin : mouvement du perp et du spot à 100/250/500 ms et 1/2 s ; réévaluation Polymarket (+1 c dans le sens) ; effet sur le règlement
  (résultat − M0, signé) ; P&L d'un achat de 20 $ du jeton dans le sens à 164 ms, conservé (frais compris).
H980 FLUX DELTA : prévoir le signe du BTC à 5/10/30/60 s (grille 5 s, 30 jours) ; modèle A = flux agressif BTC 1/5/30 s + momentum 1/5/30 s +
  volatilité ; modèle B = A + DF(1, 3, 5, 10, 30, 60 s) + volatilité implicite moyenne pondérée sur 60 s. Apprentissage < 02.10, test 02.10 → 11.10 ;
  AUC et ΔAUC, IC 90 % par jours et corrigé (4 cibles). Règlement : décisions synthétiques (même méthode que H822, Binance) à 240/180/120/60 s,
  M0 recalibré contre M0 + DF, Brier sur le test.
H983 COINBASE (Dublin) : flux agressif Coinbase net (en $) sur 1 et 5 s et écart de prix Coinbase − Binance : apport pour prévoir le signe de
  Binance à 5 et 30 s, en plus du flux et du momentum Binance (même méthode, apprentissage / validation / test Dublin).
H984/H985 : construits seulement si un instrument montre une valeur individuelle (IC corrigé > 0 sur le test) ; sinon déclarés non construits.
Usage : python3 etude/bot5min/options_h979.py dossier_btc dossier_cycles_dublin"""
import os, sys, math, time, json, gzip, glob, collections, datetime
import numpy as np, pandas as pd

ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
import latence_h766 as LH, liquidite_h833 as L, dpe_h841 as DP, barrieres_h822 as BR
RESERVE = 1791849600; COUPE = 1790899200; TEST_DEB = 1791784800; MISE = 20.0; RNG = np.random.default_rng(979); DISPO = 0.100
SORTIE = os.path.join(ICI, "resultat_options_h979.md")
fee = lambda p: 0.07 * p * (1 - p)
MOIS = {m: i + 1 for i, m in enumerate(["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"])}


def Ncdf(x): return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def charger_options(d):
    R = []
    for f in sorted(glob.glob(os.path.join(d, "deribit", "*.json.gz"))):
        for x in json.load(gzip.open(f))["trades"]:
            ts, inst, dirn, px, q, iv, S = x[0], x[1], x[2], x[3], x[4], x[5], x[6]
            if ts / 1000 >= RESERVE or not iv or not S: continue
            try:
                _, e, k, cp = inst.split("-"); dd = int(e[:-5]); mm = MOIS[e[-5:-2]]; yy = 2000 + int(e[-2:]); K = float(k)
            except Exception: continue
            T = (datetime.datetime(yy, mm, dd, 8, tzinfo=datetime.timezone.utc).timestamp() - ts / 1000) / (365 * 86400)
            if T <= 0: continue
            sig = iv / 100; d1 = (math.log(S / K) + 0.5 * sig * sig * T) / (sig * math.sqrt(T))
            delta = Ncdf(d1) if cp == "C" else Ncdf(d1) - 1
            sgn = 1 if dirn == "buy" else -1
            R.append((ts / 1000, sgn * delta * q, q * S, abs(math.log(K / S)), T * 365, iv, x[9], cp))
    D = pd.DataFrame(R, columns=["t", "dq", "notion", "mny", "jours", "iv", "bloc", "cp"]).sort_values("t")
    return D


def cell(v, g):
    v = np.asarray(v, float); g = np.asarray(g); m = np.isfinite(v)
    if m.sum() < 5: return f"— (n={int(m.sum())})"
    c = L.ic_g(g[m], v[m]); return f"{v[m].mean():+.2f} [{c[0]:+.2f} ; {c[1]:+.2f}]"


def main():
    t_go = time.time(); o = []; w = o.append
    OP = charger_options(sys.argv[1])
    B = BR.charger(os.path.join(sys.argv[1], "btc1s")); t0 = B["t0"]; n = B["n"]; c = B["c"]; flow = 2 * B["vb"] - B["v"]
    w("# Bot95 — H979 à H985 : options Deribit, CME, Coinbase, gamma des teneurs de marché, avance exécutable\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. Options Deribit : {len(OP)} transactions (12.09 → 12.10 13:00 UTC). "
      "BTC Binance 1 s : 12.09 → 11.10. Apprentissage < 02.10, test 02.10 → 11.10 ; Dublin 11.10 → 12.10. Aucun ordre ; aucun abonnement ; période réservée non lue.\n")
    w("## 0. Audit des données\n")
    w("| Source | Disponible | Limite |\n|---|---|---|\n"
      "| Deribit options : transactions (instrument, côté preneur, prix, quantité, volatilité implicite) | oui, 30 jours, API publique gratuite | heure de l'échange seulement (pas de réception) ; environ 6 000 transactions par jour, soit une toutes les 14 s en moyenne |\n"
      "| Deribit options : open interest par prix d'exercice, carnets d'options | **non** en historique | à enregistrer à partir de maintenant pour tester H981 |\n"
      "| Deribit indice, perpétuel, DVOL | oui à Dublin depuis le 12.10 11:55 UTC | trop récent pour cette étude |\n"
      "| Coinbase BTC/USD | prix et flux agressifs à Dublin depuis le 11.10 | carnet L2 non enregistré (gratuit et public, à ajouter si utile) |\n"
      "| CME BTC / Micro BTC | **non** | fournisseur payant (Databento : historique à partir de 0,50 $/Go, 125 $ de crédit offert, temps réel dans les offres payantes) |\n"
      "| Nasdaq, taux, dollar, or | **non** à la seconde | sources gratuites en bougies de 1 min seulement |\n")
    stat = OP.assign(jour=(OP.t // 86400)).groupby("jour").size()
    w(f"Transactions d'options par jour : médiane {int(stat.median())}, minimum {int(stat.min())}, maximum {int(stat.max())}.\n")

    tr_m = OP.t < COUPE
    seuil = np.percentile(OP.notion[tr_m], 95)
    OP["idx"] = np.ceil(OP.t + DISPO).astype(np.int64) - t0
    ev = OP[(OP.notion >= seuil) & (OP.idx > 700) & (OP.idx < n - 61)].copy()
    ev["sens"] = np.sign(ev.dq)
    cats = {"toutes les grosses transactions": ev, "courtes (< 2 j) proches de la monnaie": ev[(ev.jours < 2) & (ev.mny < 0.01)], "blocs": ev[ev.bloc == True]}
    w(f"## 1. H979 — Grosses transactions d'options : avance ou réaction ?\n\nGrosse transaction = notionnel ≥ {seuil:,.0f} $ (95e centile de l'apprentissage). "
      "Mouvement BTC Binance signé dans le sens delta du preneur (positif = la transaction « avait raison »), en $. « Avant » = 10 s précédant l'heure de disponibilité. "
      "Placebo = mêmes signes, instants décalés de 2 à 10 min. IC 90 % par jours.\n")
    w("| Échantillon | Catégorie | Événements | 10 s AVANT | 1 s | 2 s | 5 s | 10 s | 30 s | 60 s | Placebo 10 s |\n|---|---|---|---|---|---|---|---|---|---|---|")
    for pt, msk in (("apprentissage", lambda E: E.t < COUPE), ("test", lambda E: E.t >= COUPE)):
        for nom, E in cats.items():
            E = E[msk(E)]
            if len(E) < 5: continue
            ix = E.idx.values; s = E.sens.values; g = (E.t // 86400).values
            mv = lambda h: (c[ix + h] - c[ix]) * s
            av = (c[ix] - c[ix - 10]) * s
            pl_ix = np.clip(ix + RNG.choice([-1, 1], len(ix)) * RNG.integers(120, 600, len(ix)), 700, n - 61); pl = (c[pl_ix + 10] - c[pl_ix]) * s
            w(f"| {pt} | {nom} | {len(E)} | {cell(av, g)} | " + " | ".join(cell(mv(h), g) for h in (1, 2, 5, 10, 30, 60)) + f" | {cell(pl, g)} |")

    # ---------- H980 flux delta
    w("\n## 2. H980 — Le flux delta des options ajoute-t-il de l'information à l'OFI, au momentum et à la volatilité BTC ?\n")
    dq = np.zeros(n); ivs = np.zeros(n); qq = np.zeros(n)
    ii = OP.idx.values; okk = (ii >= 0) & (ii < n)
    np.add.at(dq, ii[okk], OP.dq.values[okk]); np.add.at(ivs, ii[okk], (OP.iv * OP.notion).values[okk]); np.add.at(qq, ii[okk], OP.notion.values[okk])
    cs = lambda x: np.concatenate([[0], np.cumsum(x)])
    Cdq, Cfl, Civ, Cq = cs(dq), cs(flow), cs(ivs), cs(qq)
    win = lambda C, i, k: C[i + 1] - C[i + 1 - k]
    r = np.diff(np.log(c), prepend=np.log(c[0])); r2 = cs(r * r)
    I = np.arange(4000, n - 61, 5)
    vol = np.sqrt((r2[I + 1] - r2[I + 1 - 300]) / 300) * c[I]
    XA = np.column_stack([win(Cfl, I, 1), win(Cfl, I, 5), win(Cfl, I, 30), (c[I] - c[I - 1]) / vol, (c[I] - c[I - 5]) / vol, (c[I] - c[I - 30]) / vol, vol])
    ivw = np.where(win(Cq, I, 60) > 0, win(Civ, I, 60) / np.maximum(win(Cq, I, 60), 1e-9), 0)
    XB = np.column_stack([XA] + [win(Cdq, I, k) for k in (1, 3, 5, 10, 30, 60)] + [ivw])
    tt = t0 + I; trm = tt < COUPE; tem = ~trm; days = tt // 86400
    w(f"{len(I)} instants (toutes les 5 s, 30 jours). IC corrigé : 4 cibles.\n")
    w("| Cible | AUC A (BTC seul) | AUC B (+ flux delta options) | ΔAUC | IC 90 % | IC corrigé |\n|---|---|---|---|---|---|")
    for h in (5, 10, 30, 60):
        y = (c[I + h] > c[I]).astype(float); pr = {}
        for lab, X in (("A", XA), ("B", XB)):
            X = np.nan_to_num(X); mu, sd = X[trm].mean(0), X[trm].std(0) + 1e-9; b = L.ajuster((X[trm] - mu) / sd, y[trm], 2.0); pr[lab] = L.predire(b, (X - mu) / sd)
        U = np.unique(days[tem]); D = []
        for _ in range(300):
            mm = tem & np.isin(days, RNG.choice(U, len(U)))
            D.append(L.auc(pr["B"][mm], y[mm]) - L.auc(pr["A"][mm], y[mm]))
        a0, a1 = L.auc(pr["A"][tem], y[tem]), L.auc(pr["B"][tem], y[tem])
        w(f"| hausse BTC à {h} s | {a0:.4f} | {a1:.4f} | {a1 - a0:+.4f} | [{np.percentile(D, 5):+.4f} ; {np.percentile(D, 95):+.4f}] | [{np.percentile(D, 1.25):+.4f} ; {np.percentile(D, 98.75):+.4f}] |")
    # règlement synthétique
    S = BR.Serie(B); Dd = []
    for s in range(t0 - t0 % 300 + 300 + 4 * 3600, t0 + n - 600, 300):
        F = c[S.i(s + 240):S.i(s + 300)].mean(); K = c[S.i(s - 60):S.i(s)].mean(); y = 1.0 if F > K else 0.0
        for rest in (240, 180, 120, 60):
            p, z, mu_, sd_, K_, i = BR.m0(S, s, rest)
            Dd.append((s, p, y, [win(Cdq, i, k) for k in (10, 30, 60)]))
    tr_ = [d for d in Dd if d[0] < COUPE]; te_ = [d for d in Dd if d[0] >= COUPE]
    XA_ = lambda Z: np.array([[L.lg(d[1])] for d in Z]); XB_ = lambda Z: np.array([[L.lg(d[1])] + d[3] for d in Z])
    bA = L.ajuster(XA_(tr_), np.array([d[2] for d in tr_]), 0.1)
    Xb = XB_(tr_); mu, sd = Xb.mean(0), Xb.std(0) + 1e-9; mu[0], sd[0] = 0, 1; bB = L.ajuster((Xb - mu) / sd, np.array([d[2] for d in tr_]), 2.0)
    yt = np.array([d[2] for d in te_]); pa = L.predire(bA, XA_(te_)); pb = L.predire(bB, (XB_(te_) - mu) / sd); dl = L.brier(pa, yt) - L.brier(pb, yt)
    ci = L.ic_g(np.array([d[0] for d in te_]), dl)
    w(f"\nRèglement (substitut Binance, {len(te_)} décisions de test) : Brier règlement seul {L.brier(pa, yt).mean():.4f}, avec flux delta {L.brier(pb, yt).mean():.4f}, "
      f"gain {dl.mean():+.5f} [{ci[0]:+.5f} ; {ci[1]:+.5f}].\n")

    # ---------- Dublin : transmission, Polymarket, règlement, exécution (H979 + H985)
    w("## 3. H979 / H985 — Après une grosse transaction d'options : perp, spot, Polymarket, règlement, exécution (Dublin)\n")
    G, cyc = L.grille(sys.argv[2]); P = L.preparer(G); L.P_sd1 = P["sd1"]; Y = L.resultats_officiels(cyc)
    cycles = sorted(s for s in cyc if s < RESERVE)
    EVd = OP[(OP.notion >= seuil) & (OP.t >= cycles[0]) & (OP.t < cycles[-1] + 300)]
    rows = []
    for _, e in EVd.iterrows():
        st = int(e.t - e.t % 300)
        if st not in cyc: continue
        try: R = json.load(gzip.open(cyc[st]["f"]))
        except Exception: continue
        ta = (e.t + DISPO) * 1000; s = int(np.sign(e.dq))
        ex = sorted(R.get("ex", []), key=lambda x: x[0])
        def px_at(k, tms):
            v = None
            for r in ex:
                if r[0] > tms: break
                x = r[1 + ("perp", "okx", "bn", "cb", "cl").index(k)]
                if x and x[0]: v = x[0]
            return v
        p0 = {k: px_at(k, ta) for k in ("perp", "bn")}
        if not p0["perp"] or not p0["bn"]: continue
        mv = {(k, d): ((px_at(k, ta + d) - p0[k]) * s if px_at(k, ta + d) else np.nan) for k in ("perp", "bn") for d in (100, 250, 500, 1000, 2000)}
        av = (p0["bn"] - (px_at("bn", ta - 10000) or p0["bn"])) * s
        rest = st + 300 - e.t; i = int(e.t) - G["t0"]
        m = L.m0(G, cyc, st, int(rest)) if 30 <= rest <= 280 else None
        regl = ((Y[st] - m[0]) * s) if (m and st in Y) else np.nan
        cy = LH.Cycle(cyc[st]["f"]); tt_ = int(ta); T = [tt_, tt_ + 164] + [tt_ + d for d in range(250, 5001, 250)]
        E = {k: DP.compact(x) for k, x in cy.etats(T).items()}; X = "Up" if s > 0 else "Down"
        def mid(L_):
            if not L_ or not L_[0] or not L_[1]: return np.nan
            mm = (L_[0][0][0] + L_[1][0][0]) / 2000; return mm if X == "Up" else 1 - mm
        m0_ = mid(E[tt_]); tpo = next((d for d in range(250, 5001, 250) if mid(E[tt_ + d]) - m0_ >= 0.01), np.nan)
        pn = np.nan; v = DP.vend(E[tt_], X)
        if v and st in Y and rest >= 30:
            q = cc = 0.0
            for px, sz in DP.vend(E[tt_ + 164], X):
                if px > v[0][0]: break
                if px <= 0 or px >= 1000: continue
                pp = px / 1000; u = pp + fee(pp); kq = min(sz, (MISE - cc) / u)
                if kq <= 1e-9: break
                q += kq; cc += kq * u
            if q > 0: pn = q * (1.0 if ((Y[st] == 1.0) == (X == "Up")) else 0.0) - cc
        rows.append(dict(st=st, mv=mv, av=av, regl=regl, tpo=tpo, pn=pn))
    w(f"{len(rows)} grosses transactions d'options pendant les cycles enregistrés à Dublin (disponibilité supposée 100 ms après l'heure de l'échange).\n")
    if rows:
        g = [r_["st"] for r_ in rows]
        w("| Mesure | Valeur (IC 90 % par cycles) |\n|---|---|")
        w(f"| BTC spot, 10 s AVANT (signé) | {cell([r_['av'] for r_ in rows], g)} $ |")
        for k in ("perp", "bn"):
            for d in (100, 250, 500, 1000, 2000):
                w(f"| {'perp Bybit' if k == 'perp' else 'Binance spot'} à {d} ms | {cell([r_['mv'][(k, d)] for r_ in rows], g)} $ |")
        tp = np.array([r_["tpo"] for r_ in rows], float)
        w(f"| Polymarket +1 c dans le sens, en 5 s | {100 * np.isfinite(tp).mean():.0f} % des cas, délai médian {np.nanmedian(tp) if np.isfinite(tp).any() else float('nan'):.0f} ms |")
        w(f"| Règlement officiel − M0 (signé) | {cell([r_['regl'] for r_ in rows], g)} |")
        pn = np.array([r_["pn"] for r_ in rows], float); mk = np.isfinite(pn)
        if mk.sum() >= 3:
            ci = L.ic_tot(np.array(g)[mk], pn[mk]); w(f"| Achat 20 $ du jeton dans le sens à 164 ms, conservé | {pn[mk].sum():+.0f} $ sur {mk.sum()} achats [{ci[0]:+.0f} ; {ci[1]:+.0f}], {int((pn[mk] > 0).sum())} gagnants |")

    # ---------- H983 Coinbase
    w("\n## 4. H983 — Coinbase BTC/USD précède-t-il Binance ? (Dublin)\n")
    cbf = np.zeros(G["n"])
    for st in cycles:
        try: R = json.load(gzip.open(cyc[st]["f"]))
        except Exception: continue
        for r_ in R.get("fx", []):
            x = r_[1].get("cb")
            if not x: continue
            i = int(math.ceil(r_[0] / 1000)) - G["t0"]
            if 0 <= i < G["n"]: cbf[i] += (x[0] - x[1])
    avant = [s for s in cycles if s < TEST_DEB]; n_tr = len(avant) * 2 // 3
    part = {s: ("apprentissage" if k < n_tr else "validation") for k, s in enumerate(avant)}; part.update({s: "test" for s in cycles if s >= TEST_DEB})
    stof = lambda i: (G["t0"] + i) - (G["t0"] + i) % 300; bn = G["bn"]; Ccb = cs(cbf); Cbg = cs(np.nan_to_num(G["agb"]) - np.nan_to_num(G["ags"]))
    I2 = [i for i in range(700, G["n"] - 31, 3) if stof(i) in part and G["ok"][i] and G["ok"][i + 30] and np.isfinite(bn[i]) and np.isfinite(G["cb"][i]) and np.isfinite(P["sd1"][i])]
    s1 = lambda i: P["sd1"][i]
    XA2 = np.nan_to_num(np.array([[win(Cbg, i, 1), win(Cbg, i, 5), (bn[i] - bn[i - 1]) / s1(i), (bn[i] - bn[i - 5]) / s1(i), (bn[i] - bn[i - 30]) / s1(i), s1(i)] for i in I2]))
    XC = np.nan_to_num(np.array([[win(Ccb, i, 1), win(Ccb, i, 5), (G["cb"][i] - bn[i]) - (G["cb"][i - 5] - bn[i - 5]), (G["cb"][i] - G["cb"][i - 1]) / s1(i)] for i in I2]))
    pI = np.array([part[stof(i)] for i in I2]); gI = np.array([stof(i) for i in I2]); trm2 = pI == "apprentissage"
    w("| Cible | Échantillon | AUC Binance seul | AUC + Coinbase | ΔAUC (IC 90 %) |\n|---|---|---|---|---|")
    for h in (5, 30):
        y = np.array([bn[i + h] > bn[i] for i in I2], float); pr = {}
        for lab, X in (("A", XA2), ("C", np.column_stack([XA2, XC]))):
            mu, sd = X[trm2].mean(0), X[trm2].std(0) + 1e-9; b = L.ajuster((X[trm2] - mu) / sd, y[trm2], 2.0); pr[lab] = L.predire(b, (X - mu) / sd)
        for pt in ("validation", "test"):
            m = pI == pt; yt = y[m]; g = gI[m]; U = np.unique(g); D = []
            for _ in range(300):
                mm = np.isin(g, RNG.choice(U, len(U)))
                if yt[mm].min() != yt[mm].max(): D.append(L.auc(pr["C"][m][mm], yt[mm]) - L.auc(pr["A"][m][mm], yt[mm]))
            w(f"| hausse Binance à {h} s | {pt} | {L.auc(pr['A'][m], yt):.3f} | {L.auc(pr['C'][m], yt):.3f} | {np.percentile(D, 50):+.3f} [{np.percentile(D, 5):+.3f} ; {np.percentile(D, 95):+.3f}] |")
    w("\n## 5. H981, H982, H984\n- **H981 gamma des teneurs de marché** : non testable — l'open interest par prix d'exercice n'existe pas en historique gratuit. "
      "Il faudrait l'enregistrer (Deribit, gratuit, toutes les minutes) à partir de maintenant.\n- **H982 CME** : non testable sans abonnement (voir l'audit).\n"
      "- **H984 combinaison** : construite seulement si un instrument a une valeur individuelle démontrée (voir verdicts).\n")
    w(f"_Calcul : {time.time() - t_go:.0f} s._\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
