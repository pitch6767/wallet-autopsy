// Sublime — fabrique des niveaux classés du plus facile au plus difficile,
// plus une réserve de grilles pour le puzzle du jour.
// Chaque grille garde une seule solution et se résout par logique seule (aucune devinette).
// Usage : node outils/fabrique2.js <nb_grilles_a_generer>
const g = require("./gen.js");
const L = require("./logique.js");
const fs = require("fs");
const path = require("path");

const total = Number(process.argv[2] || 3000);
const NB_NIVEAUX = 600, NB_JOUR = 400;
const toutes = [];
for (let s = 1; s <= total; s++) {
  const p = g.grille(100000 + s);
  const r = L.resoudre(p.n, p.z);
  if (!r) continue;
  if (r.sol.join() !== p.sol.join()) continue;
  toutes.push({ z: p.z.map((x) => x.toString(16)).join(""), s: p.sol.map((x) => x.toString(16)).join(""), d: r.score, t: r.niveauMax });
}
toutes.sort((a, b) => a.d - b.d);

// Courbe : on démarre très facile, on monte doucement, avec un niveau « respiration » tous les 5
const pris = new Uint8Array(toutes.length);
function prendre(p) {
  let k = Math.round(p * (toutes.length - 1));
  for (let e = 0; e < toutes.length; e++) {
    for (const j of [k + e, k - e]) if (j >= 0 && j < toutes.length && !pris[j]) { pris[j] = 1; return toutes[j]; }
  }
}
const niveaux = [];
for (let k = 0; k < NB_NIVEAUX; k++) {
  let p = Math.min(0.97, 0.01 + Math.pow(k / NB_NIVEAUX, 0.8) * 0.96);
  if (k % 5 === 4) p = Math.max(0, p - 0.18);
  niveaux.push(prendre(p));
}
// Puzzle du jour : grilles moyennes à difficiles, mélangées de façon fixe
const reste = toutes.filter((_, j) => !pris[j]).filter((x, j, a) => j > a.length * 0.35);
let graine = 7;
const alea = () => ((graine = (graine * 16807) % 2147483647) / 2147483647);
reste.sort(() => alea() - 0.5);
const jour = reste.slice(0, NB_JOUR);

const sortie = path.join(__dirname, "..", "public");
// Palier d'aide : 1 (tiers facile), 2 (milieu), 3 (tiers difficile)
const q1 = toutes[Math.floor(toutes.length / 3)].d, q2 = toutes[Math.floor((2 * toutes.length) / 3)].d;
const net = (x) => ({ z: x.z, s: x.s, d: x.d, a: x.d <= q1 ? 1 : x.d <= q2 ? 2 : 3 });
fs.writeFileSync(path.join(sortie, "niveaux.json"), JSON.stringify(niveaux.map(net)));
fs.writeFileSync(path.join(sortie, "jour.json"), JSON.stringify(jour.map(net)));
console.log("grilles valides", toutes.length, "niveaux", niveaux.length, "jour", jour.length);
console.log("difficulté niveaux 1-10 :", niveaux.slice(0, 10).map((x) => x.d).join(" "));
console.log("difficulté niveaux 100-110 :", niveaux.slice(100, 110).map((x) => x.d).join(" "));
console.log("difficulté niveaux 590-600 :", niveaux.slice(590).map((x) => x.d).join(" "));
