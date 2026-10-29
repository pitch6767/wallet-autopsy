#!/bin/bash
# Banc d'essai du moteur de signaux (29.10.2026). Rien n'est lancé ni déployé : copie le code de bot95/src dans un dossier,
# remplace reel.js par un module vide (aucune clé, aucun ordre possible) et en fait un fichier lisible par Node.
# usage : ./preparer.sh <index.js à tester> <dossier de sortie>
#   puis : node rejouer.mjs <dossier>/bundle.mjs ../donnees/2026-10-28/rec_BTC.json.gz sortie.json [minutes]
#          node comparer.mjs avant.json apres.json
#          node noms_visibles.mjs <dossier>/bundle.mjs
set -e
ICI=$(cd "$(dirname "$0")" && pwd); SRC=$1; OUT=$2; rm -rf "$OUT"; mkdir -p "$OUT/src"
cp "$ICI"/../src/*.js "$ICI"/../src/*.json "$OUT/src/"
cp "$SRC" "$OUT/src/index.js"
cat > "$OUT/src/reel.js" <<'R'
export class Reel { constructor(env) { this.env = env; } modeReel() { return false; } configure() { return false; } }
export async function identifiantsLecture() { return null; }
R
echo 'export { STOPPEES, ARRET_18, xlVisible, META_TOP20, PORTEFEUILLE_400, CHEF_BASES, FILTRE_HEURES, NV, CATALOGUE, RAPIDE_SEUL, DUO_REGLE };' >> "$OUT/src/index.js"
npx -y esbuild@0.23.0 "$OUT/src/index.js" --bundle --format=esm --platform=node --loader:.json=json --outfile="$OUT/bundle.mjs" --log-level=warning
