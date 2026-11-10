// Générateur Mersenne Twister identique à random.Random(seed) de Python :
// mêmes tirages que la Time Machine d'origine (graine 19 -> mêmes chiffres partout).
export class HasardPython {
  constructor(graine) {
    this.mt = new Uint32Array(624); this.i = 625;
    // init_by_array(clé) avec la clé = mots de 32 bits de |graine|, comme CPython
    let n = Math.abs(Math.trunc(graine)); const cle = [];
    if (n === 0) cle.push(0);
    while (n > 0) { cle.push(n % 4294967296); n = Math.floor(n / 4294967296); }
    this._initGenrand(19650218);
    const mt = this.mt; let i = 1, j = 0, k = Math.max(624, cle.length);
    for (; k; k--) {
      const p = mt[i - 1] ^ (mt[i - 1] >>> 30);
      mt[i] = ((mt[i] ^ this._mul(p, 1664525)) + cle[j] + j) >>> 0;
      i++; j++; if (i >= 624) { mt[0] = mt[623]; i = 1; } if (j >= cle.length) j = 0;
    }
    for (k = 623; k; k--) {
      const p = mt[i - 1] ^ (mt[i - 1] >>> 30);
      mt[i] = ((mt[i] ^ this._mul(p, 1566083941)) - i) >>> 0;
      i++; if (i >= 624) { mt[0] = mt[623]; i = 1; }
    }
    mt[0] = 0x80000000;
  }
  _mul(a, b) { return Math.imul(a, b) >>> 0; }
  _initGenrand(s) {
    const mt = this.mt; mt[0] = s >>> 0;
    for (let i = 1; i < 624; i++) mt[i] = (this._mul(1812433253, mt[i - 1] ^ (mt[i - 1] >>> 30)) + i) >>> 0;
    this.i = 624;
  }
  u32() {
    const mt = this.mt;
    if (this.i >= 624) {
      for (let k = 0; k < 624; k++) {
        const y = (mt[k] & 0x80000000) | (mt[(k + 1) % 624] & 0x7fffffff);
        mt[k] = mt[(k + 397) % 624] ^ (y >>> 1) ^ (y & 1 ? 0x9908b0df : 0);
      }
      this.i = 0;
    }
    let y = mt[this.i++];
    y ^= y >>> 11; y ^= (y << 7) & 0x9d2c5680; y ^= (y << 15) & 0xefc60000; y ^= y >>> 18;
    return y >>> 0;
  }
  // _randbelow de CPython (n < 2^32 ici)
  sous(n) {
    const k = Math.floor(Math.log2(n)) + 1; // bit_length
    let r = this.u32() >>> (32 - k);
    while (r >= n) r = this.u32() >>> (32 - k);
    return r;
  }
  entier(a, b) { return a + this.sous(b - a + 1); }
  choix(liste) { return liste[this.sous(liste.length)]; }
}
