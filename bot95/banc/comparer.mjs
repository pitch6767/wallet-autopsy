import fs from "node:fs";
const [a, b] = process.argv.slice(2).map((f) => JSON.parse(fs.readFileSync(f)));
const sig = (x) => JSON.stringify(x.signaux), nm = (x) => JSON.stringify(x.noms), jr = (x) => JSON.stringify(x.journal.map(({ clients, ...r }) => r)), cy = (x) => JSON.stringify(x.comptes);
console.log("signaux", a.signaux.length, b.signaux.length, sig(a) === sig(b) ? "IDENTIQUES" : "DIFFERENTS");
console.log("noms visibles", a.noms.length, b.noms.length, nm(a) === nm(b) ? "IDENTIQUES" : "DIFFERENTS");
console.log("journal", a.journal.length, b.journal.length, jr(a) === jr(b) ? "IDENTIQUE" : "DIFFERENT");
console.log("compteurs par cycle et côté (à chaque achat visible)", (a.comptes || []).length, (b.comptes || []).length, cy(a) === cy(b) ? "IDENTIQUES" : "DIFFERENTS");
console.log("temps moyen/message", a.moy_ms, "->", b.moy_ms, " total", a.total_ms, "->", b.total_ms, " p99", a.p99_ms, "->", b.p99_ms);
if (sig(a) !== sig(b)) { for (let i = 0; i < Math.max(a.signaux.length, b.signaux.length); i++) if (JSON.stringify(a.signaux[i]) !== JSON.stringify(b.signaux[i])) { console.log("1re diff", i, a.signaux[i], b.signaux[i]); break; } }
