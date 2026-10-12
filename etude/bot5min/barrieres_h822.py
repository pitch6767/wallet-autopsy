"""BOT95 — FUSION ENGINE F1 : H822 à H832 (Pitch, 12.10.2026 12:31 et 12:33). PROTOCOLE PRÉ-ENREGISTRÉ (ce fichier tel que committé avant
le calcul de validation). Hors ligne ; aucun ordre ; H816, H821, R4 et fantômes gelés inchangés ; période réservée (≥ 13.10.2026) jamais lue.

DONNÉES (toutes antérieures au 13.10.2026)
  B  : BTCUSDT Binance spot, bougies de 1 s (o, h, l, c, volume, volume preneur acheteur), 12.09.2026 00:00 → 11.10.2026 23:59:59 UTC
       (branche donnees-btc, workflow histo_btc.yml). CVD = cumul de (2 × volume preneur acheteur − volume).
  OI : open interest BTCUSDT futures toutes les 5 min (si disponible ; contexte seulement).
  Règlements officiels Polymarket (bot95/reglements.json) : contrôle du substitut Binance.
  Décisions Bot95 : (U1) trades des fantômes Cloudflare BTC (bot95/sauvegarde), première décision par cycle × côté, 06.10 → 11.10 ;
       (U2) décisions H816 du laboratoire de Dublin (robustesse_bot95.py, exécution 164 ms sur le carnet enregistré), 11.10.
  Non mesurable en historique (déclaré, non estimé) : profondeur loin du prix et son rechargement, liquidations.

RÈGLEMENT (substitut) : prix à battre K = moyenne des clôtures 1 s sur les 60 s avant le début ; final F = moyenne sur les 60 dernières s.
  Contrôle : accord avec le résultat officiel mesuré et publié dans le rapport.

DÉCOUPAGE CHRONOLOGIQUE STRICT
  Marchés synthétiques et contacts : apprentissage = avant le 02.10.2026 00:00 UTC ; test = 02.10 → 11.10.
  Décisions Bot95 U1 : apprentissage 06.10 → 08.10 ; test 09.10 → 11.10. U2 (11.10) : test seulement.
  Tout paramètre (probabilités de rejet, coefficients, seuils de veto) est appris sur l'apprentissage puis mesuré UNE fois sur le test.

NIVEAUX (connus à l'instant t, rien après t)
  tol = 0,0002 × prix (≈ 16 $). Bougies d'1 min ; pivot haut = plus haut des 5 minutes avant et après, utilisable seulement 6 min après
  (confirmation) ; idem pivot bas. Niveau de pivot = pivots regroupés à ± tol sur les 4 h précédentes ; n = nombre de contacts déjà faits.
  Chiffres ronds : multiples de 100 $ (mineur), 500 $ et 1 000 $ (majeurs). « Majeur » = rond 500/1000 ou niveau de pivot avec n ≥ 2.
  Placebo : pour chaque niveau réel, un niveau fictif décalé de ± 5 à 15 tol (tirage fixé, graine 822), mêmes règles de contact.

H823 CONTACTS (premier, deuxième, troisième contact)
  Contact par en dessous : le prix était ≥ 3 tol sous le niveau, puis le plus haut d'une seconde atteint niveau − tol (symétrique par au-dessus).
  Mesures avant contact : vitesse d'approche 10 s et 30 s (en tol), volume agressif signé 10 s et 30 s, pente du CVD 30 s, absorption
  (volume 10 s / |mouvement 10 s|), volatilité 60 s, distance au chiffre rond, rang du contact, temps depuis le contact précédent,
  variation d'OI sur 15 min (si disponible).
  Résultats après contact à 5 / 10 / 20 / 30 / 60 s (en tol, signés dans le sens de l'approche) ; à 60 s : cassure (> + tol au-delà),
  rejet (< − 2 tol en deçà), fausse cassure (passé + tol au-delà puis revenu en deçà à 60 s). Rejet en excès = taux réel − taux placebo,
  IC 90 % par jours.
H825 Cassure / rejet / fausse cassure : régression logistique sur les mesures avant contact (apprentissage), AUC sur le test, IC par jours,
  comparée à la même régression sur les contacts placebo.
H827–H832 FIGURES POTENTIELLES (jamais confirmées à l'instant t), signées + haussier / − baissier :
  double / triple sommet potentiel (2e / 3e contact d'un niveau de pivots hauts par en dessous), double / triple creux (symétrique),
  sommets / creux égaux (niveau de pivots avec n ≥ 2 à moins de 1 σ restant), balayage de liquidité (plus haut des 60 dernières s > niveau
  + tol puis prix revenu sous le niveau ; symétrique), fausse cassure (clôture 1 min au-delà du niveau puis retour en deçà en moins de 3 min),
  cassure + retest (clôture 1 min au-delà depuis ≥ 3 min, prix revenu à ± tol du niveau sans le retraverser), compression (à moins de 2 tol
  d'un niveau, amplitude 60 s < 0,5 × amplitude des 5 min précédentes).
H822 RÈGLEMENT AVEC BARRIÈRES : décisions à 240 / 180 / 120 / 90 / 60 / 30 s de la fin de chaque cycle de 5 min.
  M0 = modèle de règlement seul (mouvement brownien, volatilité des 300 s précédentes, moyenne finale exacte, partie déjà observée comprise).
  M0* = M0 recalibré (logistique sur logit M0, apprise) — la référence équitable.
  MC0 = simulation de 400 trajectoires (rendements 1 s de l'apprentissage, standardisés, remis à l'échelle de la volatilité courante).
  MCB = mêmes trajectoires (mêmes tirages) avec rejet au premier contact d'un niveau, probabilité = rejet en excès appris par type
     (rond majeur, rond mineur, pivot n = 1, pivot n ≥ 2) ; rejet = trajectoire réfléchie pendant 60 s. Sans excès appris > 0 : MCB = MC0.
  MF = M0* + figures et obstacles (logistique apprise). Mesures : Brier, log loss, précision directionnelle, calibration ;
  tous et sous-ensemble marge faible |z| < 0,5 ; IC 90 % des différences par cycles.
H824 MARGE DE SÉCURITÉ : P(gagner) apprise en fonction de z (marge en écarts-types), temps restant, volatilité et obstacle en face ;
  marge nécessaire pour 90 % et 95 % ; calibration vérifiée sur le test.
H826 VETO PRÈS D'UNE BARRIÈRE (et H827–H832 en veto) : sur les décisions Bot95, refuser le pari si la marge du côté parié
  z_X < m ET un obstacle / une figure contraire est présent. Famille fixée : obstacle ∈ {niveau majeur à moins de 0,5 σ restant devant le
  prix, niveau quelconque à moins de 0,5 σ, double/triple sommet ou creux potentiel contraire, balayage contraire, fausse cassure contraire,
  compression contre un niveau devant} × m ∈ {0,5 ; 1,0} = 12 règles. Choix sur l'apprentissage U1 (règle admissible : garde ≥ 50 % des
  décisions), mesure unique sur le test U1 et sur U2. Mise 20 $, frais preneur 0,07·p·(1−p) ; U1 au prix enregistré par le fantôme, U2 à
  164 ms sur le carnet. Mesures : P&L net, marginal, IC 90 % par cycles et IC corrigé Bonferroni (12), perdants évités, gagnants et
  jackpots (≥ 2 × mise) supprimés, drawdown, signaux manqués.
CRITÈRE : une règle ou un modèle n'est « démontré » que si l'IC corrigé de la différence sur le test exclut 0 dans le bon sens.
Usage : python3 etude/bot5min/barrieres_h822.py dossier_btc1s dossier_cycles_dublin [--controle]  (--controle = apprentissage seul)
Sortie : etude/bot5min/resultat_barrieres_h822.md"""
import os, sys, glob, json, math, time, collections
import numpy as np, pandas as pd

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
sys.path.insert(0, ICI)
RESERVE = 1791849600; COUPE = 1790899200; U1_DEB = 1791244800; U1_COUPE = 1791504000
CONTROLE = "--controle" in sys.argv
SORTIE = os.path.join(ICI, "resultat_barrieres_h822" + ("_controle" if CONTROLE else "") + ".md")
RNG = np.random.default_rng(822)
TOL_F = 0.0002; HZ = (5, 10, 20, 30, 60); RESTES = (240, 180, 120, 90, 60, 30); MISE = 20.0; NPATH = 400
fee = lambda p: 0.07 * p * (1 - p)
Phi = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
lg = lambda p: math.log(min(max(p, 1e-4), 1 - 1e-4) / (1 - min(max(p, 1e-4), 1 - 1e-4)))


# ---------------------------------------------------------------- données
def charger(dossier):
    fs = sorted(glob.glob(os.path.join(dossier, "*.csv.gz")))
    D = pd.concat([pd.read_csv(f) for f in fs]).drop_duplicates("t").sort_values("t")
    D = D[D.t < RESERVE]
    t = D.t.values.astype(np.int64)
    assert np.all(np.diff(t) == 1), "trous dans les données 1 s"
    return dict(t0=int(t[0]), n=len(t), o=D.o.values, h=D.h.values, l=D.l.values, c=D.c.values, v=D.v.values, vb=D.vb.values)


def charger_oi():
    for p in (os.path.join(os.path.dirname(sys.argv[1].rstrip("/")), "oi", "oi_btcusdt.csv"),):
        if os.path.exists(p):
            D = pd.read_csv(p); tt = pd.to_datetime(D.iloc[:, 0]).astype("int64") // 10**9
            return np.array(tt), D["sum_open_interest"].values.astype(float)
    return None


class Serie:
    def __init__(s, B):
        s.B = B; s.t0 = B["t0"]; c = B["c"]
        s.cvd = np.cumsum(2 * B["vb"] - B["v"]); s.cv = np.cumsum(B["v"])
        r = np.diff(np.log(c), prepend=np.log(c[0])); s.r = r; s.r2 = np.cumsum(r * r)
        m = len(c) // 60 * 60
        s.mh = B["h"][:m].reshape(-1, 60).max(1); s.ml = B["l"][:m].reshape(-1, 60).min(1); s.mc = c[:m].reshape(-1, 60)[:, -1]
        s.piv = s.pivots()

    def i(s, ts): return int(ts) - s.t0
    def vol(s, i, n=300):                                   # écart-type par seconde (en $) sur n s
        a = max(i - n, 1); v = (s.r2[i] - s.r2[a]) / max(i - a, 1); return max(math.sqrt(v), 2e-6) * s.B["c"][i]

    def pivots(s, k=5):
        P = []
        for j in range(k, len(s.mh) - k):
            w = slice(j - k, j + k + 1)
            if s.mh[j] == s.mh[w].max(): P.append((j, +1, s.mh[j]))
            if s.ml[j] == s.ml[w].min(): P.append((j, -1, s.ml[j]))
        return P                                            # (minute, +1 haut / −1 bas, prix) ; utilisable à la minute j + k + 1

    def niveaux(s, i, fen=4 * 3600, k=5):
        """niveaux connus à l'indice i (pivots confirmés avant i, sur 4 h) : liste (prix, type ±1, n contacts, dernier contact)"""
        m_now = i // 60
        Ps = [p for p in s._piv_fenetre(m_now - fen // 60, m_now - k - 1)]
        tol = TOL_F * s.B["c"][i]; G = []
        for j, ty, px in sorted(Ps, key=lambda x: x[2]):
            if G and G[-1][1] == ty and abs(px - G[-1][0]) <= tol: g = G[-1]; g[0] = (g[0] * g[2] + px) / (g[2] + 1); g[2] += 1; g[3] = max(g[3], j)
            else: G.append([px, ty, 1, j])
        return G

    def _piv_fenetre(s, m0, m1):
        if not hasattr(s, "_pm"): s._pm = np.array([p[0] for p in s.piv])
        a, b = np.searchsorted(s._pm, m0), np.searchsorted(s._pm, m1, side="right")
        return s.piv[a:b]


# ---------------------------------------------------------------- H823 contacts
def contacts(S, L, dep, fin, kind, rang0=1):
    """contacts au niveau L sur [dep, fin) dans les deux sens ; renvoie des dicts"""
    c, h, l = S.B["c"], S.B["h"], S.B["l"]; tol = TOL_F * L; out = []
    dep = max(dep, 120); fin = min(fin, len(c) - 61)
    if fin <= dep: return out
    for sens in (+1, -1):                                   # +1 = approche par en dessous (test de résistance)
        d = (L - c[dep:fin]) * sens / tol
        arm = np.flatnonzero(d >= 3) + dep
        con = np.flatnonzero(((h[dep:fin] >= L - tol) if sens > 0 else (l[dep:fin] <= L + tol))) + dep
        k = 0; rang = rang0; prev = None
        while True:
            a = np.searchsorted(arm, k);
            if a >= len(arm): break
            ia = arm[a]; b = np.searchsorted(con, ia)
            if b >= len(con): break
            i0 = con[b]
            out.append(dict(i=int(i0), L=L, sens=sens, kind=kind, rang=rang, dt_prec=(i0 - prev) if prev else np.nan))
            prev = i0; rang += 1; k = i0 + 1
    return out


def mesurer_contact(S, e, oi=None):
    i, L, sens = e["i"], e["L"], e["sens"]; c, h, l, v, vb = S.B["c"], S.B["h"], S.B["l"], S.B["v"], S.B["vb"]; tol = TOL_F * L
    agr = lambda n: float(np.sum((2 * vb[i - n:i] - v[i - n:i]))) * sens
    mv10 = (c[i - 1] - c[i - 11]) * sens / tol; mv30 = (c[i - 1] - c[i - 31]) * sens / tol
    vol60 = S.vol(i - 1, 60) / tol
    r100 = abs(L - round(L / 100) * 100) / tol
    f = dict(v10=mv10, v30=mv30, a10=agr(10), a30=agr(30), cvd30=float(S.cvd[i - 1] - S.cvd[i - 31]) * sens,
             abs10=float(np.sum(v[i - 10:i])) / max(abs(c[i - 1] - c[i - 11]) / tol, 0.25), vol60=vol60, rond=r100, rang=e["rang"],
             dtp=(e["dt_prec"] if e["dt_prec"] == e["dt_prec"] else 9999) / 60.0, oi15=np.nan)
    if oi is not None:
        tt, vv = oi; ts = S.t0 + i; a = np.searchsorted(tt, ts) - 1; b = np.searchsorted(tt, ts - 900) - 1
        if a >= 0 and b >= 0 and vv[b] > 0: f["oi15"] = (vv[a] / vv[b] - 1) * 100
    y = {H: (c[i + H] - L) * sens / tol for H in HZ}
    exc = ((h[i:i + 61].max() - L) if sens > 0 else (L - l[i:i + 61].min())) / tol
    y60 = y[60]
    cl = "cassure" if y60 > 1 else ("rejet" if y60 < -2 else "indécis")
    fausse = exc > 1 and y60 < 0
    return f, y, cl, fausse


def h823(S, oi, fin_i):
    """contacts réels (pivots, ronds) et placebo sur [0, fin_i)"""
    E = []
    # niveaux de pivots : actifs de la confirmation à 4 h après le pivot ; le pivot lui-même est le contact 1
    for j, ty, px in S.piv:
        dep = (j + 6) * 60; fin = min((j + 240) * 60, fin_i)
        if dep >= fin: continue
        kind = "pivot"
        for e in contacts(S, px, dep, fin, kind, rang0=2): E.append(e)
        off = RNG.uniform(5, 15) * RNG.choice([-1, 1]) * TOL_F * px
        for e in contacts(S, px + off, dep, fin, "placebo pivot", rang0=2): E.append(e)
    # chiffres ronds : tous les multiples de 100 traversés
    lo, hi = S.B["l"][:fin_i].min(), S.B["h"][:fin_i].max()
    for L in np.arange(math.floor(lo / 100) * 100, hi + 100, 100):
        kind = "rond 1000" if L % 1000 == 0 else ("rond 500" if L % 500 == 0 else "rond 100")
        for e in contacts(S, float(L), 0, fin_i, kind): E.append(e)
        for e in contacts(S, float(L) + 37.0 * RNG.choice([-1, 1]), 0, fin_i, "placebo rond"): E.append(e)
    R = []
    for e in E:
        if e["i"] + 61 >= fin_i or e["i"] < 400: continue
        f, y, cl, fa = mesurer_contact(S, e, oi); e.update(f=f, y=y, cl=cl, fausse=fa, jour=(S.t0 + e["i"]) // 86400); R.append(e)
    return R


# ---------------------------------------------------------------- décisions synthétiques et figures
def figures(S, i, niv, sig_rest):
    """figures potentielles à l'indice i, signées (+ haussier, − baissier) ; aucune donnée après i"""
    c, h, l = S.B["c"], S.B["h"], S.B["l"]; p = c[i]; tol = TOL_F * p; F = collections.defaultdict(float)
    m_now = i // 60
    for L, ty, n, jl in niv:
        d = L - p
        if ty > 0 and -tol <= d <= tol and (p - c[i - 30]) > 0:          # au contact d'un niveau de hauts, par en dessous
            F["double_sommet" if n == 1 else "triple_sommet"] -= 1
        if ty < 0 and -tol <= d <= tol and (p - c[i - 30]) < 0:
            F["double_creux" if n == 1 else "triple_creux"] += 1
        if n >= 2 and abs(d) <= sig_rest:
            F["sommets_egaux" if ty > 0 else "creux_egaux"] += (-1 if ty > 0 else 1)
        h60, l60 = h[i - 60:i + 1].max(), l[i - 60:i + 1].min()
        if ty > 0 and h60 > L + tol and p < L: F["balayage"] -= 1
        if ty < 0 and l60 < L - tol and p > L: F["balayage"] += 1
        # clôtures 1 min des 3 dernières minutes complètes
        mc = S.mc[max(m_now - 3, 0):m_now]
        if ty > 0 and len(mc) and mc.max() > L + tol and p < L: F["fausse_cassure"] -= 1
        if ty < 0 and len(mc) and mc.min() < L - tol and p > L: F["fausse_cassure"] += 1
        mc_old = S.mc[max(m_now - 30, 0):max(m_now - 3, 0)]
        if ty > 0 and len(mc_old) and mc_old.max() > L + tol and S.mc[max(m_now - 3, 0):m_now].min(initial=1e12) > L and 0 <= p - L <= tol: F["cassure_retest"] += 1
        if ty < 0 and len(mc_old) and mc_old.min() < L - tol and S.mc[max(m_now - 3, 0):m_now].max(initial=0) < L and 0 <= L - p <= tol: F["cassure_retest"] -= 1
        r60 = h[i - 60:i + 1].max() - l[i - 60:i + 1].min(); r300 = h[i - 360:i - 60].max() - l[i - 360:i - 60].min()
        if abs(d) <= 2 * tol and r60 < 0.5 * r300: F["compression"] += (-1 if d > 0 else 1)
    return F


def obstacles(p, niv, sig_rest, cote):
    """obstacle devant le prix dans le sens contraire au pari : pour Up, une résistance au-dessus (rejet → baisse)"""
    tol = TOL_F * p; maj = quel = 0
    cands = [(L, n) for L, ty, n, jl in niv] + [(float(r), 9) for r in np.arange(round(p / 100) * 100 - 500, p + 600, 100)]
    for L, n in cands:
        d = (L - p) * (1 if cote == "Up" else -1)
        if -tol <= d <= 0.5 * sig_rest:
            quel = 1
            if (n == 9 and L % 500 == 0) or (n != 9 and n >= 2): maj = 1
    return maj, quel


def m0(S, s, rest):
    """modèle de règlement seul : renvoie (P(Up), z, E[F], sd)"""
    i = S.i(s + 300 - rest); c = S.B["c"]; K = c[S.i(s - 60):S.i(s)].mean(); sig = S.vol(i, 300)
    a = S.i(s + 240)
    if i <= a:
        g = a - i; mu = c[i]; sd = sig * math.sqrt(g + 60 / 3.0)
    else:
        n_obs = i - a; Lf = 60 - n_obs; mu = (c[a:i].sum() + Lf * c[i]) / 60.0; sd = sig * (Lf / 60.0) * math.sqrt(Lf / 3.0)
    sd = max(sd, 1e-6); z = (mu - K) / sd
    return Phi(z), z, mu, sd, K, i


def decisions_synth(S, debut_s, fin_s):
    D = []; c = S.B["c"]
    for s in range(debut_s - debut_s % 300 + 300, fin_s - 300, 300):
        if S.i(s) < 4 * 3600 + 400: continue
        F = c[S.i(s + 240):S.i(s + 300)].mean(); K = c[S.i(s - 60):S.i(s)].mean(); y = 1.0 if F > K else 0.0
        for rest in RESTES:
            p, z, mu, sd, K_, i = m0(S, s, rest)
            niv = S.niveaux(i); sig_rest = S.vol(i, 300) * math.sqrt(rest)
            fg = figures(S, i, niv, sig_rest)
            ob = {cote: obstacles(c[i], niv, sig_rest, cote) for cote in ("Up", "Down")}
            D.append(dict(s=s, rest=rest, i=i, y=y, p=p, z=z, mu=mu, sd=sd, K=K, fig=dict(fg), ob=ob, niv=niv, sig=S.vol(i, 300)))
    return D


# ---------------------------------------------------------------- outils statistiques
def ajuster(X, y, l2=1.0):
    X = np.column_stack([np.ones(len(X)), X]); b = np.zeros(X.shape[1]); P = np.eye(X.shape[1]) * l2; P[0, 0] = 0
    for _ in range(60):
        p = 1 / (1 + np.exp(-np.clip(X @ b, -30, 30))); g = X.T @ (p - y) + P @ b; H = X.T @ (X * (p * (1 - p))[:, None]) + P
        b -= np.linalg.solve(H, g)
    return b
def predire(b, X): X = np.column_stack([np.ones(len(X)), X]); return 1 / (1 + np.exp(-np.clip(X @ b, -30, 30)))
def brier(p, y): return (np.asarray(p) - np.asarray(y)) ** 2
def ll(p, y): p = np.clip(np.asarray(p), 1e-4, 1 - 1e-4); return -(y * np.log(p) + (1 - y) * np.log(1 - p))


def ic_groupes(g, v, alpha=0.10, B=3000):
    g = np.asarray(g); v = np.asarray(v, float); U, inv = np.unique(g, return_inverse=True)
    S_ = np.bincount(inv, v); N_ = np.bincount(inv)
    if len(U) < 3: return (float("nan"), float("nan"))
    idx = RNG.integers(0, len(U), (B, len(U))); m = S_[idx].sum(1) / N_[idx].sum(1)
    return float(np.percentile(m, 100 * alpha / 2)), float(np.percentile(m, 100 * (1 - alpha / 2)))


def auc(s, y):
    s = np.asarray(s); y = np.asarray(y); o = np.argsort(s); r = np.empty(len(s)); r[o] = np.arange(1, len(s) + 1)
    n1 = y.sum(); n0 = len(y) - n1
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)) if n1 and n0 else float("nan")


# ---------------------------------------------------------------- H822 Monte-Carlo avec barrières
def mc(S, d, Zs, qtab, avec):
    """probabilité Up par trajectoires ; Zs = rendements standardisés tirés (NPATH × pas) ; mêmes tirages avec et sans barrières"""
    i, rest = d["i"], d["rest"]; c = S.B["c"]; p0 = c[i]; sig = d["sig"]; a = S.i(d["s"] + 240)
    steps = rest - 1                                        # colonne k = prix à l'indice i + k + 1 ; dernier indice du cycle = i + rest − 1
    X = p0 + np.cumsum(Zs[:, :steps] * sig, axis=1)
    if avec and steps > 0:
        tol = TOL_F * p0; portee = 4 * sig * math.sqrt(rest)
        for L, ty, n, jl in d["niv"] + [(float(r), 0, 9, 0) for r in np.arange(round(p0 / 100) * 100 - 300, p0 + 400, 100)]:
            typ = ("rond majeur" if L % 500 == 0 else "rond mineur") if n == 9 else ("pivot n=1" if n == 1 else "pivot n>=2")
            q = qtab.get(typ, 0.0)
            if q <= 0 or abs(L - p0) < tol or abs(L - p0) > portee: continue
            sens = 1 if L > p0 else -1
            touche = (X - L) * sens >= -tol
            first = np.where(touche.any(1), touche.argmax(1), -1)
            rej = (first >= 0) & (RNG.random(len(X)) < q)
            for k in np.flatnonzero(rej):
                f = first[k]; e = min(f + 60, steps)
                seg = X[k, f:e] - X[k, f]; X[k, f:e] = X[k, f] - seg            # réflexion pendant 60 s
                if e < steps: X[k, e:] -= 2 * seg[-1]
    if a > i: obs = 0.0; fut = X[:, a - i - 1:steps].sum(1)
    else: obs = c[a:i + 1].sum(); fut = X[:, :steps].sum(1) if steps > 0 else 0.0
    F = (obs + fut) / 60.0
    return float(np.mean(F > d["K"]))


# ---------------------------------------------------------------- décisions Bot95
def decisions_bot95():
    U1 = {}
    for f in glob.glob(os.path.join(RACINE, "bot95", "sauvegarde", "*BTC*.json")):
        for t in json.load(open(f))["trades"].values():
            st = t.get("start"); p = t.get("prix"); g = t.get("gagnant")
            if not st or not p or g not in ("Up", "Down") or not (U1_DEB <= st < RESERVE - 86400) or not (0.02 <= p <= 0.98): continue
            tau = pd.Timestamp(t["heure"]).timestamp()
            k = (st, t["cote"])
            if k not in U1 or tau < U1[k]["tau"]: U1[k] = dict(start=st, cote=t["cote"], prix=p, tau=tau, gagne=(g == t["cote"]), src="U1")
    return sorted(U1.values(), key=lambda x: x["tau"])


def pnl20(p, gagne):
    u = p + fee(p); q = MISE / u; return q * (1.0 if gagne else 0.0) - MISE


def decisions_u2(dossier):
    import robustesse_bot95 as H816, latence_h766 as LH
    F = {int(os.path.basename(f).split(".")[0]): f for f in glob.glob(os.path.join(dossier, "**", "*.json.gz"), recursive=True)}
    F = {k: v for k, v in F.items() if k < RESERVE - 86400}            # 11.10 au plus tard (données 1 s disponibles)
    SIG = [s for s in json.load(open(os.path.join(RACINE, "bot95", "rapide.json")))["signaux"] if s.get("gagnant") and s["start"] in F]
    DEC = H816.decisions(SIG); out = []
    for st in sorted({s["start"] for s in DEC}):
        cy = LH.Cycle(F[st]); S_ = [s for s in DEC if s["start"] == st]; E = cy.etats([s["tDecision"] + 164 for s in S_])
        for s in S_:
            q, cst = H816.acheter_mise(E[s["tDecision"] + 164], s["cote"], int(round(s["a0"] * 1000)), MISE)
            out.append(dict(start=st, cote=s["cote"], prix=s["a0"], tau=s["tDecision"] / 1000, gagne=bool(s["gagne"]), q=q, c=cst, src="U2"))
    return out


def traits_decision(S, x):
    i = S.i(math.floor(x["tau"])); s = x["start"]; rest = max(int(s + 300 - x["tau"]), 1)
    p, z, mu, sd, K, _ = m0_at(S, s, i, rest)
    niv = S.niveaux(i); sig_rest = S.vol(i, 300) * math.sqrt(rest); fg = figures(S, i, niv, sig_rest)
    sgn = 1 if x["cote"] == "Up" else -1
    x.update(zX=z * sgn, fig={k: v * sgn for k, v in fg.items()}, ob=obstacles(S.B["c"][i], niv, sig_rest, x["cote"]), pX=p if sgn > 0 else 1 - p)
    return x


def m0_at(S, s, i, rest):
    c = S.B["c"]; K = c[S.i(s - 60):S.i(s)].mean(); sig = S.vol(i, 300); a = S.i(s + 240)
    if i <= a: mu = c[i]; sd = sig * math.sqrt(a - i + 20)
    else: n_obs = i - a; Lf = 60 - n_obs; mu = (c[a:i].sum() + Lf * c[i]) / 60.0; sd = sig * (Lf / 60.0) * math.sqrt(max(Lf, 1) / 3.0)
    sd = max(sd, 1e-6); z = (mu - K) / sd; return Phi(z), z, mu, sd, K, i


REGLES = [(ob, m) for ob in ("obstacle majeur", "obstacle quelconque", "double/triple contraire", "balayage contraire", "fausse cassure contraire",
                              "compression devant") for m in (0.5, 1.0)]


def veto(x, r):
    ob, m = r; F = x["fig"]
    if x["zX"] >= m: return False
    if ob == "obstacle majeur": return x["ob"][0] == 1
    if ob == "obstacle quelconque": return x["ob"][1] == 1
    if ob == "double/triple contraire": return any(F.get(k, 0) < 0 for k in ("double_sommet", "triple_sommet", "double_creux", "triple_creux"))
    if ob == "balayage contraire": return F.get("balayage", 0) < 0
    if ob == "fausse cassure contraire": return F.get("fausse_cassure", 0) < 0
    if ob == "compression devant": return F.get("compression", 0) < 0
    return False


# ---------------------------------------------------------------- principal
def main():
    t_go = time.time()
    B = charger(sys.argv[1]); S = Serie(B); oi = charger_oi(); o = []; w = o.append
    fin_all = B["n"] if not CONTROLE else S.i(COUPE)
    w(f"# Bot95 — Fusion Engine F1 : H822 à H832 — barrières, figures de liquidité et règlement ({'CONTRÔLE, apprentissage seul' if CONTROLE else 'apprentissage → test'})\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. BTCUSDT 1 s Binance du {time.strftime('%d.%m.%Y', time.gmtime(B['t0']))} au "
      f"{time.strftime('%d.%m.%Y %H:%M', time.gmtime(B['t0'] + B['n'] - 1))} UTC. Apprentissage < 02.10.2026 ; test 02.10 → 11.10. "
      f"Open interest : {'disponible (5 min)' if oi is not None else 'non disponible'}. Profondeur loin du prix et liquidations : non mesurables. "
      "Aucun ordre ; H816, H821, R4, fantômes inchangés ; période réservée non lue.\n")

    # --- contrôle du substitut de règlement
    R = [x for x in json.load(open(os.path.join(RACINE, "bot95", "reglements.json"))) if x["a"] == "BTC" and x.get("ptb") and x["start"] + 300 <= B["t0"] + B["n"]]
    c = B["c"]; acc = []
    for x in R:
        s = x["start"]; K = c[S.i(s - 60):S.i(s)].mean(); F = c[S.i(s + 240):S.i(s + 300)].mean(); acc.append(((F > K) == (x["gagnant"] == "Up"), abs(F - K)))
    acc = np.array(acc, float)
    w(f"## 0. Substitut du règlement\nRésultat Binance (moyennes 60 s) contre résultat officiel Polymarket : **{100 * acc[:, 0].mean():.1f} %** d'accord sur "
      f"{len(acc)} cycles ; désaccords seulement quand |F − K| < 5 $ ({100 * acc[acc[:, 1] < 5, 0].mean():.0f} % d'accord sous 5 $, "
      f"{100 * acc[acc[:, 1] >= 5, 0].mean():.1f} % au-dessus).\n")

    # --- H823 / H825 contacts
    E = h823(S, oi, fin_all)
    tr = [e for e in E if S.t0 + e["i"] < COUPE]; te = [e for e in E if S.t0 + e["i"] >= COUPE]
    w("## 1. H823 — Que se passe-t-il au contact d'un niveau ?\n")
    w("Contact = le prix arrive à ± tol (≈ 16 $) d'un niveau après en avoir été à ≥ 3 tol. Résultat à 60 s : cassure (> 1 tol au-delà), rejet "
      "(> 2 tol en deçà), fausse cassure (passé au-delà puis revenu). Placebo = mêmes règles sur des niveaux fictifs décalés.\n")
    w("| Échantillon | Type de niveau | Contacts | Rejet | Cassure | Fausse cassure | Rejet en excès vs placebo (IC 90 % par jours) | Mouvement médian 5 / 10 / 20 / 30 / 60 s (tol, sens de l'approche) |\n|---|---|---|---|---|---|---|---|")
    qtab = {}
    for nom, Z in (("apprentissage", tr), ("test", te)):
        if not Z: continue
        for kind in ("rond 1000", "rond 500", "rond 100", "pivot", "placebo rond", "placebo pivot"):
            for rg in ((None,) if "rond" in kind else (2, 3, None)):
                X = [e for e in Z if e["kind"] == kind and (rg is None or (e["rang"] == rg if rg < 3 else e["rang"] >= 3))]
                if len(X) < 10: continue
                rj = np.array([e["cl"] == "rejet" for e in X], float)
                base = [e for e in Z if e["kind"] == ("placebo rond" if "rond" in kind else "placebo pivot")]
                ex = "—"
                if "placebo" not in kind and base:
                    g = [e["jour"] for e in X] + [e["jour"] for e in base]
                    diff = rj.mean() - np.mean([e["cl"] == "rejet" for e in base])
                    # IC par jours : rééchantillonnage des jours, différence de taux
                    J = sorted(set(g)); jr = {j: [0, 0, 0, 0] for j in J}
                    for e in X: jr[e["jour"]][0] += e["cl"] == "rejet"; jr[e["jour"]][1] += 1
                    for e in base: jr[e["jour"]][2] += e["cl"] == "rejet"; jr[e["jour"]][3] += 1
                    A = np.array([jr[j] for j in J], float); idx = RNG.integers(0, len(J), (2000, len(J))); Sm = A[idx].sum(1)
                    dd = Sm[:, 0] / np.maximum(Sm[:, 1], 1) - Sm[:, 2] / np.maximum(Sm[:, 3], 1)
                    ex = f"{100 * diff:+.1f} pts [{100 * np.percentile(dd, 5):+.1f} ; {100 * np.percentile(dd, 95):+.1f}]"
                    if nom == "apprentissage":
                        typ = ("rond majeur" if kind in ("rond 1000", "rond 500") else "rond mineur") if "rond" in kind else ("pivot n=1" if rg == 2 else ("pivot n>=2" if rg == 3 else None))
                        if typ and np.percentile(dd, 5) > 0: qtab[typ] = max(qtab.get(typ, 0), float(diff))
                mv = " / ".join(f"{np.median([e['y'][H] for e in X]):+.1f}" for H in HZ)
                lab = kind + ("" if rg is None else (" — 2e contact (double)" if rg == 2 else " — 3e contact et plus (triple)"))
                w(f"| {nom} | {lab} | {len(X)} | {100 * rj.mean():.0f} % | {100 * np.mean([e['cl'] == 'cassure' for e in X]):.0f} % | "
                  f"{100 * np.mean([e['fausse'] for e in X]):.0f} % | {ex} | {mv} |")
    w(f"\nProbabilités de rejet en excès retenues pour H822 (apprentissage, seulement si l'IC exclut 0) : {qtab if qtab else 'aucune'}.\n")

    # H825
    w("## 2. H825 — Prévoir cassure, rejet et fausse cassure avant le contact\n")
    feats = ["v10", "v30", "a10", "a30", "cvd30", "abs10", "vol60", "rond", "rang", "dtp"] + (["oi15"] if oi is not None else [])
    def mat(Z):
        X = np.array([[e["f"][k] for k in feats] for e in Z], float); X = np.nan_to_num(X); return X
    w("| Cible | Niveaux | AUC test (IC 90 % par jours) | Taux de base test |\n|---|---|---|---|")
    for cible, fy in (("rejet", lambda e: e["cl"] == "rejet"), ("cassure", lambda e: e["cl"] == "cassure"), ("fausse cassure", lambda e: e["fausse"])):
        for grp, pr in (("réels", lambda e: "placebo" not in e["kind"]), ("placebo", lambda e: "placebo" in e["kind"])):
            a_ = [e for e in tr if pr(e)]; b_ = [e for e in te if pr(e)]
            if len(a_) < 50 or len(b_) < 50: continue
            Xa = mat(a_); mu_, sd_ = Xa.mean(0), Xa.std(0) + 1e-9
            bb = ajuster((Xa - mu_) / sd_, np.array([fy(e) for e in a_], float), 1.0)
            pb = predire(bb, (mat(b_) - mu_) / sd_); yb = np.array([fy(e) for e in b_], float)
            J = np.array([e["jour"] for e in b_]); Ju = np.unique(J); boots = []
            for _ in range(500):
                m = np.isin(J, RNG.choice(Ju, len(Ju)));
                if yb[m].min() != yb[m].max(): boots.append(auc(pb[m], yb[m]))
            w(f"| {cible} | {grp} | {auc(pb, yb):.3f} [{np.percentile(boots, 5):.3f} ; {np.percentile(boots, 95):.3f}] | {100 * yb.mean():.0f} % |")
    w("\nLecture : un niveau n'apporte une information propre que si l'AUC sur les niveaux réels dépasse nettement celle des placebos.\n")

    # --- décisions synthétiques H822 / H824 / H827-H832
    D = decisions_synth(S, B["t0"] + 4 * 3600 + 600, B["t0"] + fin_all)
    Dtr = [d for d in D if d["s"] < COUPE]; Dte = [d for d in D if d["s"] >= COUPE]
    FIGS = ["double_sommet", "triple_sommet", "double_creux", "triple_creux", "sommets_egaux", "creux_egaux", "balayage", "fausse_cassure", "cassure_retest", "compression"]
    def Xfig(Z): return np.array([[lg(d["p"])] + [d["fig"].get(k, 0.0) for k in FIGS] + [d["ob"]["Up"][0] - d["ob"]["Down"][0], d["ob"]["Up"][1] - d["ob"]["Down"][1]] for d in Z])
    y_tr = np.array([d["y"] for d in Dtr]); b0 = ajuster(np.array([[lg(d["p"])] for d in Dtr]), y_tr, 0.1); bF = ajuster(Xfig(Dtr), y_tr, 1.0)
    w("## 3. Figures potentielles (H827–H832) : fréquence et effet sur le résultat officiel (substitut), apprentissage\n")
    w("| Figure | Décisions où elle est présente | Victoire Up quand haussière / baissière | Probabilité M0 moyenne quand haussière / baissière |\n|---|---|---|---|")
    for k in FIGS:
        up = [d for d in Dtr if d["fig"].get(k, 0) > 0]; dn = [d for d in Dtr if d["fig"].get(k, 0) < 0]
        f_ = lambda Z, f: f"{100 * np.mean([f(d) for d in Z]):.0f} %" if Z else "—"
        w(f"| {k.replace('_', ' ')} | {len(up) + len(dn)} | {f_(up, lambda d: d['y'])} / {f_(dn, lambda d: d['y'])} | {f_(up, lambda d: d['p'])} / {f_(dn, lambda d: d['p'])} |")
    w(f"\nCoefficients du modèle avec figures (logit, appris) : " + ", ".join(f"{n} {v:+.3f}" for n, v in zip(["const", "logit M0"] + FIGS + ["obstacle majeur", "obstacle"], bF)) + "\n")

    if CONTROLE:
        w("_Contrôle : arrêt avant le test._\n"); open(SORTIE, "w").write("\n".join(o)); print("\n".join(o)); return

    # H822 Monte-Carlo sur le test
    sigs = np.array([S.vol(k, 300) for k in range(400, S.i(COUPE) - 1, 10)])
    rs = S.r[400:S.i(COUPE) - 1:10] * B["c"][400:S.i(COUPE) - 1:10] / sigs           # rendements standardisés de l'apprentissage
    rs = rs[np.isfinite(rs)]; rs = np.clip(rs, -12, 12)
    p_mc0, p_mcb = [], []
    for d in Dte:
        Zs = RNG.choice(rs, (NPATH, d["rest"]))
        p_mc0.append(mc(S, d, Zs, qtab, False)); p_mcb.append(mc(S, d, Zs, qtab, True) if qtab else p_mc0[-1])
    y_te = np.array([d["y"] for d in Dte]); g_te = np.array([d["s"] for d in Dte])
    P = {"M0 règlement seul": np.array([d["p"] for d in Dte]), "M0* recalibré (référence)": predire(b0, np.array([[lg(d["p"])] for d in Dte])),
         "MC0 trajectoires sans barrières": np.clip(np.array(p_mc0), 1e-3, 1 - 1e-3), "MCB trajectoires avec barrières (H822)": np.clip(np.array(p_mcb), 1e-3, 1 - 1e-3),
         "MF avec figures et obstacles (H827–H832)": predire(bF, Xfig(Dte))}
    w("## 4. H822 / H827–H832 — Le modèle avec barrières ou figures prévoit-il mieux le résultat officiel ? (test, décisions synthétiques)\n")
    for titre, m in (("Toutes les décisions", np.ones(len(Dte), bool)), ("Marge faible |z| < 0,5", np.array([abs(d["z"]) < 0.5 for d in Dte]))):
        w(f"**{titre}** ({int(m.sum())} décisions, {len(set(g_te[m]))} cycles)\n")
        w("| Modèle | Brier | Log loss | Précision directionnelle | Brier − référence M0* | IC 90 % | IC corrigé (4 comparaisons) |\n|---|---|---|---|---|---|---|")
        ref = brier(P["M0* recalibré (référence)"][m], y_te[m])
        for k, p in P.items():
            e = brier(p[m], y_te[m]); acc_ = np.mean((p[m] > 0.5) == (y_te[m] > 0.5)); dlt = e - ref
            if k.startswith("M0*"): w(f"| {k} | {e.mean():.4f} | {ll(p[m], y_te[m]).mean():.4f} | {100 * acc_:.1f} % | — | — | — |"); continue
            c1 = ic_groupes(g_te[m], dlt); c2 = ic_groupes(g_te[m], dlt, 0.10 / 4)
            w(f"| {k} | {e.mean():.4f} | {ll(p[m], y_te[m]).mean():.4f} | {100 * acc_:.1f} % | {dlt.mean():+.5f} | [{c1[0]:+.5f} ; {c1[1]:+.5f}] | [{c2[0]:+.5f} ; {c2[1]:+.5f}] |")
        w("")
    w("**Calibration (test)**\n\n| Probabilité annoncée | Décisions | M0* : victoire observée | MF : victoire observée |\n|---|---|---|---|")
    for lo, hi in ((0, .1), (.1, .3), (.3, .5), (.5, .7), (.7, .9), (.9, 1.01)):
        m1 = (P["M0* recalibré (référence)"] >= lo) & (P["M0* recalibré (référence)"] < hi); m2 = (P["MF avec figures et obstacles (H827–H832)"] >= lo) & (P["MF avec figures et obstacles (H827–H832)"] < hi)
        w(f"| {lo:.1f}–{min(hi, 1):.1f} | {int(m1.sum())} / {int(m2.sum())} | {100 * y_te[m1].mean():.0f} % | {100 * y_te[m2].mean():.0f} % |")

    # H824 marge de sécurité
    w("\n## 5. H824 — Marge de sécurité dynamique\n")
    w("P(le côté en tête gagne) apprise en fonction de |z|, avec et sans obstacle majeur devant le prix (dans le sens d'un retour vers le prix à battre). "
      "Marge |z| nécessaire pour 90 % et 95 %, par temps restant (apprentissage), puis taux observé sur le test au-delà de cette marge.\n")
    w("| Temps restant | Obstacle | Marge pour 90 % | Taux test au-delà | Marge pour 95 % | Taux test au-delà |\n|---|---|---|---|---|---|")
    for rest in RESTES:
        for obn in (0, 1):
            def sel(Z): return [d for d in Z if d["rest"] == rest and d["ob"]["Up" if d["z"] > 0 else "Down"][0] == obn]
            A_ = sel(Dtr); T_ = sel(Dte)
            if len(A_) < 100: continue
            Xa = np.array([[abs(d["z"])] for d in A_]); ya = np.array([(d["y"] == 1) == (d["z"] > 0) for d in A_], float); b = ajuster(Xa, ya, 0.01)
            row = f"| {rest} s | {'oui' if obn else 'non'} |"
            for tgt in (0.90, 0.95):
                zz = (lg(tgt) - b[0]) / b[1] if b[1] > 0 else float("nan")
                Tm = [((d["y"] == 1) == (d["z"] > 0)) for d in T_ if abs(d["z"]) >= zz]
                row += f" {zz:.2f} σ | {100 * np.mean(Tm):.1f} % ({len(Tm)}) |" if Tm else f" {zz:.2f} σ | — |"
            w(row)

    # H826 veto sur les décisions Bot95
    w("\n## 6. H826 (et figures H827–H832 en veto) — sur les vraies décisions Bot95\n")
    U1 = [traits_decision(S, x) for x in decisions_bot95() if S.i(math.floor(x["tau"])) < B["n"] - 1]
    for x in U1: x["pnl"] = pnl20(x["prix"], x["gagne"])
    U2 = []
    if len(sys.argv) > 2 and os.path.isdir(sys.argv[2]):
        U2 = [traits_decision(S, x) for x in decisions_u2(sys.argv[2]) if S.i(math.floor(x["tau"])) < B["n"] - 1]
        for x in U2: x["pnl"] = x["q"] * (1.0 if x["gagne"] else 0.0) - x["c"]
    tr1 = [x for x in U1 if x["start"] < U1_COUPE]; te1 = [x for x in U1 if x["start"] >= U1_COUPE]
    def score(Z, r):
        gar = [x for x in Z if not veto(x, r)]
        return (sum(x["pnl"] for x in gar) - sum(x["pnl"] for x in Z)) if len(gar) >= 0.5 * len(Z) else -1e9
    w(f"U1 = fantômes Cloudflare (première décision par cycle × côté, 20 $ au prix enregistré) : apprentissage {len(tr1)}, test {len(te1)}. "
      f"U2 = H816 Dublin du 11.10 à 164 ms : {len(U2)} décisions (test).\n")
    w("| Règle (obstacle × marge m) | Gain apprentissage U1 ($) | Gain test U1 ($) |\n|---|---|---|")
    for r in REGLES: w(f"| {r[0]}, z < {r[1]} | {score(tr1, r):+.0f} | {score(te1, r):+.0f} |".replace("-1000000000", "inadmissible"))
    best = max(REGLES, key=lambda r: score(tr1, r))
    w(f"\n**Règle retenue sur l'apprentissage : {best[0]}, z < {best[1]}.**\n")
    w("| Échantillon | Décisions | Gardées | Perdants évités | Gagnants supprimés | Jackpots supprimés | P&L base ($) | P&L avec veto ($) | Marginal ($) | IC 90 % par décision | IC corrigé (12) | Drawdown base / veto |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
    def dd(v):
        cm = np.cumsum(v) if len(v) else np.array([0.0]); return float(np.max(np.maximum.accumulate(np.concatenate([[0], cm]))[1:] - cm)) if len(v) else 0.0
    for nom, Z in (("apprentissage U1", tr1), ("TEST U1", te1), ("TEST U2 (H816, 164 ms)", U2)):
        if not Z: continue
        V = [veto(x, best) for x in Z]; ex = [x for x, v in zip(Z, V) if v]
        marg = np.array([-x["pnl"] if v else 0.0 for x, v in zip(Z, V)]); g = [x["start"] for x in Z]
        c1 = ic_groupes(g, marg); c2 = ic_groupes(g, marg, 0.10 / len(REGLES))
        Zs_ = sorted(Z, key=lambda x: x["tau"])
        w(f"| {nom} | {len(Z)} | {len(Z) - len(ex)} | {sum(1 for x in ex if x['pnl'] < 0)} | {sum(1 for x in ex if x['pnl'] > 0)} | {sum(1 for x in ex if x['pnl'] >= 2 * MISE)} | "
          f"{sum(x['pnl'] for x in Z):+.0f} | {sum(x['pnl'] for x, v in zip(Z, V) if not v):+.0f} | {marg.sum():+.0f} | [{c1[0]:+.2f} ; {c1[1]:+.2f}] | [{c2[0]:+.2f} ; {c2[1]:+.2f}] | "
          f"{dd([x['pnl'] for x in Zs_]):.0f} / {dd([x['pnl'] for x in Zs_ if not veto(x, best)]):.0f} |")
    w("\n**Marge faible seulement (z du côté parié < 0,5), test U1** : décisions, taux de gain, P&L selon la présence d'un obstacle majeur devant.\n")
    w("| Obstacle majeur devant | Décisions | Taux de gain | Prix moyen | P&L ($) |\n|---|---|---|---|---|")
    for obn in (0, 1):
        Z = [x for x in te1 if x["zX"] < 0.5 and x["ob"][0] == obn]
        if Z: w(f"| {'oui' if obn else 'non'} | {len(Z)} | {100 * np.mean([x['gagne'] for x in Z]):.0f} % | {np.mean([x['prix'] for x in Z]):.2f} | {sum(x['pnl'] for x in Z):+.0f} |")
    w(f"\n## Limites\n- Règlement reconstruit avec Binance (accord {100 * acc[:, 0].mean():.1f} % avec l'officiel, désaccords sous 5 $ d'écart).\n"
      "- Profondeur loin du prix, rechargement / retrait de profondeur et liquidations : non disponibles en historique, non mesurés.\n"
      f"- Open interest : {'5 min seulement, trop grossier pour 5–60 s' if oi is not None else 'non disponible'}.\n"
      "- U1 : prix enregistrés par les fantômes Cloudflare (exécution moins réaliste que U2). U2 : une seule journée.\n"
      "- Nombreuses comparaisons : seuls les IC corrigés permettent de conclure.\n")
    w(f"_Calcul : {time.time() - t_go:.0f} s._\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o))


if __name__ == "__main__":
    main()
