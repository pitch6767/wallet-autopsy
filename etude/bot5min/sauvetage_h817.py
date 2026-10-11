"""BOT95 — H817 : moteur de sauvetage prédictif et progressif (Pitch, 11.10.2026 21:35). Hors ligne ; aucun ordre ; R4, H816 et fantômes
inchangés ; période réservée (≥ 13.10) jamais lue. PROTOCOLE VERSIONNÉ AVANT CALCUL (ce fichier tel que committé).

Positions initiales (identiques pour toutes les politiques) : décisions uniques de Bot95 (premier signal par cycle et par côté, tous prix),
mise 20 $ au prix ≤ a0, exécutée contre le carnet de Dublin à décision + 164 ms (comme H816 ; sous-ensemble H816 = prix 0,20–0,50 rapporté à part).
Décisions de sortie : toutes les 500 ms, de 0,5 s après l'achat jusqu'à 3 s avant la fin, avec les seules données reçues à cet instant.
Vente = ordre preneur limité au meilleur acheteur VU à la décision, exécuté contre le carnet à décision + 164 ms (dans la limite de la quantité
affichée ≥ ce prix ; le reste n'est pas vendu) ; frais preneur 0,07·p·(1−p). Aucune exécution à un meilleur prix futur.
P_win = modèle de Dublin recalculé (copie de proba(), mêmes flux) au moment de la décision.
Sélection chronologique : réglages choisis sur la 1re moitié des cycles (apprentissage), mesurés UNE fois sur la 2e moitié (test).
Usage : python3 etude/bot5min/sauvetage_h817.py dossier_cycles → etude/bot5min/resultat_sauvetage_h817.md"""
import json, os, sys, glob, math, time, collections, itertools, bisect
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, ICI)
import latence_h766 as LH, modele_dublin as MD, queue_race_phase12 as Q
HORS_ECH = 1791849600; SORTIE = os.path.join(ICI, "resultat_sauvetage_h817.md")
MISE = 20.0; EXEC = 164; PAS = 500
fee = lambda p: 0.07 * p * (1 - p)
rng = np.random.default_rng(817)

# ---- grilles FIXÉES avant calcul
G_SELL = list(itertools.product((0.0, 0.02, 0.05, 0.10), (0.25, 0.5, 1.0)))            # marge m, fraction f (une fois)
G_ECHELLE = list(itertools.product((0.02, 0.05, 0.10), (0.2, 0.33)))                 # marge m, fraction à chaque palier (≥ 2 s d'écart)
G_BUDGET = list(itertools.product((0.10, 0.20), (0.5, 0.7)))                         # dégradation d, plafond de perte L (part du coût)
G_REBOND = list(itertools.product((0.10, 0.20), (0.05, 0.10, 0.15), (0.5, 1.0)))     # dégradation d, rebond x, fraction
G_STOP = (0.10, 0.20)                                                                  # stop naïf : vendre tout si acheteur ≤ prix − s


def vendre(Lc, lim, q):
    """Lc = liste [(prix acheteur millièmes, taille)] décroissante ; vente preneur ≥ lim ; rend (parts vendues, produit net)"""
    v = r = 0.0
    for p, sz in Lc:
        if p < lim or q - v <= 1e-9: break
        k = min(sz, q - v); pp = p / 1000; v += k; r += k * (pp - fee(pp))
    return v, r


def acheter(Lc_a, lim, mise):
    q = c = 0.0
    for p, sz in Lc_a:
        if p > lim: break
        pp = p / 1000; u = pp + fee(pp); k = min(sz, (mise - c) / u)
        if k <= 1e-9: break
        q += k; c += k * u
    return q, c


def ic(G, fn, n=2000):
    G = [g for g in G if g]
    if len(G) < 3: return (float("nan"), float("nan"))
    v = []
    for _ in range(n):
        try: v.append(fn([x for i in rng.integers(0, len(G), len(G)) for x in G[i]]))
        except Exception: pass
    return (float(np.percentile(v, 5)), float(np.percentile(v, 95))) if v else (float("nan"), float("nan"))


def simuler(pos, regle, exec_ms=EXEC):
    """applique une politique à une position ; rend dict(pnl, ventes, produit, frais_vente, interventions, essais)"""
    q = pos["q"]; produit = 0.0; inter = 0; essais = 0; etat = {}
    for k, st_ in enumerate(pos["pas"]):
        if q <= 1e-6: break
        dec = regle(pos, st_, q, etat)
        if not dec: continue
        frac, lim = dec; essais += 1
        Lx = st_["exec"].get(exec_ms)
        if Lx is None: continue
        v, r = vendre(Lx, lim, q * frac)
        if v > 0: q -= v; produit += r; inter += 1
    pnl = produit + q * pos["y"] - pos["c"]
    return dict(pnl=pnl, reste=q, produit=produit, inter=inter, essais=essais)


# ---- politiques (données à l'instant de décision uniquement : st_["pw"], st_["bid"], st_["t"])
def p_hold(pos, s, q, e): return None
def p_sell(m, f):
    def r(pos, s, q, e):
        if e.get("fait") or s["pw"] is None or s["bid"] is None: return None
        if s["bid"] / 1000 - fee(s["bid"] / 1000) >= s["pw"] + m: e["fait"] = True; return (f, s["bid"])
    return r
def p_echelle(m, f):
    def r(pos, s, q, e):
        if s["pw"] is None or s["bid"] is None or s["t"] - e.get("der", -1e18) < 2000: return None
        if s["bid"] / 1000 - fee(s["bid"] / 1000) >= s["pw"] + m: e["der"] = s["t"]; return (f, s["bid"])
    return r
def p_budget(d, L):
    def r(pos, s, q, e):
        if e.get("fait") or s["pw"] is None or s["bid"] is None: return None
        if s["pw"] <= pos["p"] - d and s["bid"] / 1000 >= s["pw"] - 0.02:
            perte_max = L * pos["c"]; b = s["bid"] / 1000 - fee(s["bid"] / 1000)
            # vendre n parts : perte si le jeton perd = c − n·b  ≤ perte_max  →  n ≥ (c − perte_max) / b
            n = min(q, max(0.0, (pos["c"] - perte_max) / max(b, 1e-6))); e["fait"] = True
            return (n / q, s["bid"]) if n > 0 else None
    return r
def p_rebond(d, x, f):
    def r(pos, s, q, e):
        if s["pw"] is None or s["bid"] is None or e.get("fait"): return None
        if "b0" not in e:
            if s["pw"] <= pos["p"] - d: e["b0"] = s["bid"]; e["t0"] = s["t"]
            return None
        if s["t"] - e["t0"] > 30000: e["fait"] = True; return None
        if s["bid"] >= e["b0"] + x * 1000: e["fait"] = True; return (f, s["bid"])
    return r
def p_stop(sv):
    def r(pos, s, q, e):
        if e.get("fait") or s["bid"] is None: return None
        if s["bid"] / 1000 <= pos["p"] - sv: e["fait"] = True; return (1.0, s["bid"])
    return r


def main():
    dossier = sys.argv[1]
    F = {int(os.path.basename(f).split(".")[0]): f for f in glob.glob(os.path.join(dossier, "**", "*.json.gz"), recursive=True)}
    F = {k: v for k, v in F.items() if k < HORS_ECH}
    SIG = sorted([s for s in json.load(open(os.path.join(RACINE, "bot95", "rapide.json")))["signaux"] if s.get("gagnant") and s["start"] in F and s["start"] < HORS_ECH],
                 key=lambda s: (s["start"], s["cote"], s["tDecision"], s["nom"]))
    UNI = {}
    for s in SIG: UNI.setdefault((s["start"], s["cote"]), s)
    cycles = sorted({k[0] for k in UNI}); coupe = cycles[len(cycles) // 2]
    POS = []; CAL = []; LAG = []; G4 = []
    for st in cycles:
        cy = LH.Cycle(F[st]); prev = F.get(st - 300)
        Mo = MD.Modele(MD.charger_ex([f for f in (prev, F[st]) if f]), cy.strike, st + 300)
        S_ = Q.rejouer(cy.C)["serie"]
        def mid_x(t, X):
            i = np.searchsorted(S_[:, 0], t, "right") - 1
            if i < 0 or np.isnan(S_[i, 1]) or np.isnan(S_[i, 3]): return None
            m = (S_[i, 1] + S_[i, 3]) / 2000; return m if X == "Up" else 1 - m
        for (st2, X), s in UNI.items():
            if st2 != st: continue
            t0 = s["tDecision"]; a0m = int(round(s["a0"] * 1000)); y = 1.0 if s["gagne"] else 0.0; fin = (st + 300) * 1000
            grille = [t0 + EXEC + PAS * k for k in range(1, 700) if t0 + EXEC + PAS * k < fin - 3000]
            inst = [t0 + EXEC, t0 + 50, t0 + 100, t0 + 150, t0 + 50 + EXEC, t0 + 100 + EXEC, t0 + 150 + EXEC] + [t for g in grille for t in (g, g + EXEC, g + 264, g + 500)]
            E = cy.etats(inst)
            q, c = acheter(LH.vendeurs(E[t0 + EXEC], X), a0m, MISE)
            # G4 : envoi différé de δ ms ; on revérifie le modèle et le vendeur ; on n'envoie que si P_win − vendeur − frais ≥ 0,10
            g4 = {}
            for dl in (0, 50, 100, 150):
                if dl == 0: g4[dl] = (q, c); continue
                pr = Mo.proba((t0 + dl) / 1000); pw = None if pr is None else (pr[0] if X == "Up" else 1 - pr[0])
                v = LH.vendeurs(E[t0 + dl], X); a = v[0][0] / 1000 if v else None
                ok = pw is not None and a is not None and pw - a - fee(a) >= 0.10
                g4[dl] = acheter(LH.vendeurs(E[t0 + dl + EXEC], X), a0m, MISE) if ok else (0.0, 0.0)
            G4.append(dict(st=st, y=y, g4=g4, p=s["a0"]))
            if q <= 0: continue
            pas = []
            for g in grille:
                pr = Mo.proba(g / 1000); pw = None if pr is None else (pr[0] if X == "Up" else 1 - pr[0])
                b = LH.acheteurs(E[g], X); bid = b[0][0] if b else None
                ex = {d: LH.acheteurs(E[g + d], X)[:12] for d in (EXEC, 264, 500) if E.get(g + d) is not None}
                pas.append(dict(t=g, pw=pw, bid=bid, prof=sum(sz for p, sz in b[:3]) if b else 0, exec=ex, mid=mid_x(g, X)))
            pos = dict(st=st, X=X, y=y, q=q, c=c, p=c / q, nom=s["nom"], a0=s["a0"], pas=pas)
            POS.append(pos)
            for k, s_ in enumerate(pas):
                if k % 4 == 0 and s_["pw"] is not None: CAL.append((st, s_["pw"], s_["mid"], y, (fin - s_["t"]) / 1000))
            # B/J : chutes de P_win ≥ 0,05 en 1 s → l'acheteur vu est-il encore exécutable 164 ms plus tard ?
            for k in range(2, len(pas)):
                a, b_ = pas[k - 2], pas[k]
                if a["pw"] is None or b_["pw"] is None or b_["bid"] is None or a["bid"] is None: continue
                if b_["pw"] - a["pw"] <= -0.05:
                    v, r = vendre(b_["exec"].get(EXEC, []), b_["bid"], 1e9)
                    futur = [pas[j]["bid"] for j in range(k + 1, min(len(pas), k + 7)) if pas[j]["bid"] is not None]
                    LAG.append(dict(st=st, dpw=b_["pw"] - a["pw"], dbid=(b_["bid"] - a["bid"]) / 1000, q_ok=v, bid=b_["bid"],
                                    bid3=(futur[-1] - b_["bid"]) / 1000 if futur else None))
    tr = [p for p in POS if p["st"] < coupe]; te = [p for p in POS if p["st"] >= coupe]
    par_cy = lambda X_: list({x["st"]: [m for m in X_ if m["st"] == x["st"]] for x in X_}.values())
    o = []; w = o.append
    w("# Bot95 — H817 : moteur de sauvetage prédictif et progressif — PRÉLIMINAIRE (hors ligne)\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. Positions initiales : {len(POS)} décisions uniques exécutées (mise 20 $, 164 ms) sur "
      f"{len({p['st'] for p in POS})} cycles Dublin ; apprentissage {len(tr)} / test {len(te)} (coupure {time.strftime('%H:%M', time.gmtime(coupe))} UTC). "
      "Aucun ordre ; R4, H816 et fantômes inchangés ; période réservée non lue.\n")

    # ======== AUDIT
    w("## 0. Audit des données (livrable 1)\n")
    w("| Donnée | Disponible | Limite |\n|---|---|---|")
    w("| Carnet Polymarket (jeton Up ; Down = miroir) | oui, cycles Dublin | changements suivis à ±3 c du meilleur prix ; carnet complet toutes les 10 s → profondeur lointaine approximative |")
    w("| Transactions des deux jetons, heure ms | oui | — |")
    w("| Binance / Bybit / OKX / Coinbase, Chainlink (RTDS + PolyBolt) | oui, une valeur par 50 ms | ticks intermédiaires perdus (modèle recalculé fidèle à ±0,005 pour ~3/4 des signaux) |")
    w("| Prix à battre (strike), moyennes de règlement | oui (strike enregistré ; règlement officiel) | — |")
    w("| Annulation d'un ordre preneur pendant le retard | **impossible** (doc Polymarket : « pending and cannot be canceled ») | G2 réglé : seule l'option « envoi différé » (G4) reste |")
    w("| Retard preneur actuel | 150 ms (changelog du 04.09.2026) ; la page « order lifecycle » mentionne encore 250 ms | testé à 164, 264 et 500 ms |")
    w("| Couverture par la jambe inverse | carnet Down = miroir du carnet Up | **acheter Down à 1 − acheteur(Up) = vendre Up au même prix, mêmes frais, même profondeur** (voir §3) |")
    w(f"| Positions | {len(POS)} | une seule journée : faible puissance |\n")

    # ======== A : calibration
    w("## 1. H817-A — Calibration de la probabilité de victoire (pendant la vie des positions)\n")
    w("| P_win modèle | Observations | Victoire observée | Milieu Polymarket moyen |\n|---|---|---|---|")
    C = np.array([(pw, (m if m is not None else np.nan), y) for _, pw, m, y, _ in CAL])
    for lo, hi in ((0, .1), (.1, .3), (.3, .5), (.5, .7), (.7, .9), (.9, 1.01)):
        mk = (C[:, 0] >= lo) & (C[:, 0] < hi)
        if mk.sum(): w(f"| {lo:.1f}–{min(hi, 1):.1f} | {int(mk.sum())} | {100 * C[mk, 2].mean():.0f} % | {100 * np.nanmean(C[mk, 1]):.0f} % |")
    okm = ~np.isnan(C[:, 1])
    w(f"\nBrier : modèle {np.mean((C[okm, 0] - C[okm, 2]) ** 2):.3f} ; milieu Polymarket {np.mean((C[okm, 1] - C[okm, 2]) ** 2):.3f} (plus bas = mieux ; observations corrélées dans une même position).\n")

    # ======== B/J : retard du carnet
    w("## 2. H817-B / J — Le carnet réagit-il en retard sur la probabilité ?\n")
    if LAG:
        w(f"Chutes de P_win ≥ 5 points en 1 s : {len(LAG)} (sur {len({x['st'] for x in LAG})} cycles). Au même instant, l'acheteur avait déjà baissé de "
          f"{100 * np.median([x['dbid'] for x in LAG]):+.1f} c (médiane) pour une chute de P_win de {100 * np.median([x['dpw'] for x in LAG]):+.1f} points.")
        w(f"- Vente à l'acheteur vu, exécutée 164 ms plus tard : au moins une part exécutable dans {100 * np.mean([x['q_ok'] > 0 for x in LAG]):.0f} % des cas "
          f"(quantité médiane {np.median([x['q_ok'] for x in LAG]):.0f} parts).")
        b3 = [x["bid3"] for x in LAG if x["bid3"] is not None]
        if b3: w(f"- L'acheteur 3 s plus tard a encore baissé de {100 * np.median(b3):+.1f} c (médiane) ; il a remonté dans {100 * np.mean([v > 0 for v in b3]):.0f} % des cas.\n")

    # ======== C/D/O/H/L : politiques
    POL = [("HOLD", p_hold)] + [(f"SELL m={m} f={f}", p_sell(m, f)) for m, f in G_SELL] + [(f"ÉCHELLE m={m} f={f}", p_echelle(m, f)) for m, f in G_ECHELLE] \
          + [(f"BUDGET d={d} L={L}", p_budget(d, L)) for d, L in G_BUDGET] + [(f"REBOND d={d} x={x} f={f}", p_rebond(d, x, f)) for d, x, f in G_REBOND] \
          + [(f"STOP naïf −{s}", p_stop(s)) for s in G_STOP]
    RES = {nom: [simuler(p, r) for p in POS] for nom, r in POL}
    idx = {id(p): i for i, p in enumerate(POS)}
    def bilan(nom, X_, res=None):
        R = res or RES[nom]; H = RES["HOLD"]
        ii = [idx[id(p)] for p in X_]
        pn = [R[i]["pnl"] for i in ii]; dh = [R[i]["pnl"] - H[i]["pnl"] for i in ii]
        evit = sum(R[i]["pnl"] - H[i]["pnl"] for i in ii if POS[i]["y"] == 0 and R[i]["pnl"] > H[i]["pnl"])
        aband = sum(H[i]["pnl"] - R[i]["pnl"] for i in ii if POS[i]["y"] == 1 and R[i]["pnl"] < H[i]["pnl"])
        sortis_gagnants = sum(1 for i in ii if POS[i]["y"] == 1 and R[i]["reste"] < POS[i]["q"] - 1e-6)
        cum = np.cumsum(pn); dd = float(np.max(np.maximum.accumulate(np.concatenate([[0], cum]))[1:] - cum)) if len(cum) else 0
        pos_cy = par_cy(X_)
        cd = ic(pos_cy, lambda z: sum(R[idx[id(p)]]["pnl"] - H[idx[id(p)]]["pnl"] for p in z) / len(z))
        top = sorted(pn, reverse=True)[:5]
        return dict(tot=sum(pn), dh=sum(dh), dhm=np.mean(dh), cd=cd, pd=sum(pn) / sum(POS[i]["c"] for i in ii), med=float(np.median(pn)),
                    g=np.mean([POS[i]["y"] for i in ii]), dd=dd, pire=min(pn), evit=evit, aband=aband, sg=sortis_gagnants,
                    inter=sum(R[i]["inter"] for i in ii), essais=sum(R[i]["essais"] for i in ii), top5=100 * sum(top) / sum(pn) if sum(pn) > 0 else float("nan"))
    ENT = ("| Politique | P&L ($) | vs HOLD ($) | vs HOLD par position (IC 90 %) | Par $ engagé | Médiane | Drawdown | Pire | Pertes évitées | Gains abandonnés | "
           "Gagnants sortis | Ventes exécutées / tentées | 5 meilleurs / total |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    def ligne(nom, X_, res=None, lab=None):
        r = bilan(nom, X_, res)
        w(f"| {lab or nom} | {r['tot']:+.1f} | {r['dh']:+.1f} | {r['dhm']:+.2f} [{r['cd'][0]:+.2f} ; {r['cd'][1]:+.2f}] | {100 * r['pd']:+.1f} % | {r['med']:+.2f} | "
          f"{r['dd']:.1f} | {r['pire']:+.1f} | {r['evit']:+.1f} | {r['aband']:+.1f} | {r['sg']} | {r['inter']} / {r['essais']} | {r['top5']:.0f} % |")
    w("## 3. H817-D / K — Couverture par la jambe inverse\n")
    w("Fait de structure : le meilleur vendeur de Down est exactement 1 − meilleur acheteur de Up (mêmes ordres, appariés par Polymarket), et les frais "
      "0,07·q·(1−q) sont identiques pour q = 1 − p. Acheter n parts de la jambe inverse verrouille donc exactement le même résultat que vendre n parts "
      "de la position, à la même profondeur. La seule différence : la couverture immobilise le capital jusqu'au règlement (ou demande une fusion). "
      "Aucun arbitrage n'existe tant que vendeur Up + vendeur Down ≥ 1 $ (vérifié : la somme des deux meilleurs vendeurs n'est jamais < 1 $ dans nos carnets "
      "puisque le vendeur Down EST le miroir de l'acheteur Up). → Les tests de couverture se confondent avec les tests de vente partielle ci-dessous.\n")
    for groupe, nomsel in (("SELL", "SELL"), ("ÉCHELLE", "ÉCHELLE"), ("BUDGET", "BUDGET"), ("REBOND", "REBOND")):
        cands = [n for n, _ in POL if n.startswith(nomsel)]
        best = max(cands, key=lambda n: bilan(n, tr)["dh"])
        w(f"## 4. {groupe} — réglage choisi sur l'apprentissage : **{best}** (parmi {len(cands)})\n")
        w(ENT)
        for lab, X_ in (("test", te), ("apprentissage", tr), ("tout", POS)):
            ligne("HOLD", X_, lab=f"HOLD — {lab}"); ligne(best, X_, lab=f"{best} — {lab}")
        w("")
    w("## 5. Référence : stop naïf (pour mesurer le coût des faux sauvetages)\n"); w(ENT)
    for s in G_STOP: ligne(f"STOP naïf −{s}", POS)
    # sensibilité à la latence pour les meilleurs réglages (sur tout)
    w("\n## 6. Sensibilité à la latence et aux frais (réglages choisis sur l'apprentissage, toutes positions)\n")
    w("| Politique | 164 ms : vs HOLD ($) | 264 ms | 500 ms |\n|---|---|---|---|")
    for nomsel in ("SELL", "ÉCHELLE", "BUDGET", "REBOND"):
        cands = [(n, r) for n, r in POL if n.startswith(nomsel)]
        n_, r_ = max(cands, key=lambda nr: bilan(nr[0], tr)["dh"])
        cells = []
        for ex in (EXEC, 264, 500):
            R = [simuler(p, r_, ex) for p in POS]
            cells.append(f"{sum(R[i]['pnl'] - RES['HOLD'][i]['pnl'] for i in range(len(POS))):+.1f}")
        w(f"| {n_} | " + " | ".join(cells) + " |")
    # sous-ensemble H816
    w("\n## 7. Sous-ensemble H816 (prix 0,20–0,50) — mêmes réglages\n"); w(ENT)
    H8 = [p for p in POS if 0.20 <= p["a0"] <= 0.50]
    ligne("HOLD", H8, lab="HOLD — H816")
    for nomsel in ("SELL", "ÉCHELLE", "BUDGET", "REBOND"):
        n_ = max([n for n, _ in POL if n.startswith(nomsel)], key=lambda n: bilan(n, tr)["dh"]); ligne(n_, H8, lab=f"{n_} — H816")
    # G4
    w("\n## 8. H817-G — Contrôle avant exécution (envoi différé ; un ordre preneur en retard ne peut pas être annulé)\n")
    w("Avant d'envoyer, on attend δ ms, on recalcule P_win et le meilleur vendeur, et on n'envoie que si P_win − vendeur − frais ≥ 0,10 ; exécution à δ + 164 ms.\n")
    w("| Envoi | Positions exécutées | P&L ($) | vs immédiat ($) | IC 90 % par position |\n|---|---|---|---|---|")
    base = lambda x: x["g4"][0][0] * x["y"] - x["g4"][0][1]
    for dl in (0, 50, 100, 150):
        f = lambda x, dl=dl: x["g4"][dl][0] * x["y"] - x["g4"][dl][1]
        c_ = ic(par_cy(G4), lambda z: float(np.mean([f(x) - base(x) for x in z])))
        w(f"| {'immédiat' if dl == 0 else f'différé {dl} ms'} | {sum(1 for x in G4 if x['g4'][dl][0] > 0)} | {sum(f(x) for x in G4):+.1f} | {sum(f(x) - base(x) for x in G4):+.1f} | [{c_[0]:+.2f} ; {c_[1]:+.2f}] |")
    w("\n## 9. Recommandation par module\n- Voir les tableaux : un module n'est conservé que si son amélioration vs HOLD est positive sur le TEST avec un IC par cycles > 0.\n")
    w("## Limites\n- Une journée, ~50 cycles, ~100 positions : faible puissance.\n- Profondeur au-delà de ±3 c approximative.\n- P_win recalculé hors ligne.\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
