"""BOT95 — SUIVI DES MAKERS (et des preneurs) des marchés BTC Up/Down 5 min. Demande de Pitch, 11.10.2026 15:30 (« cherchons les makers et on
track leur behavior »). Lecture seule : API publiques de Polymarket (Gamma + Data API), aucune clé, aucun ordre.
Pour chaque marché terminé : toutes les exécutions (takerOnly=false) et les exécutions preneuses (takerOnly=true) ; maker = exécution qui n'est
pas preneuse. Par portefeuille : marchés, exécutions, volume, résultat au règlement, prix, moment dans le cycle, achat des deux côtés,
stock final, et — quand le cycle a été enregistré à Dublin — sélection adverse (milieu du carnet +1 / +5 / +30 s) de ses exécutions.
Usage (GitHub Actions) : python3 etude/bot5min/makers_suivi.py [nb_marchés] [dossier_cycles_dublin]
→ bot95/makers_suivi.json (cumulé, jamais effacé) + etude/bot5min/resultat_makers_suivi.md"""
import json, os, sys, time, collections, urllib.request, glob, gzip, bisect
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__)); RACINE = os.path.abspath(os.path.join(ICI, "..", ".."))
G = "https://gamma-api.polymarket.com"; D = "https://data-api.polymarket.com"
BASE = os.path.join(RACINE, "bot95", "makers_suivi.json"); SORTIE = os.path.join(ICI, "resultat_makers_suivi.md")


def get(url, tries=5):
    err = None
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "bot95-etude"}), timeout=60) as r:
                return json.loads(r.read())
        except Exception as e:
            err = e
            if "404" in str(e) or "400" in str(e): break
            time.sleep(8 if "429" in str(e) else 1.5 * (k + 1))
    raise err


def executions(cid, taker):
    out = []
    for off in range(0, 4000, 500):
        try: lot = get(f"{D}/trades?market={cid}&limit=500&offset={off}&takerOnly={'true' if taker else 'false'}")
        except Exception: break
        out += lot
        if len(lot) < 500: break
    return out


def cle(t): return (t.get("transactionHash"), t.get("proxyWallet"), t.get("asset"), t.get("side"), str(t.get("size")), str(t.get("price")), int(t.get("timestamp") or 0))


def collecter(nb):
    base = json.load(open(BASE)) if os.path.exists(BASE) else {"marches": {}}
    fin = int(time.time()) // 300 * 300 - 900                       # marchés terminés depuis au moins 10 min
    n = 0
    for k in range(nb):
        st = fin - 300 * k
        if str(st) in base["marches"]: continue
        try:
            ev = get(f"{G}/events?slug=btc-updown-5m-{st}"); m = ev[0]["markets"][0]
            outs = json.loads(m["outcomes"]); px = [float(x) for x in json.loads(m["outcomePrices"])]; toks = json.loads(m["clobTokenIds"])
            if 1.0 not in px: continue
            gagnant = outs[px.index(1.0)]
        except Exception: continue
        tout = executions(m["conditionId"], False); pren = executions(m["conditionId"], True)
        kp = collections.Counter(cle(t) for t in pren); lignes = []
        for t in tout:
            c = cle(t); role = "P" if kp[c] > 0 else "M"
            if role == "P": kp[c] -= 1
            lignes.append([t.get("proxyWallet"), role, t.get("outcome"), t.get("side"), float(t["size"]), float(t["price"]), int(t["timestamp"])])
        base["marches"][str(st)] = {"gagnant": gagnant, "up": toks[outs.index("Up")] if "Up" in outs else None, "n": len(lignes), "tronque": len(tout) >= 4000, "ex": lignes}
        n += 1
        if n % 20 == 0: print("marchés lus", n, flush=True); json.dump(base, open(BASE, "w"))
    # on garde 14 jours
    lim = fin - 14 * 86400
    base["marches"] = {k: v for k, v in base["marches"].items() if int(k) >= lim}
    json.dump(base, open(BASE, "w")); print("nouveaux marchés", n, "total", len(base["marches"]))
    return base


def milieux_dublin(dossier):
    """milieu du carnet Up (série) par cycle enregistré à Dublin"""
    out = {}
    if not dossier or not os.path.isdir(dossier): return out
    sys.path.insert(0, ICI)
    import fast_fenetre as FF, queue_race_phase12 as Q
    for fn in glob.glob(os.path.join(dossier, "**", "*.json.gz"), recursive=True):
        try:
            C = FF.normaliser(fn); Rj = Q.rejouer(C); S = Rj["serie"]
            if len(S) > 10: out[C["start"]] = S
        except Exception: pass
    return out


def mid(S, t_ms):
    i = np.searchsorted(S[:, 0], t_ms, "right") - 1
    if i < 0 or np.isnan(S[i, 1]) or np.isnan(S[i, 3]): return None
    return (S[i, 1] + S[i, 3]) / 2000.0


def analyser(base, MID):
    W = collections.defaultdict(lambda: dict(M=set(), n=0, vol=0.0, pnl=0.0, pnl_pc=collections.defaultdict(float), prix=[], t=[], deux=0, stock=[],
                                             mo=collections.defaultdict(list), achats=0, ventes=0))
    for st, mk in base["marches"].items():
        st = int(st); g = mk["gagnant"]; S = MID.get(st)
        par = collections.defaultdict(lambda: collections.defaultdict(float))
        for w, role, out, side, sz, p, ts in mk["ex"]:
            key = (w, role); X = W[key]; X["M"].add(st); X["n"] += 1; X["vol"] += sz * p
            win = 1.0 if out == g else 0.0
            pnl = sz * (win - p) if side == "BUY" else sz * (p - win)
            X["pnl"] += pnl; X["pnl_pc"][st] += pnl; X["prix"].append(p); X["t"].append(ts - st)
            if side == "BUY": X["achats"] += 1; par[key][out] += sz
            else: X["ventes"] += 1; par[key][out] -= sz
            if S is not None:                                       # sélection adverse : prix du côté acheté (ou vendu) +1/+5/+30 s
                m0 = mid(S, ts * 1000)
                if m0 is not None:
                    sens = (1 if out == "Up" else -1) * (1 if side == "BUY" else -1)
                    for h in (1, 5, 30):
                        m1 = mid(S, ts * 1000 + h * 1000)
                        if m1 is not None: X["mo"][h].append(sens * (m1 - m0))
        for key, d in par.items():
            if d.get("Up", 0) > 0 and d.get("Down", 0) > 0: W[key]["deux"] += 1
            tot = abs(d.get("Up", 0)) + abs(d.get("Down", 0))
            if tot > 0: W[key]["stock"].append(abs(d.get("Up", 0) - d.get("Down", 0)) / tot)
    return W


def rapport(base, W):
    nM = len(base["marches"]); tr = sum(1 for v in base["marches"].values() if v.get("tronque"))
    o = []; w = o.append
    w("# Bot95 — Suivi des makers et des preneurs (BTC 5 min) — lecture seule\n")
    w(f"Généré le {time.strftime('%d.%m.%Y %H:%M', time.gmtime())} UTC. {nM} marchés lus (14 jours max), dont {tr} tronqués (> 4 000 exécutions). "
      "Maker = exécution absente de la liste « preneur seulement » de l'API Data de Polymarket. Résultat = au règlement officiel, sans frais ni ristourne. "
      "Sélection adverse = milieu du carnet Up (Dublin) h secondes après, dans le sens de la position, en cents (seulement les cycles enregistrés à Dublin).\n")
    for role, nom in (("M", "MAKERS"), ("P", "PRENEURS")):
        L = [(k, X) for k, X in W.items() if k[1] == role and len(X["M"]) >= 20]
        L.sort(key=lambda kx: -kx[1]["vol"])
        w(f"## {nom} — les 25 plus gros (≥ 20 marchés)\n")
        w("| Portefeuille | Marchés | Exécutions | Volume | Résultat | par $ | Cycles gagnants | Prix médian | Moment médian (s du début) | Achète les 2 côtés | Déséquilibre final médian | Sélection adverse +1 / +5 / +30 s (c) |")
        w("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for (wal, _), X in L[:25]:
            pc = X["pnl_pc"]; gg = sum(1 for v in pc.values() if v > 0)
            mo = " / ".join(f"{100 * np.mean(X['mo'][h]):+.2f}" if X["mo"][h] else "—" for h in (1, 5, 30))
            w(f"| {wal[:10]}… | {len(X['M'])} | {X['n']} | {X['vol']:.0f} $ | {X['pnl']:+.0f} $ | {(X['pnl'] / X['vol'] if X['vol'] else 0):+.3f} | {100 * gg / len(pc):.0f} % | "
              f"{np.median(X['prix']):.2f} | {np.median(X['t']):.0f} | {100 * X['deux'] / len(X['M']):.0f} % | {np.median(X['stock']) if X['stock'] else float('nan'):.2f} | {mo} |")
        w("")
        G2 = sorted(L, key=lambda kx: -kx[1]["pnl"])[:10]
        w(f"**{nom} les plus rentables** (≥ 20 marchés) : " + " ; ".join(f"{k[0][:10]}… {X['pnl']:+.0f} $ sur {X['vol']:.0f} $" for k, X in G2) + "\n")
    w("## Limites\n- L'API Data ne donne l'heure qu'à la seconde ; un même portefeuille peut avoir plusieurs adresses.\n"
      "- Les offres posées et retirées sans exécution sont invisibles (carnet anonyme) : on ne voit que les remplissages.\n- Le résultat ignore la ristourne maker et les frais preneur.\n")
    open(SORTIE, "w").write("\n".join(o)); print("\n".join(o)[:6000])


if __name__ == "__main__":
    nb = int(sys.argv[1]) if len(sys.argv) > 1 else 288
    base = collecter(nb)
    MID = milieux_dublin(sys.argv[2] if len(sys.argv) > 2 else None)
    rapport(base, analyser(base, MID))
