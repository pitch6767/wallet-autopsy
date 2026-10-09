"""Execution des trades du modele corrige (marge 0,015 %, comme le fantome « corrige : V2-F »), BTC, 09.10.2026.
Les carnets enregistres ne gardent que le MEILLEUR vendeur (prix + quantite affichee), 4 fois par seconde : pas de profondeur.
1. Chronologie : premier signal de l'ancien modele (0,08 %, enregistre) -> validation du corrige : delai, prix, pre-alertes jamais validees.
2. Politiques d'execution sur les MEMES opportunites (resultat par opportunite, gagnants manques compris), sans regarder l'avenir pour decider :
   A immediat (quantite affichee) ; A+ immediat puis completer jusqu'a 50 $ pendant N s tant que le vendeur est <= prix d'entree ;
   W attendre 1 / 3 / 5 s puis acheter si le signal corrige tient encore ; D limite passive (prix d'entree - 1 / 2 c) pendant 20 s ;
   C hybride 15 $ immediat + limite passive -2 c pour le reste pendant 20 s.
   Remplissage passif : seulement si le meilleur vendeur descend a notre prix ou plus bas (prudent). On ne reprend jamais deux fois la meme quantite.
"""
import sys, json, time, statistics as stt, collections
sys.path.insert(0, "etude/bot5min")
from sauvetage import FEE
from edge_truth import f0, hs
from sensibilite import preparer
OUT = "etude/bot5min/"
SD = 1.5e-4


def signal(R, i, pu_i, pu_j, j):
    r, h3 = R[i], R[j]
    for up in (True, False):
        ask = r[4] if up else r[6]; a3 = h3[4] if up else h3[6]
        fair = pu_i if up else 1 - pu_i; f3 = pu_j if up else 1 - pu_j
        if ask is None or a3 is None or not (0.03 <= ask <= 0.97): continue
        if fair - ask >= 0.20 and (fair - ask) - (f3 - a3) >= 0.03: return up
    return None


def main():
    T0 = json.load(open(OUT + "v2f_tous.json"))
    _, C, RES, modele, CL1 = preparer(T0)
    O = []
    for st in sorted(C):
        g = RES.get(st)
        if g is None:
            a, b = CL1.get(st), CL1.get(st + 300) or CL1.get(st + 299)
            g = (b >= a) if a and b else None
        if g is None: continue
        R = C[st]; MC = {}
        mc = lambda k, R=R, MC=MC, st=st: MC[k] if k in MC else MC.setdefault(k, modele(R[k], st, SD))
        prem_old = None; val = None
        for i, r in enumerate(R):
            if st + 300 - r[0] < 5: break
            j = i
            while j > 0 and r[0] - R[j][0] < 3: j -= 1
            if r[0] - R[j][0] < 2.5: continue
            if prem_old is None:
                up = signal(R, i, r[2], R[j][2], j)
                if up is not None: prem_old = (i, up)
            a, b = mc(i), mc(j)
            if a is None or b is None: continue
            up = signal(R, i, a, b, j)
            if up is not None: val = (i, up); break
        if val is None:
            if prem_old: O.append({"st": st, "valide": False, "old_t": R[prem_old[0]][0]})
            continue
        i, up = val; r = R[i]; gm = g if up else (not g)
        ask = r[4] if up else r[6]
        o = {"st": st, "valide": True, "t": r[0], "i": i, "up": up, "gagne": bool(gm), "prix": ask, "reste": round(st + 300 - r[0]), "R": R, "mc": mc}
        if prem_old:
            io, uo = prem_old; xo = R[io]
            o.update(old_t=xo[0], old_prix=(xo[4] if uo else xo[6]) if uo == up else None, old_meme_cote=(uo == up))
        O.append(o)
    V = [o for o in O if o["valide"]]
    PA = [o for o in O if not o["valide"]]
    rap = [f"# Exécution du modèle corrigé (marge 0,015 %, le fantôme « corrigé » en direct) — BTC, vrais carnets ({hs(V[0]['t'])} → {hs(V[-1]['t'])})", "",
           "**Limite des données :** le bot enregistre seulement le meilleur vendeur (prix et quantité affichée) 4 fois par seconde, pas les niveaux suivants du carnet. "
           "La « liquidité multi-niveaux » ne peut donc pas être mesurée sur le passé ; seulement le meilleur prix dans le temps.", ""]
    # 1. chronologie
    av = [o for o in V if o.get("old_t") is not None and o.get("old_meme_cote")]
    d = [o["t"] - o["old_t"] for o in av]; dp = [o["prix"] - o["old_prix"] for o in av if o.get("old_prix")]
    rap += ["## 1. Pré-alerte (ancien modèle) → validation (corrigé)", "",
            f"- Opportunités validées par le corrigé : **{len(V)}** ({sum(o['gagne'] for o in V)} gagnées).",
            f"- Pré-alertes de l'ancien modèle jamais validées par le corrigé dans le cycle : **{len(PA)}** cycles (ce sont les faux désaccords évités).",
            f"- Validées après une pré-alerte du même côté : {len(av)} ; délai médian **{stt.median(d):.1f} s** (moyen {stt.mean(d):.1f} s, 0 s dans {sum(1 for x in d if x < 0.3)} cas).",
            f"- Prix à la validation − prix à la pré-alerte : médiane **{100 * stt.median(dp):+.1f} c**, moyenne {100 * stt.mean(dp):+.1f} c ; plus cher dans {sum(1 for x in dp if x > 0.005)} cas, moins cher dans {sum(1 for x in dp if x < -0.005)}.", ""]
    pre = [o for o in av if o["t"] - o["old_t"] >= 1]
    if pre:
        def pn(o, p): return (50 / p) * ((1 if o["gagne"] else 0) - p - FEE(p))
        rap += [f"Sur les {len(pre)} validations arrivées au moins 1 s après la pré-alerte : acheter au prix de la pré-alerte aurait fait {f0(sum(pn(o, o['old_prix']) for o in pre))} "
                f"contre {f0(sum(pn(o, o['prix']) for o in pre))} au prix de validation (50 $ remplis, pour mesurer le coût du délai seul).", ""]
    # 2. politiques
    def remplir(o, t0, t1, limite, budget, deja=None, passif=False):
        """achete au meilleur vendeur entre t0 et t1 si prix <= limite, sans reprendre deux fois la meme quantite"""
        R, up = o["R"], o["up"]; pris = deja if deja is not None else collections.defaultdict(float)
        parts = cout = 0.0
        for x in R:
            if x[0] < t0: continue
            if x[0] > t1 or budget - cout < 0.5: break
            a = x[4] if up else x[6]; sz = (x[8] if up else x[10]) or 0
            if a is None or a > limite + 1e-9: continue
            dispo = max(0.0, sz - pris[a])
            k = min(dispo, (budget - cout) / a)
            if k <= 0: continue
            pris[a] += k; parts += k; cout += k * a
        return parts, cout, pris
    def res(o, parts, cout):
        if parts <= 0: return 0.0, 0.0
        p = cout / parts
        return parts * ((1 if o["gagne"] else 0) - p - FEE(p)), cout
    def tient(o, dt):
        """le signal corrige existe-t-il encore dt secondes apres (decision prise a ce moment-la, sans voir la suite)"""
        R = o["R"]; t = o["t"] + dt
        for k in range(o["i"], len(R)):
            if R[k][0] >= t:
                j = k
                while j > 0 and R[k][0] - R[j][0] < 3: j -= 1
                a, b = o["mc"](k), o["mc"](j)
                if a is None or b is None: return None
                return k if signal(R, k, a, b, j) == o["up"] else None
        return None
    POL = {}
    POL["A immédiat (quantité affichée)"] = lambda o: res(o, *remplir(o, o["t"], o["t"], o["prix"], 50)[:2])
    for N in (5, 15, 30):
        def f(o, N=N):
            p, c, pr = remplir(o, o["t"], o["t"], o["prix"], 50)
            p2, c2, _ = remplir(o, o["t"] + 0.01, o["t"] + N, o["prix"], 50 - c, pr)
            return res(o, p + p2, c + c2)
        POL[f"A+ immédiat puis compléter à ≤ prix d'entrée pendant {N} s"] = f
    for w in (1, 3, 5):
        def f(o, w=w):
            k = tient(o, w)
            if k is None: return 0.0, 0.0
            x = o["R"][k]; a = x[4] if o["up"] else x[6]
            return res(o, *remplir(o, x[0], x[0], a, 50)[:2])
        POL[f"W attendre {w} s, acheter si le signal tient encore"] = f
    for c_ in (1, 2):
        def f(o, c_=c_):
            return res(o, *remplir(o, o["t"] + 0.01, o["t"] + 20, o["prix"] - c_ / 100, 50)[:2])
        POL[f"D limite passive −{c_} c pendant 20 s (rien d'immédiat)"] = f
    def hyb(o):
        p, c, pr = remplir(o, o["t"], o["t"], o["prix"], 15)
        p2, c2, _ = remplir(o, o["t"] + 0.01, o["t"] + 20, o["prix"] - 0.02, 50 - c, pr)
        return res(o, p + p2, c + c2)
    POL["C hybride : 15 $ immédiat + limite −2 c pour le reste (20 s)"] = hyb
    jack = {o["st"] for o in V if o["gagne"] and o["prix"] <= 0.25}
    VV = sorted(V, key=lambda o: o["t"]); mid = VV[len(VV) // 2]["t"]
    rap += ["## 2. Politiques d'exécution sur les mêmes " + str(len(V)) + " opportunités", "",
            f"Résultat par opportunité (une opportunité non remplie compte 0 $). Gagnants à prix ≤ 0,25 $ (petits prix qui paient gros) : {len(jack)}.", "",
            "| Politique | Remplies | Mise moyenne | Prix moyen payé | Gagnantes remplies | Petits-prix gagnants remplis | Résultat | Par $ engagé | Creux | 1re moitié | 2e moitié |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    for nom, f in POL.items():
        L = [(o, *f(o)) for o in VV]
        F = [(o, p, c) for o, p, c in L if c > 0]
        cum = pk = cr = 0.0
        for _, p, _ in L: cum += p; pk = max(pk, cum); cr = min(cr, cum - pk)
        tot = sum(p for _, p, _ in L); eng = sum(c for _, _, c in L)
        rap.append(
                   f"| {nom} | {len(F)} / {len(V)} | {stt.mean(c for _, _, c in F):.0f} $ | {stt.mean(o['prix'] for o, _, _ in F):.2f} | {sum(o['gagne'] for o, _, _ in F)} / {sum(o['gagne'] for o in V)} | "
                   f"{sum(1 for o, _, _ in F if o['st'] in jack)} / {len(jack)} | **{f0(tot)}** | {100 * tot / max(1, eng):+.0f} % | {f0(cr)} | "
                   f"{f0(sum(p for o, p, _ in L if o['t'] < mid))} | {f0(sum(p for o, p, _ in L if o['t'] >= mid))} |")
    rap += ["", "« Prix moyen payé » = meilleur vendeur au moment de la validation pour les opportunités remplies (repère)."]
    open(OUT + "resultat_execution.md", "w").write("\n".join(rap))
    print("\n".join(rap))


if __name__ == "__main__":
    main()
