"""BOT95 — H681–H710 : autopsie des makers et preneurs (priorités 1, 3, 4, 5 du message de Pitch du 11.10.2026 16:04). Lecture seule, hors ligne.
P1 paires Up/Down (25 plus gros makers + 20 plus rentables) ; P3 trois preneurs ; P4 risque d'achat à 0,95–0,99 en fin de cycle ; P5 intégrité.
Données : bot95/makers_suivi.json (branche donnees-makers) — exécutions de l'API Data (maker / preneur), activité des portefeuilles étudiés
(fusions, séparations, règlements, récompenses). FAITS = exécutions et activité ; INFÉRENCES = interprétation. Marchés incomplets signalés à part.
Période réservée (≥ 13.10.2026 00:00 UTC) exclue. Usage : python3 etude/bot5min/autopsie_wallets.py makers_suivi.json → resultat_autopsie_wallets.md"""
import json, os, sys, collections, time
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); SORTIE = os.path.join(ICI, "resultat_autopsie_wallets.md"); HORS_ECH = 1791849600
FEE = lambda p: 0.07 * p * (1 - p)
PRENEURS = ("0x11aade7b", "0xc4e21390", "0x41e2e1cc")


def charger(path):
    base = json.load(open(path))
    M = {int(k): v for k, v in base["marches"].items() if int(k) < HORS_ECH}
    return base, M


def par_wallet_marche(M):
    """(wallet, start) → liste chronologique des exécutions (role, issue, côté, parts, prix, ts)"""
    W = collections.defaultdict(list)
    for st, mk in M.items():
        for w, role, out, side, sz, p, ts in mk["ex"]: W[(w, st)].append((ts, role, out, side, sz, p))
    for k in W: W[k].sort()
    return W


def bilan_marche(ex, gagnant):
    """bilan d'un portefeuille sur un marché : paires appariées, jambes seules, frais preneur, délai entre jambes"""
    q = {"Up": 0.0, "Down": 0.0}; c = {"Up": 0.0, "Down": 0.0}; ventes = 0.0; frais = 0.0; prem = {}; court = {"Up": 0.0, "Down": 0.0}; recettes_court = 0.0
    for ts, role, out, side, sz, p in ex:
        if role == "P": frais += sz * FEE(p)
        if side == "BUY":
            q[out] += sz; c[out] += sz * p; prem.setdefault(out, ts)
        else:
            # vente : on retire au coût moyen ; gain réalisé = prix − coût moyen
            pm = c[out] / q[out] if q[out] > 1e-9 else 0.0; x = min(sz, max(q[out], 0.0))
            ventes += x * p - x * pm; q[out] -= x; c[out] -= x * pm
            if sz > x + 1e-9: court[out] += sz - x; recettes_court += (sz - x) * p   # vendu sans achat visible : jetons venus d'une SÉPARATION (1 $ → Up + Down)
    apparie = min(q["Up"], q["Down"])
    pmU = c["Up"] / q["Up"] if q["Up"] > 1e-9 else None; pmD = c["Down"] / q["Down"] if q["Down"] > 1e-9 else None
    cout_paire = (pmU + pmD) if (pmU is not None and pmD is not None) else None
    pnl_paires = apparie * (1 - cout_paire) if cout_paire is not None else 0.0
    seul_cote = "Up" if q["Up"] > q["Down"] else "Down"; reste = abs(q["Up"] - q["Down"])
    pm_reste = (pmU if seul_cote == "Up" else pmD) or 0.0
    pnl_seul = reste * ((1.0 if gagnant == seul_cote else 0.0) - pm_reste)
    delai = (abs(prem["Up"] - prem["Down"]) if len(prem) == 2 else None)
    capital = c["Up"] + c["Down"]
    # séparations déduites : il a fallu séparer au moins max(court Up, court Down) dollars ; la jambe non vendue de ces paires est gardée jusqu'au règlement
    sep = max(court["Up"], court["Down"]); pnl_sep = 0.0
    if sep > 1e-9:
        garde_up = sep - court["Up"]; garde_down = sep - court["Down"]
        pnl_sep = recettes_court + garde_up * (1.0 if gagnant == "Up" else 0.0) + garde_down * (1.0 if gagnant == "Down" else 0.0) - sep
        capital += sep
    return dict(sep=sep, pnl_sep=pnl_sep, apparie=apparie, cout_paire=cout_paire, pnl_paires=pnl_paires, reste=reste, pnl_seul=pnl_seul, ventes=ventes, frais=frais,
                total=pnl_paires + pnl_seul + ventes + pnl_sep - frais, delai=delai, capital=capital, n=len(ex),
                maker=sum(1 for e in ex if e[1] == "M"), preneur=sum(1 for e in ex if e[1] == "P"))


def main():
    base, M = charger(sys.argv[1]); W = par_wallet_marche(M)
    tronques = {st for st, mk in M.items() if mk.get("tronque")}
    o = []; w = o.append
    w("# Bot95 — Autopsie des makers et preneurs rentables (H681–H710) — PRÉLIMINAIRE\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. {len(M)} marchés BTC 5 min lus du {time.strftime('%d.%m %H:%M', time.gmtime(min(M)))} "
      f"au {time.strftime('%d.%m %H:%M', time.gmtime(max(M)))} UTC (avant la période réservée). Marchés INCOMPLETS (≥ 10 000 exécutions, plafond de l'API) : {len(tronques)} — "
      "exclus de tous les calculs de résultat ci-dessous.\n")
    w("FAITS : exécutions (API Data : portefeuille, maker/preneur, issue, côté, parts, prix, seconde) et activité (fusions, règlements, récompenses). "
      "INFÉRENCES : l'interprétation. Frais preneur 0,07·p·(1−p) comptés ; ristourne maker comptée seulement si visible dans l'activité (REWARD). "
      "Une vente sans achat visible (jetons venus d'une séparation ou d'un transfert) est signalée.\n")
    # ---------------- sélection des portefeuilles
    agg = collections.defaultdict(lambda: dict(B=[], vol=0.0, volM=0.0, volP=0.0))
    for (wal, st), ex in W.items():
        if st in tronques: continue
        b = bilan_marche(ex, M[st]["gagnant"]); b["st"] = st; A = agg[wal]; A["B"].append(b)
        for ts, role, out, side, sz, p in ex:
            A["vol"] += sz * p; A["volM" if role == "M" else "volP"] += sz * p
    ok = {k: v for k, v in agg.items() if len(v["B"]) >= 20}
    gros = sorted(ok, key=lambda k: -ok[k]["volM"])[:25]
    rent = sorted(ok, key=lambda k: -sum(b["total"] for b in ok[k]["B"]))[:20]
    pren = [k for k in ok if k.startswith(PRENEURS)]
    sel = list(dict.fromkeys(gros + rent + pren))
    act = base.get("activites", {})

    def stats(k):
        B = ok[k]["B"]; T = [b["total"] for b in sorted(B, key=lambda b: b["st"])]; cum = np.cumsum(T); creux = float(np.min(cum - np.maximum.accumulate(np.concatenate([[0], cum]))[1:]))
        tot = sum(T); top5 = sum(sorted(T, reverse=True)[:5])
        moit = len(T) // 2; s1, s2 = sum(T[:moit]), sum(T[moit:])
        return dict(tot=tot, creux=min(creux, 0), conc=(top5 / tot if tot > 0 else None), s1=s1, s2=s2, cap=np.median([b["capital"] for b in B]), capmax=max(b["capital"] for b in B))
    # ---------------- livrable 1 : tableau
    w("## 1. Les portefeuilles étudiés (25 plus gros makers, 20 plus rentables, 3 preneurs)\n")
    w("| Portefeuille (adresse complète) | Marchés | Volume maker | Volume preneur | Résultat (paires + jambes seules + ventes − frais) | par $ | 1re moitié / 2e moitié | Creux | Part des 5 meilleurs marchés | Capital médian / max par marché | Fusions | Récompenses |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k in sel:
        A = ok[k]; s = stats(k); ac = act.get(k, []); ty = collections.Counter(e["type"] for e in ac)
        rec = sum(float(e.get("usdcSize") or 0) for e in ac if e["type"] in ("REWARD", "MAKER_REBATE", "REBATE"))
        conc = "—" if s["conc"] is None else f"{100 * s['conc']:.0f} %"
        w(f"| `{k}` | {len(A['B'])} | {A['volM']:.0f} $ | {A['volP']:.0f} $ | {s['tot']:+.0f} $ | {s['tot'] / A['vol'] * 100:+.1f} % | {s['s1']:+.0f} / {s['s2']:+.0f} $ | {s['creux']:+.0f} $ | "
          f"{conc} | {s['cap']:.0f} / {s['capmax']:.0f} $ | {ty.get('MERGE', 0) if ac else 'non lu'} | {(str(round(rec)) + ' $') if ac else 'non lu'} |")
    # ---------------- livrable 2 : paires
    w("\n## 2. Paires Up + Down : d'où vient vraiment le résultat ?\n")
    w("Par portefeuille et par marché : parts appariées = min(Up acheté, Down acheté) après ventes ; coût de la paire = prix moyen Up + prix moyen Down ; "
      "résultat des paires = parts appariées × (1 − coût) (acquis quel que soit le gagnant) ; jambe seule = le reste, réglée au résultat officiel.\n")
    w("| Portefeuille | Marchés avec paire | Paire < 1 $ | < 0,98 $ | < 0,95 $ | Coût médian | Délai médian 1re → 2e jambe | Résultat des paires | Résultat des jambes seules | Ventes réalisées | Vente de jetons séparés (déduit) | Frais preneur | Part du résultat venant des paires |")
    w("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k in sel:
        B = ok[k]["B"]; P = [b for b in B if b["cout_paire"] is not None and b["apparie"] > 0]
        if not P: w(f"| `{k[:12]}…` | 0 | — | — | — | — | — | +0 $ | {sum(b['pnl_seul'] for b in B):+.0f} $ | {sum(b['ventes'] for b in B):+.0f} $ | {sum(b['pnl_sep'] for b in B):+.0f} $ ({sum(b['sep'] for b in B):.0f} $ séparés) | {sum(b['frais'] for b in B):.0f} $ | 0 % |"); continue
        cp = [b["cout_paire"] for b in P]; d = [b["delai"] for b in P if b["delai"] is not None]
        rp = sum(b["pnl_paires"] for b in B); rs = sum(b["pnl_seul"] for b in B); rv = sum(b["ventes"] for b in B); fr = sum(b["frais"] for b in B); rsep = sum(b["pnl_sep"] for b in B); tot = rp + rs + rv + rsep - fr
        w(f"| `{k[:12]}…` | {len(P)} | {100 * np.mean([x < 1 for x in cp]):.0f} % | {100 * np.mean([x < 0.98 for x in cp]):.0f} % | {100 * np.mean([x < 0.95 for x in cp]):.0f} % | {np.median(cp):.3f} | "
          f"{np.median(d) if d else float('nan'):.0f} s | {rp:+.0f} $ | {rs:+.0f} $ | {rv:+.0f} $ | {rsep:+.0f} $ ({sum(b['sep'] for b in B):.0f} $ séparés) | {fr:.0f} $ | {(100 * rp / tot if tot > 0 else float('nan')):.0f} % |")
    w("\nVente de jetons séparés : un portefeuille qui VEND des jetons sans les avoir achetés les a obtenus en séparant 1 $ en Up + Down ; on compte ce coût (1 $ la paire) "
      "et la jambe non vendue gardée jusqu'au règlement. C'est une déduction (la séparation elle-même n'est visible que dans l'activité).\n")
    w("\nLecture : un portefeuille gagne « grâce aux paires » si le résultat des paires est positif et porte l'essentiel du total ; s'il vient des jambes seules, c'est un pari directionnel.\n")
    # ---------------- livrable 4 : trois preneurs
    w("## 3. Autopsie des trois preneurs\n")
    for k in pren:
        A = ok[k]; B = A["B"]; ex = [e for (wal, st), L in W.items() if wal == k and st not in tronques for e in [(st, x) for x in L]]
        rows = collections.defaultdict(lambda: [0, 0.0, 0.0])            # (rôle, tranche de temps) → n, volume, résultat au règlement
        for st, (ts, role, out, side, sz, p) in ex:
            g = M[st]["gagnant"]; win = 1.0 if out == g else 0.0; r = sz * (win - p) if side == "BUY" else sz * (p - win)
            if role == "P": r -= sz * FEE(p)
            tr = (ts - st) // 60; key = (role, f"{tr * 60}–{tr * 60 + 60} s", side)
            rows[key][0] += 1; rows[key][1] += sz * p; rows[key][2] += r
        w(f"### `{k}`\n")
        w(f"{len(B)} marchés, volume preneur {A['volP']:.0f} $, maker {A['volM']:.0f} $ ; marchés avec les deux côtés : {sum(1 for b in B if b['cout_paire'] is not None)}.\n")
        w("| Rôle | Minute du cycle | Côté | Exécutions | Volume | Résultat au règlement (frais preneur déduits) | par $ |\n|---|---|---|---|---|---|---|")
        for (role, tr, side), (n, v, r) in sorted(rows.items(), key=lambda kv: (kv[0][0], int(kv[0][1].split('–')[0]), kv[0][2])):
            w(f"| {'preneur' if role == 'P' else 'maker'} | {tr} | {side} | {n} | {v:.0f} $ | {r:+.0f} $ | {(r / v if v else 0):+.3f} |")
        w("")
    # ---------------- livrable 5 : risque M9
    w("## 4. Risque d'achat à 0,95–0,99 en fin de cycle (M9) — toutes les exécutions de tous les portefeuilles\n")
    R = collections.defaultdict(lambda: dict(n=0, parts=0.0, gain=0.0, perdues=0, marches=set(), pertes=[]))
    for st, mk in M.items():
        if st in tronques: continue
        g = mk["gagnant"]
        for wal, role, out, side, sz, p, ts in mk["ex"]:
            if role != "M" or side != "BUY" or p < 0.95 or ts - st < 270: continue
            b = "0,95–0,97" if p < 0.97 else ("0,97–0,98" if p < 0.98 else ("0,98–0,99" if p < 0.99 else "≥ 0,99"))
            x = R[b]; win = 1.0 if out == g else 0.0; x["n"] += 1; x["parts"] += sz; x["gain"] += sz * (win - p); x["marches"].add(st)
            if win == 0: x["perdues"] += 1; x["pertes"].append(sz * p)
    w("Achats MAKER à ces prix dans les 30 dernières secondes (aucun frais maker ; ristourne non comptée, de l'ordre de 0,02 c par part à ces prix).\n")
    w("| Prix | Remplissages | Parts | Marchés | Remplissages perdants | Taux de victoire nécessaire (seuil) | Taux observé | Résultat | par part | Plus grosse perte d'un remplissage |\n|---|---|---|---|---|---|---|---|---|---|")
    for b in ("0,95–0,97", "0,97–0,98", "0,98–0,99", "≥ 0,99"):
        x = R.get(b)
        if not x: continue
        seuil = {"0,95–0,97": "≈ 96 %", "0,97–0,98": "≈ 97,5 %", "0,98–0,99": "≈ 98,5 %", "≥ 0,99": "≈ 99,3 %"}[b]
        w(f"| {b} | {x['n']} | {x['parts']:.0f} | {len(x['marches'])} | {x['perdues']} | {seuil} | {100 * (1 - x['perdues'] / x['n']):.2f} % | {x['gain']:+.0f} $ | {100 * x['gain'] / x['parts']:+.2f} c | {max(x['pertes']) if x['pertes'] else 0:.0f} $ |")
    w("\nLecture : à 0,98, une seule part perdue coûte 0,98 $ et efface 49 parts gagnées. Une politique plafonnée à 0,95 se lit sur la 1re ligne.\n")
    # même mesure séparée par fenêtre de fin de cycle (30–15 s, 15–5 s, 5–0 s restantes)
    w("**Séparation par temps restant** (achats maker, mêmes tranches de prix)\n")
    w("| Prix | 30–15 s restantes : remplis / perdants / résultat | 15–5 s | 5–0 s |\n|---|---|---|---|")
    F_ = collections.defaultdict(lambda: [0, 0, 0.0])
    for st, mk in M.items():
        if st in tronques: continue
        g = mk["gagnant"]
        for wal, role, out, side, sz, p, ts in mk["ex"]:
            if role != "M" or side != "BUY" or p < 0.95 or not (270 <= ts - st < 300): continue
            b = "0,95–0,97" if p < 0.97 else ("0,97–0,98" if p < 0.98 else ("0,98–0,99" if p < 0.99 else "≥ 0,99"))
            fen = "30–15" if ts - st < 285 else ("15–5" if ts - st < 295 else "5–0")
            win = 1.0 if out == g else 0.0; x = F_[(b, fen)]; x[0] += 1; x[1] += (win == 0); x[2] += sz * (win - p)
    for b in ("0,95–0,97", "0,97–0,98", "0,98–0,99", "≥ 0,99"):
        w(f"| {b} | " + " | ".join(f"{F_[(b, f)][0]} / {F_[(b, f)][1]} / {F_[(b, f)][2]:+.0f} $" for f in ("30–15", "15–5", "5–0")) + " |")
    w("")
    # ---------------- P5 intégrité
    w("## 5. Intégrité des données\n")
    w(f"- Marchés lus : {len(M)} ; incomplets (≥ 10 000 exécutions) : {len(tronques)} (exclus des résultats). Plafond de l'API Data : décalage ≤ 10 000.")
    w("- Événements blockchain (OrderFilled) : le sous-graphe public Goldsky a répondu « trop de requêtes » (429) depuis GitHub ; reconstruction par la blockchain NON faite à ce stade.")
    w("- Maker / preneur : déduit de l'API Data (liste « preneur seulement »), non vérifié contre les événements blockchain.")
    w("- Fusions, séparations, règlements, récompenses : lus dans l'activité des portefeuilles étudiés seulement (« non lu » sinon). Une vente sans achat visible signale des jetons venus d'une séparation.")
    w("- Ristournes maker : comptées seulement si l'activité les montre. Frais preneur : calculés (0,07·p·(1−p)).\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o)[:12000])


if __name__ == "__main__":
    main()
