# 04.11.2026 (Pitch) : stratégies de l'onglet 5, 5 jours (31.10 -> 04.11, aujourd'hui inclus), mise plafonnée à 250 $ par cycle
# (comme l'onglet 5 et le bot : trade réduit au reste disponible, sinon ignoré). Résultat total plafonné > 3000 $.
import openpyxl, datetime as dt, collections, sys
wb = openpyxl.load_workbook(sys.argv[1], read_only=True); ws = wb['Tous les trades']
rows = ws.iter_rows(values_only=True); h = list(next(rows))
def col(n): return [i for i, k in enumerate(h) if k and n.lower() in str(k).lower()][0]
cD, cN, cS, cM, cR = col('date'), col('n°'), col('stratégie'), col('mise'), col('résultat')
J = ['2026-10-31', '2026-11-01', '2026-11-02', '2026-11-03', '2026-11-04']
T = []
for r in rows:
    d = r[cD]
    if d is None: continue
    if isinstance(d, (int, float)): d = dt.datetime(1899, 12, 30) + dt.timedelta(days=d)
    if d.strftime('%Y-%m-%d') in J: T.append((d, r[cN], r[cS], float(r[cM] or 0), float(r[cR] or 0)))
T.sort(key=lambda x: x[0])
par = collections.defaultdict(lambda: {'j': collections.defaultdict(float), 'cy': collections.defaultdict(float), 'brut': 0.0, 'n': 0, 'red': 0, 'ign': 0, 'mmBrut': collections.defaultdict(float)})
for d, n, s, m, net in T:
    z = par[(n, s)]; cy = d.replace(second=0, microsecond=0, minute=d.minute - d.minute % 5)
    z['brut'] += net; z['mmBrut'][cy] += m
    reste = 250 - z['cy'][cy]
    if reste <= 0.01: z['ign'] += 1; continue
    if m > reste: net *= reste / m; m = reste; z['red'] += 1
    z['cy'][cy] += m; z['j'][d.strftime('%Y-%m-%d')] += net; z['n'] += 1
L = sorted(((sum(z['j'].values()), n, s, z) for (n, s), z in par.items()), key=lambda x: -x[0])
print('JOURS', J, '- PLAFOND 250 DOLLARS PAR CYCLE APPLIQUE')
for tot, n, s, z in L:
    if tot > 3000:
        print(f"n° {n} | {s} | total plafonné {tot:.0f} $ | sans plafond {z['brut']:.0f} $ | trades {z['n']} (réduits {z['red']}, ignorés {z['ign']}) | mise max/cycle sans plafond {max(z['mmBrut'].values()):.0f} $ | par jour {[round(z['j'].get(j, 0)) for j in J]}")
print('FIN -', sum(1 for x in L if x[0] > 3000), 'stratégies au-dessus de 3000 dollars sur', len(L))
