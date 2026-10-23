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

  function taille(niveau) {
    if (niveau <= 10) return 5;
    if (niveau <= 30) return 6;
    if (niveau <= 60) return 7;
    if (niveau <= 100) return 8;
    return 9;
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

  // Nombre de solutions (arrêt à 2)
  function compte(n, z, limite) {
    const colPris = new Array(n).fill(false);
    const zonePris = new Array(n).fill(false);
    let total = 0, prec = -9;
    function pose(l, p) {
      if (l === n) { total++; return total >= limite; }
      for (let c = 0; c < n; c++) {
        if (colPris[c] || Math.abs(p - c) <= 1) continue;
        const k = z[l * n + c];
        if (zonePris[k]) continue;
        colPris[c] = zonePris[k] = true;
        const stop = pose(l + 1, c);
        colPris[c] = zonePris[k] = false;
        if (stop) return true;
      }
      return false;
    }
    pose(0, prec);
    return total;
  }

  // Une solution différente de la vraie, ou null
  function autre(n, z, sol) {
    const colPris = new Array(n).fill(false);
    const zonePris = new Array(n).fill(false);
    const cur = new Array(n);
    let trouve = null;
    function pose(l, p) {
      if (l === n) {
        for (let i = 0; i < n; i++) if (cur[i] !== sol[i]) { trouve = cur.slice(); return true; }
        return false;
      }
      for (let c = 0; c < n; c++) {
        if (colPris[c] || Math.abs(p - c) <= 1) continue;
        const k = z[l * n + c];
        if (zonePris[k]) continue;
        colPris[c] = zonePris[k] = true; cur[l] = c;
        const stop = pose(l + 1, c);
        colPris[c] = zonePris[k] = false;
        if (stop) return true;
      }
      return false;
    }
    pose(0, -9);
    return trouve;
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
    for (let essai = 0; essai < 500; essai++) {
      const sol = solution(n, r);
      const z = zones(n, sol, r);
      for (let rep = 0; rep < 400; rep++) {
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
