// 26.10.2026 — copie de bot95 sur le serveur de Dublin (décision de Pitch : « bot95 copié à Dublin »).
// Fait tourner EXACTEMENT le même code que https://bot95.pitch67.workers.dev (paquet construit par GitHub à chaque déploiement,
// dépôt public), dans workerd via miniflare, en local seulement (127.0.0.1). Aucun ordre réel ici : MODE_REEL = "non",
// aucune clé de portefeuille. Ses seules sorties vers le bot de trading sont les SIGNAUX (POST http://127.0.0.1:8090/api/bot/signal).
// Mise à jour : toutes les 5 minutes, si le paquet publié a changé, le programme s'arrête et systemd le relance avec le nouveau.
import { Miniflare } from "miniflare";
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

const DIR = process.env.BOT95_DUBLIN_DIR || path.dirname(new URL(import.meta.url).pathname);
const URL_PAQUET = process.env.BOT95_PAQUET_URL || "https://raw.githubusercontent.com/pitch6767/wallet-autopsy/main/bot95/dublin/paquet/index.js";
const F = path.join(DIR, "paquet.js");
const log = (...x) => console.log(new Date().toISOString(), ...x);
const h = (s) => crypto.createHash("sha256").update(s).digest("hex").slice(0, 12);

async function telecharger() {
  const r = await fetch(URL_PAQUET + "?t=" + Date.now(), { headers: { "cache-control": "no-cache" } });
  if (!r.ok) throw new Error("paquet HTTP " + r.status);
  const code = await r.text();
  if (code.length < 100000) throw new Error("paquet trop petit");
  return code;
}

let code = null;
try { code = await telecharger(); fs.writeFileSync(F + ".tmp", code); fs.renameSync(F + ".tmp", F); log("paquet", h(code)); }
catch (e) { log("téléchargement :", e.message, "— version en cache"); if (fs.existsSync(F)) code = fs.readFileSync(F, "utf8"); }
if (!code) { log("aucun paquet, nouvel essai dans 30 s"); setTimeout(() => process.exit(1), 30000); }
else {
  const env = {
    MODE_REEL: "non",
    MISE_REEL: "50",
    SIGNAL_URL: process.env.SIGNAL_URL || "http://127.0.0.1:8090/api/bot/signal",
    SIGNAL_TOKEN: process.env.BOT_SIGNAL_TOKEN || "",
    SIGNAL_NUMS: process.env.SIGNAL_NUMS || "101,201,121,28,119",
    COPIE_DUBLIN: "oui",
  };
  if (!env.SIGNAL_TOKEN) log("ATTENTION : BOT_SIGNAL_TOKEN absent — les signaux seront refusés par le bot de trading");
  const mf = new Miniflare({
    modules: [{ type: "ESModule", path: F, contents: code }],
    compatibilityDate: "2026-07-30",
    compatibilityFlags: ["nodejs_compat"],
    durableObjects: { BOT: "Bot", SONDE: "Sonde" },
    durableObjectsPersist: path.join(DIR, "etat"),
    bindings: env,
    host: "127.0.0.1",
    port: +(process.env.BOT95_DUBLIN_PORT || 8787),
  });
  await mf.ready;
  log("bot95 (copie de Dublin) prêt sur 127.0.0.1:" + (process.env.BOT95_DUBLIN_PORT || 8787), "— paquet", h(code));
  const reveil = () => mf.dispatchFetch("http://bot95/api/reveil").then((r) => r.body?.cancel()).catch((e) => log("réveil :", e.message));
  reveil(); setInterval(reveil, 60000);   // remplace le cron « * * * * » de Cloudflare
  setInterval(async () => {
    try { const n = await telecharger(); if (h(n) !== h(code)) { fs.writeFileSync(F + ".tmp", n); fs.renameSync(F + ".tmp", F); log("nouveau paquet", h(n), "— redémarrage"); await mf.dispose(); process.exit(0); } }
    catch (e) { log("vérification du paquet :", e.message); }
  }, 300000);
}
