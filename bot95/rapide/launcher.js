// Lanceur installé UNE fois sur le VPS : télécharge la dernière version de rapide.js depuis le bot Cloudflare, la garde en cache, la lance.
"use strict";
const fs = require("fs"), path = require("path");
const U = process.env.BOT95_URL || "https://bot95.pitch67.workers.dev", T = process.env.BOT95_RAPIDE_TOKEN || "";
const DIR = process.env.BOT95_DIR || __dirname, F = path.join(DIR, "rapide.js");
(async () => {
  try {
    const r = await fetch(U + "/api/rapide/code", { headers: { "x-rapide": T } });
    if (r.ok) { const d = await r.json(); if (d.code) { fs.writeFileSync(F + ".tmp", d.code); fs.renameSync(F + ".tmp", F); console.log("code", d.version); } }
    else console.log("code HTTP", r.status, "— version en cache");
  } catch (e) { console.log("code", e.message, "— version en cache"); }
  if (!fs.existsSync(F)) { console.log("aucun code disponible, nouvel essai dans 30 s"); setTimeout(() => process.exit(1), 30000); return; }
  require(F);
})();
