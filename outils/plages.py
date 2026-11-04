# 04.11.2026 15:26 — Étude H-PLAGES (méthode etude-fantome de Pitch)
# Hypothèse : choisir pour chaque plage horaire (heure de Paris) la stratégie la meilleure DANS CETTE PLAGE sur les jours d'apprentissage
# rapporte plus, sur des jours inédits, que garder la meilleure stratégie unique toute la journée.
# Apprentissage : 19.10 -> 28.10 (10 jours). Verdict : 29.10 -> 03.11 (6 jours inédits, jamais utilisés pour choisir). Aujourd'hui exclu (journée en cours).
# Plafond 250 $ par cycle et par stratégie. Données : trades des fichiers Excel des onglets bot95 (fantômes, sauf onglet 5 depuis le 04.11 00:30).
import openpyxl, datetime as dt, collections, sys, random
PLAGES = [("nuit 00-08", 0, 8), ("Europe 08-15h30", 8, 15.5), ("US 15h30-22", 15.5, 22), ("soir 22-24", 22, 24)]
APP = [(dt.date(2026, 10, 19) + dt.timedelta(days=i)).isoformat() for i in range(10)]
TEST = [(dt.date(2026, 10, 29) + dt.timedelta(days=i)).isoformat() for i in range(6)]
MIN_TRADES = 20
def plage(d):
    h = d.hour + d.minute / 60
    for n, a, b in PLAGES:
        if a <= h < b: return n
Z = {}   # nom -> {(jour, plage): net}, nb trades par (periode, plage)
vus = set()
for f in sys.argv[1:]:
    wb = openpyxl.load_workbook(f, read_only=True); ws = wb['Tous les trades']; rows = ws.iter_rows(values_only=True); h = list(next(rows))
    col = lambda n: [i for i, k in enumerate(h) if k and n.lower() in str(k).lower()][0]
    cD, cN, cS, cM, cR = col('date'), col('n°'), col('stratégie'), col('mise'), col('résultat')
    T = []
    for r in rows:
        d = r[cD]
        if d is None: continue
        if isinstance(d, (int, float)): d = dt.datetime(1899, 12, 30) + dt.timedelta(days=d)
        T.append((d, r[cN], str(r[cS]), float(r[cM] or 0), float(r[cR] or 0)))
    T.sort(key=lambda x: x[0])
    noms = set(t[2] for t in T); nouveaux = noms - vus; vus |= noms
    cy = collections.defaultdict(float)
    for d, n, s, m, net in T:
        if s not in nouveaux: continue
        j = d.date().isoformat()
        if j not in APP and j not in TEST: continue
        c = (s, d.replace(second=0, microsecond=0, minute=d.minute - d.minute % 5))
        if m > 0:
            reste = 250 - cy[c]
            if reste <= 0.01: continue
            if m > reste: net *= reste / m; m = reste
        cy[c] += m
        z = Z.setdefault(s, {'num': n, 'src': f.split('/')[-1], 'r': collections.defaultdict(float), 'n': collections.defaultdict(int)})
        z['r'][(j, plage(d))] += net; z['n'][('app' if j in APP else 'test', plage(d))] += 1
print('stratégies', len(Z), '| apprentissage', APP[0], '->', APP[-1], '| verdict', TEST[0], '->', TEST[-1])
def serie(s, jours, pl=None):
    return [sum(v for (j, p), v in Z[s]['r'].items() if j == jj and (pl is None or p in pl)) for jj in jours]
def stats(jours_res):
    cum = pic = creux = 0
    for v in jours_res: cum += v; pic = max(pic, cum); creux = max(creux, pic - cum)
    random.seed(1); B = sorted(sum(random.choice(jours_res) for _ in jours_res) for _ in range(5000))
    return sum(jours_res), creux, sum(1 for v in jours_res if v > 0), (B[125], B[4875])
# A. meilleure stratégie unique (choisie sur l'apprentissage)
okA = [s for s in Z if sum(Z[s]['n'][('app', p)] for p, _, _ in PLAGES) >= MIN_TRADES * 2]
best = max(okA, key=lambda s: sum(serie(s, APP)))
print('\n=== A. MEILLEURE UNIQUE (choisie sur 19-28.10) :', Z[best]['num'], best, '| apprentissage', round(sum(serie(best, APP))))
g, c, pos, ic = stats(serie(best, TEST)); print(f'   VERDICT 29.10-03.11 : gain {g:.0f} $ | creux {c:.0f} $ | jours gagnants {pos}/6 | IC95 [{ic[0]:.0f} ; {ic[1]:.0f}] | par jour {[round(v) for v in serie(best, TEST)]}')
# B. une stratégie par plage (choisie sur l'apprentissage)
print('\n=== B. UNE STRATÉGIE PAR PLAGE (choisies sur 19-28.10) ===')
choix = {}
for p, _, _ in PLAGES:
    ok = [s for s in Z if Z[s]['n'][('app', p)] >= MIN_TRADES]
    R = sorted(ok, key=lambda s: -sum(serie(s, APP, [p])))
    choix[p] = R[0]
    print(f'-- {p} : top 5 sur l\'apprentissage -> leur résultat sur les jours inédits (même plage)')
    for s in R[:5]: print(f'   n° {Z[s]["num"]} | {s[:70]} | appr. {sum(serie(s, APP, [p])):.0f} $ | inédit {sum(serie(s, TEST, [p])):.0f} $ | trades inédits {Z[s]["n"][("test", p)]}')
tot = [sum(serie(choix[p], [j], [p])[0] for p, _, _ in PLAGES) for j in TEST]
g, c, pos, ic = stats(tot); print(f'   VERDICT changement par plage : gain {g:.0f} $ | creux {c:.0f} $ | jours gagnants {pos}/6 | IC95 [{ic[0]:.0f} ; {ic[1]:.0f}] | par jour {[round(v) for v in tot]}')
# C. contrôle : la meilleure par plage choisie APRÈS coup sur les jours inédits (impossible en vrai, sert à mesurer la perte due au choix)
print('\n=== C. CONTRÔLE (choix après coup, triche volontaire) : meilleure par plage sur les jours inédits ===')
for p, _, _ in PLAGES:
    ok = [s for s in Z if Z[s]['n'][('test', p)] >= MIN_TRADES // 2]
    s = max(ok, key=lambda s: sum(serie(s, TEST, [p]))); print(f'   {p} : n° {Z[s]["num"]} {s[:70]} | {sum(serie(s, TEST, [p])):.0f} $')
# D. stabilité : rang sur l'apprentissage vs inédit par plage (top 20 de l'apprentissage, combien restent dans le top 20 inédit)
print('\n=== D. STABILITÉ DU CLASSEMENT PAR PLAGE ===')
for p, _, _ in PLAGES:
    ok = [s for s in Z if Z[s]['n'][('app', p)] >= MIN_TRADES and Z[s]['n'][('test', p)] >= MIN_TRADES // 2]
    a = set(sorted(ok, key=lambda s: -sum(serie(s, APP, [p])))[:20]); b = set(sorted(ok, key=lambda s: -sum(serie(s, TEST, [p])))[:20])
    print(f'   {p} : {len(a & b)}/20 du top 20 restent top 20 sur les jours inédits ({len(ok)} stratégies comparées)')
