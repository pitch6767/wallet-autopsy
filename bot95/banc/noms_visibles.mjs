// Pour chaque stratégie que le moteur peut ouvrir, liste TOUS les noms affichés (xlVisible) que slNoms peut produire,
// en essayant toutes les combinaisons des champs mesurés à l'achat (flux30, saut Bybit, x2, passages, écart, carnet, pression, heure, prix, secondes restantes).
// « aucun » = la stratégie ne compte jamais dans CONSENSUS 6/8, « + idées » (≥ 10) ni dans un numéro envoyé.
// usage : node noms_visibles.mjs <bundle.mjs>
const M = await import(process.argv[2]);
const { NV, STOPPEES, Bot } = M;
function toutes(base) {
  const out = new Set();
  for (const flux30 of [null, -0.5, 0]) for (const by of [true, false, undefined]) for (const x2 of [null, { parts: 5 }]) for (const pass of [null, 1, 5])
  for (const ec of [null, 0.01, 0.05]) for (const cp of [undefined, 0.5, -0.5]) for (const pp of [undefined, 0.5, -0.5]) for (const hh of [3, 7, 12, null]) for (const prix of [0.05, 0.6, 0.3]) for (const rs of [60, 150, null]) {
    const heure = hh == null ? null : new Date(Date.UTC(2026, 9, 29, (hh - 2 + 24) % 24, 0, 0)).toISOString();
    const P = { strat: base, actif: "BTC", heure, flux30, bySautContre: by, x2, passages: pass, ecart: ec, carnetPour: cp, pressPour: pp, prix, restant_s: rs, start: 1000, cote: "Up" };
    for (const x of Bot.prototype.slNoms.call({}, P)) out.add(x.nom);
  }
  return [...out];
}
const autres = ["contrarien 5 min + 1 h", "fin", "desaccord 20", "desaccord confirme", "desaccord 20 Poly rejoint 3 s", "desaccord 20 Poly rejoint 3 s sans nuit", "V2-F + pas les deux baissent + volatilite >= 2"];
for (const n of [...NV.ACTIVES, ...autres]) {
  const v = toutes(n), st = STOPPEES.has(n + "|BTC");
  console.log((st ? "STOPPÉE (n'émet rien, consensus seulement) " : "") + (NV.ACTIVES.includes(n) ? "" : "[inactive] ") + n + " => " + (v.length ? v.join(" ; ") : "aucun nom affiché"));
}
