"""06.11.2026 (Pitch : « mettre 20 $ quand on voit un gros cluster, et quand le cluster transfère chaque wallet sur 1 pour vendre, on vend
immédiatement » — « je veux savoir à quel prix on aurait pu acheter »).

Étude sur des memecoins Solana DÉJÀ PASSÉS (données publiques, aucune clé, aucun ordre) :
  1. coins pump.fun / PumpSwap créés il y a 6 h à 4 jours, actifs (GeckoTerminal) ;
  2. leurs premières transactions (nœuds Solana publics) → achats / ventes (prix payé = SOL / jetons), transferts de jetons entre portefeuilles ;
  3. groupes (« clusters ») à la Bubblemaps : portefeuilles reliés par un transfert de jetons, ou financés en SOL par le même portefeuille ;
  4. ENTRÉE : premier instant où un groupe d'au moins 3 portefeuilles détient au moins X % des jetons → prix du premier achat suivant (+1 % de frais) ;
  5. SORTIE : premier « rapatriement » (au moins 2 portefeuilles du groupe envoient des jetons au même portefeuille) → prix des échanges
     2 s, 5 s et 30 s plus tard ; on note aussi le délai entre ce rapatriement et la première grosse vente du groupe.
Résultat pour 20 $ par coin. Sortie sans signes inférieur / supérieur.
"""
import json, time, urllib.request, collections, datetime as dt, random, threading
from concurrent.futures import ThreadPoolExecutor

RPCS = ["https://api.mainnet-beta.solana.com", "https://solana-rpc.publicnode.com", "https://solana.drpc.org"]
GT = "https://api.geckoterminal.com/api/v2"
NB_COINS = 30; NB_TX = 1200; SEUILS = [5, 10, 20]
verrou = threading.Lock(); appels = collections.Counter()

def http(url, corps=None, essais=6):
    for i in range(essais):
        try:
            req = urllib.request.Request(url, data=json.dumps(corps).encode() if corps else None, headers={"content-type": "application/json", "user-agent": "etude-clusters"})
            with urllib.request.urlopen(req, timeout=40) as r: return json.load(r)
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

# 1. coins
coins = []; vus = set(); maint = time.time()
for page in range(1, 11):
    d = http(f"{GT}/networks/solana/pools?page={page}&sort=h24_tx_count_desc")
    for p in (d or {}).get("data", []):
        a = p.get("attributes", {}); rel = p.get("relationships", {})
        dex = (rel.get("dex", {}).get("data") or {}).get("id", "")
        try: cree = dt.datetime.fromisoformat(a["pool_created_at"].replace("Z", "+00:00")).timestamp()
        except Exception: continue
        age_h = (maint - cree) / 3600
        mint = (rel.get("base_token", {}).get("data") or {}).get("id", "").replace("solana_", "")
        if not mint.endswith("pump") or mint in vus or not (6 <= age_h <= 96): continue
        vus.add(mint); coins.append(dict(mint=mint, nom=a.get("name", "")[:40], age_h=round(age_h, 1), dex=dex))
    time.sleep(2.2)
coins = coins[:NB_COINS]
print("coins retenus :", len(coins))

def signatures(mint):
    """toutes les signatures (de la plus récente à la plus ancienne), on garde les NB_TX plus anciennes"""
    toutes = []; avant = None
    for page in range(60):   # 06.11 : au plus 60 000 signatures par coin, sinon on ne remonte jamais au début (le 1er essai a tenu 5 h sans finir)
        p = {"limit": 1000}
        if avant: p["before"] = avant
        r = rpc("getSignaturesForAddress", [mint, p])
        if not r: break
        toutes += [x for x in r if not x.get("err")]
        if len(r) < 1000: break
        avant = r[-1]["signature"]
    else: return None
    toutes.sort(key=lambda x: (x.get("blockTime") or 0, x.get("slot") or 0))
    return toutes[:NB_TX]

def tx(sig):
    return rpc("getTransaction", [sig, {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0, "commitment": "confirmed"}])

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

def etudier(c):
    mint = c["mint"]
    sigs = signatures(mint)
    if sigs is None: return dict(c, erreur="plus de 60 000 transactions : début du coin hors de portée")
    if len(sigs) < 200: return dict(c, erreur=f"trop peu de transactions ({len(sigs)})")
    with ThreadPoolExecutor(6) as ex: T = list(ex.map(lambda s: analyser(tx(s["signature"]), mint), sigs))
    T = [x for x in T if x]; T.sort(key=lambda x: x["t"])
    offre = 1_000_000_000   # pump.fun : 1 milliard de jetons
    solde = collections.defaultdict(float); liens = collections.defaultdict(set); evts = []
    courbe = None
    for x in T:
        dt_ = x["d_tok"]; sg = x["signataire"]
        if courbe is None and dt_: courbe = min(dt_, key=lambda k: dt_[k])   # 1re transaction : la courbe pump.fun cède des jetons
        gagnants = [k for k, v in dt_.items() if v > 0]; perdants = [k for k, v in dt_.items() if v < 0]
        ds = x["d_sol"].get(sg, 0); dtk = dt_.get(sg, 0)
        # échange = le signataire gagne des jetons en payant des SOL (achat) ou l'inverse (vente) ; sinon simple transfert de jetons
        echange = abs(dtk) > 0 and abs(ds) > 0.002 and (dtk > 0) == (ds < 0)
        prix = abs(ds) / abs(dtk) if echange else None
        if not echange and sg in perdants:
            for b in gagnants:
                if b != courbe: liens[sg].add(b); liens[b].add(sg)
        for k, v in dt_.items(): solde[k] += v
        evts.append(dict(t=x["t"], echange=echange, prix=prix, d_tok=dt_, perdants=[sg] if (not echange and sg in perdants) else [], gagnants=gagnants, sg=sg))
    # financeurs des 40 plus gros détenteurs vus
    gros = sorted([k for k in solde if k != courbe], key=lambda k: -max(0, solde[k]))[:40]
    with ThreadPoolExecutor(6) as ex: F = dict(zip(gros, ex.map(financeur, gros)))
    par_fin = collections.defaultdict(list)
    for w, f in F.items():
        if f: par_fin[f].append(w)
    for f, ws in par_fin.items():
        for a in ws:
            for b in ws:
                if a != b: liens[a].add(b)
    # composantes connexes
    def groupe(w):
        vu = {w}; pile = [w]
        while pile:
            u = pile.pop()
            for v in liens[u]:
                if v not in vu and v != courbe: vu.add(v); pile.append(v)
        return frozenset(vu)
    groupes = {g for g in (groupe(w) for w in gros) if len(g) >= 3}
    # rejouer dans le temps : part du plus gros groupe, entrée, rapatriement
    res = dict(c, transactions=len(evts), groupes=len(groupes), plus_gros_groupe=max((len(g) for g in groupes), default=0))
    if not groupes: return dict(res, erreur="aucun groupe de 3 portefeuilles ou plus")
    sold = collections.defaultdict(float)
    for X in SEUILS:
        sold.clear(); entree = None; sortie = None; g_entree = None
        for i, e in enumerate(evts):
            for k, v in e["d_tok"].items(): sold[k] += v
            if entree is None:
                for g in groupes:
                    part = 100 * sum(max(0, sold[w]) for w in g) / offre
                    if part >= X:
                        # premier achat APRÈS ce moment = prix payable
                        p = next((f["prix"] for f in evts[i + 1:] if f["echange"] and f["prix"]), None)
                        if p: entree = dict(t=e["t"], prix=p * 1.01, part=round(part, 1)); g_entree = g
                        break
            elif sortie is None:
                envoyeurs = collections.defaultdict(set)
                if not e["echange"]:
                    for a in e["perdants"]:
                        if a in g_entree:
                            for b in e["gagnants"]: envoyeurs[b].add(a)
                # rapatriement : la même destination a reçu de 2 portefeuilles du groupe (dans cette transaction ou cumulé)
                for b, s in envoyeurs.items():
                    res.setdefault("_rap", collections.defaultdict(set))[b] |= s
                if any(len(s) >= 2 for s in res.get("_rap", {}).values()):
                    t0 = e["t"]
                    def prix_a(dl):
                        f = next((f for f in evts[i + 1:] if f["echange"] and f["prix"] and f["t"] >= t0 + dl), None)
                        return f["prix"] * 0.99 if f else None
                    vente_groupe = next((f for f in evts[i + 1:] if f["echange"] and f["sg"] in g_entree and f["d_tok"].get(f["sg"], 0) < 0), None)
                    sortie = dict(t=t0, p2=prix_a(2), p5=prix_a(5), p30=prix_a(30), delai_vente_groupe=(vente_groupe["t"] - t0) if vente_groupe else None)
        r = {}
        if entree:
            r["entree"] = entree
            dernier = next((f["prix"] for f in reversed(evts) if f["echange"] and f["prix"]), None)
            if sortie:
                r["sortie"] = sortie
                for k in ("p2", "p5", "p30"):
                    if sortie[k]: r[f"gain20_{k}"] = round(20 * (sortie[k] / entree["prix"] - 1), 2)
            else:
                r["sans_rapatriement_dernier_prix"] = round(20 * ((dernier or 0) * 0.99 / entree["prix"] - 1), 2) if dernier else None
        res[f"seuil{X}"] = r
        res.pop("_rap", None)
    return res

# 06.11.2026 (Pitch : « si ça plante on perd tout ») : sauvegarde poussée sur GitHub APRÈS CHAQUE COIN, et reprise là où on s'était arrêté
import os, subprocess
FICH = "etude/bot5min/bubble_clusters_resultats.json"
R = json.load(open(FICH)) if os.path.exists(FICH) else []
faits = {r.get("mint") for r in R}
def sauver():
    json.dump(R, open(FICH, "w"), indent=1, default=str)
    subprocess.run("git add etude/bot5min/ && git commit -qm 'Étude clusters : sauvegarde intermédiaire [skip ci]' && for k in 1 2 3 4 5; do git pull --rebase -q origin main && git push -q && break; sleep 5; done", shell=True)
for i, c in enumerate(coins):
    if c["mint"] in faits: continue
    print(f"… début {c['nom']} {time.strftime('%H:%M:%S')}", flush=True)
    try: r = etudier(c)
    except Exception as e: r = dict(c, erreur=str(e)[:100])
    R.append(r); sauver(); print(f"[{i+1}/{len(coins)}] {c['nom']} : {json.dumps({k: v for k, v in r.items() if k not in ('mint',)}, default=str)[:700]}", flush=True)
print("\n=== RÉSUMÉ (20 $ par coin, prix réels des échanges, frais 1 % à l'achat et à la vente) ===")
for X in SEUILS:
    E = [r[f"seuil{X}"] for r in R if r.get(f"seuil{X}", {}).get("entree")]
    avec = [e for e in E if e.get("sortie")]
    for k in ("p2", "p5", "p30"):
        g = [e[f"gain20_{k}"] for e in avec if f"gain20_{k}" in e]
        if g: print(f"groupe d'au moins {X} % : {len(E)} entrées, {len(avec)} rapatriements vus ; sortie {k[1:]} s après : total {sum(g):+.2f} $, gagnants {sum(1 for x in g if x > 0)}/{len(g)}, meilleur {max(g):+.2f} $, pire {min(g):+.2f} $")
    sr = [e["sans_rapatriement_dernier_prix"] for e in E if not e.get("sortie") and e.get("sans_rapatriement_dernier_prix") is not None]
    if sr: print(f"groupe d'au moins {X} % : sans rapatriement vu ({len(sr)} coins), valeur au dernier prix étudié : {sum(sr):+.2f} $")
    d = [e["sortie"]["delai_vente_groupe"] for e in avec if e["sortie"].get("delai_vente_groupe") is not None]
    if d: d.sort(); print(f"   délai entre rapatriement et première vente du groupe : médiane {d[len(d)//2]} s, mini {d[0]} s, maxi {d[-1]} s ({len(d)} cas)")
print("appels RPC :", dict(appels))
print("FIN")
