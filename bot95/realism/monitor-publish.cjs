'use strict';
// Read-only public summaries. Never copy journals, environment, or arbitrary paths.
const fs = require('node:fs/promises');
const path = require('node:path');
const { assess } = require('./readiness.cjs');
const DATA = process.env.BOT95_DATA || '/opt/bot95-protected/data';
const PUBLIC = process.env.BOT95_PUBLIC || '/opt/bot95-monitor/public';

async function publish() {
  const errors = [];
  async function read(name) {
    try {
      const raw = await fs.readFile(path.join(DATA, name), 'utf8');
      if (raw.length > 2_000_000) throw new Error('summary too large');
      const value = JSON.parse(raw);
      if (!value || typeof value !== 'object' || !Number.isFinite(value.at))
        throw new Error('invalid summary');
      return value;
    } catch {
      errors.push(`${name}: indisponible ou invalide`);
      return null;
    }
  }
  const latest = await read('latest.json');
  const report = await read('report.json');
  let readiness;
  try {
    const reference = '/opt/bot95-monitor/official-reference.js';
    readiness = assess(await fs.readFile(reference,'utf8'));
    readiness.referenceCapturedAt = (await fs.stat(reference)).mtimeMs;
  }
  catch {
    readiness = assess('');
    readiness.evidence[0].detail = 'Copie de référence inaccessible ou absente.';
  }
  const output = JSON.stringify({ generatedAt: Date.now(), latest, report, errors, readiness });
  const tmp = path.join(PUBLIC, '.status.tmp');
  await fs.writeFile(tmp, output, { mode: 0o644 });
  await fs.rename(tmp, path.join(PUBLIC, 'status.json'));
}
if (require.main === module) publish().catch(error => {
  console.error('Monitor publication failed:', error.message);
  process.exitCode = 1;
});
module.exports = { publish };
