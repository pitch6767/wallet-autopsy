"""Audit du modele corrige (0,015 %) — demande ChatGPT du 09.10.2026 au soir. BTC, carnets enregistres (bot95/donnees + bot).
1. Les 2 trades « contradiction extreme » du 09.10 (16:24:21 Up a 0,052 avec 61,7 % ; 16:29:02 Down a 0,18 avec 73,8 %) : tout l'etat du modele.
2. Hypothese : dans les 60 dernieres secondes, le modele suppose un reglement sur la MOYENNE des 60 s (TWAP) alors que Polymarket regle sur le
   prix de FIN -> incertitude trop petite -> fausses certitudes. Variante « regle de fin » : E = prix actuel, variance = sigma^2 x temps restant.
3. Rejeu complet V2-F pour : ancien (enregistre), corrige 0,015 % (TWAP, = fantome en direct), corrige 0,015 % regle de fin.
   Par ecart annonce (20-30 / 30-40 / 40-50 / 50+), par temps restant, prix x temps ; resultat rempli au carnet (quantite affichee).
4. Cycles evites par le corrige : gagnants, prix, gains, le corrige a-t-il approche le seuil ?
5. Cout de maturation : sur les cycles communs, prix du corrige - prix de l'ancien, et resultat par tranche.
"""
import os, sys, json, gzip, glob, math, time, statistics as stt, collections, bisect, calendar
import numpy as np
sys.path.insert(0, "etude/bot5min")
from sauvetage import FEE, get, U
OUT = "etude/bot5min/"
phi = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
f0 = lambda x: (f"+{x:,.0f} $" if x >= 0 else f"−{-x:,.0f} $").replace(",", "'")
hs = lambda t: time.strftime("%d.%m %H:%M:%S", time.gmtime(t + 7200))


def charger():
    L = {}
    for f in sorted(glob.glob("bot95/donnees/*/rec_BTC.json.gz")):
        for k, doc in json.load(gzip.open(f, "rt")).items():
            for r in doc["lignes"]: L[r[0]] = r
    if not os.environ.get("LOCAL"):
        try:
            apres = None
            while True:
                d = get(f"{U}/api/rec?a=BTC&n=60" + (f"&apres={apres}" if apres else ""))
                for doc in d["docs"]:
                    for r in doc["lignes"]: L[r[0]] = r
                if not d["cles"] or len(d["cles"]) < 60: break
                apres = d["suivant"]
        except Exception as e: print("api", e)
    return sorted(L.values(), key=lambda r: r[0])


def main():
    rows = charger()
    C = collections.defaultdict(list); CT = collections.defaultdict(list)
    for r in rows:
        CT[r[1]].append(r)
        if None in (r[2], r[3], r[4], r[5], r[6]): continue
        C[r[1]].append(r)
    P1, CL1 = {}, {}
    for r in rows:
        s = int(r[0]); p = r[11] or r[12]
        if p: P1[s] = p
        if r[15]: CL1[s] = r[15]
    RES = {}
    try:
        for t in json.load(open(OUT + "v2f_tous.json")): RES[t["st"]] = t["gagne"] if t["cote"] == "Up" else (not t["gagne"])
    except Exception: pass
    def res(st, K):
        if st in RES: return RES[st]
        e = CL1.get(st + 300) or CL1.get(st + 299) or CL1.get(st + 301)
        return (e >= K) if (e and K) else None
    VC, BC = {}, {}
    def vol(s):
        if s not in VC:
            x = [P1[k] for k in range(s - 300, s + 1) if k in P1]
            VC[s] = (float(np.std(np.diff(np.log(x)))) or 1e-6) if len(x) >= 150 else None
        return VC[s]
    def base(s):
        if s not in BC:
            d = [P1[k] - CL1[k] for k in range(s - 120, s + 1) if k in P1 and k in CL1]
            BC[s] = float(np.median(d)) if d else None
        return BC[s]
    def etat(r, st):
        K = r[16]; p = r[11] or r[12]; s = int(r[0])
        if not K or not p: return None
        sg, b = vol(s), base(s)
        if sg is None or b is None: return None
        return dict(K=K, S=p - b, sg=sg, s=s, end=st + 300)
    def modele(r, st, sd, mode="twap", e=None):
        e = e or etat(r, st)
        if e is None: return None
        S, K, sg, s, end = e["S"], e["K"], e["sg"], e["s"], e["end"]; deb = end - 59
        if mode == "twap" and s >= deb:
            con = [CL1[k] for k in range(deb, s + 1) if k in CL1]; nr = max(1, end - s)
            E = (sum(con) + nr * S) / (len(con) + nr); v = (sg * S) ** 2 * nr ** 3 / 3 / 3600
        elif mode == "twap": E = S; v = (sg * S) ** 2 * ((deb - s) + 20)
        else: E = S; v = (sg * S) ** 2 * max(1, end - s)
        return phi((E - K) / math.sqrt(v + (sd * S) ** 2))
    def rejouer(nom, f):
        out = []
        for st in sorted(C):
            R = C[st]; MC = {}
            mo = lambda k, R=R, st=st, MC=MC: MC[k] if k in MC else MC.setdefault(k, f(R[k], st))
            K = next((x[16] for x in R if x[16]), None); g = res(st, K)
            if g is None: continue
            for i, r in enumerate(R):
                tl = st + 300 - r[0]
                if tl < 5: break
                j = i
                while j > 0 and r[0] - R[j][0] < 3: j -= 1
                if r[0] - R[j][0] < 2.5: continue
                pu, p3 = mo(i), mo(j)
                if pu is None or p3 is None: continue
                h3 = R[j]; pris = None
                for up in (True, False):
                    ask = r[4] if up else r[6]; a3 = h3[4] if up else h3[6]
                    fair = pu if up else 1 - pu; f3 = p3 if up else 1 - p3
                    if ask is None or a3 is None or not (0.03 <= ask <= 0.97): continue
                    if fair - ask >= 0.20 and (fair - ask) - (f3 - a3) >= 0.03: pris = (up, ask, fair); break
                if pris:
                    up, ask, fair = pris; gm = g if up else (not g); taille = (r[8] if up else r[10]) or 0
                    parts = min(50 / ask, taille) if taille else 50 / ask
                    e = etat(r, st); z = ((e["S"] - e["K"]) * (1 if up else -1)) / (e["sg"] * e["S"] * math.sqrt(max(tl, 1))) if e else 0
                    out.append(dict(t=r[0], st=st, up=up, prix=ask, fair=fair, edge=fair - ask, reste=tl, z=z, gagne=bool(gm),
                                    pnl=parts * ((1 if gm else 0) - ask - FEE(ask)), mise=parts * ask, old=(r[2] if up else 1 - r[2])))
                    break
        return out
    V = {"ancien 0,08 % (V2-F en direct)": lambda r, st: r[2],
         "corrigé 0,015 % (fantôme en direct, moyenne 60 s)": lambda r, st: modele(r, st, 1.5e-4, "twap"),
         "corrigé 0,015 % règle de FIN (prix final)": lambda r, st: modele(r, st, 1.5e-4, "fin"),
         "ancien 0,08 % règle de FIN": lambda r, st: modele(r, st, 8e-4, "fin")}
    X = {k: rejouer(k, f) for k, f in V.items()}
    T0 = min(t["t"] for L in X.values() for t in L); T1 = max(t["t"] for L in X.values() for t in L)
    rap = [f"# Audit du modèle corrigé — contradictions extrêmes, règle de fin, cycles évités, coût de la confirmation (BTC, {hs(T0)[:11]} → {hs(T1)[:11]})", "",
           "Rejeu complet de la règle V2-F sur les carnets enregistrés (4 mesures/s). Résultat « rempli au carnet » : 50 $ au meilleur vendeur, limité à la quantité affichée (prudent). Frais compris.", ""]
    # 1. les 2 trades
    rap += ["## 1. Les deux contradictions extrêmes du 09.10", ""]
    for lab, hh, up in (("17:24:21 (affiché 16:24:21 dans le rapport, décalé d'une heure) — désaccord 20 corrigé, Up à 0,052 $, modèle 61,7 %", "17:24:21", True), ("17:29:02 (affiché 16:29:02) — V2-F corrigé, Down à 0,180 $, modèle 73,8 %", "17:29:02", False)):
        tt = calendar.timegm(time.strptime("2026-10-09 " + hh, "%Y-%m-%d %H:%M:%S")) - 7200
        st = int(tt // 300 * 300); R = CT.get(st, [])
        rap += [f"### {lab}", ""]
        if not R: rap += ["(cycle absent des carnets enregistrés)", ""]; continue
        rap += ["| Heure | Reste | Prix à battre | Chainlink | BTC du modèle | Écart BTC − seuil | Volatilité 5 min ($/s) | Up vendeur | Down vendeur | Ancien (Up) | Corrigé moyenne 60 s (Up) | Corrigé règle de fin (Up) |",
                "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        vus = set()
        for r in R:
            sec = int(r[0])
            if abs(r[0] - tt) <= 20 and ((sec % 2 == 0 and sec not in vus) or abs(r[0] - tt) < 1.0):
                vus.add(sec)
                e = etat(r, st)
                if not e: continue
                rap.append(("**" if abs(r[0] - tt) < 1.0 else "") + f"| {hs(r[0])} | {st + 300 - r[0]:.0f} s | {e['K']:.2f} | {r[15] or 0:.2f} | {e['S']:.2f} | {e['S'] - e['K']:+.2f} | {e['sg'] * e['S']:.2f} | {r[4] if r[4] is not None else float('nan'):.3f} | {r[6] if r[6] is not None else float('nan'):.3f} | "
                           f"{r[2] if r[2] is not None else float('nan'):.3f} | {modele(r, st, 1.5e-4, 'twap', e):.3f} | {modele(r, st, 1.5e-4, 'fin', e):.3f} |")
        fin = CL1.get(st + 300) or CL1.get(st + 299)
        K = next((x[16] for x in R if x[16]), None)
        if fin and K: rap += ["", f"Fin du cycle : Chainlink {fin:.2f} contre prix à battre {K:.2f} → **{'Up' if fin >= K else 'Down'}**.", ""]
    # 2/3. tableaux
    def tab(titre, groupes):
        o = [f"### {titre}", "", "| Groupe | " + " | ".join(k.split(" (")[0] for k in X) + " |", "|---|" + "---|" * len(X)]
        for gn, f in groupes:
            cel = []
            for k, L in X.items():
                Y = [t for t in L if f(t)]
                cel.append(f"{len(Y)} tr · {100 * sum(t['gagne'] for t in Y) / len(Y):.0f} % · {f0(sum(t['pnl'] for t in Y))}" if Y else "—")
            o.append(f"| {gn} | " + " | ".join(cel) + " |")
        return o + [""]
    rap += ["## 2. Les versions du modèle (rejeu complet)", "", "| Version | Trades | Gagnés | % | Résultat rempli au carnet | Creux | Pertes de suite max |", "|---|---|---|---|---|---|---|"]
    for k, L in X.items():
        L.sort(key=lambda t: t["t"]); cum = pk = cr = 0.0; s = sm = 0
        for t in L: cum += t["pnl"]; pk = max(pk, cum); cr = min(cr, cum - pk); s = 0 if t["gagne"] else s + 1; sm = max(sm, s)
        rap.append(f"| {k} | {len(L)} | {sum(t['gagne'] for t in L)} | {100 * sum(t['gagne'] for t in L) / len(L):.0f} % | **{f0(sum(t['pnl'] for t in L))}** | {f0(cr)} | {sm} |")
    rap += ["", "Chaque case : trades · % gagnés · résultat.", ""]
    rap += tab("Par écart annoncé (modèle − prix)", [("20-30 pts", lambda t: t["edge"] < 0.30), ("30-40 pts", lambda t: 0.30 <= t["edge"] < 0.40), ("40-50 pts", lambda t: 0.40 <= t["edge"] < 0.50), ("50 pts et plus", lambda t: t["edge"] >= 0.50)])
    rap += tab("Par temps restant", [("moins de 60 s (dans la fenêtre de moyenne)", lambda t: t["reste"] < 60), ("60-120 s", lambda t: 60 <= t["reste"] < 120), ("120-200 s", lambda t: 120 <= t["reste"] < 200), ("200 s et plus", lambda t: t["reste"] >= 200)])
    rap += tab("Prix × temps (groupes larges)", [("prix < 0,20 et < 120 s", lambda t: t["prix"] < 0.20 and t["reste"] < 120), ("prix < 0,20 et ≥ 120 s", lambda t: t["prix"] < 0.20 and t["reste"] >= 120),
                                                  ("prix ≥ 0,20 et < 120 s", lambda t: t["prix"] >= 0.20 and t["reste"] < 120), ("prix ≥ 0,20 et ≥ 120 s", lambda t: t["prix"] >= 0.20 and t["reste"] >= 120)])
    rap += tab("Contradiction extrême : écart ≥ 40 pts, modèle ≥ 60 %, prix < 0,25", [("oui", lambda t: t["edge"] >= 0.40 and t["fair"] >= 0.60 and t["prix"] < 0.25), ("non", lambda t: not (t["edge"] >= 0.40 and t["fair"] >= 0.60 and t["prix"] < 0.25))])
    # 4. cycles evites
    A = {t["st"]: t for t in X["ancien 0,08 % (V2-F en direct)"]}; Cc = {t["st"]: t for t in X["corrigé 0,015 % (fantôme en direct, moyenne 60 s)"]}
    ev = [A[k] for k in A if k not in Cc]
    rap += ["## 3. Les cycles évités par le corrigé (que l'ancien achetait)", "",
            f"- {len(ev)} cycles, {sum(t['gagne'] for t in ev)} gagnants ({100 * sum(t['gagne'] for t in ev) / max(1, len(ev)):.0f} %), résultat de l'ancien sur ces cycles **{f0(sum(t['pnl'] for t in ev))}**.",
            f"- Prix moyen payé par l'ancien : {stt.mean(t['prix'] for t in ev):.2f} ; probabilité de l'ancien modèle : {stt.mean(t['fair'] for t in ev):.2f}.",
            f"- Les gagnants évités : {f0(sum(t['pnl'] for t in ev if t['gagne']))} au total ; les perdants évités : {f0(sum(t['pnl'] for t in ev if not t['gagne']))}.", ""]
    G = sorted([t for t in ev if t["gagne"]], key=lambda t: -t["pnl"])[:10]
    if G:
        rap += ["Les 10 plus gros gagnants évités :", "", "| Heure | Prix | Ancien modèle | Reste | Distance (écarts-types) | Gain (rempli au carnet) |", "|---|---|---|---|---|---|"]
        rap += [f"| {hs(t['t'])} | {t['prix']:.3f} | {t['fair']:.2f} | {t['reste']:.0f} s | {t['z']:+.2f} | {f0(t['pnl'])} |" for t in G]
        rap.append("")
    # 5. cout de maturation
    com = [k for k in A if k in Cc and A[k]["up"] == Cc[k]["up"]]
    rap += ["## 4. Coût de la confirmation (cycles achetés par les deux, même côté)", "",
            f"{len(com)} cycles. Prix corrigé − prix ancien : médiane {100 * stt.median(Cc[k]['prix'] - A[k]['prix'] for k in com):+.1f} c ; achat {stt.median(Cc[k]['t'] - A[k]['t'] for k in com):.0f} s plus tard (médiane).", "",
            "| Surcoût de la confirmation | Cycles | Gagnés | Résultat corrigé | Résultat ancien (mêmes cycles) |", "|---|---|---|---|---|"]
    for lab, a, b in (("prix égal ou plus bas", -9, 0.005), ("+1 à +5 c", 0.005, 0.05), ("+5 à +10 c", 0.05, 0.10), ("plus de +10 c", 0.10, 9)):
        Y = [k for k in com if a <= Cc[k]["prix"] - A[k]["prix"] < b]
        if Y: rap.append(f"| {lab} | {len(Y)} | {sum(Cc[k]['gagne'] for k in Y)} | {f0(sum(Cc[k]['pnl'] for k in Y))} | {f0(sum(A[k]['pnl'] for k in Y))} |")
    open(OUT + "resultat_audit_corrige.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
