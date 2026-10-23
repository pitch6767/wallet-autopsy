// Pré-calcul des grilles 12×12 (une génération prend plusieurs secondes : trop lent sur téléphone)
const g = require("./gen.js");
const [de, a] = process.argv.slice(2).map(Number);
const out = [];
for (let lv = de; lv <= a; lv++) {
  const p = g.grille(lv);
  out.push({ z: p.z.map((x) => x.toString(16)).join(""), s: p.sol.map((x) => x.toString(16)).join("") });
}
process.stdout.write(JSON.stringify(out));
