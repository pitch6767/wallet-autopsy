// Atelier de rendu des vidéos « bonshommes bâtons » de Pitch (08.11.2026).
// Tourne dans un conteneur Cloudflare (node + ffmpeg). Reçoit un sujet, écrit le scénario avec Gemini,
// dessine les scènes (Gemini image, même personnage partout), enregistre la voix (Gemini TTS),
// puis monte le MP4 (zoom lent sur chaque image, sous-titres incrustés, voix).
// Inspiré du mode B « Autopilot » de kaomei/stickman-video-director (licence MIT) : structure du récit et styles.
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";

const PORT = 8080, RACINE = "/tmp/travaux";
const API = "https://generativelanguage.googleapis.com/v1beta";
const SIMULE = process.env.SIMULE === "1"; // test local sans Gemini
const travaux = new Map(); // id → { etape, pct, erreur, pret, fichier, cout }

const STYLES = {
  minimal: "Minimal hand-drawn explainer illustration: expressive slender stick figure with a modest round head, black oval eyes and clearly readable facial expression, fine slightly irregular black pen outlines, on near-white warm paper with an extremely faint square grid. A few hand-drawn colored props with limited warm yellow, red and green marker accents and curved arrows. Clean composition with generous negative space.",
  couleur: "Colorful hand-drawn storybook illustration: ordinary round-headed stick figure with sparse dot eyes and a short line mouth, irregular fine ink contours, warm paper texture, muted but varied colored props and a recognizable hand-drawn everyday environment with simple graphic depth. Cozy, warm and readable.",
  bonnet: "Minimalist 2D animated stick figure wearing a bright red beanie (smooth knit, no pom-pom) and a yellow t-shirt, with simple black stick limbs and shorts, no detailed eyes or pupils. Simple black lines, vibrant flat colors, clean modern explainer style with a bright background.",
  prehistoire: "Prehistoric dark-comedy cartoon: stick figure with an expressive white filled round head, black stick limbs, wearing a simple animal-hide outfit, in an earthy prehistoric setting with caves, rocks and fire, hand-drawn texture, warm earthy palette, comedic expressions.",
};
const SANS_TEXTE = "Absolutely no written words, letters, numbers, captions, speech bubbles or watermarks anywhere in the image.";

const attendre = (ms) => new Promise((r) => setTimeout(r, ms));
function lancer(cmd, args) {
  return new Promise((ok, ko) => {
    const p = spawn(cmd, args, { stdio: ["ignore", "pipe", "pipe"] });
    let out = "", err = "";
    p.stdout.on("data", (d) => (out += d)); p.stderr.on("data", (d) => (err += d));
    p.on("close", (c) => (c === 0 ? ok(out) : ko(new Error(`${cmd} a échoué : ${err.slice(-600)}`))));
  });
}
const duree = async (f) => Number((await lancer("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f])).trim());

async function gemini(cle, modele, corps, essais = 4) {
  for (let i = 0; ; i++) {
    const r = await fetch(`${API}/models/${modele}:generateContent`, { method: "POST", headers: { "content-type": "application/json", "x-goog-api-key": cle }, body: JSON.stringify(corps), signal: AbortSignal.timeout(180000) });
    if (r.ok) return r.json();
    const t = await r.text();
    if ((r.status === 429 || r.status >= 500) && i < essais) { await attendre(4000 * (i + 1)); continue; }
    let m = t; try { m = JSON.parse(t).error.message; } catch {}
    const e = new Error(`Gemini ${modele} : HTTP ${r.status} — ${m.slice(0, 300)}`); e.status = r.status; throw e;
  }
}

async function choisirModeles(cle) {
  const r = await fetch(`${API}/models?pageSize=200`, { headers: { "x-goog-api-key": cle } });
  if (!r.ok) throw new Error(r.status === 400 || r.status === 403 ? "Google refuse la clé Gemini." : `Liste des modèles Gemini : HTTP ${r.status}`);
  const noms = ((await r.json()).models || []).filter((m) => (m.supportedGenerationMethods || []).includes("generateContent")).map((m) => m.name.replace("models/", ""));
  const prend = (tests) => { for (const t of tests) { const n = noms.filter(t).sort().reverse()[0]; if (n) return n; } return null; };
  const texte = prend([(n) => n === "gemini-2.5-flash", (n) => /^gemini-\d(\.\d)?-flash$/.test(n), (n) => /flash/.test(n) && !/image|tts|audio|live|lite|thinking/.test(n)]);
  const image = prend([(n) => n === "gemini-2.5-flash-image", (n) => /flash.*image/.test(n) && !/preview/.test(n), (n) => /image/.test(n) && /gemini/.test(n)]);
  const voix = prend([(n) => /flash.*tts/.test(n), (n) => /tts/.test(n)]);
  if (!texte || !image || !voix) throw new Error(`Modèles Gemini introuvables pour cette clé (texte ${texte}, image ${image}, voix ${voix}).`);
  return { texte, image, voix };
}

// ---------- 1. Scénario ----------
async function scenario(t, M) {
  const nb = Math.max(4, Math.round(t.duree / 5));
  const consigne = `Tu écris le scénario d'une vidéo explicative de ${t.duree} secondes en ${t.langue}, animée avec des bonshommes bâtons, pour une chaîne YouTube.
Sujet : ${t.sujet}
Structure obligatoire en 5 temps : 1) accroche immédiate (question ou paradoxe, jamais de « bonjour ») ; 2) ce que tout le monde croit, puis on le contredit ; 3) le détail caché ou le vrai obstacle ; 4) la vérité de fond ; 5) une chute mémorable et une question qui pousse à commenter.
Découpe en exactement ${nb} scènes d'environ 5 secondes. Chaque scène : 11 à 15 mots de narration parlée (pas de liste, pas d'emoji), et une description visuelle concrète EN ANGLAIS du dessin (le personnage principal, son action précise, son expression, les objets, le décor). Le personnage principal est le même du début à la fin.
N'invente aucun chiffre, aucune citation, aucun fait douteux. Donne aussi le titre de la vidéo et une description EN ANGLAIS du personnage principal (apparence fixe).`;
  const schema = { type: "OBJECT", properties: { titre: { type: "STRING" }, personnage: { type: "STRING" }, scenes: { type: "ARRAY", items: { type: "OBJECT", properties: { narration: { type: "STRING" }, visuel: { type: "STRING" } }, required: ["narration", "visuel"] } } }, required: ["titre", "personnage", "scenes"] };
  const r = await gemini(t.cle, M.texte, { contents: [{ role: "user", parts: [{ text: consigne }] }], generationConfig: { responseMimeType: "application/json", responseSchema: schema, temperature: 0.9 } });
  const txt = r.candidates?.[0]?.content?.parts?.map((p) => p.text || "").join("") || "";
  const s = JSON.parse(txt);
  if (!s.scenes?.length) throw new Error("Gemini n'a pas rendu de scénario.");
  return s;
}

// ---------- 2. Images ----------
async function dessiner(t, M, prompt, reference, sortie) {
  const parts = [{ text: prompt }];
  if (reference) parts.push({ inlineData: { mimeType: "image/png", data: fs.readFileSync(reference).toString("base64") } });
  const cfg = { responseModalities: ["TEXT", "IMAGE"], imageConfig: { aspectRatio: t.format } };
  let r;
  try { r = await gemini(t.cle, M.image, { contents: [{ role: "user", parts }], generationConfig: cfg }); }
  catch (e) { if (e.status === 400) { delete cfg.imageConfig; r = await gemini(t.cle, M.image, { contents: [{ role: "user", parts }], generationConfig: cfg }); } else throw e; }
  const p = (r.candidates?.[0]?.content?.parts || []).map((x) => x.inlineData || x.inline_data).find((x) => x?.mimeType?.startsWith("image/"));
  if (!p) throw new Error("Gemini n'a pas rendu d'image (contenu refusé ?).");
  fs.writeFileSync(sortie + ".brut", Buffer.from(p.data, "base64"));
  const [w, h] = t.format === "9:16" ? [1080, 1920] : [1920, 1080];
  // recadrage exact au format, sans déformation
  await lancer("ffmpeg", ["-v", "error", "-y", "-i", sortie + ".brut", "-vf", `scale=${w}:${h}:force_original_aspect_ratio=increase,crop=${w}:${h}`, "-frames:v", "1", sortie]);
  t.cout += 0.039;
}

// ---------- 3. Voix ----------
function wav(pcm, rate) {
  const h = Buffer.alloc(44); h.write("RIFF"); h.writeUInt32LE(36 + pcm.length, 4); h.write("WAVEfmt ", 8); h.writeUInt32LE(16, 16); h.writeUInt16LE(1, 20); h.writeUInt16LE(1, 22);
  h.writeUInt32LE(rate, 24); h.writeUInt32LE(rate * 2, 28); h.writeUInt16LE(2, 32); h.writeUInt16LE(16, 34); h.write("data", 36); h.writeUInt32LE(pcm.length, 40); return Buffer.concat([h, pcm]);
}
async function parler(t, M, texte, sortie) {
  const r = await gemini(t.cle, M.voix, { contents: [{ role: "user", parts: [{ text: texte }] }], generationConfig: { responseModalities: ["AUDIO"], speechConfig: { voiceConfig: { prebuiltVoiceConfig: { voiceName: t.voix } } } } });
  const p = (r.candidates?.[0]?.content?.parts || []).map((x) => x.inlineData || x.inline_data).find((x) => x?.mimeType?.startsWith("audio/"));
  if (!p) throw new Error("Gemini n'a pas rendu de voix.");
  const rate = Number(p.mimeType.match(/rate=(\d+)/)?.[1] || 24000);
  fs.writeFileSync(sortie, wav(Buffer.from(p.data, "base64"), rate));
}

// ---------- 4. Montage ----------
const PETITS = new Set("à a au aux de du des d' le la les l' un une et ou ton ta tes ton son sa ses mon ma mes ce cette ces en pour par sur dans que qui ne n' se s' te t' me m' je tu il elle on nous vous ils elles y the a an of to and or in on for with".split(" "));
function morceaux(phrase, max) { // sous-titres d'une ligne, coupés aux pauses naturelles, jamais après un petit mot
  const mots = phrase.trim().split(/\s+/), out = []; let cur = [];
  const pousse = () => { if (!cur.length) return; const reste = []; while (cur.length > 1 && PETITS.has(cur[cur.length - 1].toLowerCase())) reste.unshift(cur.pop()); out.push(cur.join(" ")); cur = reste; };
  for (const m of mots) {
    if (cur.length && (cur.join(" ") + " " + m).length > max) pousse();
    cur.push(m);
    if (/[.,;:!?…]$/.test(m) && cur.join(" ").length > max * 0.55) pousse();
  }
  if (cur.length) out.push(cur.join(" "));
  return out;
}
const tps = (s) => { const h = Math.floor(s / 3600), m = Math.floor(s / 60) % 60, x = (s % 60).toFixed(2).padStart(5, "0"); return `${h}:${String(m).padStart(2, "0")}:${x}`; };
const echapASS = (s) => s.replace(/[{}]/g, "").replace(/\\/g, "");

async function monter(t, scenes, dossier) {
  const vertical = t.format === "9:16", W = vertical ? 1080 : 1920, H = vertical ? 1920 : 1080, FPS = 25;
  const max = vertical ? 26 : 44, taille = vertical ? 64 : 62, marge = vertical ? 330 : 70;
  let ass = `[Script Info]\nScriptType: v4.00+\nPlayResX: ${W}\nPlayResY: ${H}\nWrapStyle: 2\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: S,Noto Sans,${taille},&H00FFFFFF,&H00FFFFFF,&H00141414,&H96000000,1,0,0,0,100,100,0,0,3,14,0,2,60,60,${marge},1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n`;
  const clips = []; let t0 = 0;
  for (let i = 0; i < scenes.length; i++) {
    const sc = scenes[i], d = (await duree(sc.audio)) + 0.35, n = Math.ceil(d * FPS);
    // zoom lent alterné (avant / arrière) + léger glissement : l'image vit sans déformer le dessin
    const avant = i % 2 === 0, z = avant ? `min(1+0.10*on/${n},1.10)` : `max(1.10-0.10*on/${n},1.0)`;
    const x = i % 3 === 0 ? `iw/2-(iw/zoom/2)` : i % 3 === 1 ? `(iw-iw/zoom)*on/${n}` : `(iw-iw/zoom)*(1-on/${n})`;
    const clip = path.join(dossier, `c${i}.mp4`);
    await lancer("ffmpeg", ["-v", "error", "-y", "-i", sc.image, "-i", sc.audio,
      "-filter_complex", `[0:v]scale=${W * 2}:${H * 2},zoompan=z='${z}':x='${x}':y='ih/2-(ih/zoom/2)':d=${n}:s=${W}x${H}:fps=${FPS},format=yuv420p[v];[1:a]aresample=44100,apad=pad_dur=0.35[a]`,
      "-map", "[v]", "-map", "[a]", "-t", d.toFixed(3), "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-c:a", "aac", "-b:a", "160k", clip]);
    clips.push(clip);
    const bouts = morceaux(sc.narration, max), tot = bouts.reduce((a, b) => a + b.length, 0) || 1, parle = d - 0.35;
    let c = t0 + 0.05;
    for (const b of bouts) { const f = c + parle * (b.length / tot); ass += `Dialogue: 0,${tps(c)},${tps(Math.min(f, t0 + d))},S,,0,0,0,,${echapASS(b)}\n`; c = f; }
    t0 += d;
    t.pct = 75 + Math.round((20 * (i + 1)) / scenes.length);
  }
  fs.writeFileSync(path.join(dossier, "sous-titres.ass"), ass);
  fs.writeFileSync(path.join(dossier, "liste.txt"), clips.map((c) => `file '${c}'`).join("\n"));
  const brut = path.join(dossier, "brut.mp4"), final = path.join(dossier, "video.mp4");
  await lancer("ffmpeg", ["-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", path.join(dossier, "liste.txt"), "-c", "copy", brut]);
  await lancer("ffmpeg", ["-v", "error", "-y", "-i", brut, "-vf", `ass=${path.join(dossier, "sous-titres.ass")}`, "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-c:a", "copy", "-movflags", "+faststart", final]);
  return final;
}

// ---------- Orchestration ----------
async function parLots(liste, n, f) { const r = []; for (let i = 0; i < liste.length; i += n) r.push(...(await Promise.all(liste.slice(i, i + n).map(f)))); return r; }

async function travail(t) {
  const dossier = path.join(RACINE, t.id); fs.mkdirSync(dossier, { recursive: true });
  try {
    t.etape = "Préparation"; t.pct = 2;
    const M = SIMULE ? { texte: "x", image: "x", voix: "x" } : await choisirModeles(t.cle);
    t.modeles = M;
    t.etape = "Écriture du scénario"; t.pct = 5;
    const s = SIMULE ? simuScenario(t) : await scenario(t, M);
    t.titre = s.titre; t.narration = s.scenes.map((x) => x.narration);
    const style = STYLES[t.style] || STYLES.minimal;
    t.etape = "Dessin du personnage"; t.pct = 10;
    const ref = path.join(dossier, "personnage.png");
    if (SIMULE) await simuImage(t, ref, "personnage");
    else await dessiner(t, M, `${style}\nCharacter reference sheet: the main character standing in a neutral pose, full body, centered, plain background. Character: ${s.personnage}\n${SANS_TEXTE}`, null, ref);
    let faits = 0;
    t.etape = "Dessin des scènes";
    const scenes = s.scenes.map((x, i) => ({ ...x, image: path.join(dossier, `s${i}.png`), audio: path.join(dossier, `s${i}.wav`) }));
    await parLots(scenes, 3, async (sc, i) => {
      if (SIMULE) await simuImage(t, sc.image, String(i));
      else await dessiner(t, M, `${style}\nKeep exactly the same main character as in the reference image (same face, proportions, clothes and line style). Character: ${s.personnage}\nScene: ${sc.visuel}\nFormat ${t.format}. ${SANS_TEXTE}`, ref, sc.image);
      faits++; t.pct = 10 + Math.round((45 * faits) / scenes.length);
    });
    t.etape = "Enregistrement de la voix"; faits = 0;
    await parLots(scenes, 3, async (sc) => {
      if (SIMULE) await simuVoix(sc.narration, sc.audio); else await parler(t, M, sc.narration, sc.audio);
      faits++; t.pct = 55 + Math.round((20 * faits) / scenes.length);
    });
    t.etape = "Montage de la vidéo";
    t.fichier = await monter(t, scenes, dossier);
    t.taille = fs.statSync(t.fichier).size; t.secondes = Math.round(await duree(t.fichier));
    t.etape = "Prête"; t.pct = 100; t.pret = true;
  } catch (e) {
    t.erreur = String(e.message || e); t.etape = "Échec";
    console.error(t.id, e);
  } finally { delete t.cle; }
}

// ---------- Simulation locale (tests sans Gemini) ----------
function simuScenario(t) { const n = Math.max(4, Math.round(t.duree / 5)); return { titre: "Test", personnage: "x", scenes: Array.from({ length: n }, (_, i) => ({ narration: `Scène ${i + 1} : pourquoi ton cerveau adore remettre à demain, et comment l'en empêcher vraiment ?`, visuel: "x" })) }; }
async function simuImage(t, f, txt) { const [w, h] = t.format === "9:16" ? [1080, 1920] : [1920, 1080]; await lancer("ffmpeg", ["-v", "error", "-y", "-f", "lavfi", "-i", `testsrc2=s=${w}x${h}`, "-frames:v", "1", f]); }
async function simuVoix(txt, f) { await lancer("ffmpeg", ["-v", "error", "-y", "-f", "lavfi", "-i", "sine=frequency=330:duration=4.2", "-ar", "24000", "-ac", "1", f]); }

// ---------- Serveur ----------
const VOIX = ["Charon", "Kore", "Puck", "Aoede", "Fenrir", "Leda", "Orus", "Zephyr"];
function json(res, o, s = 200) { res.writeHead(s, { "content-type": "application/json; charset=utf-8" }); res.end(JSON.stringify(o)); }
http.createServer(async (req, res) => {
  const u = new URL(req.url, "http://x");
  try {
    if (u.pathname === "/sante") return json(res, { ok: true, ffmpeg: (await lancer("ffmpeg", ["-version"])).split("\n")[0], travaux: travaux.size });
    if (u.pathname === "/job" && req.method === "POST") {
      let b = ""; for await (const c of req) b += c; const j = JSON.parse(b || "{}");
      if (!j.id || !j.sujet || (!j.cle && !SIMULE)) return json(res, { erreur: "id, sujet et clé requis" }, 400);
      if (travaux.has(j.id)) return json(res, { ok: true, deja: true });
      const t = { id: j.id, cle: j.cle, sujet: String(j.sujet).slice(0, 2000), style: j.style in STYLES ? j.style : "minimal", duree: Math.min(120, Math.max(20, Number(j.duree) || 60)),
        format: j.format === "9:16" ? "9:16" : "16:9", langue: j.langue || "français", voix: VOIX.includes(j.voix) ? j.voix : "Charon", etape: "En attente", pct: 0, cout: 0, debut: Date.now() };
      travaux.set(j.id, t); travail(t);
      return json(res, { ok: true });
    }
    if (u.pathname === "/etat") {
      const t = travaux.get(u.searchParams.get("id"));
      if (!t) return json(res, { inconnu: true }, 404);
      const { cle, fichier, ...pub } = t; return json(res, pub);
    }
    if (u.pathname === "/fichier") {
      const t = travaux.get(u.searchParams.get("id"));
      if (!t?.pret) return json(res, { erreur: "pas prête" }, 404);
      res.writeHead(200, { "content-type": "video/mp4", "content-length": t.taille }); fs.createReadStream(t.fichier).pipe(res); return;
    }
    if (u.pathname === "/oublier" && req.method === "POST") {
      const id = u.searchParams.get("id"); travaux.delete(id); fs.rmSync(path.join(RACINE, id), { recursive: true, force: true }); return json(res, { ok: true });
    }
    json(res, { erreur: "inconnu" }, 404);
  } catch (e) { json(res, { erreur: String(e.message || e) }, 500); }
}).listen(PORT, () => console.log("atelier prêt", PORT));
