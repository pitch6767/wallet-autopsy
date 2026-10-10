// Emballe rapide.js pour le bot Cloudflare (qui le sert au VPS). Lancer : node bot95/rapide/pack.js
const fs = require("fs"), crypto = require("crypto"), p = __dirname;
const src = fs.readFileSync(p + "/rapide.js", "utf8");
const version = crypto.createHash("sha256").update(src).digest("hex").slice(0, 12);
const code = src.replace("__VERSION__", version);
fs.writeFileSync(p + "/../src/rapide_code.js", "// généré par bot95/rapide/pack.js — ne pas modifier à la main\nexport const RAPIDE_VERSION = " + JSON.stringify(version) + ";\nexport const RAPIDE_CODE = " + JSON.stringify(code) + ";\nexport const RAPIDE_LAUNCHER = " + JSON.stringify(fs.readFileSync(p + "/launcher.js", "utf8")) + ";\n");
console.log("version", version);
