// Horloge des marchés : New York pour les actions US (NYSE), UTC pour le BTC (24 h/24).
// Repris de day-trader-skill (Jakeschincariol, licence MIT) : mêmes règles d'heure d'été et mêmes jours fériés.

export const NYSE_FERIES = {
  "2026-01-01": "Nouvel An", "2026-01-19": "Martin Luther King Day", "2026-02-16": "Washington's Birthday",
  "2026-04-03": "Vendredi saint", "2026-05-25": "Memorial Day", "2026-06-19": "Juneteenth",
  "2026-07-03": "Fête nationale (observée)", "2026-09-07": "Labor Day", "2026-11-26": "Thanksgiving",
  "2026-12-25": "Noël", "2027-01-01": "Nouvel An", "2027-01-18": "Martin Luther King Day",
  "2027-02-15": "Washington's Birthday", "2027-03-26": "Vendredi saint", "2027-05-31": "Memorial Day",
  "2027-06-18": "Juneteenth (observé)", "2027-07-05": "Fête nationale (observée)", "2027-09-06": "Labor Day",
  "2027-11-25": "Thanksgiving", "2027-12-24": "Noël (observé)",
};
export const NYSE_FERMETURE_13H = { "2026-11-27": "lendemain de Thanksgiving", "2026-12-24": "veille de Noël", "2027-11-26": "lendemain de Thanksgiving" };

// Deux marchés. Les minutes sont comptées depuis minuit, heure locale du marché.
export const MARCHES = {
  actions: { nom: "actions US", tz: "New York", ouverture: 9 * 60 + 30, fermeture: 16 * 60, fermetureCourte: 13 * 60 },
  btc: { nom: "BTC", tz: "UTC", ouverture: 0, fermeture: 24 * 60, fermetureCourte: null },
};

export function estBtc(sym) { return /^BTC(-USD)?$/i.test(String(sym || "").trim()); }
export function marcheDe(sym) { return estBtc(sym) ? MARCHES.btc : MARCHES.actions; }
export function symYahoo(sym) { return estBtc(sym) ? "BTC-USD" : String(sym).toUpperCase().replace(".", "-"); }

function nthDimanche(annee, mois, n) { // mois 1-12 -> date UTC (jour)
  const d = new Date(Date.UTC(annee, mois - 1, 1));
  const decal = (7 - d.getUTCDay()) % 7;
  return Date.UTC(annee, mois - 1, 1 + decal + 7 * (n - 1));
}
// Décalage de New York en heures (-4 heure d'été, -5 sinon), pour un instant UTC (ms).
export function decalageNY(ms) {
  const a = new Date(ms).getUTCFullYear();
  const debut = nthDimanche(a, 3, 2) + 7 * 3600e3;  // 2 h EST
  const fin = nthDimanche(a, 11, 1) + 6 * 3600e3;   // 2 h EDT
  return ms >= debut && ms < fin ? -4 : -5;
}
// Instant (ms UTC) -> heure locale du marché {date:"AAAA-MM-JJ", min: minutes depuis minuit, sec}
export function local(ms, marche) {
  const off = marche.tz === "UTC" ? 0 : decalageNY(ms);
  const d = new Date(ms + off * 3600e3);
  return { date: d.toISOString().slice(0, 10), min: d.getUTCHours() * 60 + d.getUTCMinutes(), sec: d.getUTCSeconds(), jourSemaine: d.getUTCDay() };
}
// Heure locale du marché -> instant UTC (ms)
export function versUtc(date, min, marche) {
  const base = Date.parse(date + "T00:00:00Z") + min * 60e3;
  if (marche.tz === "UTC") return base;
  for (const off of [-4, -5]) { const u = base - off * 3600e3; if (decalageNY(u) === off) return u; }
  return base + 5 * 3600e3;
}
export function jourOuvre(date, marche) {
  if (marche.tz === "UTC") return [true, ""];
  const js = new Date(date + "T12:00:00Z").getUTCDay();
  if (js === 0 || js === 6) return [false, "week-end"];
  if (NYSE_FERIES[date]) return [false, "jour férié NYSE : " + NYSE_FERIES[date]];
  return [true, ""];
}
// [ouverture, fermeture] en minutes, ou null si fermé toute la journée
export function seance(date, marche) {
  if (!jourOuvre(date, marche)[0]) return null;
  return [marche.ouverture, (marche.fermetureCourte && NYSE_FERMETURE_13H[date]) ? marche.fermetureCourte : marche.fermeture];
}
export function hhmm(min) { min = ((min % 1440) + 1440) % 1440; return String(Math.floor(min / 60)).padStart(2, "0") + ":" + String(min % 60).padStart(2, "0"); }
export function lireHeure(t) {
  const m = /^\s*(\d{1,2})[:h](\d{2})\s*$/.exec(t || "");
  if (!m || +m[1] > 23 || +m[2] > 59) return null;
  return +m[1] * 60 + +m[2];
}
// Jour ouvré précédent (pour la clôture de la veille)
export function maintenant() { return Date.now(); }
