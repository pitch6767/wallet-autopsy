// Sublime — résolveur « humain » : résout une grille par logique seule et mesure sa difficulté.
// Techniques, de la plus simple à la plus dure :
//  1. seule case possible dans une couleur, une ligne ou une colonne
//  2. cases éliminées par toutes les cases restantes d'une couleur, ligne ou colonne
//  3. groupes : N couleurs enfermées dans N lignes (ou colonnes), et l'inverse
//  4. essai court : poser un chat mène vite à une impasse, donc la case est barrée
// Une grille qui demande de deviner est refusée.
(function (root) {
  function resoudre(n, z) {
    const N = n * n;
    const cand = new Uint8Array(N).fill(1);
    const chat = new Uint8Array(N);
    const unites = [];
    for (let l = 0; l < n; l++) unites.push([...Array(n).keys()].map((c) => l * n + c));
    for (let c = 0; c < n; c++) unites.push([...Array(n).keys()].map((l) => l * n + c));
    const zon = Array.from({ length: n }, () => []);
    for (let i = 0; i < N; i++) zon[z[i]].push(i);
    unites.push(...zon);
    // cases barrées si un chat est posé en i
    const tue = [];
    for (let i = 0; i < N; i++) {
      const l = (i / n) | 0, c = i % n, s = new Set();
      for (let j = 0; j < N; j++) {
        if (j === i) continue;
        const lj = (j / n) | 0, cj = j % n;
        if (lj === l || cj === c || z[j] === z[i] || (Math.abs(lj - l) <= 1 && Math.abs(cj - c) <= 1)) s.add(j);
      }
      tue.push([...s]);
    }

    function poser(cd, ch, i) {
      ch[i] = 1; cd[i] = 0;
      for (const j of tue[i]) cd[j] = 0;
    }
    // propagation simple (techniques 1 et 2) ; renvoie false si impasse
    function propage(cd, ch, compte) {
      let bouge = true;
      while (bouge) {
        bouge = false;
        for (const u of unites) {
          if (u.some((i) => ch[i])) continue;
          const libres = u.filter((i) => cd[i]);
          if (!libres.length) return false;
          if (libres.length === 1) { poser(cd, ch, libres[0]); if (compte) compte[1]++; bouge = true; continue; }
        }
        if (bouge) continue;
        for (const u of unites) {
          if (u.some((i) => ch[i])) continue;
          const libres = u.filter((i) => cd[i]);
          let inter = null;
          for (const i of libres) {
            const s = new Set(tue[i]);
            inter = inter ? inter.filter((j) => s.has(j)) : [...s];
          }
          for (const j of inter || []) if (cd[j]) { cd[j] = 0; bouge = true; if (compte) compte[2]++; }
          if (bouge) break;
        }
      }
      return true;
    }
    function groupes(cd, ch, compte) {
      // familles : lignes, colonnes, couleurs
      const lignes = unites.slice(0, n), cols = unites.slice(n, 2 * n);
      const paires = [[zon, lignes, (i) => (i / n) | 0], [zon, cols, (i) => i % n], [lignes, zon, (i) => z[i]], [cols, zon, (i) => z[i]]];
      for (const [A, B, idx] of paires) {
        const ouverts = [];
        for (let a = 0; a < n; a++) {
          if (A[a].some((i) => ch[i])) continue;
          const libres = A[a].filter((i) => cd[i]);
          ouverts.push({ a, ens: new Set(libres.map(idx)) });
        }
        // combinaisons de 2 à 4 unités
        const m = ouverts.length;
        const essai = (choix) => {
          const u = new Set();
          for (const o of choix) for (const b of o.ens) u.add(b);
          if (u.size !== choix.length) return false;
          const dedans = new Set(choix.map((o) => o.a));
          let fait = false;
          for (const b of u) for (const i of B[b]) {
            if (!cd[i]) continue;
            const a = A === zon ? z[i] : A === lignes ? (i / n) | 0 : i % n;
            if (!dedans.has(a)) { cd[i] = 0; fait = true; compte[3]++; }
          }
          return fait;
        };
        for (let x = 0; x < m; x++) for (let y = x + 1; y < m; y++) {
          if (essai([ouverts[x], ouverts[y]])) return true;
          for (let w = y + 1; w < m; w++) {
            if (essai([ouverts[x], ouverts[y], ouverts[w]])) return true;
            for (let v = w + 1; v < m; v++) if (essai([ouverts[x], ouverts[y], ouverts[w], ouverts[v]])) return true;
          }
        }
      }
      return false;
    }
    function essais(cd, ch, compte) {
      for (let i = 0; i < N; i++) {
        if (!cd[i]) continue;
        const cd2 = cd.slice(), ch2 = ch.slice();
        poser(cd2, ch2, i);
        if (!propage(cd2, ch2, null)) { cd[i] = 0; compte[4]++; return true; }
      }
      return false;
    }
    const compte = [0, 0, 0, 0, 0];
    let niveauMax = 1;
    for (let tour = 0; tour < 500; tour++) {
      if (!propage(cand, chat, compte)) return null;
      if (chat.reduce((a, b) => a + b, 0) === n) break;
      if (groupes(cand, chat, compte)) { niveauMax = Math.max(niveauMax, 3); continue; }
      if (essais(cand, chat, compte)) { niveauMax = Math.max(niveauMax, 4); continue; }
      return null; // il faudrait deviner
    }
    if (chat.reduce((a, b) => a + b, 0) !== n) return null;
    if (compte[2]) niveauMax = Math.max(niveauMax, 2);
    const score = compte[1] * 1 + compte[2] * 2 + compte[3] * 6 + compte[4] * 15;
    const sol = new Array(n);
    for (let i = 0; i < N; i++) if (chat[i]) sol[(i / n) | 0] = i % n;
    return { score, niveauMax, compte, sol };
  }

  const api = { resoudre };
  if (typeof module !== "undefined") module.exports = api;
  else root.SublimeLogique = api;
})(this);
