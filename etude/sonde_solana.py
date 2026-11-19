# reel var8 + securite env/git 2026-11-19T19:10Z
import json, urllib.request, time
print("lu à", time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), time.time())
def g(u):
    try: return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"user-agent": "verif"}), timeout=200).read())
    except Exception as e: return {"ERREUR": str(e)}
V = g("https://72-11-157-70.sslip.io/api/bot/vitesse?historique=70")
print("vitesse", json.dumps({k: V.get(k) for k in ("ERREUR", "feu", "raisons", "achatMs", "trajetSignalMs", "blocageServeurMs", "moteur", "signaux", "issues", "dernierSignal")}, ensure_ascii=False)[:2500])
H = V.get("minutesNonVertes", []) or []; print("minutes non vertes :", len(H))
for h in H[-70:]: print(h.get("t", "")[11:16], h.get("feu"), "; ".join(h.get("raisons") or [])[:200])
M = g("https://72-11-157-70.sslip.io/api/bot/moteur"); s = M.get("statut") or {}
print("moteur", M.get("ERREUR"), "lu", M.get("lu"), "flux", json.dumps(s.get("flux"), ensure_ascii=False)[:800], "reconnexions", s.get("reconnexions"), "erreurs", json.dumps((s.get("erreurs") or [])[:10], ensure_ascii=False)[:800])
J = g("https://72-11-157-70.sslip.io/api/bot/maj"); print("MAJ-AUTO", json.dumps({k: v for k, v in J.items() if k != "journal"}, ensure_ascii=False)[:2000]); print("MAJ-JOURNAL", json.dumps((J.get("journal") or [])[-15:], ensure_ascii=False)[:3000])

print("BLOCAGES", json.dumps(V.get("blocages"), ensure_ascii=False)[:4000])

MC = g("https://72-11-157-70.sslip.io/api/bot/moteur"); st = (MC or {}).get("statut") or {}
print("MOTEUR-COMPLET", json.dumps({k: st.get(k) for k in ("heure", "clients", "cycle", "pause429", "rondesBloquees", "rondeEnCoursS", "secoursPrixABattre", "relaisSecours", "doublonsPoly", "ouvertes", "strategies", "nums", "ages_s")}, ensure_ascii=False)[:2500])
print("MOTEUR-PERF", json.dumps(st.get("perf"), ensure_ascii=False)[:1500])
BE = g("https://72-11-157-70.sslip.io/api/bot/banc/etat"); print("SOURCE", json.dumps((BE or {}).get("sourceSignaux"), ensure_ascii=False)[:800], json.dumps((BE or {}).get("moteur"), ensure_ascii=False)[:800])

DG = g("https://72-11-157-70.sslip.io/api/bot/diag?heures=14"); print("DIAG-HEURES", json.dumps(DG, ensure_ascii=False)[:6000])

print("EXECUTEUR", json.dumps((V or {}).get("executeur"), ensure_ascii=False)[:1200]); print("MEMOIRE", json.dumps((V or {}).get("memoire"), ensure_ascii=False)[:1200])

R = g("https://bot95.pitch67.workers.dev/api/reel")
print("REEL-DEPUIS", R.get("depuis"), "TOTAL", R.get("total"), R.get("ERREUR"))
for x in (R.get("strats") or []):
    pj = x.get("parJour") or {}
    print("REEL", json.dumps({k: x.get(k) for k in ("num","nom","estimee","n","gains","pertes","pnl","mise","miseMaxCycle","pire","creux","capital")}, ensure_ascii=False), "JOURS", json.dumps(dict(sorted(pj.items())[-6:])))


R = g("https://bot95.pitch67.workers.dev/api/reel")
V = [x for x in (R.get("strats") or []) if x.get("variante")]
print("REEL-TOTAL", R.get("total"), "variantes", len(V), R.get("ERREUR"))
for x in sorted(V, key=lambda x: -(x.get("pnl") or 0))[:40]: print("VAR8", x["num"], x["nom"][:90], x["n"], x["pnl"], x.get("creux"), json.dumps(dict(sorted((x.get("parJour") or {}).items())[-6:])))
M = g("https://72-11-157-70.sslip.io/api/bot/maj"); print("MAJ", M.get("bot"), M.get("maj"))
import ssl
H = ["72-11-157-70.sslip.io"] + [a + ".pitch67.workers.dev" for a in "bot95 caisse economat emploi compta billetterie fiche-recettes binance-relais creneaux parking capito chef-orchestre play-agents meme-sniper btc-physics nurserie shadow-arb away hermes-bridge legion conv-rev-scanner enveloppe tresorerie bullseye barrieres bonshommes day-trader flashback funding-arb peptides mp4 casque wallet-autopsy sublime radar-ia".split()]
for h in H:
    for path in ("/.env", "/.git/config", "/.git/HEAD", "/.env.local", "/.dev.vars", "/wrangler.toml", "/wrangler.jsonc", "/package.json", "/.npmrc"):
        try:
            r = urllib.request.urlopen(urllib.request.Request("https://" + h + path, headers={"user-agent": "verif-securite"}), timeout=15)
            b = r.read(400).decode("utf8", "replace"); ct = r.headers.get("content-type", "")
            html = "<html" in b.lower() or "<!doctype" in b.lower()
            sus = (not html) and any(k in b for k in ("[core]", "ref: refs", "=", "\"name\"", "compatibility_date", "_authToken"))
            print("SECU", "ALERTE" if sus else "ok", h, path, r.status, ct[:30], ("" if html else b[:60].replace("\n", " ")) if sus else "")
        except Exception as e:
            print("SECU ok", h, path, str(e)[:40])
