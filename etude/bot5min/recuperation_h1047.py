"""BOT95 — RÉCUPÉRATION, FAUX SAUVETAGES, TRAILING FONDAMENTAL, PROTECTION SÉLECTIVE : H1047 à H1050 (Pitch, 12.10.2026 18:26).
ÉTUDE SÉPARÉE, PRÉ-ENREGISTRÉE (ce fichier tel que committé le 12.10.2026, avant le calcul du test). Elle n'ajoute rien au protocole figé
H1003–H1046 et ne le modifie pas : elle réutilise seulement son moteur d'exécution (reversal_h1003.Inv, Moteur, simuler, signal_fav) en lecture.
Hors ligne ; aucun ordre ; aucun bot actif, H816, H821, R4 ni fantôme modifié.

PÉRIODES (celles de H1003–H1040) : apprentissage = 2/3 premiers cycles avant le 12.10 12:00 UTC, validation = 1/3 suivant ; test = 12.10 12:00 →
  13.10 00:00 UTC (calculé une seule fois) ; --confirmation = cycles ≥ 13.10 00:00 UTC. L'apprentissage ne sert qu'au cerveau B (même formule
  que H1003 : logit p = a + b·logit(M0) + c·logit(milieu Polymarket), pas de décision sans carnet à deux côtés) et aux modèles descriptifs de H1047.
POSITION ÉTUDIÉE : entrée 10 $ sur le favori du marché (famille « favori » de H1003 : première seconde entre 60 et 180 s écoulées où le côté favori
  a un vendeur entre 0,60 et 0,85), exécution preneur à 164 ms (sensibilité 200 / 250 / 500 ms), frais 0,07·p·(1−p), profondeur affichée.
  (La famille « avantage » de H1003 ne produit presque aucune entrée depuis l'amendement A1 ; elle n'est pas reprise.)
H1047 RÉCUPÉRATION CONTRE PERTE DÉFINITIVE : au premier instant où p_X (cerveau B) ≤ p_X d'entrée − d, d ∈ {0,10 ; 0,15 ; 0,20 ; 0,30} :
  probabilité de récupération du prix (plus tard dans le cycle, acheteur net ≥ prix payé), probabilité de victoire finale, probabilité de perte
  définitive ; comparées au milieu Polymarket, au cerveau B et à M0 (Brier, IC 90 % par cycles). Tableaux par temps restant (240–181, 180–121,
  120–61, 60–1 s) et par perte latente liquidable (0 à −2, −2 à −4, −4 à −6, < −6 $), à d = 0,15. Modèles logistiques (apprentissage) pour la
  récupération et pour la victoire : AUC contre le milieu du marché seul.
H1048 COÛT DES FAUX SAUVETAGES : décomposition des interventions de H1036 rejouées par le même moteur (R1 vente totale, R3 couverture complète,
  R4 couverture tardive, R5 moitié-moitié, contre R0 conserver) : pertes réellement évitées (cycles perdants de R0), gagnants sacrifiés (cycles
  gagnants de R0), jackpots supprimés, frais, coût d'écart, capital supplémentaire, P&L marginal contre R0 (IC 90 %).
H1049 TRAILING FONDAMENTAL (règles nouvelles, fixées ici) : marge Chainlink z_X = (moyenne finale attendue − prix à battre) / écart-type restant,
  signée dans le sens de X (modèle M0).
  F1 : tout vendre si p_X ≤ max(p_X depuis l'entrée) − 0,20 ET z_X ≤ max(z_X) − 1,0 ET z_X < 0.
  F2 : tout vendre si temps restant ≤ 120 s ET z_X ≤ −1,0.
  Trailing classique : C1 acheteur X ≤ max(acheteur X) − 0,15 ; C2 profit liquidable ≤ 70 % de son maximum (maximum ≥ 2 $).
  Comparés à H0 (conserver). IC corrigé : 4 comparaisons.
H1050 PROTECTION SÉLECTIVE : rien tant que le gain liquidable (vente de tout l'inventaire sur les acheteurs affichés, frais compris) n'atteint pas
  G ∈ {2 ; 5 ; 8} $ ; dès qu'il l'atteint : S-V vente de la quantité minimale qui garantit 0 $ dans le cas perdant ; S-A achat de l'opposé pour
  la même garantie ; S-M moitié-moitié. Comparés à H0. IC corrigé : 9 comparaisons.
MESURES : P&L net, écart avec H0 / R0 et IC 90 % par cycles (et corrigé), gagnants sacrifiés, pertes évitées, jackpots supprimés (prix d'entrée ≤ 0,25
  et cycle gagnant : rares ici puisque l'entrée est ≥ 0,60), frais, coût d'écart, capital max, fills partiels, latence 164 / 200 / 250 / 500 ms.
VERDICT : une règle n'est retenue que si l'IC corrigé de son écart avec H0 est > 0 sur le test, que la validation va dans le même sens et que
  l'écart reste > 0 à 500 ms. Sinon : abandonner.
Usage : python3 etude/bot5min/recuperation_h1047.py dossier_cycles_dublin [--controle | --confirmation]"""
import os, sys, math, time, collections
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
CONTROLE = "--controle" in sys.argv; CONFIRM = "--confirmation" in sys.argv
import liquidite_h833 as L, latence_h766 as LH, dpe_h841 as DP
import reversal_h1003 as RV
if CONFIRM: L.RESERVE = 10 ** 12
DEV_FIN, RESERVE = RV.DEV_FIN, RV.RESERVE
SORTIE = os.path.join(ICI, "resultat_recuperation_h1047" + ("_controle" if CONTROLE else "_confirmation" if CONFIRM else "") + ".md")
LATS = (164, 200, 250, 500); RNG = np.random.default_rng(1047); MISE = 10.0
meilleur, autre = DP.meilleur, RV.autre
NEWPOL = ["H0", "C1", "C2", "F1", "F2"] + [f"S-{a}-{g}" for g in (2, 5, 8) for a in ("V", "A", "M")]


def ic_cy(d, alpha=0.10, B=4000):
    d = np.asarray(d, float)
    if len(d) < 3: return (float("nan"), float("nan"))
    idx = RNG.integers(0, len(d), (B, len(d))); m = d[idx].sum(1)
    return float(np.percentile(m, 100 * alpha / 2)), float(np.percentile(m, 100 * (1 - alpha / 2)))


def jouer(pol, C):
    """nouvelles règles H1049/H1050 sur la position « favori » ; renvoie (inv, pnl) ou None sans entrée"""
    sg = RV.signal_fav(C)
    if sg is None: return None
    k0, X, p0, a0 = sg; Y = autre(X); st, E, PT, y = C["st"], C["E"], C["p"], C["y"]
    fee = RV.fee; inv = RV.Inv(); M = RV.Moteur(E, False); mem = dict(pmax=-1, zmax=-99, bmax=0)
    for k in range(k0, len(C["T"])):
        t = C["T"][k]; Lo = E.get(t)
        if Lo is None or PT[k] is None: continue
        pX = {"Up": PT[k], "Down": 1 - PT[k]}
        ask = {S: meilleur(Lo, S, "a") for S in pX}; bid = {S: meilleur(Lo, S, "b") for S in pX}
        mid = {S: ((ask[S] + bid[S]) / 2000 if ask[S] and bid[S] else None) for S in pX}
        u = {S: (ask[S] / 1000 + fee(ask[S] / 1000)) if ask[S] else None for S in pX}
        if k == k0:
            M.acheter(inv, t, X, MISE, ask[X], mid[X], "entrée"); continue
        if inv.q[X] <= 1e-9 and inv.q[Y] <= 1e-9: break
        inv.fusion(); rest = 300 - (t // 1000 - st)
        z = C["z"][k]; zX = (z if X == "Up" else -z) if z is not None else None
        Lnow = inv.cash + RV.liqval(Lo, X, inv.q[X]) + RV.liqval(Lo, Y, inv.q[Y]); inv.Lmax = max(inv.Lmax, Lnow)
        mem["pmax"] = max(mem["pmax"], pX[X]); mem["bmax"] = max(mem["bmax"], bid[X] or 0)
        if zX is not None: mem["zmax"] = max(mem["zmax"], zX)
        if mem.get("fait") or pol == "H0": continue
        sell_all = lambda tag: M.vendre(inv, t, X, inv.q[X], bid[X], mid[X], tag) > 0
        ok = False
        if pol == "C1" and bid[X] and bid[X] <= mem["bmax"] - 150: ok = sell_all("trailing billet")
        elif pol == "C2" and inv.Lmax >= 2.0 and Lnow <= 0.7 * inv.Lmax: ok = sell_all("trailing profit")
        elif pol == "F1" and zX is not None and pX[X] <= mem["pmax"] - 0.20 and zX <= mem["zmax"] - 1.0 and zX < 0: ok = sell_all("trailing fondamental")
        elif pol == "F2" and zX is not None and rest <= 120 and zX <= -1.0: ok = sell_all("marge Chainlink")
        elif pol.startswith("S-"):
            _, a, g = pol.split("-"); g = float(g)
            if Lnow >= g:
                need = 0.0 - (inv.cash + inv.q[Y])
                if need <= 1e-9: ok = True
                else:
                    if a in ("V", "M"):
                        zq = RV.qte_pour(Lo, X, need * (0.5 if a == "M" else 1.0), inv.q[X])
                        if zq: M.vendre(inv, t, X, zq[0], zq[1], mid[X], "protection sélective")
                    if a in ("A", "M"):
                        need2 = 0.0 - (inv.cash + inv.q[Y])
                        if need2 > 1e-9 and u[Y] and u[Y] < 1: M.acheter(inv, t, Y, need2 / (1 - u[Y]) * u[Y], ask[Y], mid[Y], "protection sélective")
                    ok = inv.cash + inv.q[Y] >= -1e-6
        if ok: mem["fait"] = 1
    inv.fusion()
    return inv, inv.cash + inv.q["Up"] * y + inv.q["Down"] * (1 - y)


def main():
    t_go = time.time(); o = []; w = o.append
    G, cyc = L.grille(sys.argv[1]); P = L.preparer(G); L.P_sd1 = P["sd1"]; Y = L.resultats_officiels(cyc); t0 = G["t0"]
    cycles = sorted(s for s in cyc if s in Y)
    dev = [s for s in cycles if s < DEV_FIN]; ntr = len(dev) * 2 // 3; TR, VA = dev[:ntr], dev[ntr:]
    TE = [] if CONTROLE else ([s for s in cycles if s >= RESERVE] if CONFIRM else [s for s in cycles if DEV_FIN <= s < RESERVE])
    nomT = "CONFIRMATION (≥ 13.10)" if CONFIRM else "TEST"
    part = {**{s: "apprentissage" for s in TR}, **{s: "validation" for s in VA}, **{s: nomT for s in TE}}
    w(f"# Bot95 — Récupération, faux sauvetages, trailing fondamental, protection sélective : H1047–H1050 ({'CONTRÔLE' if CONTROLE else nomT})\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. Étude séparée (le protocole figé H1003–H1046 n'est pas modifié). Cycles : "
      f"apprentissage {len(TR)}, validation {len(VA)}, {nomT.lower()} {len(TE)}. Position : 10 $ sur le favori du marché. Aucun ordre.\n")
    def tstates(st, T):
        try: return {k: DP.compact(v) for k, v in LH.Cycle(cyc[st]["f"]).etats(T).items()}
        except Exception: return {}
    def midU(Lo):
        a, b = meilleur(Lo, "Up", "a"), meilleur(Lo, "Up", "b")
        return (a + b) / 2000 if a and b and 0 < (a + b) / 2000 < 1 else None
    Xb, yb = [], []
    for st in TR:
        T = [st * 1000 + s * 1000 for s in range(10, 291, 10)]; E = tstates(st, T)
        for t in T:
            m = L.m0(G, cyc, st, 300 - (t // 1000 - st)); mu = midU(E.get(t))
            if m and mu: Xb.append([L.lg(m[0]), L.lg(min(max(mu, 0.005), 0.995))]); yb.append(Y[st])
    bB = L.ajuster(np.array(Xb), np.array(yb), 0.1)
    w(f"Cerveau B (apprentissage, {len(yb)} décisions) : logit p = {bB[0]:+.3f} + {bB[1]:.3f} × logit(M0) + {bB[2]:.3f} × logit(milieu).\n")
    def preparer(st):
        T = [st * 1000 + s * 1000 for s in range(10, 291)]
        E = tstates(st, T + [t + l for t in T for l in LATS]); p, z, mids, m0 = [], [], [], []
        for t in T:
            m = L.m0(G, cyc, st, 300 - (t // 1000 - st)); mu = midU(E.get(t))
            p.append(float(L.predire(bB, np.array([[L.lg(m[0]), L.lg(min(max(mu, 0.005), 0.995))]]))[0]) if (m and mu) else None)
            z.append(m[1] if m else None); mids.append(mu); m0.append(m[0] if m else None)
        return dict(st=st, E=E, T=T, p=p, z=z, mid=mids, m0=m0, a30=[None] * len(T), y=Y[st], ofi=[0.0] * len(T), liq=[0.0] * len(T))
    RES = collections.defaultdict(dict); EV = []
    RV.ENTREE = "favori"; RV.REC_MODEL = None; RV.STRESS = {}; RV.FEE_K = 1.0
    for st in TR + VA + TE:
        C = preparer(st); pt = part[st]
        # H1047 : événements sur la position conservée
        sg = RV.signal_fav(C)
        if sg:
            k0, X, p0, a0 = sg; Lo0 = C["E"].get(C["T"][k0]); yX = C["y"] if X == "Up" else 1 - C["y"]
            prix0 = a0 + RV.fee(a0); q0 = MISE / prix0
            for d in (0.10, 0.15, 0.20, 0.30):
                for k in range(k0 + 1, len(C["T"])):
                    pU = C["p"][k]
                    if pU is None: continue
                    pX = pU if X == "Up" else 1 - pU
                    if pX <= p0 - d:
                        Lo = C["E"].get(C["T"][k]); rest = 300 - (C["T"][k] // 1000 - st)
                        lat = RV.liqval(Lo, X, q0) - MISE if Lo else np.nan
                        rec = False
                        for k2 in range(k + 1, len(C["T"])):
                            L2 = C["E"].get(C["T"][k2]); b2 = meilleur(L2, X, "b") if L2 else None
                            if b2 and b2 / 1000 - RV.fee(b2 / 1000) >= prix0: rec = True; break
                        md = C["mid"][k]; mX = (md if X == "Up" else 1 - md) if md else None
                        m0X = (C["m0"][k] if X == "Up" else 1 - C["m0"][k]) if C["m0"][k] is not None else None
                        zz = C["z"][k]; zX = (zz if X == "Up" else -zz) if zz is not None else None
                        EV.append(dict(st=st, pt=pt, d=d, rest=rest, lat=lat, pB=pX, mid=mX, m0=m0X, z=zX, rec=rec, win=yX))
                        break
        if pt == "apprentissage": continue
        for lat in LATS:
            if pt == "validation" and lat not in (164, 500): continue
            RV.EXEC = lat
            for pol in ("R0", "R1", "R3", "R4", "R5"):
                inv, pnl = RV.simuler(pol, C, 0.10); RES[(pt, lat, pol)][st] = (pnl, inv)
            for pol in NEWPOL:
                out = jouer(pol, C)
                RES[(pt, lat, pol)][st] = (out[1], out[0]) if out else (0.0, RV.Inv())
        RV.EXEC = 164
    SPL = [(p_, S_) for p_, S_ in (("validation", VA), (nomT, TE)) if S_]
    # ------------------------------------------------ H1047
    w("## 1. H1047 — Récupération contre perte définitive (au premier instant défavorable)\n")
    w("| Échantillon | Détérioration d | Positions | Prix récupéré plus tard | Victoire finale | Perte définitive | Milieu Polymarket moyen | Cerveau B moyen | M0 moyen | Brier milieu | Brier cerveau B | Brier M0 | Cerveau B − milieu (IC 90 %) |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for pt in ["apprentissage", "validation", nomT]:
        for d in (0.10, 0.15, 0.20, 0.30):
            Z = [e for e in EV if e["pt"] == pt and e["d"] == d and e["mid"] is not None and e["m0"] is not None]
            if not Z: continue
            yv = np.array([e["win"] for e in Z]); g = np.array([e["st"] for e in Z]); pm = np.array([e["mid"] for e in Z]); pb = np.array([e["pB"] for e in Z]); p0_ = np.array([e["m0"] for e in Z])
            dd = L.brier(pb, yv) - L.brier(pm, yv); c = L.ic_g(g, dd)
            w(f"| {pt} | {d:.2f} | {len(Z)} | {100 * np.mean([e['rec'] for e in Z]):.0f} % | {100 * yv.mean():.0f} % | {100 * (1 - yv.mean()):.0f} % | {pm.mean():.3f} | {pb.mean():.3f} | "
              f"{p0_.mean():.3f} | {L.brier(pm, yv).mean():.4f} | {L.brier(pb, yv).mean():.4f} | {L.brier(p0_, yv).mean():.4f} | {dd.mean():+.4f} [{c[0]:+.4f} ; {c[1]:+.4f}] |")
    w("\n**Par temps restant et perte latente liquidable (d = 0,15, toutes périodes hors apprentissage)** — récupération du prix / victoire finale / milieu moyen (n)\n")
    RB = ((181, 240), (121, 180), (61, 120), (1, 60)); LB = ((-2, 0.01), (-4, -2), (-6, -4), (-99, -6))
    w("| Temps restant | " + " | ".join(f"perte {a:+.0f} à {b:+.0f} $" if a > -99 else "perte < −6 $" for a, b in LB) + " |\n|---|" + "---|" * len(LB))
    Z15 = [e for e in EV if e["d"] == 0.15 and e["pt"] != "apprentissage" and e["mid"] is not None]
    for a, b in RB:
        cells = []
        for la, lb in LB:
            Z = [e for e in Z15 if a <= e["rest"] <= b and la <= e["lat"] < lb]
            cells.append(f"{100 * np.mean([e['rec'] for e in Z]):.0f} % / {100 * np.mean([e['win'] for e in Z]):.0f} % / {np.mean([e['mid'] for e in Z]):.2f} ({len(Z)})" if Z else "—")
        w(f"| {a}–{b} s | " + " | ".join(cells) + " |")
    w("\n**Modèles (apprentissage) : AUC contre le milieu du marché seul**\n")
    w("| Cible | Échantillon | AUC milieu seul | AUC modèle (cerveau B, milieu, z Chainlink, temps restant, perte latente) |\n|---|---|---|---|")
    fx = lambda e: [L.lg(min(max(e["pB"], 0.005), 0.995)), L.lg(min(max(e["mid"], 0.005), 0.995)), e["z"] or 0.0, e["rest"] / 300, (e["lat"] if np.isfinite(e["lat"]) else 0) / 10]
    Ztr = [e for e in EV if e["pt"] == "apprentissage" and e["mid"] is not None]
    for cible in ("rec", "win"):
        if len(Ztr) < 30: break
        X_ = np.array([fx(e) for e in Ztr]); y_ = np.array([float(e[cible]) for e in Ztr]); mu, sd = X_.mean(0), X_.std(0) + 1e-9; b = L.ajuster((X_ - mu) / sd, y_, 2.0)
        for pt, _ in SPL:
            Z = [e for e in EV if e["pt"] == pt and e["mid"] is not None]
            if not Z: continue
            yy = np.array([float(e[cible]) for e in Z]); pr = L.predire(b, (np.array([fx(e) for e in Z]) - mu) / sd)
            w(f"| {'récupération du prix' if cible == 'rec' else 'victoire finale'} | {pt} | {L.auc(np.array([e['mid'] for e in Z]), yy):.3f} | {L.auc(pr, yy):.3f} |")
    # ------------------------------------------------ H1048
    w("\n## 2. H1048 — Coût des faux sauvetages (interventions H1036 contre R0, 164 ms)\n")
    for pt, S_ in SPL:
        w(f"### {pt} ({len(S_)} cycles)\n")
        w("| Intervention | Pertes évitées ($, cycles perdants de R0) | Gagnants sacrifiés ($, cycles gagnants de R0) | Cycles gagnants abîmés | Jackpots supprimés | Frais en plus ($) | Coût d'écart en plus ($) | Capital supplémentaire moyen ($) | P&L − R0 ($) | IC 90 % |\n|---|---|---|---|---|---|---|---|---|---|")
        R0 = RES[(pt, 164, "R0")]
        for pol, lab in (("R1", "R1 vente totale"), ("R3", "R3 couverture complète"), ("R4", "R4 couverture tardive"), ("R5", "R5 moitié-moitié")):
            Rp = RES[(pt, 164, pol)]; d = np.array([Rp[s][0] - R0[s][0] for s in S_])
            perd = [s for s in S_ if R0[s][0] < 0]; gagn = [s for s in S_ if R0[s][0] > 0]
            ev = sum(max(Rp[s][0] - R0[s][0], 0) for s in perd); sac = sum(max(R0[s][0] - Rp[s][0], 0) for s in gagn)
            jk = sum(1 for s in gagn if R0[s][1].prix0 is not None and R0[s][1].prix0 <= 0.25 and Rp[s][0] < 0.5 * R0[s][0])
            c = ic_cy(d)
            w(f"| {lab} | {ev:+.0f} | {-sac:+.0f} | {sum(1 for s in gagn if Rp[s][0] < R0[s][0] - 1e-6)} / {len(gagn)} | {jk} | {sum(Rp[s][1].frais - R0[s][1].frais for s in S_):+.1f} | "
              f"{sum(Rp[s][1].ecart - R0[s][1].ecart for s in S_):+.1f} | {np.mean([Rp[s][1].maxcap - R0[s][1].maxcap for s in S_]):+.2f} | {d.sum():+.0f} | [{c[0]:+.0f} ; {c[1]:+.0f}] |")
        w("")
    # ------------------------------------------------ H1049 / H1050
    def tab(titre, pols, ncomp):
        w(f"## {titre}\n")
        for pt, S_ in SPL:
            H = RES[(pt, 164, "H0")]
            w(f"### {pt} ({len(S_)} cycles)\n")
            w(f"| Règle | Cycles où elle a agi | P&L net ($) | Cycles gagnants | Perte max | Gagnants sacrifiés ($) | Pertes évitées ($) | Frais ($) | Fills partiels | Capital max | P&L − H0 ($) | IC 90 % | IC corrigé ({ncomp}) | 500 ms : P&L − H0 |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
            for pol in pols:
                Rp = RES[(pt, 164, pol)]; v = np.array([Rp[s][0] for s in S_]); d = v - np.array([H[s][0] for s in S_])
                agi = sum(1 for s in S_ if Rp[s][1].nv > 0 or Rp[s][1].na > 1)
                sac = sum(max(H[s][0] - Rp[s][0], 0) for s in S_ if H[s][0] > 0); ev = sum(max(Rp[s][0] - H[s][0], 0) for s in S_ if H[s][0] < 0)
                c1 = ic_cy(d) if pol != "H0" else (np.nan, np.nan); c2 = ic_cy(d, 0.10 / ncomp) if pol != "H0" else (np.nan, np.nan)
                d5 = sum(RES[(pt, 500, pol)][s][0] - RES[(pt, 500, "H0")][s][0] for s in S_) if (pt, 500, pol) in RES else float("nan")
                w(f"| {pol} | {agi} | {v.sum():+.0f} | {int((v > 0).sum())} | {v.min():+.1f} | {-sac:+.0f} | {ev:+.0f} | {sum(Rp[s][1].frais for s in S_):.1f} | "
                  f"{sum(Rp[s][1].partiel for s in S_)} | {max(Rp[s][1].maxcap for s in S_):.0f} | {d.sum():+.0f} | [{c1[0]:+.0f} ; {c1[1]:+.0f}] | [{c2[0]:+.0f} ; {c2[1]:+.0f}] | {d5:+.0f} |")
            w("")
    tab("3. H1049 — Trailing fondamental contre trailing classique et conservation (164 ms)", ["H0", "C1", "C2", "F1", "F2"], 4)
    tab("4. H1050 — Protection sélective après un gain réellement liquidable (164 ms)", ["H0"] + [p for p in NEWPOL if p.startswith("S-")], 9)
    if TE:
        w(f"## 5. Latence ({nomT}) : P&L − H0 ($)\n\n| Règle | " + " | ".join(f"{l} ms" for l in LATS) + " |\n|---|" + "---|" * len(LATS))
        for pol in NEWPOL[1:]:
            w(f"| {pol} | " + " | ".join(f"{sum(RES[(nomT, l, pol)][s][0] - RES[(nomT, l, 'H0')][s][0] for s in TE):+.0f}" for l in LATS) + " |")
        w(f"\n## 6. Verdict ({nomT})\n\n| Règle | IC corrigé > 0 | Validation même sens | > 0 à 500 ms | Verdict |\n|---|---|---|---|---|")
        for pol in NEWPOL[1:]:
            nc = 4 if pol[0] in "CF" else 9
            d = np.array([RES[(nomT, 164, pol)][s][0] - RES[(nomT, 164, "H0")][s][0] for s in TE]); c2 = ic_cy(d, 0.10 / nc)
            cv = (sum(RES[("validation", 164, pol)][s][0] - RES[("validation", 164, "H0")][s][0] for s in VA) > 0) if VA else None
            c5 = sum(RES[(nomT, 500, pol)][s][0] - RES[(nomT, 500, "H0")][s][0] for s in TE) > 0
            ok = c2[0] > 0 and cv is not False and c5; yn = lambda b: "—" if b is None else ("oui" if b else "non")
            w(f"| {pol} | {yn(c2[0] > 0)} | {yn(cv)} | {yn(c5)} | {'**poursuivre**' if ok else 'abandonner'} |")
    w("\n## Limites\n- Exécution preneur ; peu de cycles ; une seule famille d'entrée (favori) ; règles H1049/H1050 fixées a priori, sans réglage.\n")
    w(f"_Calcul : {time.time() - t_go:.0f} s._\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
