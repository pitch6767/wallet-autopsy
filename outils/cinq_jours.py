# 04.11.2026 (Pitch) : stratégies de l'onglet 5 avec plus de 3000 $ sur 5 jours (31.10 → 04.11, aujourd'hui inclus) et mise max par cycle ≤ 250 $
import openpyxl, datetime as dt, collections, sys
wb = openpyxl.load_workbook(sys.argv[1], read_only=True); ws = wb['Tous les trades']
rows = ws.iter_rows(values_only=True); h = list(next(rows)); print('colonnes', h)
ix = {k: i for i, k in enumerate(h)}
def col(*noms):
    for n in noms:
        for k, i in ix.items():
            if k and n.lower() in str(k).lower(): return i
    raise SystemExit('colonne absente ' + str(noms))
cD, cN, cS, cM, cR = col('date'), col('n°'), col('stratégie'), col('mise'), col('résultat')
J = ['2026-10-31', '2026-11-01', '2026-11-02', '2026-11-03', '2026-11-04']
par = collections.defaultdict(lambda: {'j': collections.defaultdict(float), 'cy': collections.defaultdict(float), 'n': 0})
for r in rows:
    d = r[cD]
    if d is None: continue
    if isinstance(d, (int, float)): d = dt.datetime(1899, 12, 30) + dt.timedelta(days=d)
    j = d.strftime('%Y-%m-%d')
    if j not in J: continue
    k = (r[cN], r[cS]); z = par[k]; z['j'][j] += float(r[cR] or 0); z['n'] += 1
    cy = d.replace(second=0, microsecond=0, minute=d.minute - d.minute % 5); z['cy'][cy] += float(r[cM] or 0)
L = []
for (n, s), z in par.items():
    tot = sum(z['j'].values()); mm = max(z['cy'].values()) if z['cy'] else 0
    L.append((tot, n, s, mm, z['n'], [round(z['j'].get(j, 0)) for j in J]))
L.sort(reverse=True)
print('jours', J)
print('=== RETENUES : total > 3000 $ et mise max par cycle <= 250 $ ===')
for tot, n, s, mm, nt, pj in L:
    if tot > 3000 and mm <= 250.5: print(f'n° {n} | {s} | total {tot:.0f} $ | mise max/cycle {mm:.0f} $ | trades {nt} | par jour {pj}')
print('=== total > 3000 $ mais mise max par cycle > 250 $ ===')
for tot, n, s, mm, nt, pj in L:
    if tot > 3000 and mm > 250.5: print(f'n° {n} | {s} | total {tot:.0f} $ | mise max/cycle {mm:.0f} $ | par jour {pj}')
