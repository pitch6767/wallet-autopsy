"""07.11.2026 (Pitch : « ces wallets clusters achètent toujours les premiers, donc pourquoi chercher 60 000 transactions » → « oui »).
Étude en DIRECT sur des memecoins pump.fun NÉS depuis moins de 2 h (données publiques Solana + GeckoTerminal, aucune clé, aucun ordre) :
  1. on prend les coins tout jeunes : leur histoire est courte, on arrive au début en une ou deux pages ;
  2. sur leurs 1200 premières transactions : groupes de portefeuilles à la Bubblemaps (transfert de jetons entre eux, ou même financeur en SOL) ;
  3. ENTRÉE : premier instant où un groupe d'au moins 3 portefeuilles détient au moins X % des jetons → prix du premier achat suivant (+1 % de frais) ;
  4. ensuite on ne suit QUE les portefeuilles du groupe (peu de transactions chacun) : RAPATRIEMENT = au moins 2 portefeuilles du groupe
     envoient leurs jetons au même portefeuille → prix des vrais échanges du coin 2 s, 5 s et 30 s plus tard (−1 % de frais), et délai
     jusqu'à la première vente du groupe.
Résultat pour 20 $ par coin. Sauvegarde poussée sur GitHub après chaque événement et toutes les 15 minutes.
07.11 : transactions Solana « version 1 » acceptées (refusées avant → chaque appel échouait et réessayait : étude bloquée) ; nœud drpc retiré (400).
07.11 (2e) : 1 h sans aucun coin enregistré → journal poussé toutes les 5 min et étapes affichées, pour voir où ça bloque.
07.11 (3e) : VRAIE cause : le workflow ne donne l'identité git qu'à la fin → aucune sauvegarde intermédiaire ne passait. Corrigé ici.
07.11 (4e) : lire 1200 transactions prenait plus de 13 min par coin (limites des serveurs publics) → 300 premières transactions (les groupes achètent en premier) et 20 plus gros portefeuilles.
07.11 (5e) : nœuds centraux retirés (plus de 15 liens ou plus de 30 % des jetons) — ils fabriquaient des faux groupes.
"""
import json, time, urllib.request, collections, datetime as dt, random, threading, os, subprocess
from concurrent.futures import ThreadPoolExecutor

RPCS = ["https://api.mainnet-beta.solana.com", "https://solana-rpc.publicnode.com"]
GT = "https://api.geckoterminal.com/api/v2"
NB_COINS = 30; NB_TX = 300; SEUILS = [5, 10, 20]
verrou = threading.Lock(); appels = collections.Counter()

def http(url, corps=None, essais=6):
    for i in range(essais):
        try:
            req = urllib.request.Request(url, data=json.dumps(corps).encode() if corps else None, headers={"content-type": "application/json", "user-agent": "etude-clusters"})
            with urllib.request.urlopen(req, timeout=15) as r: return json.load(r)
        except Exception as e:
            if i == essais - 1: return None
            time.sleep(1.5 * (i + 1) + random.random())

def rpc(methode, params):
    for k in range(len(RPCS) * 2):
        url = RPCS[(appels[methode] + k) % len(RPCS)]
        with verrou: appels[methode] += 1
        r = http(url, {"jsonrpc": "2.0", "id": 1, "method": methode, "params": params}, essais=2)
        if r and "result" in r: return r["result"]
        time.sleep(0.5)
    return None


def tx(sig):
    return rpc("getTransaction", [sig, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 1, "commitment": "confirmed"}])

def analyser(t, mint):
    """→ liste de mouvements : (portefeuille, Δjetons, ΔSOL) et transferts de jetons (source → destination)"""
    if not t or not t.get("meta"): return None
    m = t["meta"]; cles = [k["pubkey"] if isinstance(k, dict) else k for k in t["transaction"]["message"]["accountKeys"]]
    pre = {(b["owner"]): float(b["uiTokenAmount"]["uiAmount"] or 0) for b in m.get("preTokenBalances") or [] if b.get("mint") == mint and b.get("owner")}
    post = {(b["owner"]): float(b["uiTokenAmount"]["uiAmount"] or 0) for b in m.get("postTokenBalances") or [] if b.get("mint") == mint and b.get("owner")}
    d_tok = {o: post.get(o, 0) - pre.get(o, 0) for o in set(pre) | set(post)}
    d_sol = {cles[i]: (m["postBalances"][i] - m["preBalances"][i]) / 1e9 for i in range(len(cles))}
    signataire = cles[0]
    return dict(t=t.get("blockTime") or 0, signataire=signataire, d_tok={k: v for k, v in d_tok.items() if abs(v) > 1e-9}, d_sol=d_sol)

def financeur(wallet):
    """premier portefeuille qui a envoyé des SOL à ce portefeuille (approximation : plus ancienne transaction du portefeuille)"""
    r = rpc("getSignaturesForAddress", [wallet, {"limit": 1000}])
    if not r: return None
    t = tx(r[-1]["signature"])
    if not t or not t.get("meta"): return None
    cles = [k["pubkey"] if isinstance(k, dict) else k for k in t["transaction"]["message"]["accountKeys"]]
    if wallet not in cles: return None
    i = cles.index(wallet)
    if t["meta"]["postBalances"][i] - t["meta"]["preBalances"][i] <= 0: return None
    return cles[0] if cles[0] != wallet else None


DEBUT = time.time(); DUREE = 4 * 3600 + 30 * 60          # le workflow est coupé à 5 h
MAX_COINS = 25; AGE_MAX_H = 2; PAGES_MAX = 15; OFFRE = 1_000_000_000
FICH = "etude/bot5min/bubble_naissance_resultats.json"
R = json.load(open(FICH)) if os.path.exists(FICH) else {}
subprocess.run("git config user.name tests; git config user.email bot@users.noreply.github.com", shell=True)   # 07.11 : sans identité git, toutes les sauvegardes en cours d'étude échouaient en silence
dernier_push = [0.0]; verrou_git = threading.Lock()
def sauver(force=False):
    with verrou_git:
        json.dump(R, open(FICH, "w"), indent=1, default=str)
        if not force and time.time() - dernier_push[0] < 600: return
        dernier_push[0] = time.time()
        subprocess.run("git add etude/bot5min/ && git commit -qm 'Étude naissance : sauvegarde intermédiaire [skip ci]' && for k in 1 2 3 4 5; do git pull --rebase --autostash -q origin main && git push -q && break; sleep 5; done", shell=True)
def log(*a): print(time.strftime("%H:%M:%S"), *a, flush=True)

def nouveaux_coins():
    L = []; maint = time.time()
    for url in [f"{GT}/networks/solana/new_pools?page={p}" for p in range(1, 11)] + [f"{GT}/networks/solana/pools?page={p}&sort=h24_tx_count_desc" for p in range(1, 6)]:
        d = http(url); time.sleep(2.2)
        for p in (d or {}).get("data", []):
            a = p.get("attributes", {}); rel = p.get("relationships", {})
            try: cree = dt.datetime.fromisoformat(a["pool_created_at"].replace("Z", "+00:00")).timestamp()
            except Exception: continue
            mint = (rel.get("base_token", {}).get("data") or {}).get("id", "").replace("solana_", "")
            tx24 = sum((a.get("transactions", {}).get("h1") or {}).get(k, 0) or 0 for k in ("buys", "sells"))
            if mint.endswith("pump") and (maint - cree) / 3600 <= AGE_MAX_H and tx24 >= 100:
                L.append(dict(mint=mint, nom=a.get("name", "")[:40], age_min=round((maint - cree) / 60), tx_1h=tx24))
    vus = set(); return [c for c in sorted(L, key=lambda c: -c["tx_1h"]) if not (c["mint"] in vus or vus.add(c["mint"]))]

def histoire(mint):
    toutes = []; avant = None
    for _ in range(PAGES_MAX):
        p = {"limit": 1000}
        if avant: p["before"] = avant
        r = rpc("getSignaturesForAddress", [mint, p])
        if not r: break
        toutes += [x for x in r if not x.get("err")]
        if len(r) < 1000: break
        avant = r[-1]["signature"]
    else: return None
    toutes.sort(key=lambda x: (x.get("blockTime") or 0, x.get("slot") or 0)); return toutes

def evenements(sigs, mint):
    with ThreadPoolExecutor(6) as ex: T = list(ex.map(lambda s: analyser(tx(s["signature"]), mint), sigs))
    T = [x for x in T if x]; T.sort(key=lambda x: x["t"]); E = []
    for x in T:
        d = x["d_tok"]; sg = x["signataire"]; ds = x["d_sol"].get(sg, 0); dtk = d.get(sg, 0)
        ech = abs(dtk) > 0 and abs(ds) > 0.002 and (dtk > 0) == (ds < 0)
        E.append(dict(t=x["t"], echange=ech, prix=abs(ds) / abs(dtk) if ech else None, d_tok=d, sg=sg, achat=ech and dtk > 0,
                      perdants=[sg] if (not ech and dtk < 0) else [], gagnants=[k for k, v in d.items() if v > 0]))
    return E

def preparer(c):
    log("  préparation", c["nom"]); sigs = histoire(c["mint"]); log("   historique :", None if sigs is None else len(sigs), "transactions,", dict(appels))
    if sigs is None: return dict(c, erreur="histoire déjà trop longue")
    if len(sigs) < 150: return dict(c, erreur=f"trop peu de transactions ({len(sigs)})")
    E = evenements(sigs[:NB_TX], c["mint"]); log("   transactions lues :", len(E), dict(appels))
    courbe = None; solde = collections.defaultdict(float); liens = collections.defaultdict(set)
    for e in E:
        if courbe is None and e["d_tok"]: courbe = min(e["d_tok"], key=lambda k: e["d_tok"][k])
        for a in e["perdants"]:
            for b in e["gagnants"]:
                if b != courbe: liens[a].add(b); liens[b].add(a)
        for k, v in e["d_tok"].items(): solde[k] += v
    gros = sorted([k for k in solde if k != courbe], key=lambda k: -max(0, solde[k]))[:20]
    with ThreadPoolExecutor(6) as ex: F = dict(zip(gros, ex.map(financeur, gros)))
    log("   financeurs lus :", sum(1 for v in F.values() if v), "/", len(F))
    pf = collections.defaultdict(list)
    for w, f in F.items():
        if f: pf[f].append(w)
    for ws in pf.values():
        for a in ws:
            for b in ws:
                if a != b: liens[a].add(b)
    # 07.11 (5e) : les premiers résultats donnaient un « groupe » de 754 portefeuilles et un autre à 79 % des jetons → reliés par un nœud central
    # (piscine d'échange, routeur, distributeur), pas par un vrai groupe. Comme Bubblemaps, on retire ces nœuds : plus de 15 liens, ou plus de 30 % des jetons.
    centres = {k for k in liens if len(liens[k]) > 15} | {k for k in solde if solde[k] > 0.3 * OFFRE}
    for k in list(liens):
        if k in centres: liens[k] = set()
        else: liens[k] -= centres
    gros = [k for k in gros if k not in centres]
    def groupe(w):
        vu = {w}; pile = [w]
        while pile:
            for v in liens[pile.pop()]:
                if v not in vu and v != courbe: vu.add(v); pile.append(v)
        return frozenset(vu)
    groupes = {g for g in (groupe(w) for w in gros) if len(g) >= 3}
    res = dict(c, transactions_vues=len(sigs), groupes=len(groupes), plus_gros_groupe=max((len(g) for g in groupes), default=0), courbe=courbe, seuils={})
    if not groupes: return dict(res, erreur="aucun groupe de 3 portefeuilles ou plus")
    sold = collections.defaultdict(float)
    for X in SEUILS:
        sold.clear()
        for i, e in enumerate(E):
            for k, v in e["d_tok"].items(): sold[k] += v
            g = next((g for g in groupes if 100 * sum(max(0, sold[w]) for w in g) / OFFRE >= X), None)
            if g:
                p = next((f["prix"] for f in E[i + 1:] if f["achat"] and f["prix"]), None)
                if p: res["seuils"][str(X)] = dict(t=e["t"], prix=p * 1.01, part=round(100 * sum(max(0, sold[w]) for w in g) / OFFRE, 1), groupe=sorted(g))
                break
    if not res["seuils"]: return dict(res, erreur="aucun groupe n'atteint 5 %")
    res["suivi"] = {w: None for s in res["seuils"].values() for w in s["groupe"]}   # dernière signature vue par portefeuille
    res["rap"] = {}; res["sortie"] = None; res["vente_groupe_t"] = None
    return res

def prix_apres(mint, t0):
    """vrais échanges du coin après t0 : prix 2 s, 5 s, 30 s plus tard (on remonte l'histoire récente jusqu'à t0)"""
    toutes = []; avant = None
    for _ in range(10):
        p = {"limit": 1000}
        if avant: p["before"] = avant
        r = rpc("getSignaturesForAddress", [mint, p])
        if not r: break
        toutes += [x for x in r if not x.get("err")]
        if len(r) < 1000 or (r[-1].get("blockTime") or 0) < t0: break
        avant = r[-1]["signature"]
    fen = sorted([s for s in toutes if t0 <= (s.get("blockTime") or 0) <= t0 + 90], key=lambda s: (s["blockTime"], s.get("slot") or 0))
    out = {}
    for dl in (2, 5, 30):
        cand = [s for s in fen if s["blockTime"] >= t0 + dl][:8]
        for e in evenements(cand, mint):
            if e["echange"] and e["prix"]: out[f"p{dl}"] = e["prix"] * 0.99; break
    return out

def prix_actuel(mint):
    r = rpc("getSignaturesForAddress", [mint, {"limit": 15}]) or []
    for e in reversed(evenements([x for x in r if not x.get("err")], mint)):
        if e["echange"] and e["prix"]: return e["prix"] * 0.99
    return None

def suivre(c):
    """nouvelles transactions des portefeuilles du groupe : rapatriement vers un même portefeuille, première vente du groupe"""
    mint = c["mint"]; groupe = set(c["suivi"])
    for w in list(groupe):
        p = {"limit": 25}
        if c["suivi"][w]: p["until"] = c["suivi"][w]
        r = rpc("getSignaturesForAddress", [w, p]) or []
        if not r: continue
        c["suivi"][w] = r[0]["signature"]
        for e in evenements([x for x in r if not x.get("err")], mint):
            if e["t"] and e["echange"] and e["sg"] in groupe and e["d_tok"].get(e["sg"], 0) < 0 and c["vente_groupe_t"] is None and e["t"] > min(s["t"] for s in c["seuils"].values()):
                c["vente_groupe_t"] = e["t"]; log("   vente du groupe", c["nom"], e["t"])
            if not e["echange"] and e["t"] > min(s["t"] for s in c["seuils"].values()):
                for a in e["perdants"]:
                    if a in groupe:
                        for b in e["gagnants"]:
                            if b != c.get("courbe"): c["rap"].setdefault(b, []); c["rap"][b] = sorted(set(c["rap"][b]) | {a})
                if c["sortie"] is None and any(len(v) >= 2 for v in c["rap"].values()):
                    t0 = e["t"]; px = prix_apres(mint, t0)
                    c["sortie"] = dict(t=t0, **px)
                    for X, s in c["seuils"].items():
                        if s["t"] < t0: s.update({f"gain20_{k}": round(20 * (v / s["prix"] - 1), 2) for k, v in px.items()})
                    log("   RAPATRIEMENT", c["nom"], json.dumps(c["sortie"], default=str)); sauver(True)

# 1. coins nés depuis moins de 2 h, découverts toutes les 20 minutes pendant les 2 premières heures
def pousse_journal():          # 07.11 : journal poussé toutes les 5 min, pour voir l'avancement pendant l'étude
    while True:
        time.sleep(300); sauver(True)
threading.Thread(target=pousse_journal, daemon=True).start()
log("départ"); dernier_tour = 0
while time.time() - DEBUT < DUREE:
    if time.time() - DEBUT < 2 * 3600 and time.time() - dernier_tour > 1200 and sum(1 for c in R.values() if "seuils" in c and "erreur" not in c) < MAX_COINS:
        dernier_tour = time.time(); L = nouveaux_coins(); log("coins jeunes trouvés :", len(L))
        for c in L:
            if c["mint"] in R or time.time() - DEBUT > DUREE: continue
            if sum(1 for x in R.values() if "seuils" in x and "erreur" not in x) >= MAX_COINS: break
            try: r = preparer(c)
            except Exception as e: r = dict(c, erreur=str(e)[:100])
            R[c["mint"]] = r; log(c["nom"], c["age_min"], "min :", r.get("erreur") or {X: (s["part"], s["prix"]) for X, s in r["seuils"].items()}); sauver()
    for c in [x for x in R.values() if "suivi" in x and x.get("sortie") is None]:
        try: suivre(c)
        except Exception as e: log("erreur suivi", c["nom"], str(e)[:80])
    sauver(); time.sleep(20)

# 2. résumé
for c in R.values():
    if "suivi" in c and c.get("sortie") is None:
        p = prix_actuel(c["mint"])
        for s in c["seuils"].values(): s["sans_rapatriement_prix_fin"] = round(20 * (p / s["prix"] - 1), 2) if p else None
print("\n=== RÉSUMÉ (20 $ par coin, vrais prix d'échange, 1 % de frais à l'achat et à la vente) ===")
print("coins étudiés :", len(R), "; avec groupe et entrée :", sum(1 for c in R.values() if c.get("seuils") and "erreur" not in c))
for X in map(str, SEUILS):
    E = [(c, c["seuils"][X]) for c in R.values() if X in (c.get("seuils") or {})]
    for k in ("p2", "p5", "p30"):
        g = [s[f"gain20_{k}"] for c, s in E if f"gain20_{k}" in s]
        if g: print(f"groupe d'au moins {X} % : {len(E)} entrées, sortie {k[1:]} s après le rapatriement : {len(g)} cas, total {sum(g):+.2f} $, gagnants {sum(1 for x in g if x > 0)}/{len(g)}, meilleur {max(g):+.2f}, pire {min(g):+.2f}")
    sr = [s["sans_rapatriement_prix_fin"] for c, s in E if s.get("sans_rapatriement_prix_fin") is not None]
    if sr: print(f"groupe d'au moins {X} % : pas de rapatriement vu ({len(sr)} coins), valeur à la fin : total {sum(sr):+.2f} $")
d = sorted(c["vente_groupe_t"] - c["sortie"]["t"] for c in R.values() if c.get("sortie") and c.get("vente_groupe_t"))
if d: print(f"délai rapatriement → première vente du groupe : médiane {d[len(d)//2]} s, mini {d[0]} s, maxi {d[-1]} s ({len(d)} cas)")
print("appels RPC :", dict(appels)); sauver(True); print("FIN")
