"""BOT95 — TRAILING SUR LES ACHATS TRÈS BAS ET LES STRATÉGIES DES PREMIERS JOURS : H1051 (Pitch, 12.10.2026 18:40 : « Trailing à faire aussi
les tests sur les achats très très bas aussi. Les stratégies des premiers jours »). ÉTUDE SÉPARÉE, PRÉ-ENREGISTRÉE (ce fichier tel que committé
avant le calcul du test). Ne modifie ni H1003–H1046 ni H1047–H1050 ; réutilise seulement leur moteur d'exécution en lecture. Hors ligne ;
aucun ordre ; aucun bot actif, H816, H821, R4 ni fantôme modifié.

PÉRIODES (celles de H1003) : apprentissage = 2/3 premiers cycles avant le 12.10 12:00 UTC (sert seulement au cerveau B de F1), validation = 1/3
  suivant ; test = 12.10 12:00 → 13.10 00:00 UTC, calculé une seule fois ; --confirmation = cycles ≥ 13.10 00:00 UTC.
ENTRÉES (10 $ chacune, exécution preneur à 164 ms sur le carnet enregistré, limitée au prix vu, profondeur affichée, frais 0,07·p·(1−p)) :
  Stratégies des premiers jours = les signaux réellement émis par les fantômes de Dublin (champ « sig » des cycles) : « desaccord 30 »,
  « desaccord 20 60-180 s », « V2-F ecart qui grandit », « V2-F incertitude 0,01 % », « cohorte B : V2-F corrige 0,015 % » ; premier signal
  de chaque stratégie par cycle ; achat à la seconde qui suit la décision, prix limite = prix vu par le fantôme (a0).
  Achats très bas génériques : première seconde avec 60 à 240 s restantes et carnet à deux côtés où un côté a un vendeur entre 0,01 et 0,10
  (« ≤ 0,10 ») ; idem entre 0,11 et 0,25 (« 0,11–0,25 »).
RÈGLES DE SORTIE (fixées ici, aucun réglage) :
  H0 conserver jusqu'au règlement.
  TP2 / TP3 / TP5 : tout vendre dès que l'acheteur net de frais ≥ 2 / 3 / 5 × le prix payé.
  FR (free-roll) : vendre la quantité minimale qui récupère la mise de 10 $ dès que la profondeur le permet ; garder le reste.
  TR30 / TR50 : trailing sur le profit liquidable (vente de tout sur les acheteurs affichés, frais compris), activé quand ce profit a atteint
       ≥ 5 $ ; tout vendre quand il retombe de 30 % / 50 % sous son maximum.
  TB : trailing sur le billet : activé quand l'acheteur a atteint ≥ 2 × le prix payé ; tout vendre si l'acheteur retombe à ≤ 50 % de son maximum.
  F1 : trailing fondamental (H1049) : p de règlement ≤ son maximum − 0,20 ET marge Chainlink z ≤ son maximum − 1,0 ET z < 0 → tout vendre.
  F2 : temps restant ≤ 120 s ET z ≤ −1,0 → tout vendre.
  SV5 / SV10 : dès que le profit liquidable atteint 5 / 10 $, vendre la quantité minimale qui garantit 0 $ dans le cas perdant.
MESURES par famille d'entrée : P&L net, écart avec H0 (IC 90 % par cycles, IC corrigé pour 11 comparaisons), cycles gagnants, jackpots (cycles où
  H0 gagne ≥ 4 × la mise) conservés ou supprimés, gagnants sacrifiés, pertes évitées, profit latent maximal, fills partiels, frais, 500 ms.
VERDICT : une règle n'est retenue pour une famille que si l'IC corrigé de l'écart avec H0 est > 0 sur le test, que la validation va dans le même sens
  et que l'écart reste > 0 à 500 ms. Sinon : abandonner.
Usage : python3 etude/bot5min/trailing_bas_h1051.py dossier_cycles_dublin [--controle | --confirmation]"""
import os, sys, math, time, json, gzip, collections
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, ICI)
CONTROLE = "--controle" in sys.argv; CONFIRM = "--confirmation" in sys.argv
import liquidite_h833 as L, latence_h766 as LH, dpe_h841 as DP
import reversal_h1003 as RV
if CONFIRM: L.RESERVE = 10 ** 12
DEV_FIN, RESERVE = RV.DEV_FIN, RV.RESERVE
SORTIE = os.path.join(ICI, "resultat_trailing_bas_h1051" + ("_controle" if CONTROLE else "_confirmation" if CONFIRM else "") + ".md")
LATS = (164, 500); RNG = np.random.default_rng(1051); MISE = 10.0; NCOMP = 11
meilleur, autre = DP.meilleur, RV.autre
STRATS = ["desaccord 30", "desaccord 20 60-180 s", "V2-F ecart qui grandit", "V2-F incertitude 0,01 %", "cohorte B : V2-F corrige 0,015 %"]
FAMS = STRATS + ["très bas ≤ 0,10", "bas 0,11–0,25"]
REGLES = ["H0", "TP2", "TP3", "TP5", "FR", "TR30", "TR50", "TB", "F1", "F2", "SV5", "SV10"]


def ic_cy(d, alpha=0.10, B=4000):
    d = np.asarray(d, float)
    if len(d) < 3: return (float("nan"), float("nan"))
    idx = RNG.integers(0, len(d), (B, len(d))); m = d[idx].sum(1)
    return float(np.percentile(m, 100 * alpha / 2)), float(np.percentile(m, 100 * (1 - alpha / 2)))


def entree_bas(C, lo, hi):
    for k, t in enumerate(C["T"]):
        Lo = C["E"].get(t); rest = 300 - (t // 1000 - C["st"])
        if Lo is None or not (60 <= rest <= 240): continue
        if not (meilleur(Lo, "Up", "a") and meilleur(Lo, "Up", "b")): continue
        for X in ("Up", "Down"):
            a = meilleur(Lo, X, "a")
            if a and lo <= a <= hi: return k, X, a
    return None


def jouer(regle, C, k0, X, lim):
    st, E, PT, y = C["st"], C["E"], C["p"], C["y"]; Y = autre(X); fee = RV.fee
    inv = RV.Inv(); M = RV.Moteur(E, False); mem = dict(pmax=-1, zmax=-99, bmax=0)
    for k in range(k0, len(C["T"])):
        t = C["T"][k]; Lo = E.get(t)
        if Lo is None: continue
        bid = meilleur(Lo, X, "b"); midX = None
        a_, b_ = meilleur(Lo, X, "a"), bid
        if a_ and b_: midX = (a_ + b_) / 2000
        if k == k0:
            if M.acheter(inv, t, X, MISE, lim, midX, "entrée") <= 0: return None
            mem["prix"] = -inv.cash / inv.q[X]; continue
        if inv.q[X] <= 1e-9: break
        rest = 300 - (t // 1000 - st); bn = (bid / 1000 - fee(bid / 1000)) if bid else None
        Lnow = inv.cash + RV.liqval(Lo, X, inv.q[X]) + RV.liqval(Lo, Y, inv.q[Y]); inv.Lmax = max(inv.Lmax, Lnow)
        mem["bmax"] = max(mem["bmax"], bid or 0)
        pX = (PT[k] if X == "Up" else 1 - PT[k]) if PT[k] is not None else None
        z = C["z"][k]; zX = (z if X == "Up" else -z) if z is not None else None
        if pX is not None: mem["pmax"] = max(mem["pmax"], pX)
        if zX is not None: mem["zmax"] = max(mem["zmax"], zX)
        if mem.get("fait") or regle == "H0": continue
        tout = lambda tag: M.vendre(inv, t, X, inv.q[X], bid, midX, tag) > 0
        ok = False
        if regle in ("TP2", "TP3", "TP5") and bn and bn >= int(regle[2]) * mem["prix"]: ok = tout("prise de gain")
        elif regle == "FR":
            need = -inv.cash                                                      # récupérer la mise : cash net ≥ 0
            if need <= 1e-9: ok = True
            else:
                zq = RV.qte_pour(Lo, X, need, inv.q[X])
                if zq: M.vendre(inv, t, X, zq[0], zq[1], midX, "free-roll"); ok = inv.cash >= -1e-6
        elif regle in ("TR30", "TR50") and inv.Lmax >= 5.0 and Lnow <= (1 - int(regle[2:]) / 100) * inv.Lmax: ok = tout("trailing profit")
        elif regle == "TB" and mem["bmax"] / 1000 >= 2 * mem["prix"] and bid and bid <= 0.5 * mem["bmax"]: ok = tout("trailing billet")
        elif regle == "F1" and pX is not None and zX is not None and pX <= mem["pmax"] - 0.20 and zX <= mem["zmax"] - 1.0 and zX < 0: ok = tout("trailing fondamental")
        elif regle == "F2" and zX is not None and rest <= 120 and zX <= -1.0: ok = tout("marge Chainlink")
        elif regle in ("SV5", "SV10") and Lnow >= float(regle[2:]):
            need = -(inv.cash + inv.q[Y])
            if need <= 1e-9: ok = True
            else:
                zq = RV.qte_pour(Lo, X, need, inv.q[X])
                if zq: M.vendre(inv, t, X, zq[0], zq[1], midX, "protection"); ok = inv.cash + inv.q[Y] >= -1e-6
        if ok: mem["fait"] = 1
    inv.fusion()
    return inv, inv.cash + inv.q["Up"] * y + inv.q["Down"] * (1 - y)


def main():
    t_go = time.time(); o = []; w = o.append
    G, cyc = L.grille(sys.argv[1]); P = L.preparer(G); L.P_sd1 = P["sd1"]; Y = L.resultats_officiels(cyc)
    cycles = sorted(s for s in cyc if s in Y)
    dev = [s for s in cycles if s < DEV_FIN]; ntr = len(dev) * 2 // 3; TR, VA = dev[:ntr], dev[ntr:]
    TE = [] if CONTROLE else ([s for s in cycles if s >= RESERVE] if CONFIRM else [s for s in cycles if DEV_FIN <= s < RESERVE])
    nomT = "CONFIRMATION (≥ 13.10)" if CONFIRM else "TEST"
    part = {**{s: "apprentissage" for s in TR}, **{s: "validation" for s in VA}, **{s: nomT for s in TE}}
    w(f"# Bot95 — Trailing sur les achats très bas et les stratégies des premiers jours : H1051 ({'CONTRÔLE' if CONTROLE else nomT})\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. Étude séparée. Cycles : apprentissage {len(TR)}, validation {len(VA)}, "
      f"{nomT.lower()} {len(TE)}. Mise 10 $ par entrée. Aucun ordre.\n")
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
    RV.STRESS = {}; RV.FEE_K = 1.0
    RES = collections.defaultdict(dict)                                           # (famille, part, latence, règle) -> {(st): (pnl, inv)}
    for st in VA + TE:
        pt = part[st]
        T = [st * 1000 + s * 1000 for s in range(10, 291)]
        E = tstates(st, T + [t + l for t in T for l in LATS]); p, z = [], []
        for t in T:
            m = L.m0(G, cyc, st, 300 - (t // 1000 - st)); mu = midU(E.get(t))
            p.append(float(L.predire(bB, np.array([[L.lg(m[0]), L.lg(min(max(mu, 0.005), 0.995))]]))[0]) if (m and mu) else None)
            z.append(m[1] if m else None)
        C = dict(st=st, E=E, T=T, p=p, z=z, y=Y[st])
        ent = {}
        try: R = json.load(gzip.open(cyc[st]["f"]))
        except Exception: R = {}
        for s_ in R.get("sig", []):
            if not isinstance(s_, dict) or s_.get("nom") not in STRATS or s_["nom"] in ent: continue
            k = int(math.ceil(s_["tDecision"] / 1000 - st)) - 10
            if 0 <= k < len(T) and s_.get("a0"): ent[s_["nom"]] = (k, s_["cote"], int(round(s_["a0"] * 1000)))
        for fam, (lo, hi) in (("très bas ≤ 0,10", (10, 100)), ("bas 0,11–0,25", (110, 250))):
            e_ = entree_bas(C, lo, hi)
            if e_: ent[fam] = e_
        for fam, (k0, X, lim) in ent.items():
            for lat in LATS:
                RV.EXEC = lat
                for rg in REGLES:
                    out = jouer(rg, C, k0, X, lim)
                    if out: RES[(fam, pt, lat, rg)][st] = (out[1], out[0])
        RV.EXEC = 164
    SPL = [(p_, S_) for p_, S_ in (("validation", VA), (nomT, TE)) if S_]
    w("Règles : H0 conserver ; TP2/TP3/TP5 prise de gain à 2/3/5 × le prix payé ; FR free-roll (mise récupérée) ; TR30/TR50 trailing sur le profit "
      "liquidable (activé à ≥ 5 $) ; TB trailing sur le billet (activé à 2 × le prix, sortie à 50 % du maximum) ; F1 trailing fondamental ; F2 marge "
      "Chainlink ; SV5/SV10 verrou de 0 $ dès 5 / 10 $ de profit liquidable.\n")
    for fam in FAMS:
        w(f"## {fam}\n")
        for pt, S_ in SPL:
            H = RES.get((fam, pt, 164, "H0"), {}); sts = sorted(H)
            if not sts: w(f"_{pt} : aucune entrée._\n"); continue
            jk = [s for s in sts if H[s][0] >= 4 * MISE]
            w(f"### {pt} — {len(sts)} entrées, prix payé moyen {np.mean([H[s][1].prix0 or 0 for s in sts]):.3f}, "
              f"{int(sum(H[s][0] > 0 for s in sts))} gagnantes, jackpots (≥ 4 × la mise) {len(jk)}, profit latent maximal moyen {np.mean([H[s][1].Lmax for s in sts]):+.2f} $\n")
            w(f"| Règle | P&L net ($) | Cycles gagnants | Jackpots conservés | Gagnants sacrifiés ($) | Pertes évitées ($) | Frais ($) | Fills partiels | P&L − H0 ($) | IC 90 % | IC corrigé ({NCOMP}) | 500 ms : P&L − H0 |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
            for rg in REGLES:
                Rr = RES.get((fam, pt, 164, rg), {})
                v = np.array([Rr[s][0] if s in Rr else H[s][0] for s in sts]); d = v - np.array([H[s][0] for s in sts])
                c1 = ic_cy(d) if rg != "H0" else (np.nan, np.nan); c2 = ic_cy(d, 0.10 / NCOMP) if rg != "H0" else (np.nan, np.nan)
                kept = sum(1 for s in jk if s in Rr and Rr[s][0] >= 0.5 * H[s][0])
                sac = sum(max(H[s][0] - v[i], 0) for i, s in enumerate(sts) if H[s][0] > 0); ev = sum(max(v[i] - H[s][0], 0) for i, s in enumerate(sts) if H[s][0] < 0)
                R5, H5 = RES.get((fam, pt, 500, rg), {}), RES.get((fam, pt, 500, "H0"), {})
                d5 = sum(R5[s][0] - H5[s][0] for s in R5 if s in H5)
                w(f"| {rg} | {v.sum():+.0f} | {int((v > 0).sum())} | {kept} / {len(jk)} | {-sac:+.0f} | {ev:+.0f} | {sum(Rr[s][1].frais for s in Rr):.1f} | "
                  f"{sum(Rr[s][1].partiel for s in Rr)} | {d.sum():+.0f} | [{c1[0]:+.0f} ; {c1[1]:+.0f}] | [{c2[0]:+.0f} ; {c2[1]:+.0f}] | {d5:+.0f} |")
            w("")
        if TE:
            w(f"**Verdict ({fam}, {nomT})** : " + ", ".join(
                f"{rg} {'retenue' if verdict else 'abandon'}" for rg, verdict in
                ((rg, (lambda H, Rr, sts: (ic_cy(np.array([(Rr[s][0] if s in Rr else H[s][0]) - H[s][0] for s in sts]), 0.10 / NCOMP)[0] > 0) if sts else False)(
                    RES.get((fam, nomT, 164, "H0"), {}), RES.get((fam, nomT, 164, rg), {}), sorted(RES.get((fam, nomT, 164, "H0"), {})))
                  and (sum(RES.get((fam, "validation", 164, rg), {}).get(s, (0,))[0] - RES.get((fam, "validation", 164, "H0"), {}).get(s, (0,))[0]
                           for s in RES.get((fam, "validation", 164, "H0"), {})) > 0)
                  and (sum(RES.get((fam, nomT, 500, rg), {}).get(s, (0,))[0] - v_[0] for s, v_ in RES.get((fam, nomT, 500, "H0"), {}).items()) > 0))
                 for rg in REGLES[1:])) + ".\n")
    w("\n## Limites\n- Entrée des stratégies à la seconde qui suit la décision du fantôme (jusqu'à 1 s plus tard que le fantôme réel).\n"
      "- Exécution preneur seulement ; peu d'entrées par famille ; règles fixées a priori.\n")
    w(f"_Calcul : {time.time() - t_go:.0f} s._\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
