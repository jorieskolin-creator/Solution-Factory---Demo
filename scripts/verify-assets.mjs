import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import assert from 'node:assert/strict';
const scenario = JSON.parse(readFileSync(new URL('../src/scenario.json', import.meta.url), 'utf8'));
const manifest = JSON.parse(readFileSync(new URL('../src/asset-manifest.json', import.meta.url), 'utf8'));
for (const [file, expected] of [[scenario.inputFile, manifest.inputSha256], [scenario.approvalFile, manifest.approvalSha256]]) {
  const bytes = readFileSync(new URL(`../public/documents/${file}`, import.meta.url));
  assert.equal(createHash('sha256').update(bytes).digest('hex'), expected, `${file} changed; regenerate the approved document pair and manifest deliberately.`);
}
assert.equal(manifest.scenarioId, scenario.id);
assert.equal(manifest.version, scenario.version);
console.log('Document fingerprints and scenario identity verified.');
