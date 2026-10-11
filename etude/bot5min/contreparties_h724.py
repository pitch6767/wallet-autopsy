"""BOT95 — COUNTERPARTY INTELLIGENCE LAB, H724–H765 (Pitch, 11.10.2026 16:29). Lecture seule, hors ligne, aucun ordre, aucun fantôme touché.
Période réservée (≥ 13.10 00:00 UTC) jamais lue. Aucune transaction postérieure au signal n'entre dans une variable « avant signal ».

Tests : A (correspondances), B (trois wallets : inventaire, coût, profits), C (flux avant signal), D (calibration avec / sans identité),
E (Reverse Bot95), F (veto / confirmation, filtre de flux global), G (placebo des identités), plus H727 (empreinte), H728 (sélection),
H765 (disponibilité temporelle).

Règles de disponibilité (H765) :
- l'API Data date à la SECONDE ; une transaction datée de la seconde s du signal peut être postérieure → on n'utilise que ts ≤ floor(t0) − 1.
- l'identité des wallets n'est pas dans le flux carnet temps réel ; on la suppose disponible avec un délai D (0, 2, 5 s) → variante ts ≤ floor(t0) − 1 − D.
Exécution simulée : prix réellement achetable 250 ms après la décision (délai preneur 150 ms + trajet), enregistré par Dublin (champ « apres »).
Usage : python3 etude/bot5min/contreparties_h724.py makers_suivi.json dossier_cycles → etude/bot5min/resultat_contreparties_h724.md"""
import json, os, sys, glob, collections, math, time, random
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, ICI)
HORS_ECH = 1791849600; SORTIE = os.path.join(ICI, "resultat_contreparties_h724.md")
PREFIXES = ("0xf9b7876b", "0x4c949794", "0x568b0798")
FEN = (60, 30, 10, 3, 1)
frais = lambda p: 0.07 * p * (1 - p)
rng = np.random.default_rng(724)


def boot(groupes, fn, n=2000):
    """IC 90 % par rééchantillonnage de CYCLES (groupes = liste de listes d'éléments)"""
    G = [g for g in groupes if g]
    if len(G) < 3: return (float("nan"), float("nan"))
    v = []
    for _ in range(n):
        s = [x for i in rng.integers(0, len(G), len(G)) for x in G[i]]
        try: r = fn(s)
        except ZeroDivisionError: continue
        if r is not None and not math.isnan(r): v.append(r)
    return (np.percentile(v, 5), np.percentile(v, 95)) if v else (float("nan"), float("nan"))


def sens_x(out, side, X):
    """+1 si la transaction AUGMENTE l'exposition du wallet au côté X (achète X ou vend l'autre), −1 sinon"""
    return 1 if (out == X) == (side == "BUY") else -1


def reconstruire(mk, W):
    """inventaire FIFO de chaque wallet de W dans un marché ; ventes au-delà du stock = split déduit (≡ achat de l'autre côté à 1 − p).
    Rend : par wallet la liste des ventes [(ts, issue, q, prix, q_stock, cout_stock, q_split, inv_avant{Up,Down})] et le bilan du marché."""
    g = mk["gagnant"]; R = {}
    ex = sorted((x for x in mk["ex"] if x[0] in W), key=lambda x: (x[6], 0 if x[3] == "BUY" else 1))
    for w in W:
        lots = {"Up": collections.deque(), "Down": collections.deque()}; ventes = []; real = 0.0; cash = 0.0; nsplit = 0.0
        for ww, role, out, side, sz, p, ts in ex:
            if ww != w: continue
            if side == "BUY":
                lots[out].append([sz, p]); cash -= sz * p
            else:
                inv = {k: sum(l[0] for l in v) for k, v in lots.items()}
                reste = sz; qs = 0.0; cs = 0.0
                while reste > 1e-9 and lots[out]:
                    l = lots[out][0]; q = min(reste, l[0]); qs += q; cs += q * l[1]; l[0] -= q; reste -= q
                    if l[0] <= 1e-9: lots[out].popleft()
                if reste > 1e-9:                                   # split déduit : la jambe vendue coûte p, l'autre 1 − p (gardée)
                    autre = "Down" if out == "Up" else "Up"; lots[autre].append([reste, 1 - p]); nsplit += reste; cash -= reste
                real += qs * p - cs; cash += sz * p
                ventes.append(dict(ts=ts, out=out, q=sz, p=p, role=role, q_stock=qs, cout=(cs / qs if qs else None), q_split=reste, inv=inv))
        resid = {k: sum(l[0] for l in v) for k, v in lots.items()}
        regl = sum(q for k, q in resid.items() if k == g)
        R[w] = dict(ventes=ventes, realise=real, cash=cash, regl=regl, pnl=cash + regl, resid=resid, split=nsplit)
    return R


def logit(p): p = min(max(p, 1e-4), 1 - 1e-4); return math.log(p / (1 - p))


def ajuster(X, y, l2=1.0):
    """régression logistique (Newton, pénalité L2 hors constante)"""
    X = np.column_stack([np.ones(len(X)), X]); b = np.zeros(X.shape[1]); P = np.eye(X.shape[1]) * l2; P[0, 0] = 0
    for _ in range(50):
        p = 1 / (1 + np.exp(-X @ b)); g = X.T @ (p - y) + P @ b; H = X.T @ (X * (p * (1 - p))[:, None]) + P
        b -= np.linalg.solve(H, g)
    return b


def predire(b, X): X = np.column_stack([np.ones(len(X)), X]); return 1 / (1 + np.exp(-X @ b))


def ll(p, y): p = np.clip(p, 1e-4, 1 - 1e-4); return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def brier(p, y): return float(np.mean((p - y) ** 2))


def main():
    base = json.load(open(sys.argv[1])); dossier = sys.argv[2] if len(sys.argv) > 2 else None
    TOUS = {int(k): v for k, v in base["marches"].items() if int(k) < HORS_ECH}
    M = {k: v for k, v in TOUS.items() if not v.get("tronque")}
    adr = {x[0] for mk in M.values() for x in mk["ex"]}
    TROIS = [next(a for a in adr if a.startswith(p)) for p in PREFIXES if any(a.startswith(p) for a in adr)]
    # résultats globaux par wallet (makers) — pour les classements
    pnl = collections.Counter(); vol = collections.Counter(); nmk = collections.defaultdict(set); tmk = collections.defaultdict(list)
    for st, mk in M.items():
        g = mk["gagnant"]
        for w, role, out, side, sz, p, ts in mk["ex"]:
            if role != "M": continue
            win = 1.0 if out == g else 0.0; vol[w] += sz * p; pnl[w] += sz * (win - p) if side == "BUY" else sz * (p - win); nmk[w].add(st)
    SIG_all = [s for s in json.load(open(os.path.join(RACINE, "bot95", "rapide.json")))["signaux"] if s.get("gagnant") and s["start"] < HORS_ECH]
    SIG = sorted([s for s in SIG_all if s["start"] in M], key=lambda s: s["tDecision"])
    cycles = sorted({s["start"] for s in SIG}); coupe = cycles[len(cycles) // 2]          # séparation chronologique par cycle
    # carnet Dublin pour le côté opposé (Reverse)
    SER = {}
    if dossier:
        import fast_fenetre as FF, queue_race_phase12 as Q
        for fn in glob.glob(os.path.join(dossier, "**", "*.json.gz"), recursive=True):
            st = int(os.path.basename(fn).split(".")[0])
            if st in cycles and st not in SER:
                try: SER[st] = Q.rejouer(FF.normaliser(fn))["serie"]
                except Exception: pass

    o = []; w_ = o.append
    w_("# Bot95 — Counterparty Intelligence Lab, H724–H765 — PRÉLIMINAIRE\n")
    w_(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. Marchés lus avant le 13.10 : {len(TOUS)} dont {len(TOUS) - len(M)} tronqués (≥ 10 000 exécutions, exclus). "
       f"Signaux Bot95 réglés : {len(SIG_all)} ; sur des marchés complets : **{len(SIG)}**, répartis sur **{len(cycles)} cycles** (les variantes du même cycle ne sont pas "
       f"indépendantes : les intervalles de confiance rééchantillonnent des cycles). Séparation chronologique : apprentissage = cycles < {time.strftime('%d.%m %H:%M', time.gmtime(coupe))} UTC, test = après. "
       f"Cycles avec carnet Dublin (Reverse) : {len(SER)}. Les trois wallets : {', '.join('`' + w + '`' for w in TROIS)}.\n")
    w_("**Biais de sélection à garder en tête :** les trois wallets ont été repérés sur ces mêmes signaux (E1). Tout résultat « avec les trois wallets » est donc "
       "en partie dans l'échantillon. Le contrôle honnête est la version chronologique (wallets choisis sur la première moitié, mesurés sur la seconde) et le placebo.\n")

    # ================= Reconstruction par marché pour TOUS les makers qui vendent nos billets
    REC = {}
    def rec(st):
        if st not in REC:
            mk = M[st]; REC[st] = reconstruire(mk, {x[0] for x in mk["ex"]})
        return REC[st]

    # ================= H724 / Test A
    w_("## 1. H724 / Test A — Les signaux et leurs correspondances maker (livrables 1, 2, 3)\n")
    LIG = []
    for s in SIG:
        st = s["start"]; mk = M[st]; t0 = s["tDecision"] / 1000; T0 = int(t0); X = s["cote"]; a0 = s["a0"]
        ap = s.get("apres") or {}; q250 = (ap.get("250") or {}).get("q", 0) or 0; c250 = (ap.get("250") or {}).get("c", 0) or 0
        q100 = (ap.get("100") or {}).get("q", 0) or 0
        corr = []
        for w, role, out, side, sz, p, ts in mk["ex"]:
            if role != "M" or not (T0 - 1 <= ts <= T0 + 10): continue
            if out == X and side == "SELL" and p <= a0 + 1e-9: corr.append((w, ts, sz, p, "vend X"))
            elif out != X and side == "BUY" and p >= 1 - a0 - 1e-9: corr.append((w, ts, sz, 1 - p, "achète l'autre (mint)"))
        prix_egal = [c for c in corr if abs(c[3] - a0) < 1e-9]
        contemp = [c for c in corr if c[1] == T0]
        avant = [c for c in corr if c[1] == T0 - 1]
        apres_ = [c for c in corr if c[1] > T0]
        pps = (c250 / q250) if q250 > 0 else None
        LIG.append(dict(s=s, st=st, X=X, a0=a0, mod=s["modele"], q0=s["q0"], q250=q250, q100=q100, pps=pps, y=1.0 if s["gagne"] else 0.0,
                        pnlA=((1.0 if s["gagne"] else 0.0) - pps) if pps else None, corr=corr, egal=prix_egal, contemp=contemp, avant=avant, apres=apres_,
                        trois=[c for c in corr if c[0] in TROIS], restant=s["restant_s"], nom=s["nom"], t0=t0, T0=T0))
    n = len(LIG)
    cnt = lambda f: sum(1 for L in LIG if f(L))
    w_(f"| Catégorie (sur {n} signaux) | Signaux | Lecture |\n|---|---|---|")
    w_(f"| Au moins une vente maker du côté Bot95 au prix du signal ou mieux, de −1 s à +10 s | {cnt(lambda L: L['corr'])} | correspondance « dans les 10 s » (c'est le chiffre 157 d'E1, recalculé) |")
    w_(f"| … dont au même prix exact | {cnt(lambda L: L['egal'])} | |")
    w_(f"| … dans la seconde de la décision (contemporaine, ordre inconnu à la seconde) | {cnt(lambda L: L['contemp'])} | ambigu : avant ou après nous |")
    w_(f"| … dans la seconde précédente | {cnt(lambda L: L['avant'])} | l'offre a été servie AVANT nous (par un autre preneur) |")
    w_(f"| … uniquement après la seconde de décision | {cnt(lambda L: L['apres'] and not L['contemp'] and not L['avant'])} | n'est pas une information disponible au signal |")
    w_(f"| Offre présente au signal (carnet Dublin, quantité au prix du signal) | {cnt(lambda L: L['q0'] > 0)} | fait mesuré |")
    w_(f"| Encore achetable 100 ms après | {cnt(lambda L: L['q100'] > 0)} | borne optimiste |")
    w_(f"| **Encore achetable 250 ms après (exécution simulée retenue)** | {cnt(lambda L: L['q250'] > 0)} | délai preneur 150 ms + trajet |")
    w_(f"| Impossible après latence (plus rien au prix) | {cnt(lambda L: L['q250'] <= 0)} | |")
    w_("\nUne correspondance dans les 10 s **n'est pas** un remplissage garanti : la plupart des ventes maker servent d'autres preneurs.\n")
    # wallets impliqués
    srv = collections.Counter(); srvq = collections.Counter(); mint = collections.Counter()
    for L in LIG:
        vus = set()
        for w, ts, sz, p, typ in L["corr"]:
            srvq[w] += sz; vus.add(w)
            if typ.startswith("achète"): mint[w] += sz
        for w in vus: srv[w] += 1
    w_("**Wallets réellement impliqués (livrable 3)** — top 12 par nombre de signaux servis\n")
    w_("| Wallet | Signaux servis | Parts | dont « achète l'autre côté » | Marchés actifs | Résultat global par $ |\n|---|---|---|---|---|---|")
    for w, k in srv.most_common(12):
        w_(f"| `{w[:10]}…`{' ★' if w in TROIS else ''} | {k} | {srvq[w]:.0f} | {100 * mint[w] / srvq[w]:.0f} % | {len(nmk[w])} | {100 * pnl[w] / vol[w] if vol[w] else 0:+.1f} % |")
    w_(f"\nNombre total de wallets distincts : {len(srv)}. ★ = les trois wallets étudiés.\n")
    # tableau des signaux (livrable 1) — en annexe compacte
    ANN = ["| Cycle (UTC) | Variante | Côté | Prix | Modèle | Restant | Achetable 250 ms | Gagné | P&L/part A | Ventes maker ±10 s | dont 3 wallets | Δt 1re (s) |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for L in LIG:
        d1 = min((c[1] - L["t0"] for c in L["corr"]), default=None)
        ANN.append(f"| {time.strftime('%H:%M', time.gmtime(L['st']))} | {L['nom'][:22]} | {L['X']} | {L['a0']:.2f} | {L['mod']:.2f} | {L['restant']:.0f} | {L['q250']:.0f} | {'oui' if L['y'] else 'non'} | "
                   f"{'%+.2f' % L['pnlA'] if L['pnlA'] is not None else '—'} | {sum(c[2] for c in L['corr']):.0f} | {sum(c[2] for c in L['trois']):.0f} | {'%+.1f' % d1 if d1 is not None else '—'} |")

    # ================= Test B / H746–H749
    w_("## 2. Test B — Les trois wallets : inventaire, coût, profits (livrables 4, 5, 6, 7)\n")
    w_("Méthode : inventaire reconstruit marché par marché (premier entré, premier sorti). Une vente sans stock = **split déduit** : la jambe vendue coûte "
       "son prix de vente, l'autre jambe (gardée) coûte 1 − p. Économiquement, c'est identique à **acheter le côté opposé** à 1 − p. Transferts et splits "
       "hors marché non vus (activités pas encore collectées) → les inventaires peuvent être incomplets.\n")
    def bilan(W, filtre_signal=False):
        A = collections.defaultdict(float)
        for st in M:
            R = rec(st)
            for w in W:
                r = R.get(w)
                if not r: continue
                A["pnl"] += r["pnl"]; A["realise"] += r["realise"]; A["split"] += r["split"]
                for v in r["ventes"]:
                    A["vq"] += v["q"]; A["vstock"] += v["q_stock"]; A["vsplit"] += v["q_split"]; A["v$"] += v["q"] * v["p"]
                    if v["q_stock"]: A["cout$"] += v["cout"] * v["q_stock"]; A["vstock$"] += v["q_stock"] * v["p"]
                    autre = "Down" if v["out"] == "Up" else "Up"
                    expo_av = v["inv"][v["out"]] - v["inv"][autre]
                    if v["q_stock"] > 0: A["reduit"] += v["q"] if abs(expo_av - v["q"]) < abs(expo_av) else 0
        return A
    w_("| Groupe | Résultat total | dont réalisé sur ventes depuis stock | Parts vendues | depuis stock | via split (≡ achat de l'autre côté) | Prix moyen de vente (stock) | Coût moyen (stock) | Ventes qui réduisent l'exposition |\n|---|---|---|---|---|---|---|---|---|")
    autres_srv = [w for w in srv if w not in TROIS]
    for nom, W in [(w[:10] + "…", [w]) for w in TROIS] + [("les 3 ensemble", TROIS), ("autres makers qui servent nos signaux", autres_srv)]:
        A = bilan(W)
        if not A["vq"]: continue
        w_(f"| {nom} | {A['pnl']:+.0f} $ | {A['realise']:+.0f} $ | {A['vq']:.0f} | {100 * A['vstock'] / A['vq']:.0f} % | {100 * A['vsplit'] / A['vq']:.0f} % | "
           f"{A['vstock$'] / A['vstock'] if A['vstock'] else 0:.3f} | {A['cout$'] / A['vstock'] if A['vstock'] else 0:.3f} | {100 * A['reduit'] / A['vq']:.0f} % |")
    w_("\n**Profil des trois wallets (tous marchés complets)** — achats / ventes, paires et jambes résiduelles\n")
    w_("| Wallet | Achats (parts) | Ventes (parts) | Coût moyen d'une paire Up+Down | Parts appariées | Résultat des paires | Résultat des jambes résiduelles | Total |\n|---|---|---|---|---|---|---|---|")
    for w in TROIS:
        ach = ven = pq = pr = rr = 0.0; pc = 0.0
        for st, mk in M.items():
            E_ = [x for x in mk["ex"] if x[0] == w]
            if not E_: continue
            g = mk["gagnant"]; q = {"Up": 0.0, "Down": 0.0}; c = {"Up": 0.0, "Down": 0.0}
            for _, role, out, side, sz, p, ts in E_:
                if side == "BUY": q[out] += sz; c[out] += sz * p; ach += sz
                else: q[out] -= sz; c[out] -= sz * p; ven += sz
            m = max(0.0, min(q["Up"], q["Down"]))
            if m > 0 and q["Up"] > 0 and q["Down"] > 0:
                cu, cd = c["Up"] / q["Up"], c["Down"] / q["Down"]; pq += m; pc += m * (cu + cd); pr += m * (1 - cu - cd)
                for k, ck in (("Up", cu), ("Down", cd)): rr += (q[k] - m) * ((1.0 if g == k else 0.0) - ck)
            else:
                for k in q:
                    if q[k] > 0: rr += q[k] * ((1.0 if g == k else 0.0)) - c[k]
        w_(f"| `{w[:10]}…` | {ach:.0f} | {ven:.0f} | {pc / pq if pq else 0:.3f} | {pq:.0f} | {pr:+.0f} $ | {rr:+.0f} $ | {pr + rr:+.0f} $ |")
    w_("")
    cap = [L for L in LIG if L["q250"] > 0]; ncap = [L for L in LIG if L["q250"] <= 0]
    w_(f"Taux de gain des signaux : tous {100 * np.mean([L['y'] for L in LIG]):.0f} % (prix moyen {np.mean([L['a0'] for L in LIG]):.2f}) ; encore achetables à 250 ms "
       f"{100 * np.mean([L['y'] for L in cap]):.0f} % (prix {np.mean([L['a0'] for L in cap]):.2f}) ; partis avant 250 ms {100 * np.mean([L['y'] for L in ncap]):.0f} % (prix {np.mean([L['a0'] for L in ncap]):.2f}).\n")
    # ventes faites AUX signaux Bot95
    w_("\n**Les ventes des trois wallets au moment des signaux (de −1 s à +10 s)**\n")
    VS = []
    for L in LIG:
        R = rec(L["st"])
        for w, ts, sz, p, typ in L["trois"]:
            r = R[w]
            # retrouver la vente correspondante (même seconde, même quantité)
            v = next((v for v in r["ventes"] if v["ts"] == ts and abs(v["q"] - sz) < 1e-6 and v["out"] == L["X"]), None)
            autre = "Down" if L["X"] == "Up" else "Up"
            if v: VS.append(dict(L=L, w=w, q=sz, p=p, typ="vente depuis stock" if v["q_stock"] >= sz - 1e-6 else ("split déduit" if v["q_stock"] <= 1e-6 else "mixte"),
                                 cout=v["cout"], inv=v["inv"], marche=r["pnl"]))
            else: VS.append(dict(L=L, w=w, q=sz, p=p, typ="achat de l'autre côté (mint)", cout=None, inv=None, marche=r["pnl"]))
    if VS:
        c = collections.Counter(v["typ"] for v in VS); cq = collections.Counter(); [cq.update({v["typ"]: v["q"]}) for v in VS]
        w_("| Type de vente | Ventes | Parts | Coût moyen du stock vendu | Prix moyen | Gain réalisé/part | Billet vendu gagnant | Résultat final du wallet dans ces marchés |\n|---|---|---|---|---|---|---|---|")
        for t in c:
            X_ = [v for v in VS if v["typ"] == t]; q = sum(v["q"] for v in X_)
            cst = [v for v in X_ if v["cout"] is not None]; qc = sum(v["q"] for v in cst)
            cm = sum(v["cout"] * v["q"] for v in cst) / qc if qc else None
            pm = sum(v["p"] * v["q"] for v in X_) / q
            gw = sum(v["q"] for v in X_ if v["L"]["y"]) / q
            mk_ = sum({(v["L"]["st"], v["w"]): v["marche"] for v in X_}.values())
            w_(f"| {t} | {c[t]} | {q:.0f} | {'%.3f' % cm if cm is not None else '—'} | {pm:.3f} | {'%+.3f' % (pm - cm) if cm is not None else '—'} | {100 * gw:.0f} % | {mk_:+.0f} $ |")
        # inventaire au moment de la vente
        avec = [v for v in VS if v["inv"]]
        if avec:
            ex_ = [v["inv"][v["L"]["X"]] - v["inv"]["Down" if v["L"]["X"] == "Up" else "Up"] for v in avec]
            w_(f"\nInventaire juste avant la vente (parts du côté Bot95 moins parts de l'autre côté) : médiane {np.median(ex_):+.0f}, "
               f"long le côté Bot95 dans {100 * np.mean([e > 0 for e in ex_]):.0f} % des cas, court (ou nul) dans {100 * np.mean([e <= 0 for e in ex_]):.0f} %.\n")
        w_(f"Rendement de l'acheteur sur ces billets (Bot95 au même prix) : {100 * sum(v['q'] * ((1 if v['L']['y'] else 0) - v['p']) for v in VS) / sum(v['q'] * v['p'] for v in VS):+.1f} % par $ "
           f"(avant frais), contre {100 * sum(L['y'] - L['a0'] for L in LIG) / sum(L['a0'] for L in LIG):+.1f} % sur tous les signaux.\n")

    # ================= H728 — sélection : les trois wallets vendent-ils de moins bons billets que les autres makers ?
    w_("## 3. H728 — Les trois wallets vendent-ils de moins bons billets que les autres makers ? (livrable 7)\n")
    w_("Toutes les ventes maker (vendre X ou acheter l'autre côté) de tous les marchés complets ; rendement de l'ACHETEUR au règlement ; comparaison à "
       "prix (tranche de 0,10) × minute du cycle identiques.\n")
    ST = collections.defaultdict(lambda: {"t": [0.0, 0.0], "a": [0.0, 0.0]}); par_cycle = collections.defaultdict(list)
    for st, mk in M.items():
        g = mk["gagnant"]
        for w, role, out, side, sz, p, ts in mk["ex"]:
            if role != "M": continue
            if side == "SELL": X, px = out, p
            else: X, px = ("Down" if out == "Up" else "Up"), 1 - p          # acheter l'autre côté = vendre X à 1 − p
            k = (min(int(px * 10), 9), min(int((ts - st) // 60), 4)); grp = "t" if w in TROIS else "a"
            r = (1.0 if g == X else 0.0) - px
            ST[k][grp][0] += sz * r; ST[k][grp][1] += sz * px; par_cycle[st].append((k, grp, sz * r, sz * px))
    def diff(items):
        S_ = collections.defaultdict(lambda: {"t": [0.0, 0.0], "a": [0.0, 0.0]})
        for k, grp, r, c in items: S_[k][grp][0] += r; S_[k][grp][1] += c
        num = den = 0.0
        for k, d in S_.items():
            if d["t"][1] > 0 and d["a"][1] > 0:
                num += d["t"][1] * (d["t"][0] / d["t"][1] - d["a"][0] / d["a"][1]); den += d["t"][1]
        return num / den if den else None
    dv = diff([x for v in par_cycle.values() for x in v]); ci = boot(list(par_cycle.values()), diff, 500)
    tt = [sum(ST[k]["t"][i] for k in ST) for i in (0, 1)]; aa = [sum(ST[k]["a"][i] for k in ST) for i in (0, 1)]
    w_(f"- Rendement brut de l'acheteur : face aux trois wallets {100 * tt[0] / tt[1]:+.1f} % par $ ; face aux autres makers {100 * aa[0] / aa[1]:+.1f} %.")
    w_(f"- **Écart à prix et minute identiques : {100 * dv:+.1f} points** (IC 90 % par cycles [{100 * ci[0]:+.1f} ; {100 * ci[1]:+.1f}]). Négatif = les trois wallets vendent des billets plus mauvais pour l'acheteur.\n")

    # ================= Test C — flux avant signal (H730, H731, H750, H755)
    w_("## 4. Test C — Flux observés AVANT les signaux (livrables 8, 9)\n")
    w_("Variables calculées uniquement avec des transactions datées ≤ seconde de décision − 1 (− délai de disponibilité D). Flux net vers le côté Bot95 "
       "(+ = le groupe achète le côté Bot95 ou vend l'autre ; − = il vend notre côté). Inventaire = position nette (côté Bot95 − autre côté) depuis l'ouverture du marché.\n")
    def flux(L, W, fen, role=None, D=0):
        mk = M[L["st"]]; fin = L["T0"] - 1 - D; deb = fin - fen + 1 if fen else -1
        s_ = 0.0
        for w, r, out, side, sz, p, ts in mk["ex"]:
            if ts > fin or ts < deb: continue
            if role and r != role: continue
            if W is not None and w not in W: continue
            s_ += sens_x(out, side, L["X"]) * sz
        return s_
    GRP = {"3 wallets (makers)": (set(TROIS), "M"), "tous les makers": (None, "M"), "tous les preneurs": (None, "P")}
    for L in LIG:
        L["f"] = {}
        for g, (W, role) in GRP.items():
            for fen in FEN: L["f"][(g, fen)] = flux(L, W, fen, role)
            L["f"][(g, "inv")] = flux(L, W, 0, role)
        for D in (2, 5): L["f"][("3 wallets (makers)", 30, D)] = flux(L, set(TROIS), 30, "M", D)
    cyc_of = lambda X_: list({L["st"]: [l for l in X_ if l["st"] == L["st"]] for L in X_}.values())
    err = lambda X_: float(np.mean([l["y"] - l["mod"] for l in X_])) if X_ else float("nan")
    w_("Erreur Bot95 = gagné (1/0) − probabilité du modèle. Négatif = Bot95 surestime.\n")
    w_("| Groupe | Fenêtre | Signaux avec flux contre nous | erreur | Signaux flux nul | erreur | Signaux flux pour nous | erreur | Écart contre − reste (IC 90 %) |\n|---|---|---|---|---|---|---|---|---|")
    for g in GRP:
        for fen in list(FEN) + ["inv"]:
            k = (g, fen); C_ = [l for l in LIG if l["f"][k] < 0]; Z = [l for l in LIG if l["f"][k] == 0]; P_ = [l for l in LIG if l["f"][k] > 0]
            fn = lambda X_: (err([l for l in X_ if l["f"][k] < 0]) - err([l for l in X_ if l["f"][k] >= 0])) if any(l["f"][k] < 0 for l in X_) and any(l["f"][k] >= 0 for l in X_) else None
            d = fn(LIG); ci = boot(cyc_of(LIG), fn, 800)
            w_(f"| {g} | {'inventaire' if fen == 'inv' else str(fen) + ' s'} | {len(C_)} | {err(C_):+.2f} | {len(Z)} | {err(Z):+.2f} | {len(P_)} | {err(P_):+.2f} | "
               f"{'%+.2f' % d if d is not None else '—'} [{ci[0]:+.2f} ; {ci[1]:+.2f}] |")
    w_("")

    # ================= Test D — calibration (H736, H754, H764)
    w_("## 5. Test D — Calibration avec et sans identité des wallets (livrable 10)\n")
    tr = [l for l in LIG if l["st"] < coupe]; te = [l for l in LIG if l["st"] >= coupe]
    sg = lambda x: math.copysign(math.log1p(abs(x)), x)
    def feats(L, cles): return [logit(L["mod"])] + [sg(L["f"][c]) for c in cles]
    MOD = {"Bot95 brut": None, "Bot95 recalibré": [], "+ 3 wallets (30 s + inventaire)": [("3 wallets (makers)", 30), ("3 wallets (makers)", "inv")],
           "+ flux global (makers + preneurs 30 s)": [("tous les makers", 30), ("tous les preneurs", 30)],
           "+ les deux": [("3 wallets (makers)", 30), ("3 wallets (makers)", "inv"), ("tous les makers", 30), ("tous les preneurs", 30)]}
    ytr = np.array([l["y"] for l in tr]); yte = np.array([l["y"] for l in te])
    w_(f"Apprentissage {len(tr)} signaux / {len({l['st'] for l in tr})} cycles ; test {len(te)} signaux / {len({l['st'] for l in te})} cycles (chronologique, aucun signal commun).\n")
    w_("| Modèle | Log loss test | Brier test | Log loss apprentissage |\n|---|---|---|---|")
    RES = {}
    for nom, cles in MOD.items():
        if cles is None:
            pte = np.array([l["mod"] for l in te]); ptr = np.array([l["mod"] for l in tr])
        else:
            b = ajuster(np.array([feats(l, cles) for l in tr]), ytr); pte = predire(b, np.array([feats(l, cles) for l in te])); ptr = predire(b, np.array([feats(l, cles) for l in tr]))
        RES[nom] = (ll(pte, yte), brier(pte, yte)); w_(f"| {nom} | {ll(pte, yte):.4f} | {brier(pte, yte):.4f} | {ll(ptr, ytr):.4f} |")
    gain_reel = RES["Bot95 recalibré"][0] - RES["+ 3 wallets (30 s + inventaire)"][0]
    w_(f"\nGain de log loss apporté par les trois wallets sur le test : {gain_reel:+.4f} (positif = mieux).\n")

    # ================= Test G — placebo des identités (H743, H764)
    w_("## 6. Test G — Placebo : trois wallets tirés au hasard (livrable 15)\n")
    actifs = [w for w in nmk if len(nmk[w]) >= max(5, min(len(nmk[t]) for t in TROIS) // 2) and w not in TROIS]
    gains = []; ecarts = []
    for _ in range(200):
        W = set(random.Random(len(gains) + 1).sample(actifs, 3))
        for l in LIG: l["fp30"] = flux(l, W, 30, "M"); l["fpinv"] = flux(l, W, 0, "M")
        Xtr = np.array([[logit(l["mod"]), sg(l["fp30"]), sg(l["fpinv"])] for l in tr]); Xte = np.array([[logit(l["mod"]), sg(l["fp30"]), sg(l["fpinv"])] for l in te])
        b = ajuster(Xtr, ytr); gains.append(RES["Bot95 recalibré"][0] - ll(predire(b, Xte), yte))
        C_ = [l for l in LIG if l["fp30"] < 0]; R_ = [l for l in LIG if l["fp30"] >= 0]
        if C_ and R_: ecarts.append(err(C_) - err(R_))
    # placebo des fenêtres courtes (1 s et 3 s), sans réapprentissage
    for fen in (3, 1):
        kf = ("3 wallets (makers)", fen); er = err([l for l in LIG if l["f"][kf] < 0]) - err([l for l in LIG if l["f"][kf] >= 0]); E2 = []
        for i in range(200):
            W = set(random.Random(1000 + i).sample(actifs, 3)); C_ = []; R_ = []
            for l in LIG: (C_ if flux(l, W, fen, "M") < 0 else R_).append(l)
            if len(C_) >= 5 and R_: E2.append(err(C_) - err(R_))
        w_(f"- Fenêtre {fen} s : écart d'erreur vrais wallets {er:+.3f} ; placebo médiane {np.median(E2):+.3f} ; part des placebos aussi négatifs ou plus : **{100 * np.mean([e <= er for e in E2]):.0f} %** ({len(E2)} tirages avec ≥ 5 signaux).")
    # wallets choisis SANS regarder le test : rentables sur les marchés d'apprentissage et qui servent le plus nos signaux d'apprentissage
    ptr_ = collections.Counter(); vtr_ = collections.Counter(); srv_tr = collections.Counter()
    for st, mk in M.items():
        if st >= coupe: continue
        g = mk["gagnant"]
        for w, role, out, side, sz, p, ts in mk["ex"]:
            if role == "M": win = 1.0 if out == g else 0.0; vtr_[w] += sz * p; ptr_[w] += sz * (win - p) if side == "BUY" else sz * (p - win)
    for L in LIG:
        if L["st"] < coupe:
            for w in {c[0] for c in L["corr"]}: srv_tr[w] += 1
    CH = [w for w, _ in srv_tr.most_common() if vtr_[w] and ptr_[w] / vtr_[w] >= 0.01][:3]
    for l in te: l["fc"] = {fen: flux(l, set(CH), fen, "M") for fen in (30, 10, 3, 1)}
    w_(f"- **Version chronologique** (wallets choisis sur l'apprentissage : {', '.join('`' + w[:10] + '…`' for w in CH)} ; "
       f"{len(set(CH) & set(TROIS))} en commun avec les trois) — écart d'erreur sur le TEST, flux contre nous − reste : " +
       " ; ".join(f"{fen} s {err([l for l in te if l['fc'][fen] < 0]) - err([l for l in te if l['fc'][fen] >= 0]):+.3f} (n = {sum(1 for l in te if l['fc'][fen] < 0)})" for fen in (30, 10, 3, 1)
                  if any(l['fc'][fen] < 0 for l in te) and any(l['fc'][fen] >= 0 for l in te)) + "\n")
    k3 = ("3 wallets (makers)", 30)
    e_reel = err([l for l in LIG if l["f"][k3] < 0]) - err([l for l in LIG if l["f"][k3] >= 0]) if any(l["f"][k3] < 0 for l in LIG) else float("nan")
    w_(f"{len(actifs)} makers comparables (actifs sur assez de marchés) ; 200 tirages de trois wallets.\n")
    w_(f"- Gain de log loss test : vrais wallets {gain_reel:+.4f} ; placebo médiane {np.median(gains):+.4f}, 90e centile {np.percentile(gains, 90):+.4f} ; "
       f"part des placebos ≥ réel : **{100 * np.mean([g >= gain_reel for g in gains]):.0f} %**.")
    if ecarts and not math.isnan(e_reel):
        w_(f"- Écart d'erreur Bot95 « flux 30 s contre nous » − reste : vrais wallets {e_reel:+.3f} ; placebo médiane {np.median(ecarts):+.3f} ; "
           f"part des placebos aussi négatifs ou plus : **{100 * np.mean([e <= e_reel for e in ecarts]):.0f} %**.\n")

    # ================= Test E — Reverse Bot95 (H725) et Test F — veto / confirmation (H739–H741, H761–H762)
    w_("## 7. Test E — Reverse Bot95 (livrables 11, 17, 18)\n")
    w_("A = acheter le côté Bot95 au prix achetable 250 ms après la décision (frais compris, quantité réellement présente). "
       "B = acheter le côté OPPOSÉ à son meilleur vendeur 250 ms après (carnet Dublin ; quantité au meilleur niveau ; frais preneur). C = ne rien faire. "
       "Mise : 1 part par signal (le P&L par $ est aussi donné).\n")
    for L in LIG:
        L["pnlB"] = None; L["prixB"] = None
        S = SER.get(L["st"])
        if S is None or not len(S): continue
        i = np.searchsorted(S[:, 0], L["t0"] * 1000 + 250, "right") - 1
        if i < 0: continue
        bb, bq, ba, aq = S[i, 1], S[i, 2], S[i, 3], S[i, 4]
        if L["X"] == "Up": pB, qB = (1 - bb / 1000, bq) if not np.isnan(bb) and bb > 0 else (None, 0)
        else: pB, qB = (ba / 1000, aq) if not np.isnan(ba) and ba > 0 else (None, 0)
        if pB is None or qB <= 0 or pB >= 0.995: continue
        L["prixB"] = pB; L["pnlB"] = (1 - L["y"]) - pB - frais(pB)
    def stats(X_, cle, cout=None):
        v = [l for l in X_ if l[cle] is not None]
        if not v: return None
        r = np.array([l[cle] for l in v]); cum = np.cumsum(r); dd = float(np.max(np.maximum.accumulate(np.concatenate([[0], cum]))[1:] - cum)) if len(cum) else 0
        serie = 0; pire = 0
        for x in r:
            serie = serie + 1 if x < 0 else 0; pire = max(pire, serie)
        c_ = sum((l["pps"] if cle == "pnlA" else l["prixB"]) for l in v)
        jack = sum(1 for l in v if l[cle] > 0 and (l["pps"] if cle == "pnlA" else l["prixB"]) <= 0.25)
        return dict(n=len(v), tot=float(r.sum()), moy=float(r.mean()), parD=float(r.sum() / c_), dd=dd, pire=pire, jack=jack,
                    ci=boot(cyc_of(v), lambda s: float(np.mean([l[cle] for l in s])), 1000), g=float(np.mean([r_ > 0 for r_ in r])))
    w_("| Politique | Échantillon | Exécutés | P&L total (parts) | par signal (IC 90 %) | par $ | Taux de gain | Drawdown max | Pire série de pertes | Jackpots (gain à prix ≤ 0,25) |\n|---|---|---|---|---|---|---|---|---|---|")
    comm = [l for l in LIG if l["pnlA"] is not None and l["pnlB"] is not None]
    for nom_e, E_ in (("tous les signaux", LIG), ("cycles avec carnet Dublin (A et B exécutables)", comm), ("test (2e moitié)", [l for l in comm if l["st"] >= coupe])):
        for pol, cle in (("A — côté Bot95", "pnlA"), ("B — côté opposé", "pnlB")):
            s_ = stats(E_, cle)
            if s_: w_(f"| {pol} | {nom_e} | {s_['n']} | {s_['tot']:+.2f} | {s_['moy']:+.3f} [{s_['ci'][0]:+.3f} ; {s_['ci'][1]:+.3f}] | {100 * s_['parD']:+.1f} % | {100 * s_['g']:.0f} % | {s_['dd']:.2f} | {s_['pire']} | {s_['jack']} |")
        w_(f"| C — rien | {nom_e} | 0 | 0 | 0 | — | — | 0 | 0 | 0 |")
    w_("\nAcheter le côté opposé n'est PAS vendre le billet Bot95 : on paie le vendeur opposé + frais, l'écart vendeur-acheteur est payé deux fois.\n")

    w_("## 8. Test F — Veto et confirmation par contrepartie, contre un filtre de flux global (livrables 12, 13, 14, 18)\n")
    w_("Règles fixées a priori (aucun seuil optimisé) : **veto** = on n'achète pas si le groupe a un flux net CONTRE notre côté sur la fenêtre ; "
       "**confirmation** = on n'achète que si le flux est POUR notre côté. Politique de base = A (côté Bot95, 250 ms).\n")
    w_("| Filtre | Fenêtre / délai | Signaux gardés | Perdants évités | Gagnants supprimés | Jackpots supprimés | P&L marginal (parts) | IC 90 % | P&L gardé sur le test |\n|---|---|---|---|---|---|---|---|---|")
    base_ = [l for l in LIG if l["pnlA"] is not None]
    def ligne_filtre(nom, cle, mode):
        garde = (lambda l: l["f"][cle] >= 0) if mode == "veto" else (lambda l: l["f"][cle] > 0)
        sup = [l for l in base_ if not garde(l)]; kept = [l for l in base_ if garde(l)]
        marg = -sum(l["pnlA"] for l in sup)
        ci = boot(cyc_of(base_), lambda s: -sum(l["pnlA"] for l in s if not garde(l)), 800)
        tst = sum(l["pnlA"] for l in kept if l["st"] >= coupe)
        w_(f"| {mode} {nom} | {cle[1] if isinstance(cle[1], str) else str(cle[1]) + ' s'}{'' if len(cle) < 3 else ' (D = ' + str(cle[2]) + ' s)'} | {len(kept)} / {len(base_)} | "
           f"{sum(1 for l in sup if l['y'] == 0)} | {sum(1 for l in sup if l['y'] == 1)} | {sum(1 for l in sup if l['pnlA'] > 0 and l['pps'] <= 0.25)} | {marg:+.2f} | [{ci[0]:+.2f} ; {ci[1]:+.2f}] | {tst:+.2f} |")
    for mode in ("veto", "confirmation"):
        for fen in (60, 30, 10):
            ligne_filtre("3 wallets", ("3 wallets (makers)", fen), mode)
        ligne_filtre("3 wallets", ("3 wallets (makers)", "inv"), mode)
        for D in (2, 5): ligne_filtre("3 wallets", ("3 wallets (makers)", 30, D), mode)
        for fen in (30, 10):
            ligne_filtre("flux global makers", ("tous les makers", fen), mode); ligne_filtre("flux global preneurs", ("tous les preneurs", fen), mode)
    tA = sum(l["pnlA"] for l in base_ if l["st"] >= coupe)
    w_(f"\nRéférence sans filtre : P&L A total {sum(l['pnlA'] for l in base_):+.2f} parts ; sur le test {tA:+.2f}.\n")

    # ================= H727 — empreinte même opérateur
    w_("## 9. H727 — Empreinte « même opérateur » (statistique seulement)\n")
    w_("| Wallet | Exécutions maker | Taille médiane (parts) | Tailles rondes | Prix médian | Part Up | Part achats | Marchés | Résultat par $ |\n|---|---|---|---|---|---|---|---|---|")
    EXW = {w: [x + [st] for st, mk in M.items() for x in mk["ex"] if x[0] == w and x[1] == "M"] for w in TROIS}
    for w in TROIS:
        E_ = EXW[w]
        if not E_: continue
        sz = np.array([x[4] for x in E_])
        w_(f"| `{w[:10]}…` | {len(E_)} | {np.median(sz):.1f} | {100 * np.mean(np.abs(sz - np.round(sz)) < 1e-6):.0f} % | {np.median([x[5] for x in E_]):.2f} | "
           f"{100 * np.mean([x[2] == 'Up' for x in E_]):.0f} % | {100 * np.mean([x[3] == 'BUY' for x in E_]):.0f} % | {len(nmk[w])} | {100 * pnl[w] / vol[w]:+.1f} % |")
    w_("\n| Paire | Marchés communs (Jaccard) | Secondes communes d'activité | Attendu au hasard (même marchés) |\n|---|---|---|---|")
    for i in range(len(TROIS)):
        for j in range(i + 1, len(TROIS)):
            a, b = TROIS[i], TROIS[j]; ma, mb = nmk[a], nmk[b]
            sa = {(x[7], x[6]) for x in EXW[a]}; sb = {(x[7], x[6]) for x in EXW[b]}
            commun = ma & mb; obs = len(sa & sb)
            att = sum(len({x[6] for x in EXW[a] if x[7] == st}) * len({x[6] for x in EXW[b] if x[7] == st}) / 300 for st in commun)
            w_(f"| {a[:8]} / {b[:8]} | {len(commun)} ({100 * len(commun) / max(1, len(ma | mb)):.0f} %) | {obs} | {att:.0f} |")
    w_("\nTransferts publics, splits / merges hors marché : **non vérifiés** (activités en cours de collecte). Similarité statistique ≠ contrôle commun.\n")

    # ================= H765 — disponibilité temporelle
    w_("## 10. H765 — Audit de disponibilité temporelle (livrable 16)\n")
    w_("- **Fait** : l'API Data date à la seconde. Une transaction datée de la seconde du signal peut être postérieure → exclue de toutes les variables.")
    w_("- **Fait** : le flux carnet temps réel de Polymarket donne prix, taille, côté — pas l'adresse des wallets.")
    w_("- **Hypothèse à mesurer** : l'identité n'arrive qu'avec la chaîne (blocs Polygon ≈ 2 s + délai de soumission) ou l'API Data (délai inconnu). "
       "Les fenêtres 1 et 3 s ne sont donc probablement PAS disponibles en direct ; les tests avec D = 2 et 5 s simulent ce retard.")
    w_("- Les correspondances « dans les 10 s » de la section 1 sont presque toutes postérieures au signal : elles décrivent, elles ne prédisent pas.\n")

    w_("## Limites\n- Une seule journée, ~" + str(len(cycles)) + " cycles : puissance statistique faible ; tout est PRÉLIMINAIRE.\n"
       "- Marchés tronqués exclus (les plus actifs) ; à refaire sur la collecte complète.\n- Inventaires sans transferts ni splits hors marché.\n"
       "- Le choix des trois wallets est in-sample.\n")
    w_("## Annexe — Tableau des signaux (livrable 1)\n"); o.extend(ANN)
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o[:400]))


if __name__ == "__main__":
    main()
