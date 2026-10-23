// Sublime — générateur de grilles (déterministe par niveau : même niveau = même grille pour tout le monde)
(function (root) {
  function rng(seed) {
    let a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function taille() {
    return 10;
  }

  // Position d'un chat par ligne : colonnes toutes différentes, jamais collées (même en diagonale)
  function solution(n, r) {
    const col = new Array(n).fill(-1);
    const pris = new Array(n).fill(false);
    function pose(l) {
      if (l === n) return true;
      const ordre = [...Array(n).keys()].sort(() => r() - 0.5);
      for (const c of ordre) {
        if (pris[c]) continue;
        if (l > 0 && Math.abs(col[l - 1] - c) <= 1) continue;
        col[l] = c; pris[c] = true;
        if (pose(l + 1)) return true;
        pris[c] = false;
      }
      return false;
    }
    pose(0);
    return col;
  }

  // Zones de couleur qui poussent autour de chaque chat
  function zones(n, sol, r) {
    const z = new Array(n * n).fill(-1);
    for (let l = 0; l < n; l++) z[l * n + sol[l]] = l;
    let restant = n * n - n;
    const voisins = (i) => {
      const l = Math.floor(i / n), c = i % n, v = [];
      if (l > 0) v.push(i - n);
      if (l < n - 1) v.push(i + n);
      if (c > 0) v.push(i - 1);
      if (c < n - 1) v.push(i + 1);
      return v;
    };
    while (restant > 0) {
      const k = Math.floor(r() * n);
      const bord = [];
      for (let i = 0; i < n * n; i++) {
        if (z[i] !== k) continue;
        for (const v of voisins(i)) if (z[v] === -1) bord.push(v);
      }
      if (!bord.length) continue;
      const v = bord[Math.floor(r() * bord.length)];
      z[v] = k; restant--;
    }
    return z;
  }

  // Recherche des solutions (zone la plus contrainte d'abord), arrêt à « limite »
  function chercher(n, z, limite) {
    const cellules = Array.from({ length: n }, () => []);
    for (let i = 0; i < n * n; i++) cellules[z[i]].push(i);
    const ligne = new Uint8Array(n), col = new Uint8Array(n), bloque = new Uint8Array(n * n);
    const faite = new Uint8Array(n), pos = new Array(n);
    const sols = [];
    function libre(i) { return !ligne[(i / n) | 0] && !col[i % n] && !bloque[i]; }
    function marque(i, d) {
      const l = (i / n) | 0, c = i % n;
      ligne[l] += d; col[c] += d;
      for (let dl = -1; dl <= 1; dl += 2) for (let dc = -1; dc <= 1; dc += 2) {
        const l2 = l + dl, c2 = c + dc;
        if (l2 >= 0 && l2 < n && c2 >= 0 && c2 < n) bloque[l2 * n + c2] += d;
      }
    }
    function pose(reste) {
      if (reste === 0) {
        const s = new Array(n);
        for (let k = 0; k < n; k++) s[(pos[k] / n) | 0] = pos[k] % n;
        sols.push(s);
        return sols.length >= limite;
      }
      let best = -1, bestCand = null;
      for (let k = 0; k < n; k++) {
        if (faite[k]) continue;
        const cand = [];
        for (const i of cellules[k]) if (libre(i)) cand.push(i);
        if (!cand.length) return false;
        if (!bestCand || cand.length < bestCand.length) { best = k; bestCand = cand; if (cand.length === 1) break; }
      }
      faite[best] = 1;
      for (const i of bestCand) {
        pos[best] = i; marque(i, 1);
        const stop = pose(reste - 1);
        marque(i, -1);
        if (stop) { faite[best] = 0; return true; }
      }
      faite[best] = 0;
      return false;
    }
    pose(n);
    return sols;
  }

  function compte(n, z, limite) { return chercher(n, z, limite).length; }

  function autre(n, z, sol) {
    for (const s of chercher(n, z, 2)) for (let i = 0; i < n; i++) if (s[i] !== sol[i]) return s;
    return null;
  }

  function voisins4(n, i) {
    const l = Math.floor(i / n), c = i % n, v = [];
    if (l > 0) v.push(i - n);
    if (l < n - 1) v.push(i + n);
    if (c > 0) v.push(i - 1);
    if (c < n - 1) v.push(i + 1);
    return v;
  }

  // La zone k reste-t-elle d'un seul tenant sans la case x ?
  function connexeSans(n, z, k, x) {
    const cases = [];
    for (let i = 0; i < n * n; i++) if (z[i] === k && i !== x) cases.push(i);
    if (!cases.length) return false;
    const vu = new Set([cases[0]]), pile = [cases[0]];
    while (pile.length) {
      const i = pile.pop();
      for (const v of voisins4(n, i)) if (v !== x && z[v] === k && !vu.has(v)) { vu.add(v); pile.push(v); }
    }
    return vu.size === cases.length;
  }

  function grille(niveau) {
    const n = taille(niveau);
    const r = rng(niveau * 7919 + 2026);
    for (let essai = 0; essai < 3000; essai++) {
      const sol = solution(n, r);
      const z = zones(n, sol, r);
      for (let rep = 0; rep < 3000; rep++) {
        const alt = autre(n, z, sol);
        if (!alt) return { n, sol, z, niveau };
        // Casser cette autre solution : déplacer une de ses cases vers une zone voisine
        const lignes = [];
        for (let l = 0; l < n; l++) if (alt[l] !== sol[l]) lignes.push(l);
        let fait = false;
        for (const l of lignes.sort(() => r() - 0.5)) {
          const x = l * n + alt[l], k = z[x];
          const cand = [...new Set(voisins4(n, x).map((v) => z[v]))].filter((k2) => k2 !== k);
          if (!cand.length || !connexeSans(n, z, k, x)) continue;
          z[x] = cand[Math.floor(r() * cand.length)];
          fait = true; break;
        }
        if (!fait) break;
      }
    }
    throw new Error("grille introuvable");
  }

  const api = { grille, taille, compte };
  if (typeof module !== "undefined") module.exports = api;
  else root.SublimeGen = api;
})(this);
