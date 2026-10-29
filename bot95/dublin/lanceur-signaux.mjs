// 29.10.2026 (Pitch : « décider et acheter au même endroit ») — moteur de signaux LOCAL sur le serveur de Dublin.
// Même code que bot95-signaux (MOTEUR="signaux"), dans workerd via miniflare, sur 127.0.0.1 seulement.
// Le bot de trading s'y connecte en websocket local (ws://127.0.0.1:8788/api/flux_signaux) : plus de trajet Cloudflare → Dublin.
// Aucun ordre ici, aucune clé de portefeuille. Le paquet n'est relu qu'au démarrage (pas de redémarrage automatique en journée).
import { Miniflare } from "miniflare";
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

const DIR = process.env.MOTEUR_DIR || path.dirname(new URL(import.meta.url).pathname);
const URL_PAQUET = process.env.BOT95_PAQUET_URL || "https://raw.githubusercontent.com/pitch6767/wallet-autopsy/main/bot95/dublin/paquet/index.js";
const F = path.join(DIR, "paquet.js");
const PORT = +(process.env.MOTEUR_PORT || 8788);
const log = (...x) => console.log(new Date().toISOString(), ...x);
const h = (s) => crypto.createHash("sha256").update(s).digest("hex").slice(0, 12);

let code = null;
try {
  const r = await fetch(URL_PAQUET + "?t=" + Date.now(), { headers: { "cache-control": "no-cache" } });
  if (!r.ok) throw new Error("paquet HTTP " + r.status);
  const c = await r.text(); if (c.length < 100000) throw new Error("paquet trop petit");
  fs.writeFileSync(F + ".tmp", c); fs.renameSync(F + ".tmp", F); code = c; log("paquet téléchargé", h(c));
} catch (e) { log("téléchargement :", e.message, "— version en cache"); if (fs.existsSync(F)) code = fs.readFileSync(F, "utf8"); }
if (!code) { log("aucun paquet, nouvel essai dans 30 s"); setTimeout(() => process.exit(1), 30000); }
else {
  const env = { MOTEUR: "signaux", SIGNAL_FLUX: "oui", MODE_REEL: "non", MISE_REEL: "50", SIGNAL_NUMS: process.env.SIGNAL_NUMS || "101,201,121,28,119" };
  if (process.env.CHAINLINK_SOURCE) env.CHAINLINK_SOURCE = process.env.CHAINLINK_SOURCE;
  const mf = new Miniflare({
    modules: [{ type: "ESModule", path: F, contents: code }],
    compatibilityDate: "2026-07-30",
    compatibilityFlags: ["nodejs_compat"],
    durableObjects: { BOT: "Bot", SONDE: "Sonde" },
    durableObjectsPersist: path.join(DIR, "etat"),
    bindings: env,
    host: "127.0.0.1",
    port: PORT,
  });
  await mf.ready;
  log("moteur de signaux local prêt sur 127.0.0.1:" + PORT, "— paquet", h(code));
  const reveil = () => mf.dispatchFetch("http://moteur/api/reveil").then((r) => r.body?.cancel()).catch((e) => log("réveil :", e.message));
  reveil(); setInterval(reveil, 60000);   // remplace le cron « * * * * * » de Cloudflare
}
