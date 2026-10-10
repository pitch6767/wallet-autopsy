"""BOT95 V3 — expérience 003 : modèle logistique simple, PRÉ-ENREGISTRÉ (hors ligne).
Pré-enregistrement (écrit avant toute exécution, rien n'est modifié après avoir vu validation / inédit) :
- Candidats : (1) les signaux V2-F original (O8), (2) les premiers désaccords ≥ 0,20 du cycle (désaccord 20). Les deux jeux sont rapportés, aucun n'est choisi après coup.
- Cible : le jeton acheté gagne (résultat officiel).
- 10 variables connues à l'instant de la décision : écart modèle − vendeur ; prix vendeur ; log du temps restant ; log(1 + taille affichée) ;
  écart acheteur-vendeur de notre côté (c) ; mouvement du perp Bybit sur 5 s dans notre sens divisé par (vol × √5) ; mouvement Coinbase sur 3 s dans notre sens (en 10 $) ;
  log de la volatilité 5 min ; âge de l'épisode de désaccord (s, plafonné à 5) ; nuit (22-08 h suisse).
- Standardisation avec moyenne / écart type de l'apprentissage ; régression logistique avec pénalité L2 fixe λ = 1 (pas de réglage) ; valeurs manquantes → moyenne d'apprentissage.
- Règle de décision fixée : acheter si p̂ − prix − frais(prix) > 0 (gain attendu positif par part). Aucun seuil réglé.
- Évaluation : validation et inédit, exécution au meilleur vendeur, quantité affichée, prix ≤ prix de décision, délai 0 et 0,5 s. Comparaison avec « tout prendre »."""
exec(open("etude/bot5min/v3_commun.py").read())
def edge_age(st, s):
    R_ = C[st]; i = s["i"]; up = s["up"]; j = i
    def e(k):
        r = R_[k]; a = r[4] if up else r[6]
        return None if a is None else ((r[2] if up else 1 - r[2]) - a)
    while j - 1 >= 0 and R_[j][0] - R_[j - 1][0] < 1.0 and (e(j - 1) or -1) >= 0.20: j -= 1
    return R_[i][0] - R_[j][0]
def mvt(st, t, col, a):
    T_ = TT[st]; R_ = C[st]; k1 = bisect.bisect_right(T_, t) - 1; k0 = bisect.bisect_right(T_, t - a) - 1
    if k0 < 0 or k1 < 0 or not R_[k1][col] or not R_[k0][col]: return None
    return R_[k1][col] - R_[k0][col]
FN = ["écart modèle − vendeur", "prix vendeur", "log temps restant", "log(1 + taille affichée)", "écart acheteur-vendeur (c)", "perp 5 s / (vol·√5)",
      "Coinbase 3 s (10 $)", "log volatilité 5 min", "âge de l'épisode (s, ≤ 5)", "nuit"]
def feats(st, s):
    r = C[st][s["i"]]; up = s["up"]; sg = 1 if up else -1; t = s["t"]
    a = s["a"]; fair = r[2] if up else 1 - r[2]; bid = r[3] if up else r[5]; z = (r[8] if up else r[10]) or 0
    v = vol(int(t)); m5 = mvt(st, t, 11, 5); c3 = mvt(st, t, 13, 3); h = time.gmtime(t + 7200).tm_hour
    return [fair - a, a, math.log(max(1, s["tl"])), math.log1p(z), None if bid is None else 100 * (a - bid),
            None if (m5 is None or not v) else sg * m5 / (v * math.sqrt(5)), None if c3 is None else sg * c3 / 10,
            None if not v else math.log(v), min(5.0, edge_age(st, s)), 1.0 if (h >= 22 or h < 8) else 0.0]
def fit(X, y, lam=1.0, it=50):
    X1 = np.column_stack([np.ones(len(X)), X]); w = np.zeros(X1.shape[1]); P = np.eye(X1.shape[1]) * lam; P[0, 0] = 0
    for _ in range(it):
        p = 1 / (1 + np.exp(-X1 @ w)); g = X1.T @ (p - y) + P @ w; H = (X1.T * (p * (1 - p))) @ X1 + P
        d = np.linalg.solve(H, g); w -= d
        if np.abs(d).max() < 1e-8: break
    return w
pred = lambda w, X: 1 / (1 + np.exp(-np.column_stack([np.ones(len(X)), X]) @ w))
out = ["# BOT95 V3 — Expérience 003 : modèle logistique simple pré-enregistré", "", ENTETE, "",
       "**Pré-enregistrement** (fixé avant de lancer le calcul) : 10 variables connues à la décision, standardisées sur l'apprentissage, régression logistique L2 (λ = 1, non réglé), "
       "règle d'achat « probabilité estimée − prix − frais > 0 », entraînement sur l'apprentissage SEULEMENT, jugement sur validation puis inédit. Deux jeux de candidats déclarés d'avance : "
       "signaux V2-F original (O8) et premiers désaccords ≥ 0,20 (désaccord 20).", "",
       "Variables : " + " ; ".join(f"{k + 1}. {n}" for k, n in enumerate(FN)) + ".", ""]
for nomc, S in (("V2-F original (O8)", STRATS["V2-F original (O8)"]), ("désaccord 20 (premier franchissement ≥ 0,20)", D20)):
    keys = sorted(S); F = np.array([[np.nan if v is None else v for v in feats(st, S[st])] for st in keys], dtype=float)
    y = np.array([1.0 if ((O[f"BTC:{st}"]["gagnant"] == "Up") == S[st]["up"]) else 0.0 for st in keys])
    per = np.array([PER(st) for st in keys]); tr = per == "apprentissage"
    mu = np.nanmean(F[tr], axis=0); sd = np.nanstd(F[tr], axis=0); sd[sd == 0] = 1
    miss = np.isnan(F).sum(axis=0); F = np.where(np.isnan(F), mu, F); X = (F - mu) / sd
    w = fit(X[tr], y[tr]); ph = pred(w, X)
    ask = np.array([S[st]["a"] for st in keys]); fair = np.array([F[k, 0] + F[k, 1] for k in range(len(keys))])
    take = ph - ask - np.array([FEE(a) for a in ask]) > 0
    out += [f"## Candidats : {nomc}", "", f"{len(keys)} candidats (app. {tr.sum()} · valid. {(per == 'validation').sum()} · inédit {(per == 'inédit').sum()}). "
            f"Valeurs manquantes remplacées par la moyenne d'apprentissage : " + ", ".join(f"{FN[k]} {miss[k]}" for k in range(len(FN)) if miss[k]) + ".", "",
            "### Coefficients (variables standardisées, apprentissage)", "", "| Variable | Coefficient |", "|---|---|", f"| constante | {w[0]:+.3f} |"]
    out += [f"| {FN[k]} | {w[k + 1]:+.3f} |" for k in range(len(FN))]
    out += ["", "### Qualité de prévision (score de Brier, plus bas = mieux ; « prix » = prendre le prix vendeur comme probabilité ; « modèle du bot » = probabilité du modèle 0,08 %)", "",
            "| Période | Candidats | Taux de gain réel | Brier logistique | Brier prix | Brier modèle du bot | Proba logistique moyenne |", "|---|---|---|---|---|---|---|"]
    for p in PERS:
        m = per == p
        if m.sum() == 0: continue
        out.append(f"| {p} | {m.sum()} | {100 * y[m].mean():.0f} % | {np.mean((ph[m] - y[m]) ** 2):.4f} | {np.mean((ask[m] - y[m]) ** 2):.4f} | {np.mean((fair[m] - y[m]) ** 2):.4f} | {ph[m].mean():.3f} |")
    out += ["", "### Résultat en exécution réaliste", ""]
    for dl in (0, 0.5):
        out += [f"**Délai {str(dl).replace('.', ',')} s**", "", hdr("Période · politique")]
        for p in PERS:
            cyc = CYC[p]; ks = [k for k in range(len(keys)) if per[k] == p]
            out.append(lig(f"{p} · tout prendre ({len(ks)})", bilan([exe(keys[k], S[keys[k]], dl) for k in ks], cyc)))
            out.append(lig(f"{p} · filtre logistique ({sum(take[k] for k in ks)} retenus)", bilan([exe(keys[k], S[keys[k]], dl) for k in ks if take[k]], cyc)))
            out.append(lig(f"{p} · rejetés par le filtre", bilan([exe(keys[k], S[keys[k]], dl) for k in ks if not take[k]], cyc)))
        out.append("")
open("etude/bot5min/resultat_v3_exp003.md", "w").write("\n".join(out)); print("\n".join(out))
