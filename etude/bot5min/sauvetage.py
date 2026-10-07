"""Sauvetage des desaccords (07.10.2026, demande de Pitch) — sur les VRAIS carnets enregistres par le bot (4/s, 48 h).
1. Rejoue les desaccords 10 / 15 / 20 exactement comme le bot (1 achat par cycle, au meilleur vendeur, 50 $), et exporte TOUS les trades
   (avec le chemin du prix apres l'entree) -> sauvetage_trades.json (pour le PDF).
2. Teste ~1 000 combinaisons de sauvetage : entree (direct / confirme / confirme + perp) x prise de gain (+25/+50/+100/+200 %, totale ou moitie)
   x coupe (-30/-50/-70 %, -10 c) x action a la coupe (sortir / inverser / couvrir) x sortie en fin de cycle (aucune / a 60 s si perdant / a 30 s si perdant).
   Classement sur la 1re moitie, verification sur la 2e.
"""
import json, sys, time, statistics, collections, urllib.request, itertools

U = "https://bot95.pitch67.workers.dev"
OUT = "etude/bot5min/"
FEE = lambda p: 0.072 * p * (1 - p)
MISE = 50.0


def get(url):
    err = None
    for k in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "analyse"}), timeout=90) as r: return json.loads(r.read())
        except Exception as e: err = e; time.sleep(3)
    raise err


def log(*a): print(*a, flush=True)


def charger(a):
    L, apres = [], None
    while True:
        d = get(f"{U}/api/rec?a={a}&n=60" + (f"&apres={apres}" if apres else ""))
        for doc in d["docs"]: L += doc["lignes"]
        if not d["cles"] or len(d["cles"]) < 60: break
        apres = d["suivant"]
    L.sort(key=lambda r: r[0])
    C = collections.defaultdict(list)
    for r in L:
        if None in (r[2], r[3], r[4], r[5], r[6]): continue
        if C[r[1]] and r[0] - C[r[1]][-1][0] < 1: continue
        C[r[1]].append(r)
    return C


RES = {}
def resultat(a, st):
    if (a, st) in RES: return RES[(a, st)]
    r = None
    try:
        ev = get(f"https://gamma-api.polymarket.com/events?slug={a.lower()}-updown-5m-{st}")
        m = ev[0]["markets"][0]; px = [float(x) for x in json.loads(m["outcomePrices"])]; outs = json.loads(m["outcomes"])
        if sorted(px) == [0.0, 1.0]: r = outs[px.index(1.0)].lower() == "up"
    except Exception: pass
    RES[(a, st)] = r
    return r


def cote(r, up): return (r[3], r[4], r[2]) if up else (r[5], r[6], 1 - r[2])


def detecter(R, E):
    """comme le bot : premier instant (tl >= 5) ou un cote a modele - vendeur >= E ; un seul achat par cycle"""
    st = R[0][1]
    for i, r in enumerate(R):
        if st + 300 - r[0] < 5: return None
        for up in (True, False):
            b, a, f = cote(r, up)
            if 0.03 <= a <= 0.97 and f - a >= E: return (i, up)
    return None


def perp_ok(R, i, up):
    j = next((j for j in range(i, -1, -1) if R[i][0] - R[j][0] >= 5), None)
    if j is None or R[i][11] is None or R[j][11] is None: return False
    return (R[i][11] - R[j][11]) * (1 if up else -1) >= 0


def entree(R, i0, up, mode):
    if mode == "direct": return i0
    b0, a0, _ = cote(R[i0], up); m0 = (b0 + a0) / 2; st = R[0][1]
    for j in range(i0, len(R)):
        if R[j][0] - R[i0][0] >= 20:
            b, a, f = cote(R[j], up)
            if (b + a) / 2 - m0 >= 0.03 and f - a >= 0.03 and st + 300 - R[j][0] >= 5 and a <= 0.97:
                if mode == "confirme+perp" and not perp_ok(R, j, up): return None
                return j
            return None
    return None


def jouer(R, up, ie, gagne, tp, tp_moitie, sl, act, fin):
    """gain en $ pour une mise de 50 $"""
    st = R[0][1]
    b, a, f = cote(R[ie], up)
    n = MISE / a; cash = -n * (a + FEE(a)); main = n; autre = 0.0; tp_fait = False; sl_fait = False
    for j in range(ie + 1, len(R)):
        tl = st + 300 - R[j][0]
        if tl < 1: break
        b2, a2, _ = cote(R[j], up)
        if main > 0 and tp and not tp_fait and b2 >= a * (1 + tp):
            q = main / 2 if tp_moitie else main
            cash += q * (b2 - FEE(b2)); main -= q; tp_fait = True
            if main <= 0: break
        if main > 0 and sl is not None and not sl_fait and ((b2 <= a * (1 + sl)) if sl < 0 else (a - b2 >= sl)):
            sl_fait = True
            if act in ("sortir", "inverser"): cash += main * (b2 - FEE(b2))
            if act in ("inverser", "couvrir"):
                ob, oa, _ = cote(R[j], not up)
                q = main if act == "couvrir" else (main * b2) / max(oa, 0.01)       # couvrir : autant de parts de l'autre cote ; inverser : l'argent recupere va de l'autre cote
                cash -= q * (oa + FEE(oa)); autre += q
            if act in ("sortir", "inverser"): main = 0
        if main > 0 and fin and ((fin == 60 and tl <= 60) or (fin == 30 and tl <= 30)) and b2 < a:
            cash += main * (b2 - FEE(b2)); main = 0; break
    if gagne is None: return None
    gm = gagne if up else (not gagne)
    return cash + main * (1 if gm else 0) + autre * (0 if gm else 1)


def main():
    rap = ["# Sauvetage des desaccords — vrais carnets du bot", ""]
    tous = {}
    data = {a: charger(a) for a in ("BTC", "ETH")}
    for a, C in data.items():
        log(a, len(C), "cycles")
        for st in sorted(C): resultat(a, st)
    # ---------- 1. tous les trades (desaccord simple, comme le bot)
    for a, C in data.items():
        for E in (0.10, 0.15, 0.20):
            L = []
            for st in sorted(C):
                R = C[st]; d = detecter(R, E)
                if not d: continue
                i, up = d; b, k, f = cote(R[i], up); g = RES.get((a, st))
                bids = [cote(R[j], up)[0] for j in range(i, len(R))]
                n = MISE / k; gm = None if g is None else (g if up else not g)
                pnl = None if gm is None else n * ((1 if gm else 0) - k - FEE(k))
                L.append({"heure": time.strftime('%d.%m %H:%M:%S', time.gmtime(R[i][0] + 7200)), "t": R[i][0], "start": st, "cote": "Up" if up else "Down", "prix": k, "modele": round(f, 3),
                          "ecart": round(f - k, 3), "reste_s": int(st + 300 - R[i][0]), "perp_avec": perp_ok(R, i, up), "bid_min": min(bids), "bid_max": max(bids),
                          "bid_fin": bids[-1], "gagne": gm, "gain_50": None if pnl is None else round(pnl, 2)})
            tous[f"desaccord {int(E * 100)} {a}"] = L
    json.dump(tous, open(OUT + "sauvetage_trades.json", "w"))
    # ---------- 2. ~1 000 combinaisons
    TP = [None, 0.25, 0.5, 1.0, 2.0]
    SL = [None, -0.3, -0.5, -0.7, 0.10]
    ACT = ["sortir", "inverser", "couvrir"]
    FIN = [None, 60, 30]
    combos = []
    for ent in ("direct", "confirme", "confirme+perp"):
        for tp in TP:
            for moit in ([False] if tp is None else [False, True]):
                for sl in SL:
                    for act in (["-"] if sl is None else ACT):
                        for fin in FIN:
                            combos.append((ent, tp, moit, sl, act, fin))
    log(len(combos), "combinaisons")
    rap += [f"**{len(combos)} combinaisons** testees sur chaque strategie. Gain en $ pour une mise de 50 $, frais compris, resultat officiel. "
            "Prise de gain = revente quand le meilleur acheteur atteint +x % du prix d'entree (toute la position, ou la moitie). Coupe = quand il tombe a -x % (ou -10 c). "
            "Fin = revendre a 60 s / 30 s de la fin si on est en perte.", ""]
    nom = lambda c: f"{c[0]} · gain {('+' + str(int(c[1] * 100)) + ' %' + (' (moitie)' if c[2] else '')) if c[1] else 'non'} · coupe {('-' + str(int(-c[3] * 100)) + ' %' if c[3] and c[3] < 0 else ('-10 c' if c[3] else 'non'))}{(' → ' + c[4]) if c[3] else ''} · fin {str(c[5]) + ' s' if c[5] else 'non'}"
    for a, C in data.items():
        sts = sorted(C); mi = sts[len(sts) // 2]
        for E in (0.10, 0.15, 0.20):
            EV = [(st,) + detecter(C[st], E) for st in sts if detecter(C[st], E)]
            res = []
            for c in combos:
                A, B = [], []
                for st, i0, up in EV:
                    ie = entree(C[st], i0, up, c[0])
                    if ie is None: continue
                    g = jouer(C[st], up, ie, RES.get((a, st)), c[1], c[2], c[3], c[4], c[5])
                    if g is None: continue
                    (A if st < mi else B).append(g)
                if len(A) >= 10 and len(B) >= 8: res.append((sum(A), len(A), sum(B), len(B), c))
            if not res: continue
            res.sort(key=lambda x: -x[0])
            ref = next((x for x in res if x[4] == ("direct", None, False, None, "-", None)), None)
            pos2 = sum(1 for x in res if x[2] > 0)
            rap += [f"## Desaccord {int(E * 100)} {a} — {len(EV)} trades ({time.strftime('%d.%m %H:%M', time.gmtime(sts[0] + 7200))} → {time.strftime('%d.%m %H:%M', time.gmtime(sts[-1] + 7500))})", ""]
            if ref: rap.append(f"Tel quel (direct, rien) : 1re moitie **{ref[0]:+.0f} $** ({ref[1]}) · 2e moitie **{ref[2]:+.0f} $** ({ref[3]})")
            rap += [f"Combinaisons positives sur la 2e moitie : **{pos2} / {len(res)}** · positives sur les DEUX moities : **{sum(1 for x in res if x[0] > 0 and x[2] > 0)}**", "",
                    "| Combinaison (classee sur la 1re moitie) | 1re moitie | **2e moitie (verification)** |", "|---|---|---|"]
            for x in res[:15]: rap.append(f"| {nom(x[4])} | {x[0]:+.0f} $ ({x[1]}) | **{x[2]:+.0f} $** ({x[3]}) |")
            # effet moyen de chaque element (2e moitie)
            for k, lab in ((0, "Entree"), (1, "Prise de gain"), (3, "Coupe"), (4, "Action a la coupe"), (5, "Fin de cycle")):
                par = collections.defaultdict(list)
                for x in res: par[x[4][k]].append(x[2] / max(x[3], 1))
                rap.append(f"- {lab} (gain moyen par trade, 2e moitie) : " + " · ".join(f"{v if v is not None else 'non'} {statistics.mean(l):+.2f} $" for v, l in sorted(par.items(), key=lambda kv: -statistics.mean(kv[1]))))
            rap.append("")
            open(OUT + "resultat_sauvetage.md", "w").write("\n".join(rap))
    open(OUT + "resultat_sauvetage.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
