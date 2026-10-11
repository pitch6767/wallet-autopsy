"""BOT95 HEDGE LAB V1 — suite « paires rentables » (demande de Pitch, 11.10.2026). Hors ligne, aucune modification du bot.
Réutilise tout le moteur de hedge_lab.py (mêmes entrées, mêmes scénarios, mêmes statistiques), ajoute H25 (Early Conversion Scanner)
et H26 (Jackpot Preservation Optimizer), répond aux questions 1-8 et à l'audit des données live.
Usage : python3 etude/bot5min/hedge_lab_paires.py → etude/bot5min/resultat_hedge_lab_paires.md"""
exec(open("etude/bot5min/hedge_lab.py").read().split("# ================================================================ rédaction")[0])
for c_ in COH:
    for s_ in COH[c_].values(): s_["coh"] = c_
CP = ("A", "B")
FR = (0.25, 0.5, 0.75, 1.0)
pf = lambda f: f"{int(round(100 * f))} %"

# ================================================================ H25 / H26 et ventes miroirs
def mk25(f, mode, vente=False):
    def H(p):
        c = p.cand(p.pcost() < 1)                 # paire STRICTEMENT rentable tous frais compris : a + frais(a) + vendeur opposé + frais < 1
        if not len(c): return
        p.mark(int(c[0])); rows = c[:1] if mode == "premier" else c
        if vente: p.loop(rows, "own", "sell", lambda: f * p.q0 - p.sell_q)
        else: p.loop(rows, "opp", "buy", lambda: f * p.q0 - p.qp)
    return H
V25 = []
for f in FR:
    for mode in ("premier", "continu"):
        n = f"H25 {pf(f)} {mode}"; HEDGES[n] = mk25(f, mode); V25.append(n)
        HEDGES[f"VENTE {pf(f)} {mode}"] = mk25(f, mode, vente=True)
F26 = {}
def H26(p): mk25(F26[p.sig["coh"]], "continu")(p)
HEDGES["H26"] = H26
G26 = {}
for coh in CP:                                     # fraction figée sur l'apprentissage (prudent, 50 $ indépendants), parmi 25 / 50 / 75 %
    G26[coh] = {}
    for f in (0.25, 0.5, 0.75):
        tot = 0.0
        for st, s in COH[coh].items():
            if PER(st) != "apprentissage": continue
            p = Pos(st, s, "prudent")
            if p.ok: mk25(f, "continu")(p); tot += p.pnl()
        G26[coh][f] = tot
    F26[coh] = max(G26[coh], key=lambda f: G26[coh][f])
HEDGES["VENTE H26"] = lambda p: mk25(F26[p.sig["coh"]], "continu", vente=True)(p)
print("H26 fractions", F26, G26, flush=True)

NEW = V25 + ["H26"]
NEWS = [f"VENTE {pf(f)} {m}" for f in FR for m in ("premier", "continu")] + ["VENTE H26"]
for coh in CP:
    for sc in SCN:
        for pol in NEW + NEWS: RI[(coh, sc, pol)] = run_indep(coh, sc, pol)
        for per in PERS:
            for pol in NEW + NEWS:
                r_, a_, b_ = run_cap(coh, sc, pol, per); RC[(coh, sc, pol, per)] = r_; NRC[(coh, sc, pol, per)] = (a_, b_)
            Rh = RC[(coh, sc, "HOLD", per)]
            for pol in NEW + NEWS:
                ST[("cap", coh, sc, pol, per)] = stats(RC[(coh, sc, pol, per)], Rh, per)
                ST[("ind", coh, sc, pol, per)] = stats(RI[(coh, sc, pol)], RI[(coh, sc, "HOLD")], per)
print("H25/H26 simulés", f"{_time.time() - _T0:.0f} s", flush=True)
VMAP = {**{f"H25 {pf(f)} {m}": f"VENTE {pf(f)} {m}" for f in FR for m in ("premier", "continu")}, "H26": "VENTE H26"}

# ================================================================ Q1 / Q2 / Q7 : moments, quantités, fenêtres
def pos_list(coh, sc, per=None):
    for st in sorted(COH[coh]):
        if per and PER(st) != per: continue
        p = Pos(st, COH[coh][st], sc)
        if p.ok: yield p
Q1 = {}
for coh in CP:
    for sc in SCN:
        for per in PERS:
            n = ng = nm = nf = 0; rows = rg = rm = rf = 0; mis_g = mis_f = 0; mar_all, mar_first, mmar_first = [], [], []
            for p in pos_list(coh, sc, per):
                n += 1; a = p.a; pa = p.v["pa"][p.je + 1:p.kend]; ob = p.v["ob"][p.je + 1:p.kend]
                ok_ = np.isfinite(pa) & np.isfinite(ob); pa, ob = pa[ok_], ob[ok_]
                g = a + pa < 1 - 1e-9; m = a + pa + FEEV(pa) < 1 - 1e-9; fu = a + FEE(a) + pa + FEEV(pa) < 1 - 1e-9
                rows += len(pa); rg += int(g.sum()); rm += int(m.sum()); rf += int(fu.sum())
                ng += bool(g.any()); nm += bool(m.any()); nf += bool(fu.any())
                mis_g += int((g != (ob > a + 1e-9)).sum()); mis_f += int((fu != (ob - FEEV(ob) > a + FEE(a) + 1e-9)).sum())
                if fu.any():
                    mg = 100 * (1 - a - FEE(a) - pa[fu] - FEEV(pa[fu])); mar_all.append(mg); mar_first.append(mg[0])
                    mmar_first.append(100 * (1 - a - pa[fu][0] - FEE(pa[fu][0])))
            Q1[(coh, sc, per)] = dict(n=n, ng=ng, nm=nm, nf=nf, rows=rows, rg=rg, rm=rm, rf=rf, mis_g=mis_g, mis_f=mis_f,
                                      mall=np.concatenate(mar_all) if mar_all else np.zeros(0), mfirst=np.array(mar_first), mmfirst=np.array(mmar_first))
# Q2 : quantité appariable au meilleur niveau, au premier moment éligible
Q2 = {}
for coh in CP:
    for sc in ("prudent", "pessimiste"):
        R = []
        for p in pos_list(coh, sc):
            c = p.cand(p.pcost() < 1)
            if not len(c): continue
            k = int(c[0]); j = p.row(k)
            if j is None: R.append(0.0); continue
            ok_ = p.v["pa"][j] <= p.v["pa"][k] + 1e-9
            R.append((p.v["paz"][j] * p.qf / p.q0) if ok_ else 0.0)
        cov = [r["cov"] for r in RI[(coh, sc, "H25 100 % continu")].values() if r["ok"] and r["att"]]
        Q2[(coh, sc)] = (np.array(R), np.array(cov))
# Q7 : durée des fenêtres de paire rentable (lignes 0,3 s et photos 100 ms), entrées du scénario prudent
Q7 = {}
for coh in CP:
    dur_s, dur_r, st03, st06, fi03, fi06 = [], [], 0, 0, 0, 0
    l_dur, l03, l06, lf03, lf06 = [], 0, 0, 0, 0
    for p in pos_list(coh, "prudent"):
        T = p.T; ks = np.arange(p.je + 1, p.kend); pa = p.v["pa"]
        if not len(ks): continue
        cr = p.a + FEE(p.a) + pa + FEEV(pa) < 1 - 1e-9; cr = cr & np.isfinite(pa)
        k = p.je + 1
        while k < p.kend:
            if not cr[k]: k += 1; continue
            e = k
            while e + 1 < p.kend and cr[e + 1]: e += 1
            dur_r.append(e - k + 1); dur_s.append((T[e + 1] if e + 1 < len(T) else T[e] + 0.3) - T[k])
            for d, nm in ((0.3, "03"), (0.6, "06")):
                j = int(ge(T, T[k] + d))
                still = j < len(T) and bool(cr[j]); fil = still and pa[j] <= pa[k] + 1e-9
                if nm == "03": st03 += still; fi03 += fil
                else: st06 += still; fi06 += fil
            k = e + 1
        if p.st in LEAD:                                # photos 100 ms
            up_opp = not p.sig["up"]; t0 = T[p.je]
            L_ = [(t_, (x[0] if up_opp else x[1])) for t_, x in LEAD[p.st] if t0 < t_ < p.end - 1]
            L_ = [(t_, a_[0][0]) for t_, a_ in L_ if a_]
            if len(L_) < 3: continue
            lt = np.array([x[0] for x in L_]); lo = np.array([x[1] for x in L_])
            lc = p.a + FEE(p.a) + lo + FEEV(lo) < 1 - 1e-9
            seg = np.concatenate([[0], np.cumsum(np.diff(lt) > 0.25)])
            i = 0
            while i < len(lt):
                if not lc[i]: i += 1; continue
                e = i
                while e + 1 < len(lt) and lc[e + 1] and seg[e + 1] == seg[i]: e += 1
                inner = i > 0 and seg[i - 1] == seg[i] and e + 1 < len(lt) and seg[e + 1] == seg[i]
                if inner:
                    l_dur.append(lt[e + 1] - lt[i])
                    for d, nm in ((0.3, "03"), (0.6, "06")):
                        j = int(np.searchsorted(lt, lt[i] + d))
                        still = j < len(lt) and seg[j] == seg[i] and bool(lc[j]); fil = still and lo[j] <= lo[i] + 1e-9
                        if nm == "03": l03 += still; lf03 += fil
                        else: l06 += still; lf06 += fil
                i = e + 1
    Q7[coh] = dict(n=len(dur_s), ds=np.array(dur_s), dr=np.array(dur_r), st03=st03, st06=st06, fi03=fi03, fi06=fi06,
                   ln=len(l_dur), ld=np.array(l_dur), l03=l03, l06=l06, lf03=lf03, lf06=lf06)
print("questions 1, 2, 7", f"{_time.time() - _T0:.0f} s", flush=True)

# ================================================================ rédaction
q = lambda x, v: f2(np.percentile(x, v)) if len(x) else "—"
def dci(s): return f"{f0(s['d'])} [{f0(s['lo'])} ; {f0(s['hi'])}]"
out = ["# BOT95 HEDGE LAB — paires rentables, H25 / H26, contribution marginale et audit live", "",
       f"Étude hors ligne du {_time.strftime('%d.%m.%Y')} — aucun bot, aucun workflow modifié, rien publié. Complète resultat_hedge_lab.md (mêmes entrées A et B, mêmes scénarios, mêmes périodes : "
       f"apprentissage < {hs(CUT)} · validation → {hs(MATIN0)} · test inédit après). Δ = P&L avec la couverture − P&L en gardant, sur les MÊMES positions, frais compris ; IC 90 % par blocs d'une heure. "
       "Sauf mention : version « 50 $ indépendants » (le portefeuille de 250 $ est ruiné par GARDER en prudent, voir question 6).", ""]
VERD = len(out)

# ---- Q1
out += ["## 1. Moments où Up + Down coûte < 1 $ — combien restent rentables après TOUS les frais ?", "",
        "Pour chaque position (entrée du scénario), chaque ligne 0,3 s après l'entrée et ≥ 1 s avant la fin. Trois critères : "
        "**brut** a + vendeur opposé < 1 ; **marginal** a + vendeur opposé + frais preneur de l'achat opposé < 1 (frais d'entrée déjà payés, ignorés pour la décision) ; "
        "**tous frais** a + frais(a) + vendeur opposé + frais < 1 (ce qui compte dans le P&L total). a = prix d'entrée payé.", "",
        "| Cohorte | Scénario | Période | Positions | avec ≥ 1 moment brut | marginal | tous frais | Lignes | lignes brut | marginal | tous frais | Écarts à « acheteur de notre côté > a » | Écarts à « acheteur − frais > a + frais(a) » |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for coh in CP:
    for sc in SCN:
        for per in PERS:
            x = Q1[(coh, sc, per)]
            out.append(f"| {coh} | {sc} | {per} | {x['n']} | {x['ng']} | {x['nm']} | **{x['nf']}** ({pc(x['nf'] / max(1, x['n']))}) | {x['rows']} | {x['rg']} | {x['rm']} | **{x['rf']}** | {x['mis_g']} | {x['mis_f']} |")
out += ["", "**Équivalence miroir** : vendeur opposé = 1 − acheteur de notre côté (même taille) ⇒ a + vendeur opposé < 1 ⇔ **acheteur de notre côté > a**, et « tous frais » ⇔ acheteur − frais(acheteur) > a + frais(a) "
        "(les frais sont symétriques). Les deux dernières colonnes comptent les lignes où l'équivalence ne tient pas : 0 partout = vérifiée ligne par ligne. "
        "Une paire rentable n'existe donc QUE quand notre côté a monté au-dessus du prix payé : c'est une prise de bénéfice.", "",
        "Marge nette par paire (cents, tous frais, prudent, toutes périodes) :", "",
        "| Cohorte | Moments | 10 % | médiane | 90 % | moyenne | Premier moment de chaque position : n · 10 % · médiane · 90 % | Marge marginale au premier moment (sans frais d'entrée) : médiane |", "|---|---|---|---|---|---|---|---|"]
for coh in CP:
    ma = np.concatenate([Q1[(coh, "prudent", per)]["mall"] for per in PERS]); mf = np.concatenate([Q1[(coh, "prudent", per)]["mfirst"] for per in PERS])
    mm = np.concatenate([Q1[(coh, "prudent", per)]["mmfirst"] for per in PERS])
    out.append(f"| {coh} | {len(ma)} | {q(ma, 10)} | {q(ma, 50)} | {q(ma, 90)} | {f2(ma.mean()) if len(ma) else '—'} | {len(mf)} · {q(mf, 10)} · {q(mf, 50)} · {q(mf, 90)} | {q(mm, 50)} |")
out.append("")
# ---- Q2
out += ["## 2. Quantité réellement appariable au seul meilleur niveau", "",
        "Premier moment éligible (tous frais) de chaque position ; ordre au prix vu, exécuté sur la ligne + 0,3 s (prudent, taille affichée) ou + 0,6 s (pessimiste, moitié de la taille) ; "
        "si le vendeur opposé a monté entre-temps : 0. Rapport à la taille de la position (parts d'entrée). Puis couverture obtenue en balayant tous les moments éligibles (H25 100 % continu).", "",
        "| Cohorte | Scénario | Positions avec moment éligible | Appariable au 1er moment : 10 % · médiane · 90 % | 0 (prix parti) | ≥ 25 % | ≥ 50 % | ≥ 75 % | ≥ 100 % | H25 continu : couverture médiane · part à 100 % |",
        "|---|---|---|---|---|---|---|---|---|---|"]
for coh in CP:
    for sc in ("prudent", "pessimiste"):
        R, cov = Q2[(coh, sc)]
        out.append(f"| {coh} | {sc} | {len(R)} | {pc(np.percentile(R, 10))} · {pc(np.median(R))} · {pc(np.percentile(R, 90))} | {pc(np.mean(R == 0))} | {pc(np.mean(R >= 0.25))} | {pc(np.mean(R >= 0.5))} | "
                   f"{pc(np.mean(R >= 0.75))} | {pc(np.mean(R >= 1 - 1e-9))} | {pc(np.median(cov)) if len(cov) else '—'} · {pc(np.mean(cov >= 0.999)) if len(cov) else '—'} |")
out += ["", "Idéal : quantité illimitée au meilleur niveau par hypothèse (borne haute, non atteignable).", ""]
# ---- Q3 / Q4 / Q5
out += ["## 3-5. Couvrir SEULEMENT les paires strictement rentables (H25) : 25 / 50 / 75 / 100 %, premier moment ou balayage continu", "",
        "Décision avec la seule information du moment (critère tous frais sur la ligne de décision, ordre au prix vu). « premier » = un seul essai au premier moment éligible ; « continu » = on réessaie à chaque moment éligible jusqu'à la fraction visée. "
        "Jackpots = gain ≥ 4 × la mise en gardant ; perdus = jackpots de GARDER qui ne sont plus ≥ 4 × la mise avec la variante.", ""]
for coh in CP:
    for sc in SCN:
        out += [f"### {COHN[coh]} — {sc}", "",
                "| Variante | Δ app. [IC 90 %] | Δ valid. [IC 90 %] | Δ test [IC 90 %] | Positions couvertes app. / valid. / test | Jackpots perdus app. / valid. / test | Profit sacrifié jackpots (valid. / test) | Profit verrouillé (valid. / test) |",
                "|---|---|---|---|---|---|---|---|"]
        for v_ in V25 + ["H26"]:
            S3 = [ST[("ind", coh, sc, v_, per)] for per in PERS]
            out.append(f"| {v_ if v_ != 'H26' else 'H26 (' + pf(F26[coh]) + ' continu, figé app.)'} | " + " | ".join(dci(s_) for s_ in S3) + " | " + " / ".join(str(s_["exe"]) for s_ in S3) + " | "
                       + " / ".join(f"{s_['jk'] - s_['kept']}/{s_['jk']}" for s_ in S3) + f" | {f0(S3[1]['sac'])} / {f0(S3[2]['sac'])} | {f0(S3[1]['locked'])} / {f0(S3[2]['locked'])} |")
        h0 = [ST[("ind", coh, sc, "HOLD", per)] for per in PERS]
        out += ["", "GARDER : " + " · ".join(f"{per} {h_['n']} positions {f0(h_['pnl'])}" for per, h_ in zip(PERS, h0)) + ".", ""]
out += [f"H26 : fraction choisie sur l'apprentissage (prudent, Σ P&L, 25 / 50 / 75 %) puis figée : " + " · ".join(f"{coh} → {pf(F26[coh])} (" + ", ".join(f"{pf(f)} : {f0(v_)}" for f, v_ in G26[coh].items()) + ")" for coh in CP) + ".", ""]
# ---- H25 / H26 contre VENTE
out += ["### H25 / H26 contre VENTE de la même fraction au même moment (mêmes lignes, même règle)", "",
        "Différence de P&L attendue : 0 (miroir) ; seule différence : le capital reste immobilisé jusqu'au règlement avec la paire, il revient tout de suite avec la vente.", "",
        "| Cohorte | Variante | Scénario | Δ P&L couverture − vente (app. / valid. / test) | Capital immobilisé max : couverture / vente | Capital immobilisé moyen à la fin du cycle (valid.) : couverture / vente |", "|---|---|---|---|---|---|"]
def immob_fin(R, per): L = [r for r in R.values() if r["ok"] and r["per"] == per]; return float(np.mean([r["stake"] + r["oppnf"] for r in L])) if L else 0.0
for coh in CP:
    for v_ in ("H25 100 % continu", "H25 50 % continu", "H26"):
        for sc in SCN:
            vs = VMAP[v_]
            dd_ = [ST[("ind", coh, sc, v_, per)]["pnl"] - ST[("ind", coh, sc, vs, per)]["pnl"] for per in PERS]
            pk = max(ST[("ind", coh, sc, v_, per)]["peak"] for per in PERS); pks = max(ST[("ind", coh, sc, vs, per)]["peak"] for per in PERS)
            Lh = [r for r in RI[(coh, sc, v_)].values() if r["ok"] and r["per"] == "validation"]; Ls = [r for r in RI[(coh, sc, vs)].values() if r["ok"] and r["per"] == "validation"]
            ih = float(np.mean([r["stake"] + r["oppnf"] for r in Lh])) if Lh else 0.0
            isell = float(np.mean([r["stake"] * (1 - r["sellq"] / r["q0"]) for r in Ls])) if Ls else 0.0
            out.append(f"| {coh} | {v_} | {sc} | {' / '.join(f0(x) for x in dd_)} | {f0(pk)} / {f0(pks)} | {f0(ih)} / {f0(isell)} |")
out += ["", "Idéal : la fusion Up + Down rend le capital tout de suite (hypothèse), d'où un capital immobilisé égal à celui de la vente.", ""]
# ---- Q6
out += ["## 6. Avec 250 $ partagés (chronologique, entrées ≤ 50 $) : quelle part du profit verrouillé est atteignable ?", "",
        "Profit verrouillé = Σ des paires formées × (1 − coût unitaire des deux jambes, frais compris). « Part atteignable » = profit verrouillé dans le portefeuille 250 $ / profit verrouillé en 50 $ indépendants.", "",
        "| Cohorte | Variante | Scénario | Période | Verrouillé 50 $ indép. | Verrouillé 250 $ | Part atteignable | P&L 250 $ (GARDER) | P&L 250 $ (variante) | Positions jouées / refusées faute de capital (variante) | Capital immobilisé max (250 $) |",
        "|---|---|---|---|---|---|---|---|---|---|---|"]
for coh in CP:
    for v_ in ("H25 100 % continu", "H26"):
        for sc in SCN:
            for per in PER2:
                si, sc_ = ST[("ind", coh, sc, v_, per)], ST[("cap", coh, sc, v_, per)]
                nb = sum(1 for r in RC[(coh, sc, v_, per)].values() if r["ok"]); rf = sum(1 for r in RC[(coh, sc, v_, per)].values() if not r["ok"] and r.get("why") == "capital")
                out.append(f"| {coh} | {v_} | {sc} | {per} | {f0(si['locked'])} | {f0(sc_['locked'])} | {pc(sc_['locked'] / si['locked']) if si['locked'] > 0.5 else '—'} | "
                           f"{f0(ST[('cap', coh, sc, 'HOLD', per)]['pnl'])} | {f0(sc_['pnl'])} | {nb} / {rf} | {f0(sc_['peak'])} |")
out += ["", "Une seule position est ouverte à la fois (un signal par cycle, cycles successifs) : l'immobilisation du capital par la paire ne bloque jamais une AUTRE entrée ; "
        "ce qui limite le profit atteignable est la **ruine** du portefeuille par les pertes des positions non couvertes, pas le capital bloqué.", ""]
# ---- Q7
out += ["## 7. Les fenêtres de paire rentable durent-elles assez pour la latence réelle ?", "",
        "Fenêtre = suite ininterrompue de lignes où la paire est rentable tous frais compris (entrées du scénario prudent). Durée = jusqu'à la première ligne où elle ne l'est plus. "
        "« Encore là » = critère toujours vrai sur la première ligne ≥ début + délai ; « encore achetable » = en plus, vendeur opposé ≤ prix vu au début (l'ordre au prix vu passe).", "",
        "| Cohorte | Source | Fenêtres | Durée (s) : 10 % · médiane · 90 % | Durée (lignes) : médiane · 90 % | Fenêtres d'une seule ligne | Encore là après 0,3 s | encore achetable 0,3 s | Encore là après 0,6 s | encore achetable 0,6 s |",
        "|---|---|---|---|---|---|---|---|---|---|"]
for coh in CP:
    x = Q7[coh]
    out.append(f"| {coh} | lignes 0,3 s | {x['n']} | {q(x['ds'], 10)} · {q(x['ds'], 50)} · {q(x['ds'], 90)} | {q(x['dr'], 50)} · {q(x['dr'], 90)} | {pc(np.mean(x['dr'] == 1)) if x['n'] else '—'} | "
               f"{pc(x['st03'] / max(1, x['n']))} | {pc(x['fi03'] / max(1, x['n']))} | {pc(x['st06'] / max(1, x['n']))} | {pc(x['fi06'] / max(1, x['n']))} |")
    out.append(f"| {coh} | photos 100 ms (fenêtres entières dans la photo) | {x['ln']} | {q(x['ld'], 10)} · {q(x['ld'], 50)} · {q(x['ld'], 90)} | — | — | "
               f"{pc(x['l03'] / max(1, x['ln']))} | {pc(x['lf03'] / max(1, x['ln']))} | {pc(x['l06'] / max(1, x['ln']))} | {pc(x['lf06'] / max(1, x['ln']))} |")
out += ["", "Les photos 100 ms ne couvrent que ~20 s autour du premier désaccord de chaque cycle (souvent juste après l'entrée) : petit échantillon, mais à la bonne résolution. "
        "Une fenêtre plus courte qu'une ligne (0,3 s) est invisible dans les lignes.", ""]
# ---- tableau principal : contribution marginale
ALLH = [f"H{n:02d}" for n in range(1, 25)] + V25 + ["H26"]
NM = {**HNOM, **{v_: "conversion précoce (paires strictement rentables)" for v_ in V25}, "H26": "préservation du jackpot (fraction figée app.)"}
out += ["## Tableau principal — contribution marginale de chaque couverture (Δ P&L vs GARDER, mêmes positions, frais + latence)", "",
        "Prudent = scénario principal ; idéal (borne haute) et pessimiste donnés. 50 $ indépendants (le capital bloqué par la paire ne gêne aucune autre entrée : une position à la fois) ; "
        "dernière colonne : même Δ dans le portefeuille 250 $ (dominé par la ruine). Jackpots perdus = validation + test, prudent.", ""]
for coh in CP:
    out += [f"### {COHN[coh]}", "",
            "| Couverture | Prudent app. | Prudent valid. [IC 90 %] | Prudent test [IC 90 %] | Idéal valid. / test | Pessimiste valid. / test | Jackpots perdus (valid. + test) | Profit sacrifié jackpots | Capital immobilisé max | Δ 250 $ valid. / test |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for h in ALLH:
        sv, stt = ST[("ind", coh, "prudent", h, "validation")], ST[("ind", coh, "prudent", h, "inédit")]
        jl = (sv["jk"] - sv["kept"]) + (stt["jk"] - stt["kept"]); jt = sv["jk"] + stt["jk"]
        lab = f"H26 {NM['H26']} ({pf(F26[coh])})" if h == "H26" else (f"{h} {NM[h]}" if len(h) == 3 else h)
        out.append(f"| {lab} | {f0(ST[('ind', coh, 'prudent', h, 'apprentissage')]['d'])} | {dci(sv)} | {dci(stt)} | {f0(ST[('ind', coh, 'idéal', h, 'validation')]['d'])} / {f0(ST[('ind', coh, 'idéal', h, 'inédit')]['d'])} | "
                   f"{f0(ST[('ind', coh, 'pessimiste', h, 'validation')]['d'])} / {f0(ST[('ind', coh, 'pessimiste', h, 'inédit')]['d'])} | {jl}/{jt} | {f0(sv['sac'] + stt['sac'])} | {f0(max(sv['peak'], stt['peak']))} | "
                   f"{f0(ST[('cap', coh, 'prudent', h, 'validation')]['d'])} / {f0(ST[('cap', coh, 'prudent', h, 'inédit')]['d'])} |")
    hv, ht = ST[("ind", coh, "prudent", "HOLD", "validation")], ST[("ind", coh, "prudent", "HOLD", "inédit")]
    out += ["", f"GARDER prudent : app. {f0(ST[('ind', coh, 'prudent', 'HOLD', 'apprentissage')]['pnl'])} · valid. {f0(hv['pnl'])} ({hv['n']} positions) · test {f0(ht['pnl'])} ({ht['n']}).", ""]
# ---- Q8
def eqsell(h):
    """part des positions déclenchées (A + B, prudent, valid. + test) où le P&L = VENTE 100 % au même instant (à 1 cent près)"""
    n = e = 0
    for coh in CP:
        for st, r in RI[(coh, "prudent", h)].items():
            if not r["ok"] or not r["att"] or r["per"] == "apprentissage": continue
            s_ = RI[(coh, "prudent", h, "SELL100")].get(st)
            if s_ and s_["ok"]: n += 1; e += abs(r["pnl"] - s_["pnl"]) < 0.01
    return e, n
def dd2(h): return " · ".join(f"{coh} {f0(ST[('ind', coh, 'prudent', h, 'validation')]['d'])} → {f0(ST[('ind', coh, 'prudent', h, 'inédit')]['d'])}" for coh in CP)
DEC8 = [("H01", "fusionner → H25", "règle identique à H25 100 % continu (même critère tous frais, même balayage)"),
        ("H02", "fusionner → H25", "= H25 25 % continu"), ("H03", "fusionner → H25", "= H25 50 % continu"),
        ("H04", "fusionner → H26", "plancher ≥ 0 sur les deux issues = paire partielle rentable ; même famille que H26, sans règle de fraction apprise"),
        ("H05", "fusionner → H26", "fraction fixée par le jackpot ; H26 la choisit sur l'apprentissage"),
        ("H06", "fusionner → H25", "échelle = H25 avec seuils plus stricts ; rien de plus"),
        ("H07", "abandonner (= vente stop-loss)", "miroir : acheter l'opposé à la perte latente −25 $ = vendre la position à ce moment"),
        ("H08", "abandonner (= vente stop-loss)", "idem à −10 $"),
        ("H09", "abandonner", "après modèle −10 la pire issue ≥ 0 est presque toujours infaisable (miroir : il faudrait que notre côté soit au-dessus du prix payé)"),
        ("H10", "fusionner → VENTE", "avantage net = 0 dans 100 % des cas (miroir) : = vendre 100 % au déclencheur"),
        ("H11", "fusionner → VENTE 25 %", "achat opposé 25 % = vente 25 % au même instant"),
        ("H12", "abandonner", "attente 3 s : prédicteurs faibles (hedge predictor, AUC 0,52-0,59 sur les moments vivants), retombe sur la vente"),
        ("H13", "abandonner", "idem 1 s"), ("H14", "abandonner", "idem 3 s"), ("H15", "abandonner", "idem 5 s"), ("H16", "abandonner", "idem 10 s"),
        ("H17", "abandonner (en attente de données)", "choisit l'immédiat presque toujours (le vendeur opposé monte après modèle −10) ; un vrai test exige les remplissages réels"),
        ("H18", "abandonner (en attente de données)", "seuil appris = jamais ; ordre passif à 0,95 non mesurable sans file d'attente"),
        ("H19", "garder en test LIVE seulement", "remplissage passif non mesurable hors ligne (29-41 % selon l'hypothèse) ; à mesurer avec un ordre fantôme réel"),
        ("H20", "fusionner → H19 (live)", "prédicteur de « traversée », pas de file ; même besoin de données que H19"),
        ("H21", "abandonner", "= immédiat (= vente) sauf sur les sauts, qui ne reviennent presque jamais après modèle −10"),
        ("H22", "fusionner → H19 (live)", "moitié vente + moitié H19"),
        ("H23", "garder comme variante de H25 (observation)", "= H25 + revente de l'opposé à +5 c : pari sur le retour, signe instable entre validation et test"),
        ("H24", "abandonner", "ajoute de l'exposition (rachat de notre côté) : ce n'est pas une couverture ; signe instable")]
out += ["## 8. Les 24 fantômes prévus : garder / fusionner / abandonner", "",
        "« = VENTE 100 % » : part des positions déclenchées (A + B, prudent, validation + test) où le P&L est identique à celui de la vente de toute la position au même instant (à 1 cent près).", "",
        "| Fantôme | Décision | Raison | = VENTE 100 % | Δ prudent valid. → test (50 $ indép.) |", "|---|---|---|---|---|"]
for h, dcs, why in DEC8:
    e, n = eqsell(h)
    out.append(f"| {h} {HNOM[h]} | **{dcs}** | {why} | {e}/{n} ({pc(e / n) if n else '—'}) | {dd2(h)} |")
out += [f"| H25 conversion précoce | **garder** (remplace H01-H03, H06) | seule règle « paire strictement rentable » ; = vente de la même fraction au même instant (Δ 0 $), capital bloqué en plus | — | {dd2('H25 100 % continu')} |",
        f"| H26 préservation du jackpot | **garder** (remplace H04-H05) | fraction figée sur l'apprentissage ({', '.join(f'{c} {pf(F26[c])}' for c in CP)}) | — | {dd2('H26')} |", ""]
# ---- audit live
out += ["## 9. Audit des données pour faire tourner ces fantômes EN DIRECT", "",
        "| Donnée | Bot Cloudflare (bot95/src/index.js) aujourd'hui | Programme Dublin (bot95/rapide/rapide.js) aujourd'hui | Nécessaire pour H25 / H26 / H19 |", "|---|---|---|---|",
        "| Carnet du côté OPPOSÉ après l'entrée | meilleur niveau + taille toutes les 0,3 s (rec) ; 3 niveaux à 100 ms seulement ~10 s avant / après le 1er désaccord (photos) | tient le carnet complet des deux jetons EN MÉMOIRE, mais n'enregistre rien du côté opposé (seulement notre côté au signal, jusqu'à 2 s) | carnet opposé complet (≥ 5 niveaux, prix + taille) à chaque message, de l'entrée au règlement, pour chaque position fantôme |",
        "| Transactions (prix, taille, côté) | flux agrégé en $ par seconde (sig) et par 100 ms (photos) ; enregistreur au message près (best bid/ask + chaque transaction) actif 10 min par heure, gardé 24 h, pas exporté | reçoit last_trade_price mais l'ignore | chaque transaction des deux jetons : prix, taille, côté, horodatage Polymarket |",
        "| Annulations / ajouts | agrégés en $ (retraits / ajouts) | appliqués au carnet en mémoire, non enregistrés | événements price_change bruts (prix, taille avant / après, côté) pour reconstruire la file à notre prix |",
        "| Horodatages | réception Cloudflare seulement dans les lignes | réception locale (µs) + horodatage Polymarket du message, utilisés seulement en statistiques | les deux horodatages sur chaque événement enregistré |",
        "| Règles A et B | A (« desaccord 30 zone + modele monte ») et « corrige : V2-F » (moteur 0,015 %) existent comme fantômes | règles V2-F 0,08 % / 0,01 %, désaccord 30, etc. ; **ni A ni B** (pas de sdRel 1,5e-4, pas de zone + modèle monte) | ajouter A et B à rapide.js pour mesurer la latence réelle des mêmes entrées |",
        "| Suivi après l'entrée | aucun suivi d'une paire possible | « achetable » à 1 ms … 2 s, survie de l'offre de NOTRE côté seulement | à chaque message : coût de paire tous frais, quantité appariable au meilleur niveau et en profondeur, début / fin de chaque fenêtre rentable |",
        "| Ordres passifs | — | aucun (fantôme, pas d'ordre) | pour H19 : un ordre réel minuscule (1 part) ou un suivi de file fantôme (taille devant nous + transactions à notre prix) |",
        "| Fusion Up + Down | — | — | non nécessaire au P&L ; à tracer seulement si on veut libérer le capital avant le règlement |",
        "| Latence | — | rapide.json vide : pas encore de résultats reçus | temps aller-retour d'un ordre (déjà sondé : /time), délai message → décision (déjà calculé) — à joindre à chaque fenêtre |", "",
        "**À ajouter exactement dans l'enregistreur live** (rapide.js de préférence, car il tient déjà le carnet complet en mémoire) :", "",
        "1. Les règles d'entrée A et B (modèle corrigé sdRel = 1,5e-4 ; zone 0,15-0,35 + modèle monte) en fantômes, mêmes définitions que le hors ligne.",
        "2. Pour chaque position fantôme ouverte : à chaque message Polymarket des deux jetons jusqu'au règlement, une ligne [heure locale µs, heure Polymarket, meilleur vendeur et acheteur opposés + 5 niveaux (prix, taille), coût de paire tous frais, parts appariables au prix rentable].",
        "3. Toutes les transactions last_trade_price des deux jetons (prix, taille, côté, heure Polymarket, heure locale) et les événements price_change bruts (prix, taille, côté).",
        "4. Pour chaque fenêtre de paire rentable : heure de début et de fin, quantité disponible au début, après 1 / 10 / 100 / 300 / 600 ms.",
        "5. Un ordre passif fantôme suivi en file (taille devant nous à la pose, transactions à notre prix ensuite), ou un ordre réel de 1 part si Pitch l'autorise — c'est la seule façon de mesurer H19.",
        "6. Envoi au bot Cloudflare et sauvegarde dans bot95/ (rapide.json ou un fichier par jour), comme les autres données.", "",
        f"Durée de calcul : {_time.time() - _T0:.0f} s."]

# ---- verdict
V = ["## Réponse courte (en tête)", ""]
for coh in CP:
    x = {per: Q1[(coh, "prudent", per)] for per in PERS}
    nT = sum(v_["n"] for v_ in x.values()); nf = sum(v_["nf"] for v_ in x.values()); ng = sum(v_["ng"] for v_ in x.values())
    rf = sum(v_["rf"] for v_ in x.values()); rg = sum(v_["rg"] for v_ in x.values())
    mf = np.concatenate([x[per]["mfirst"] for per in PERS])
    R, cov = Q2[(coh, "prudent")]
    s25 = {per: ST[("ind", coh, "prudent", "H25 100 % continu", per)] for per in PERS}; s26 = {per: ST[("ind", coh, "prudent", "H26", per)] for per in PERS}
    V.append(f"- **{COHN[coh]}** (prudent) : {ng}/{nT} positions ont au moins un moment Up + Down < 1 $ ({rg} lignes) ; **{nf}/{nT}** restent rentables tous frais compris ({rf} lignes) ; "
             f"marge au premier moment : médiane {q(mf, 50)} c par paire. Appariable au 1er moment au meilleur niveau : médiane {pc(np.median(R)) if len(R) else '—'} de la position "
             f"(0 dans {pc(np.mean(R == 0)) if len(R) else '—'} des cas). H25 100 % continu : Δ vs GARDER app. {dci(s25['apprentissage'])}, valid. {dci(s25['validation'])}, test {dci(s25['inédit'])} ; "
             f"jackpots perdus valid. {s25['validation']['jk'] - s25['validation']['kept']}/{s25['validation']['jk']}, test {s25['inédit']['jk'] - s25['inédit']['kept']}/{s25['inédit']['jk']}. "
             f"H26 ({pf(F26[coh])}) : valid. {dci(s26['validation'])}, test {dci(s26['inédit'])}.")
V.append("- **Mécanique** : carnets miroirs ⇒ « paire < 1 » ⇔ acheteur de notre côté > prix payé (vérifié ligne par ligne, 0 écart). Apparier = vendre la même fraction au même instant : "
         "Δ couverture − vente = 0 $ dans tous les scénarios (section 3-5), la paire bloque seulement le capital jusqu'au règlement. Verrouiller tôt coupe surtout les positions gagnantes (qui montent d'abord) : "
         "petit profit sûr contre jackpots perdus.")
V.append(f"- **Latence** : fenêtres rentables (lignes 0,3 s) médiane {q(np.concatenate([Q7[c]['ds'] for c in CP]), 50)} s ; encore achetables au prix vu après 0,3 s dans "
         f"{pc(sum(Q7[c]['fi03'] for c in CP) / max(1, sum(Q7[c]['n'] for c in CP)))} des fenêtres, après 0,6 s dans {pc(sum(Q7[c]['fi06'] for c in CP) / max(1, sum(Q7[c]['n'] for c in CP)))} (section 7).")
V.append("- **Capital 250 $** : une position à la fois, donc le capital bloqué ne coûte aucune entrée ; c'est la ruine par GARDER (prudent) qui limite tout (section 6).")
V.append("- **Ménage des 24 fantômes** : garder H25 (remplace H01-H03, H06), H26 (remplace H04-H05), H19 en test live seulement (avec H20, H22), H23 en variante d'observation ; "
         "H07, H08, H10, H11 = ventes (miroir) ; H09, H12-H18, H21, H24 abandonnés (section 8).")
V.append("- **Live** : ni le bot Cloudflare ni rapide.js n'enregistrent le carnet opposé complet après l'entrée, les transactions individuelles ni les événements d'annulation, et rapide.js n'a ni A ni B : liste exacte section 9.")
V.append("")
out[VERD:VERD] = V
open("etude/bot5min/resultat_hedge_lab_paires.md", "w").write("\n".join(out))
print("\n".join(V)); print(f"fini en {_time.time() - _T0:.0f} s")
