# 06.11.2026 — Étude H-NOUVELLES (méthode etude-fantome) : nouvelles idées pour la NUIT et le BTC CALME, sur les données seconde par seconde de bot95
# (sig:BTC:<minute>, depuis le 19.10). Exécution PRUDENTE : achat au meilleur vendeur de la seconde SUIVANTE (1 s de retard), seulement la quantité
# affichée à ce prix, mise 50 $, frais Polymarket 0,07 × p × (1 − p) par part. Résultat du cycle : moyenne Chainlink des 60 dernières secondes contre
# le prix à battre (approximation du règlement Polymarket). Paramètres choisis sur 19.10 → 31.10 (apprentissage) ; verdict sur 01.11 → 05.11 (jours inédits).
import json, sys, os, urllib.request, collections, datetime as dt, math, statistics
BOT95, OUT = sys.argv[1], sys.argv[2]
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "etude"}), timeout=120) as r: return json.load(r)
# 1) téléchargement (cache sur disque)
cache = os.path.join(OUT, "sig_btc.jsonl")
if not os.path.exists(cache):
    apres, n = None, 0
    with open(cache, "w") as f:
        while True:
            d = get(f"{BOT95}/api/sig?a=BTC&n=120" + (f"&apres={urllib.parse.quote(apres)}" if apres else ""))
            for k, doc in zip(d["cles"], d["docs"]): f.write(json.dumps({"k": k, "d": doc}) + "\n"); n += 1
            if not d["cles"] or len(d["cles"]) < 120: break
            apres = d["suivant"]
    print("minutes téléchargées", n)
import urllib.parse
cols = None; R = {}
for ligne in open(cache):
    e = json.loads(ligne); doc = e["d"]; cols = doc["colonnes"]; I = {c: i for i, c in enumerate(cols)}
    for l in doc["lignes"]:
        t = l[I["t"]]; t = t if isinstance(t, (int, float)) else int(dt.datetime.fromisoformat(str(t).replace("Z", "+00:00")).timestamp())
        R[int(t if t < 1e12 else t / 1000)] = l
I = {c: i for i, c in enumerate(cols)}
print("secondes", len(R))
def v(t, c):
    l = R.get(t); 
    if l is None: return None
    x = l[I[c]]; return None if x is None or x == "" else float(x)
# 2) cycles
starts = sorted(set(int(v(t, "start")) for t in R if v(t, "start")))
def jour(s): return (dt.datetime.fromtimestamp(s, dt.timezone.utc) + dt.timedelta(hours=1)).strftime("%Y-%m-%d")
def nuit(s): return (dt.datetime.fromtimestamp(s, dt.timezone.utc) + dt.timedelta(hours=1)).hour < 8
APP = lambda j: "2026-10-19" <= j <= "2026-10-31"; TEST = lambda j: "2026-11-01" <= j <= "2026-11-05"
cyc = {}
for s in starts:
    k = v(s + 150, "prix_a_battre") or v(s + 10, "prix_a_battre")
    fin = [v(u, "chainlink") for u in range(s + 240, s + 300)]; fin = [x for x in fin if x]
    if not k or len(fin) < 40: continue
    up = sum(fin) / len(fin) > k
    c0 = v(s - 1, "chainlink") or v(s, "chainlink"); c60 = v(s - 3600, "chainlink")
    tend = abs(c0 / c60 - 1) * 1e4 if c0 and c60 else None
    cyc[s] = {"k": k, "up": up, "tend": tend, "nuit": nuit(s), "jour": jour(s)}
print("cycles utilisables", len(cyc))
def achat(s, u, cote, mise=50.0):
    """achat au meilleur vendeur à la seconde u+1 (1 s de retard), quantité affichée seulement"""
    a = v(u + 1, "pm_up_vente") if cote == "Up" else (lambda b: None if b is None else 1 - b)(v(u + 1, "pm_up_achat"))
    tl = v(u + 1, "pm_up_vente_taille") if cote == "Up" else v(u + 1, "pm_up_achat_taille")
    if a is None or tl is None or not (0.01 <= a <= 0.99): return None
    parts = min(mise / (a + 0.07 * a * (1 - a)), tl)
    if parts * a < 1: return None
    cout = parts * (a + 0.07 * a * (1 - a)); g = cyc[s]["up"] == (cote == "Up")
    return (parts if g else 0) - cout, cout, a
def vol60(s, u):
    x = [v(w, "chainlink") for w in range(u - 60, u + 1)]; x = [y for y in x if y]
    return statistics.pstdev([x[i] - x[i - 1] for i in range(1, len(x))]) if len(x) > 20 else None
# 3) idées (une décision par cycle au plus)
def S1(p):   # fin de cycle quasi sûre : dernier quart de minute, côté gagnant probable, prix entre pmin et pmax, écart au prix à battre ≥ z × agitation
    z, fen, pmin, pmax = p
    def f(s):
        c = cyc[s]
        for u in range(s + 300 - fen, s + 295):
            cl = v(u, "chainlink"); sd = vol60(s, u) if (u - s) % 5 == 0 else None
            if cl is None or sd is None or sd <= 0: continue
            e = (cl - c["k"]) / (sd * math.sqrt(max(1, s + 300 - u)))
            cote = "Up" if e > 0 else "Down"
            if abs(e) < z: continue
            a = v(u, "pm_up_vente") if cote == "Up" else (lambda b: None if b is None else 1 - b)(v(u, "pm_up_achat"))
            if a is None or not (pmin <= a <= pmax): continue
            return achat(s, u, cote)
    return f
def S2(p):   # retour vers le prix à battre : 30-180 s, BTC tout près du prix à battre mais un côté très bon marché → on achète ce côté
    x, amax = p
    def f(s):
        c = cyc[s]
        for u in range(s + 30, s + 180, 2):
            cl = v(u, "chainlink"); aU = v(u, "pm_up_vente"); bU = v(u, "pm_up_achat")
            if cl is None or aU is None or bU is None: continue
            if abs(cl / c["k"] - 1) * 1e4 > x: continue
            if aU <= amax: return achat(s, u, "Up")
            if 1 - bU <= amax: return achat(s, u, "Down")
    return f
def S3(p):   # retard de Polymarket : Binance a bougé de y pb en 3 s, le prix Polymarket du côté concerné n'a pas encore suivi
    y, retard = p
    def f(s):
        for u in range(s + 20, s + 270):
            b0, b3 = v(u, "binance_spot"), v(u - 3, "binance_spot"); pr = v(u, "proba_up_modele")
            if not b0 or not b3 or pr is None: continue
            m = (b0 / b3 - 1) * 1e4
            if abs(m) < y: continue
            cote = "Up" if m > 0 else "Down"
            a = v(u, "pm_up_vente") if cote == "Up" else (lambda b: None if b is None else 1 - b)(v(u, "pm_up_achat"))
            juste = pr if cote == "Up" else 1 - pr
            if a is None or a > juste - retard: continue
            return achat(s, u, cote)
    return f
GRILLE = {"S1 fin de cycle quasi sûre": (S1, [(z, fen, pm, px) for z in (1.5, 2, 3) for fen in (30, 60) for pm, px in ((0.80, 0.95), (0.85, 0.97), (0.70, 0.90))]),
          "S2 retour vers le prix à battre": (S2, [(x, am) for x in (2, 4, 6) for am in (0.15, 0.25, 0.35)]),
          "S3 retard de Polymarket": (S3, [(y, r) for y in (3, 5, 8) for r in (0.03, 0.06, 0.10)])}
def bilan(res):
    if not res: return (0, 0, 0, 0, 0)
    cum = pic = cr = 0
    for g in res: cum += g; pic = max(pic, cum); cr = max(cr, pic - cum)
    return len(res), sum(1 for g in res if g > 0) / len(res) * 100, sum(res), cr, 0
FILTRES = {"tout": lambda c: True, "nuit": lambda c: c["nuit"], "calme": lambda c: c["tend"] is not None and c["tend"] < 13.8, "nuit ou calme": lambda c: c["nuit"] or (c["tend"] is not None and c["tend"] < 13.8)}
print("\n=== RÉSULTATS (exécution prudente, 50 $ par trade) ===")
for nom, (fab, grille) in GRILLE.items():
    for fn, flt in FILTRES.items():
        meil = None
        for p in grille:
            f = fab(p); app = [r[0] for s, c in cyc.items() if APP(c["jour"]) and flt(c) for r in [f(s)] if r]
            n, pct, g, cr, _ = bilan(app)
            if n >= 30 and (meil is None or g > meil[1]): meil = (p, g, n, pct, cr)
        if not meil: print(f"{nom} [{fn}] : pas assez de trades"); continue
        p = meil[0]; f = fab(p)
        test = collections.defaultdict(list)
        for s, c in sorted(cyc.items()):
            if TEST(c["jour"]) and flt(c):
                r = f(s)
                if r: test[c["jour"]].append(r[0])
        tous = [g for j in sorted(test) for g in test[j]]; n, pct, g, cr, _ = bilan(tous)
        print(f"{nom} [{fn}] paramètres {p} | APPRENTISSAGE {meil[2]} trades, {meil[3]:.0f} % gagnés, {meil[1]:+.0f} $, creux {meil[4]:.0f} | "
              f"JOURS INÉDITS {n} trades, {pct:.0f} % gagnés, {g:+.0f} $, creux {cr:.0f}, par jour {[round(sum(test[j])) for j in sorted(test)]}")
print("\nFIN")
