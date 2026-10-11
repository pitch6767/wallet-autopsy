"""Reconstruction hors ligne du modèle de Dublin (proba() de bot95/rapide/rapide.js) à partir des fichiers de cycle (champ « ex »).
Sert à H775 (décision anticipée) et H771–H773 (offres prépositionnées). Aucune donnée postérieure à l'instant t n'est utilisée pour p(t).
Validation : comparaison avec la probabilité enregistrée au moment de chaque signal (« modele »)."""
import gzip, json, math, bisect
import numpy as np

SRC = ("perp", "okx", "bn", "cb", "cl")


def phi(x):
    t = 1 / (1 + 0.2316419 * abs(x)); d = 0.3989422804014327 * math.exp(-x * x / 2)
    p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))))
    return 1 - p if x > 0 else p


def charger_ex(fichiers):
    """fusionne les « ex » de plusieurs cycles consécutifs → par source : listes triées (tRecu_s, prix)"""
    S = {k: [] for k in SRC}
    for fn in fichiers:
        try: R = json.load(gzip.open(fn))
        except Exception: continue
        for row in R.get("ex", []):
            for k, v in zip(SRC, row[1:]):
                if v and v[0]: S[k].append((float(v[2]), float(v[0])))
    out = {}
    for k, L in S.items():
        L = sorted(set(L)); out[k] = (np.array([x[0] for x in L]), np.array([x[1] for x in L]))
    return out


class Modele:
    def __init__(self, ex, strike, end):
        self.ex = ex; self.strike = strike; self.end = end
        self.sec = {}                                            # seconde de réception → dernier prix par source
        for k, (T, P) in ex.items():
            for t, p in zip(T, P): self.sec.setdefault(int(math.floor(t)), {})[k] = p

    def dernier(self, k, t):
        T, P = self.ex[k]; i = bisect.bisect_right(T, t) - 1
        return (T[i], P[i]) if i >= 0 else None

    def prixA(self, k, s):
        for i in range(6):
            o = self.sec.get(s - i)
            if o and k in o: return o[k]
        return None

    def serie(self, k, n, t):
        ts = int(math.floor(t)); out = []; last = None
        for s in range(ts - n, ts + 1):
            o = self.sec.get(s)
            if o and k in o: last = o[k]
            if last is not None: out.append((s, last))
        return out

    def _lent(self, ts):
        """volatilité et bases (recalculées au plus une fois par seconde, comme sgc / okxB du bot)"""
        if not hasattr(self, "_c"): self._c = {}
        if ts in self._c: return self._c[ts]
        t = ts + 0.999
        ser = self.serie("perp", 300, t)
        if len(ser) < 60: self._c[ts] = None; return None
        r = [math.log(ser[i][1] / ser[i - 1][1]) for i in range(1, len(ser))]
        mo = sum(r) / len(r); sg = math.sqrt(sum((x - mo) ** 2 for x in r) / len(r)) or 1e-6
        def med(L): L = sorted(L); return L[len(L) // 2] if L else None
        base = med([p - c for s2, p in self.serie("perp", 120, t) for c in [self.prixA("cl", s2)] if c])
        okb = med([p - c for s2, p in self.serie("okx", 120, t) for c in [self.prixA("cl", s2)] if c])
        self._c[ts] = (sg, base, okb); return self._c[ts]

    def proba(self, t, sdRels=(8e-4, 1e-4, 1.5e-4), rapide=None):
        """p(Up) au temps t (s), avec uniquement les données reçues à t. rapide = source (« bn », « cb ») dont le mouvement depuis la
        dernière observation Bybit/OKX utilisée est ajouté au prix (H775 : décision avec un flux plus rapide)."""
        if self.strike is None or self.dernier("cl", t) is None: return None
        L = self._lent(int(math.floor(t)) - 1)
        if L is None: return None
        sg, base, okb = L
        c = []
        fp = self.dernier("perp", t); fo = self.dernier("okx", t)
        if fp and base is not None: c.append((fp[0], fp[1] - base))
        if fo and okb is not None: c.append((fo[0], fo[1] - okb))
        if not c: return None
        c.sort(key=lambda x: -x[0]); tS, S = c[0]
        if rapide:
            a = self.dernier(rapide, t); b = self.dernier(rapide, tS)
            if a and b: S = S + (a[1] - b[1])
        ts = int(math.floor(t)); deb = self.end - 60
        if ts >= deb:
            connus = [x for s2 in range(deb, min(ts, self.end - 1) + 1) for x in [self.prixA("cl", s2)] if x]
            nr = max(1, self.end - 1 - ts); E = (sum(connus) + nr * S) / (len(connus) + nr); v = (sg * S) ** 2 * nr ** 3 / 3 / 3600
        else:
            E = S; v = (sg * S) ** 2 * ((deb - ts) + 20)
        return tuple(phi((E - self.strike) / math.sqrt(v + (sd * S) ** 2)) for sd in sdRels)
