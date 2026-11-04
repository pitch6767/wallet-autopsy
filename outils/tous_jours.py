# 04.11.2026 15:07 (Pitch) : stratégies gagnantes CHAQUE jour depuis le 19.10 avec plus de 2000 $ de gain.
# Plafond 250 $ par cycle appliqué (trade réduit au reste, sinon ignoré). Aujourd'hui (journée en cours) affiché à part.
import openpyxl, datetime as dt, collections, sys
J = [(dt.date(2026, 10, 19) + dt.timedelta(days=i)).isoformat() for i in range(17)]   # 19.10 -> 04.11
AUJ = J[-1]
par = collections.defaultdict(lambda: {'j': collections.defaultdict(float), 'cy': collections.defaultdict(float), 'n': 0, 'src': set()})
for f in sys.argv[1:]:
    wb = openpyxl.load_workbook(f, read_only=True)
    if 'Tous les trades' not in wb.sheetnames: print('pas de feuille Tous les trades dans', f, wb.sheetnames[:5]); continue
    ws = wb['Tous les trades']; rows = ws.iter_rows(values_only=True); h = list(next(rows))
    def col(n):
        x = [i for i, k in enumerate(h) if k and n.lower() in str(k).lower()]; return x[0] if x else None
    cD, cN, cS, cM, cR = col('date'), col('n°'), col('stratégie'), col('mise'), col('résultat')
    T = []
    for r in rows:
        d = r[cD]
        if d is None: continue
        if isinstance(d, (int, float)): d = dt.datetime(1899, 12, 30) + dt.timedelta(days=d)
        T.append((d, r[cN] if cN is not None else '', r[cS], float(r[cM] or 0) if cM is not None else 0.0, float(r[cR] or 0)))
    T.sort(key=lambda x: x[0]); print(f, 'trades', len(T), 'du', T[0][0] if T else '-', 'au', T[-1][0] if T else '-')
    for d, n, s, m, net in T:
        j = d.date().isoformat()
        if j not in J: continue
        k = (f.split('/')[-1], n, s); z = par[k]
        cy = d.replace(second=0, microsecond=0, minute=d.minute - d.minute % 5)
        reste = 250 - z['cy'][cy]
        if m > 0:
            if reste <= 0.01: continue
            if m > reste: net *= reste / m; m = reste
        z['cy'][cy] += m; z['j'][j] += net; z['n'] += 1
R = []
for (f, n, s), z in par.items():
    jours = J[:-1]
    tot = sum(z['j'].values())
    neg = [j for j in jours if z['j'].get(j, 0) <= 0]
    R.append((len(neg), -tot, f, n, s, tot, neg, z))
R.sort()
print('=== GAGNANTES CHAQUE JOUR du 19.10 au 03.11 (16 jours complets) ET total > 2000 $ (plafond 250 $ par cycle) ===')
k = 0
for nneg, _, f, n, s, tot, neg, z in R:
    if nneg == 0 and tot > 2000:
        k += 1; print(f"{f} | n° {n} | {s} | total {tot:.0f} $ | aujourd'hui {z['j'].get(AUJ, 0):.0f} $ | pire jour {min(z['j'].get(j, 0) for j in J[:-1]):.0f} $ | trades {z['n']}")
print('nombre :', k)
print('=== LES PLUS PROCHES : 1 ou 2 jours perdants, total > 2000 $ ===')
for nneg, _, f, n, s, tot, neg, z in R:
    if 1 <= nneg <= 2 and tot > 2000:
        print(f"{f} | n° {n} | {s} | total {tot:.0f} $ | jours perdants ou nuls {neg} : {[round(z['j'].get(j, 0)) for j in neg]} | trades {z['n']}")
