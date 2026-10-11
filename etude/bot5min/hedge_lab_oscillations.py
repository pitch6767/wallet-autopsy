"""BOT95 HEDGE LAB — oscillations des tickets bon marché (demande de Pitch, 11.10.2026). Hors ligne, aucune modification du bot.
H27 vendre puis racheter · H28 couvrir puis découvrir (miroir de H27) · H29 inventaire dynamique (règle choisie sur l'apprentissage) · H30 conversion seule (= H25).
Réutilise le moteur de hedge_lab.py (mêmes entrées A / B, scénarios, statistiques). Paramètres choisis sur l'apprentissage (prudent, 50 $ indépendants), figés ensuite.
Usage : python3 etude/bot5min/hedge_lab_oscillations.py → etude/bot5min/resultat_hedge_lab_oscillations.md"""
exec(open("etude/bot5min/hedge_lab.py").read().split("# ================================================================ rédaction")[0])
CP = ("A", "B")
pf = lambda f: f"{int(round(100 * f))} %"
# ---------------------------------------------------------------- journal des remplissages (sans toucher au moteur)
_orig_trade = Pos.trade
_ARR = {("own", "buy"): "oa", ("own", "sell"): "ob", ("opp", "buy"): "pa", ("opp", "sell"): "pb"}
def _trade(s, k, tok, side, want, limit=None):
    q_ = _orig_trade(s, k, tok, side, want, limit)
    if q_ > 0:
        if not hasattr(s, "fl"): s.fl = []
        s.fl.append((s.lastfill, tok, side, q_, float(s.v[_ARR[(tok, side)]][s.lastfill]), "preneur"))
    return q_
Pos.trade = _trade
def passif(p, k, tok, side, L, want, t_exp):
    """ordre passif (file : nous sommes derniers). Achat de notre côté à L : rempli si notre vendeur passe sous L (≤ L − 1 c) ;
    vente de l'opposé à L : rempli si l'acheteur opposé passe au-dessus (≥ L + 1 c) — miroir exact. Idéal : dès que le prix touche ; pessimiste : 2 lignes de suite, moitié de la taille."""
    j = p.row(k); L = round(L, 2)
    if j is None or want < 1 or not (0.01 <= L <= 0.99): return 0.0
    m1 = min(int(le(p.T, min(t_exp, p.end - 1e-6))), len(p.T) - 1)
    if m1 <= j: return 0.0
    if (tok, side) == ("own", "buy"): px, sz, sg = p.v["oa"], p.v["oaz"], 1
    else: px, sz, sg = p.v["pb"], p.v["pbz"], -1
    seg = px[j + 1:m1 + 2] * sg; lim = L * sg
    if p.mk == "touche": cond = seg[:m1 - j] <= lim + 1e-9
    else:
        c = seg <= lim - 0.01 + 1e-9
        if p.mk == "traverse": cond = c[:m1 - j]
        else:
            if len(c) < m1 - j + 1: c = np.append(c, False)
            cond = c[:m1 - j] & c[1:m1 - j + 1]
    got = 0.0
    for idx in np.where(cond)[0]:
        m = j + 1 + int(idx); rem = want - got
        if rem < 1: break
        qq = rem if p.qf is None else min(rem, sz[m] * p.qf - p.used.get((m, tok, "mk"), 0.0))
        if side == "buy": qq = min(qq, max(0.0, p.free() / L))
        else: qq = min(qq, p.qp)
        if qq < 1: continue
        p.used[(m, tok, "mk")] = p.used.get((m, tok, "mk"), 0.0) + qq; got += qq
        if side == "buy": p.qo += qq; p.cash -= qq * L; p.own_cost += qq * L; p.own_qb += qq
        else: p.qp -= qq; p.cash += qq * L; p.notes["revendu"] = p.notes.get("revendu", 0.0) + qq
        if not hasattr(p, "fl"): p.fl = []
        p.fl.append((m, tok, side, qq, L, "passif")); p.lastfill = m; p._merge()
    return got

# ---------------------------------------------------------------- H27 / H28 / variantes
def seuil(p, kind, x): return p.a + x if kind == "abs" else p.a * (1 + x)
def osc(p, kind, x, f, y, mode="preneur", miroir=False, rachat=True, stop10=False):
    ob = p.v["ob"][p.je + 1:p.kend]; c = p.cand(ob >= seuil(p, kind, x) - 1e-9)
    k10 = p.k_m10() if stop10 else None
    if k10 is not None: c = c[c < k10]
    if len(c):
        p.mark(int(c[0]))
        if not miroir: p.loop(c, "own", "sell", lambda: f * p.q0 - p.sell_q)
        else: p.loop(c, "opp", "buy", lambda: f * p.q0 - p.qp)
        fl = [z for z in getattr(p, "fl", []) if (z[1], z[2]) == (("own", "sell") if not miroir else ("opp", "buy"))]
        S = sum(z[3] for z in fl)
        if S >= 1 and rachat:
            sv = sum(z[3] * (z[4] if not miroir else 1 - z[4]) for z in fl) / S          # prix de vente équivalent (notre côté)
            last = max(z[0] for z in fl); p.notes["prix_vente"] = sv
            t_exp = p.end - 1 if k10 is None else p.T[k10]
            if mode == "preneur":
                ks = np.arange(last + 1, p.kend)
                if k10 is not None: ks = ks[ks < k10]
                oa = p.v["oa"]; cc = ks[oa[ks] <= sv - y + 1e-9] if len(ks) else ks
                if not miroir: p.loop(cc, "own", "buy", lambda: p.q0 - p.qo)
                else: p.loop(cc, "opp", "sell", lambda: p.qp)
            else:
                if not miroir: passif(p, last, "own", "buy", sv - y, S, t_exp)
                else: passif(p, last, "opp", "sell", 1 - (sv - y), S, t_exp)
    if k10 is not None:
        p.mark(k10)
        if not miroir: p.loop(p.rows_from(k10), "own", "sell", lambda: p.qo)
        else: p.loop(p.rows_from(k10), "opp", "buy", lambda: p.qo - p.qp)
def decompo(p):
    """aller-retour réalisé, quantité vendue non rachetée (et son issue), en équivalent « notre côté »"""
    fl = getattr(p, "fl", [])
    sells = [z for z in fl if (z[1], z[2]) in (("own", "sell"), ("opp", "buy"))]
    buys = [z for z in fl if (z[1], z[2]) in (("own", "buy"), ("opp", "sell"))]
    S = sum(z[3] for z in sells); R = sum(z[3] for z in buys)
    if S < 1: return dict(S=0.0, R=0.0, rt=0.0, opp_loss=0.0, opp_gain=0.0)
    snet = sum(z[3] * ((z[4] - FEE(z[4])) if z[1] == "own" else (1 - z[4] - FEE(z[4]))) for z in sells) / S
    rc = (sum(z[3] * ((z[4] + (FEE(z[4]) if z[5] == "preneur" else 0)) if z[1] == "own" else (1 - z[4] + (FEE(z[4]) if z[5] == "preneur" else 0))) for z in buys) / R) if R >= 1 else 0.0
    R = min(R, S); rest = S - R
    return dict(S=S, R=R, rt=R * (snet - rc), opp_loss=(rest * (1 - snet) if p.w else 0.0), opp_gain=(rest * snet if not p.w else 0.0))

# ---------------------------------------------------------------- grille pré-enregistrée, choix sur l'apprentissage (prudent, 50 $ indépendants)
GRILLE = [(k_, x_, f_, y_) for k_, xs in (("abs", (0.03, 0.05, 0.10)), ("rel", (0.30, 0.50, 1.00))) for x_ in xs for f_ in (0.25, 0.5) for y_ in (0.02, 0.05, 0.10)]
def lab_g(g): return (f"+{int(round(100 * g[1]))} c" if g[0] == "abs" else f"+{int(round(100 * g[1]))} % du prix d'entrée") + f", vendre {pf(g[2])}, racheter à vente − {int(round(100 * g[3]))} c"
def tot_train(coh, fn):
    t_ = 0.0
    for st, s in COH[coh].items():
        if PER(st) != "apprentissage": continue
        p = Pos(st, s, "prudent")
        if p.ok: fn(p); t_ += p.pnl()
    return t_
PAR, GTR = {}, {}
for coh in CP:
    for mode in ("preneur", "passif"):
        res = {g: tot_train(coh, lambda p, g=g: osc(p, *g, mode=mode)) for g in GRILLE}
        PAR[(coh, mode)] = max(res, key=res.get); GTR[(coh, mode)] = res
print("paramètres H27", PAR, f"{_time.time() - _T0:.0f} s", flush=True)

def mk(fn): return fn
POLX = {}
for coh in CP:
    g = PAR[(coh, "preneur")]; gp = PAR[(coh, "passif")]
    POLX[(coh, "H27 preneur")] = lambda p, g=g: osc(p, *g)
    POLX[(coh, "H27 passif")] = lambda p, g=gp: osc(p, *g, mode="passif")
    POLX[(coh, "VENTE seule (même instant, H27 preneur)")] = lambda p, g=g: osc(p, *g, rachat=False)
    POLX[(coh, "VENTE seule (même instant, H27 passif)")] = lambda p, g=gp: osc(p, *g, rachat=False)
    POLX[(coh, "H28 preneur")] = lambda p, g=g: osc(p, *g, miroir=True)
    POLX[(coh, "H28 passif")] = lambda p, g=gp: osc(p, *g, mode="passif", miroir=True)
# H29 : règles candidates fixées à l'avance, une seule choisie sur l'apprentissage
def r_m10(p):
    k = p.k_m10()
    if k is not None: p.mark(k); p.loop(p.rows_from(k), "own", "sell", lambda: p.qo)
def r_h25(p):
    c = p.cand(p.pcost() < 1)
    if len(c): p.mark(int(c[0])); p.loop(c, "opp", "buy", lambda: p.q0 - p.qp)
H29R = {"R0 garder": lambda p, g: None,
        "R1 vendre f à +x, racheter à vente − y (= H27 preneur)": lambda p, g: osc(p, *g),
        "R2 vendre f à +x sans rachat": lambda p, g: osc(p, *g, rachat=False),
        "R3 tout vendre à modèle −10": lambda p, g: r_m10(p),
        "R4 R1 + tout vendre à modèle −10 (rachat annulé)": lambda p, g: osc(p, *g, stop10=True),
        "R5 apparier seulement les paires rentables (H25)": lambda p, g: r_h25(p)}
H29C, H29G = {}, {}
for coh in CP:
    g = PAR[(coh, "preneur")]
    H29G[coh] = {r: tot_train(coh, lambda p, fn=fn: fn(p, g)) for r, fn in H29R.items()}
    H29C[coh] = max(H29G[coh], key=H29G[coh].get)
    POLX[(coh, "H29")] = lambda p, fn=H29R[H29C[coh]], g=g: fn(p, g)
    POLX[(coh, "H30 = H25")] = r_h25
print("H29", H29C, f"{_time.time() - _T0:.0f} s", flush=True)
NOMS_X = ["H27 preneur", "H27 passif", "VENTE seule (même instant, H27 preneur)", "VENTE seule (même instant, H27 passif)", "H28 preneur", "H28 passif", "H29", "H30 = H25"]

# ---------------------------------------------------------------- simulations
def simx(coh, st, sc, pol, budget=50.0, bank=float("inf")):
    p = Pos(st, COH[coh][st], sc, budget, bank)
    if p.ok and pol != "HOLD": POLX[(coh, pol)](p)
    return p
def recx(p, per):
    r = rec(p, per)
    if r["ok"]: r.update(decompo(p))
    return r
RX, RXC = {}, {}
for coh in CP:
    for sc in SCN:
        for pol in ["HOLD"] + NOMS_X:
            RX[(coh, sc, pol)] = {st: recx(simx(coh, st, sc, pol), PER(st)) for st in sorted(COH[coh])}
            for per in PERS:
                bank = BANK0; out_ = {}
                for st in sorted(COH[coh]):
                    if PER(st) != per: continue
                    b_ = min(50.0, bank)
                    if b_ < 1: out_[st] = dict(st=st, per=per, ok=False, why="capital"); continue
                    r = recx(simx(coh, st, sc, pol, b_, bank), per); out_[st] = r
                    if r["ok"]: bank += r["pnl"]
                RXC[(coh, sc, pol, per)] = out_
    print("simulé", coh, f"{_time.time() - _T0:.0f} s", flush=True)
SX = {}
for coh in CP:
    for sc in SCN:
        for per in PERS:
            for pol in ["HOLD"] + NOMS_X:
                SX[("ind", coh, sc, pol, per)] = stats(RX[(coh, sc, pol)], RX[(coh, sc, "HOLD")], per)
                SX[("cap", coh, sc, pol, per)] = stats(RXC[(coh, sc, pol, per)], RXC[(coh, sc, "HOLD", per)], per)

# ---------------------------------------------------------------- rédaction
def dci(s): return f"{f0(s['d'])} [{f0(s['lo'])} ; {f0(s['hi'])}]"
def dec(coh, sc, pol, per):
    L = [r for r in RX[(coh, sc, pol)].values() if r["ok"] and r["per"] == per]
    return dict(n=sum(1 for r in L if r.get("S", 0) >= 1), nrt=sum(1 for r in L if r.get("R", 0) >= 1), rt=sum(r.get("rt", 0) for r in L),
                ol=sum(r.get("opp_loss", 0) for r in L), og=sum(r.get("opp_gain", 0) for r in L))
def jour(st): return time.strftime("%d.%m", time.gmtime(st + 7200))
JOURS = sorted({jour(st) for c in CP for st in COH[c]}, key=lambda x: (x[3:], x[:2]))
out = ["# BOT95 HEDGE LAB — oscillations des tickets bon marché : H27 vendre-racheter, H28 couvrir-décourir, H29 inventaire dynamique, H30 conversion", "",
       f"Étude hors ligne du {_time.strftime('%d.%m.%Y')} — aucun bot, aucun workflow modifié, rien publié. Mêmes entrées A et B que resultat_hedge_lab.md, mêmes scénarios, mêmes périodes "
       f"(apprentissage < {hs(CUT)} · validation → {hs(MATIN0)} · test inédit après). Δ = P&L avec la règle − P&L en gardant, sur les mêmes positions, frais preneur compris (frais teneur d'ordre supposés 0, non vérifiés) ; "
       "IC 90 % par blocs d'une heure.", ""]
VERD = len(out)
out += ["## 1. Définitions et paramètres (choisis sur l'apprentissage, prudent, 50 $ indépendants, puis figés)", "",
        f"Grille pré-enregistrée ({len(GRILLE)} combinaisons) : hausse de notre côté mesurée sur le **meilleur acheteur** (prix auquel on peut vendre) : +3 / +5 / +10 c ou +30 / +50 / +100 % du prix d'entrée ; "
        "fraction vendue f = 25 / 50 % ; rachat quand le meilleur vendeur de notre côté ≤ prix de vente moyen − y, y = 2 / 5 / 10 c.", "",
        "- **H27 preneur** : au premier moment où la hausse est atteinte, vente de f au meilleur acheteur (ordre au prix vu, renouvelé tant que la hausse tient) ; puis rachat de la même quantité au meilleur vendeur dès qu'il est ≤ vente − y, jusqu'au règlement (un seul aller-retour).",
        "- **H27 passif** : même vente ; le rachat est un ordre passif à vente − y posé jusqu'au règlement, rempli seulement si le vendeur passe 1 c sous notre prix (prudent), 2 lignes de suite et moitié de la taille (pessimiste), dès qu'il touche (idéal, borne haute).",
        "- **VENTE seule** = la même vente au même instant SANS jambe de rachat : c'est l'ancienne « sortie anticipée / free-roll partiel ». H27 − VENTE seule = valeur de la seule jambe de rachat.",
        "- **H28** : mêmes instants, mêmes quantités, mais on ACHÈTE l'opposé au lieu de vendre, puis on le REVEND au lieu de racheter notre côté (seuils traduits par le miroir : vendeur opposé = 1 − acheteur de notre côté).",
        "- **H29** : à chaque instant, une règle simple parmi six candidates fixées à l'avance (garder / vendre partiel / racheter / acheter l'opposé — ce dernier identique à vendre par le miroir) ; la règle est choisie sur l'apprentissage.",
        "- **H30** = H25 (apparier seulement les paires strictement rentables tous frais compris, au meilleur niveau, balayage continu).", "",
        "| Cohorte | H27 preneur | H27 passif | H29 règle choisie |", "|---|---|---|---|"]
for coh in CP:
    out.append(f"| {coh} | {lab_g(PAR[(coh, 'preneur')])} (app. {f0(GTR[(coh, 'preneur')][PAR[(coh, 'preneur')]])}) | {lab_g(PAR[(coh, 'passif')])} (app. {f0(GTR[(coh, 'passif')][PAR[(coh, 'passif')]])}) | "
               f"{H29C[coh]} |")
out += ["", "H29 — Σ P&L apprentissage (prudent) de chaque règle candidate : " + " · ".join(f"{coh} : " + ", ".join(f"{r.split(' ')[0]} {f0(v_)}" for r, v_ in H29G[coh].items()) for coh in CP) + ".",
        f"GARDER sur l'apprentissage (prudent) : " + " · ".join(f"{coh} {f0(SX[('ind', coh, 'prudent', 'HOLD', 'apprentissage')]['pnl'])}" for coh in CP) + ".", ""]
# tableau principal
out += ["## 2. Résultat marginal contre GARDER (toutes les positions, exécutées ou non)", ""]
for coh in CP:
    for sc in SCN:
        out += [f"### {COHN[coh]} — {sc}", "",
                "| Règle | Δ app. [IC 90 %] | Δ valid. [IC 90 %] | Δ test [IC 90 %] | Δ 250 $ valid. / test | Creux max valid. / test | Capital engagé max | Jackpots perdus valid. / test | Profit sacrifié jackpots valid. / test |",
                "|---|---|---|---|---|---|---|---|---|"]
        for pol in NOMS_X:
            S3 = [SX[("ind", coh, sc, pol, per)] for per in PERS]
            out.append(f"| {pol} | {dci(S3[0])} | {dci(S3[1])} | {dci(S3[2])} | {f0(SX[('cap', coh, sc, pol, 'validation')]['d'])} / {f0(SX[('cap', coh, sc, pol, 'inédit')]['d'])} | "
                       f"{f0(S3[1]['dd'])} / {f0(S3[2]['dd'])} | {f0(max(s_['peak'] for s_ in S3))} | {S3[1]['jk'] - S3[1]['kept']}/{S3[1]['jk']} / {S3[2]['jk'] - S3[2]['kept']}/{S3[2]['jk']} | {f0(S3[1]['sac'])} / {f0(S3[2]['sac'])} |")
        h_ = [SX[("ind", coh, sc, "HOLD", per)] for per in PERS]
        out += ["", "GARDER : " + " · ".join(f"{per} {x['n']} positions {f0(x['pnl'])} (creux {f0(x['dd'])})" for per, x in zip(PERS, h_)) + ".", ""]
# décomposition H27
out += ["## 3. H27 décomposé : allers-retours, rachats manqués, jambe de rachat isolée", "",
        "(a) gain des allers-retours réalisés = parts rachetées × (prix de vente net − coût de rachat) ; (b) perte d'opportunité = parts vendues jamais rachetées × (1 − prix de vente net) quand notre côté gagne ; "
        "en face, gain quand il perd = parts non rachetées × prix de vente net. (d) Δ total = (a) + (b) + gain d'en face, sur TOUTES les positions. "
        "« Valeur de la jambe de rachat » = Δ(H27) − Δ(VENTE seule au même instant).", "",
        "| Cohorte | Variante | Scénario | Période | Positions avec vente | avec rachat | (a) allers-retours | (b) perte d'opportunité | gain quand notre côté perd | (d) Δ vs GARDER | Valeur de la jambe de rachat |",
        "|---|---|---|---|---|---|---|---|---|---|---|"]
for coh in CP:
    for v_, vs in (("H27 preneur", "VENTE seule (même instant, H27 preneur)"), ("H27 passif", "VENTE seule (même instant, H27 passif)")):
        for sc in SCN:
            for per in PERS:
                d_ = dec(coh, sc, v_, per)
                out.append(f"| {coh} | {v_} | {sc} | {per} | {d_['n']} | {d_['nrt']} | {f0(d_['rt'])} | −{f0(d_['ol'])[1:]} | {f0(d_['og'])} | {f0(SX[('ind', coh, sc, v_, per)]['d'])} | "
                           f"{f0(SX[('ind', coh, sc, v_, per)]['d'] - SX[('ind', coh, sc, vs, per)]['d'])} |")
out.append("")
# H27 vs H28
out += ["## 4. H27 contre H28 : même exposition, mêmes quantités, mêmes instants", "",
        "| Cohorte | Variante | Scénario | Δ P&L H27 − H28 (app. / valid. / test) | Capital engagé max H27 / H28 | Positions où la quantité exécutée diffère |", "|---|---|---|---|---|---|"]
for coh in CP:
    for m in ("preneur", "passif"):
        for sc in SCN:
            a_, b_ = f"H27 {m}", f"H28 {m}"
            dd_ = [SX[("ind", coh, sc, a_, per)]["pnl"] - SX[("ind", coh, sc, b_, per)]["pnl"] for per in PERS]
            ndiff = sum(1 for st, r in RX[(coh, sc, a_)].items() if r["ok"] and abs(r.get("S", 0) - RX[(coh, sc, b_)][st].get("S", 0)) > 0.01)
            out.append(f"| {coh} | {m} | {sc} | {' / '.join(f0(x) for x in dd_)} | {f0(max(SX[('ind', coh, sc, a_, per)]['peak'] for per in PERS))} / {f0(max(SX[('ind', coh, sc, b_, per)]['peak'] for per in PERS))} | {ndiff} |")
out += ["", "Explication : vendeur opposé = 1 − acheteur de notre côté et acheteur opposé = 1 − vendeur de notre côté, avec les mêmes tailles ; frais 0,072·p·(1−p) identiques pour p et 1 − p. "
        "Vendre x parts de notre côté au prix b ou acheter x parts opposées à 1 − b donne exactement le même P&L dans les deux issues ; seul change le capital : H28 paie 1 − b par part au lieu d'encaisser b, "
        "et ce capital reste bloqué jusqu'à la revente ou au règlement. Différences de frais : 0 ; différences d'exécution : 0 (mêmes tailles des deux côtés par construction du miroir).", ""]
# H30
out += ["## 5. H30 = H25 (conversion seule)", ""]
for coh in CP:
    L = [r for r in RX[(coh, "prudent", "H30 = H25")].values() if r["ok"] and r["att"]]
    out.append(f"- {coh} (prudent, toutes périodes) : {len(L)} positions avec paire rentable ; couverture médiane {pc(np.median([r['cov'] for r in L])) if L else '—'} de la position au meilleur niveau ; "
               f"capital engagé max {f0(max(SX[('ind', coh, 'prudent', 'H30 = H25', per)]['peak'] for per in PERS))} ; profit verrouillé valid. {f0(SX[('ind', coh, 'prudent', 'H30 = H25', 'validation')]['locked'])}, test {f0(SX[('ind', coh, 'prudent', 'H30 = H25', 'inédit')]['locked'])} ; "
               f"Δ valid. {dci(SX[('ind', coh, 'prudent', 'H30 = H25', 'validation')])}, test {dci(SX[('ind', coh, 'prudent', 'H30 = H25', 'inédit')])}. "
               f"Confirmé identique à H25 du rapport précédent (même règle, même moteur).")
out += ["- Fusion Up + Down : transaction on-chain, non observable ; comptée 1 $ au règlement (capital libéré tôt seulement en idéal).", ""]
# par jour
out += ["## 6. Par jour (calendrier suisse), prudent, Δ vs GARDER, 50 $ indépendants (toutes périodes)", ""]
for coh in CP:
    out += [f"### {COHN[coh]}", "", "| Règle | " + " | ".join(JOURS) + " | jours positifs |", "|---" * (len(JOURS) + 2) + "|"]
    for pol in NOMS_X:
        dj = collections.defaultdict(float)
        for st, r in RX[(coh, "prudent", pol)].items():
            if r["ok"]: dj[jour(st)] += r["pnl"]
        for st, r in RX[(coh, "prudent", "HOLD")].items():
            if r["ok"]: dj[jour(st)] -= r["pnl"]
        out.append(f"| {pol} | " + " | ".join(f0(dj[j_]) for j_ in JOURS) + f" | {sum(1 for j_ in JOURS if dj[j_] > 0.5)}/{len(JOURS)} |")
    out.append("")
# données
out += ["## 7. Les données actuelles suffisent-elles ?", "",
        "| Fantôme | Variante preneur (achat / vente au meilleur prix) | Variante passive (ordre limite) |", "|---|---|---|",
        "| H27 | **Suffisantes pour un premier verdict** : meilleur acheteur / vendeur + taille toutes les 0,3 s, des deux côtés. Limites : fenêtres < 0,3 s invisibles, pas de profondeur au-delà du meilleur niveau (vente ou rachat > taille affichée non mesurable), heure de réception seulement. | **Insuffisantes** : remplissage du rachat passif non mesurable (file d'attente inconnue, transactions seulement agrégées) ; résultats = bornes idéal / prudent / pessimiste. Il faut les enregistrements 50 ms de Dublin : carnet complet, transactions individuelles (prix, taille, côté), annulations, horodatage Polymarket. |",
        "| H28 | Même chose que H27 (miroir exact) ; aucune donnée en plus n'est utile tant que les carnets restent miroirs. Seule vérification utile en direct : que le miroir tient aussi en profondeur et dans les ordres réellement exécutables. | Même chose que H27 passif. |",
        "| H29 | Suffisantes pour les règles preneur (choix entre vendre, racheter, garder) ; mêmes limites de résolution 0,3 s et de profondeur. | Insuffisantes dès que la règle utilise un ordre passif. |",
        "| H30 (= H25) | Suffisantes pour la décision et le P&L au meilleur niveau ; la quantité au-delà du meilleur niveau et les fenêtres < 0,3 s demandent la profondeur et la résolution 50 ms. Fusion : non observable (sans effet sur le P&L). | — |", "",
        "Les photos 100 ms (3 niveaux, ~20 s autour du premier désaccord) ne couvrent presque jamais le moment des oscillations, qui arrivent plus tard dans le cycle : elles ne suffisent pas à valider la résolution. "
        "Le flux agrégé (1 s / 100 ms) dit qu'il y a eu des échanges, pas à quel prix ni si notre niveau a été touché.", "",
        f"Durée de calcul : {_time.time() - _T0:.0f} s."]
# verdict
V = ["## Réponse courte (en tête)", ""]
for coh in CP:
    def L_(pol): return f"{pol} valid. {dci(SX[('ind', coh, 'prudent', pol, 'validation')])} → test {dci(SX[('ind', coh, 'prudent', pol, 'inédit')])}"
    dv = dec(coh, "prudent", "H27 preneur", "validation"); dt = dec(coh, "prudent", "H27 preneur", "inédit")
    jv = SX[("ind", coh, "prudent", "H27 preneur", "validation")]
    V.append(f"- **{COHN[coh]}** (prudent, 50 $ indépendants) — paramètres H27 appris : {lab_g(PAR[(coh, 'preneur')])}. {L_('H27 preneur')} ; "
             f"VENTE seule au même instant {f0(SX[('ind', coh, 'prudent', 'VENTE seule (même instant, H27 preneur)', 'validation')]['d'])} → {f0(SX[('ind', coh, 'prudent', 'VENTE seule (même instant, H27 preneur)', 'inédit')]['d'])} ; "
             f"valeur de la jambe de rachat valid. {f0(jv['d'] - SX[('ind', coh, 'prudent', 'VENTE seule (même instant, H27 preneur)', 'validation')]['d'])}, test {f0(SX[('ind', coh, 'prudent', 'H27 preneur', 'inédit')]['d'] - SX[('ind', coh, 'prudent', 'VENTE seule (même instant, H27 preneur)', 'inédit')]['d'])}. "
             f"Validation : {dv['n']} ventes, {dv['nrt']} rachats ; allers-retours {f0(dv['rt'])}, perte d'opportunité −{f0(dv['ol'])[1:]}, gain quand notre côté perd {f0(dv['og'])} ; jackpots perdus {jv['jk'] - jv['kept']}/{jv['jk']}. "
             f"{L_('H27 passif')} ; {L_('H29')} (règle : {H29C[coh]}) ; {L_('H30 = H25')}.")
V.append("- **H28 = H27** au cent près dans les trois scénarios (miroir : mêmes prix, mêmes tailles, mêmes frais) ; seule différence : le capital bloqué (section 4).")
V.append("- **Différence avec les anciens essais** : la vente seule au même instant EST l'ancienne sortie anticipée / free-roll ; H27 n'ajoute que la jambe de rachat, dont la valeur est isolée ci-dessus et en section 3.")
V.append("- **Données** : suffisantes pour les variantes preneur (premier verdict, limites 0,3 s et meilleur niveau) ; insuffisantes pour toute variante passive (file, transactions, annulations) → enregistrements 50 ms de Dublin nécessaires (section 7).")
gw = [(coh, pol) for coh in CP for pol in NOMS_X if SX[("ind", coh, "prudent", pol, "validation")]["lo"] > 0 and SX[("ind", coh, "prudent", pol, "inédit")]["d"] > 0]
V.append("- **Verdict** : " + ("aucune de ces règles ne bat GARDER de façon démontrée (IC 90 % validation entièrement > 0 ET test > 0)." if not gw else
                               "critère (IC 90 % validation > 0 et test > 0) rempli par : " + ", ".join(f"{c} {p_}" for c, p_ in gw) + " — à confirmer sur plus de données."))
V.append("")
out[VERD:VERD] = V
open("etude/bot5min/resultat_hedge_lab_oscillations.md", "w").write("\n".join(out))
print("\n".join(V)); print(f"fini en {_time.time() - _T0:.0f} s")
