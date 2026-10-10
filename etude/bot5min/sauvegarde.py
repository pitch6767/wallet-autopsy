"""Sauvegarde permanente de TOUS les trades des fantomes (09.10.2026) : toutes les 30 min, on lit les 60 derniers trades complets
de chaque strategie (/api/hist) et on les ajoute a bot95/sauvegarde/<strategie>.json (fusion par heure + cote, rien n'est jamais efface)."""
import json, os, re, sys, urllib.parse, urllib.request, time
U = "https://bot95.pitch67.workers.dev"
D = "bot95/sauvegarde/"
def get(url):
    for k in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "sauvegarde"}), timeout=90) as r: return json.loads(r.read())
        except Exception as e: err = e; time.sleep(5)
    raise err
def fichier(nom): return D + re.sub(r"[^A-Za-z0-9,.+-]+", "_", nom).strip("_") + ".json"
def fusion(nom, trades, resume=None, archive=None):
    f = fichier(nom); old = json.load(open(f)) if os.path.exists(f) else {"nom": nom, "trades": {}}
    for t in trades:
        k = f"{t.get('heure')}|{t.get('cote')}"; old["trades"][k] = {**old["trades"].get(k, {}), **{x: t.get(x) for x in ("heure", "cote", "prix", "parts", "U", "D", "cash", "net", "issue", "gagnant", "proba0", "restant_s", "journal", "start", "slug", "carnet", "tAchat", "tailleAffichee", "prixABattre", "clObs", "clRecu", "clDernier", "btc") if x in t}}
    if resume: old["resume_bot"] = resume
    if archive:                                              # archive compacte du bot : [heure, cote, prix, net, issue, proba0, restant_s]
        A = {f"{l[0]}|{l[1]}": l for l in old.get("archive", [])}
        for l in archive: A[f"{l[0]}|{l[1]}"] = l
        old["archive"] = sorted(A.values(), key=lambda l: l[0])
    old["n_sauves"] = len(old["trades"]); old["maj"] = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    json.dump(old, open(f, "w"), ensure_ascii=False, indent=0)
    return len(old["trades"])
def main():
    os.makedirs(D, exist_ok=True)
    if len(sys.argv) > 1:                                    # import d'un ancien fichier (ex. zone_trades.json du 08.10)
        for nom, v in json.load(open(sys.argv[1])).items(): print(nom, fusion(nom, v.get("trades", [])))
    n = get(U + "/api/nouveaux")
    for nom in sorted(n.get("strats", {})):
        h = get(U + "/api/hist?s=" + urllib.parse.quote(nom))
        print(nom, fusion(nom, h.get("derniers", []), h.get("resume"), h.get("archive")))
main()
try:                                                         # reglements officiels (prix a battre, prix final, gagnant) contre nos donnees
    R = get(U + "/api/reglements"); f = "bot95/reglements.json"
    old = json.load(open(f)) if os.path.exists(f) else []
    vu = {(x["a"], x["start"]) for x in old}
    old += [x for x in R.get("lignes", []) if (x["a"], x["start"]) not in vu]
    old.sort(key=lambda x: (x["start"], x["a"])); json.dump(old, open(f, "w"), ensure_ascii=False, indent=0); print("reglements", len(old))
except Exception as e: print("reglements", e)
try:                                                         # journal du fantome « TWAP fin confirme Chainlink » (tous les signaux, achetes ou abandonnes)
    J = get(U + "/api/twap_confirme").get("signaux", []); f = "bot95/twap_confirme.json"
    old = json.load(open(f)) if os.path.exists(f) else []
    vu = {x["start"] for x in old}; old += [x for x in J if x["start"] not in vu]
    old.sort(key=lambda x: x["start"]); json.dump(old, open(f, "w"), ensure_ascii=False, indent=0); print("twap_confirme", len(old))
except Exception as e: print("twap_confirme", e)
try:                                                         # carnets 8 niveaux au signal TWAP fin et 0,25 / 0,5 / 1 / 2 / 5 s apres
    J = get(U + "/api/twap_carnets").get("signaux", []); f = "bot95/twap_carnets.json"
    old = json.load(open(f)) if os.path.exists(f) else []
    vu = {(x["start"], x["nom"]) for x in old}; old += [x for x in J if (x["start"], x["nom"]) not in vu]
    old.sort(key=lambda x: (x["start"], x["nom"])); json.dump(old, open(f, "w"), ensure_ascii=False, indent=0); print("twap_carnets", len(old))
except Exception as e: print("twap_carnets", e)
try:                                                         # V2-F et ses 3 variantes (10.10) : chaque opportunite achetee ou refusee
    J = get(U + "/api/v2f_variantes").get("signaux", []); f = "bot95/v2f_variantes.json"
    old = json.load(open(f)) if os.path.exists(f) else []
    vu = {(x["start"], x["nom"]) for x in old}; old += [x for x in J if (x["start"], x["nom"]) not in vu]
    old.sort(key=lambda x: (x["start"], x["nom"])); json.dump(old, open(f, "w"), ensure_ascii=False, indent=0); print("v2f_variantes", len(old))
except Exception as e: print("v2f_variantes", e)
try:                                                         # vitesse (10.10) : age des donnees a la decision et achetable 0,1 a 2 s plus tard
    d = get(U + "/api/vitesse"); J = d.get("signaux", []); f = "bot95/vitesse.json"
    old = json.load(open(f)) if os.path.exists(f) else []
    vu = {(x["start"], x["nom"]) for x in old}; old += [x for x in J if (x["start"], x["nom"]) not in vu]
    old.sort(key=lambda x: (x["start"], x["nom"])); json.dump(old, open(f, "w"), ensure_ascii=False, indent=0); print("vitesse", len(old), d.get("latPoly"), d.get("latDec"))
except Exception as e: print("vitesse", e)
