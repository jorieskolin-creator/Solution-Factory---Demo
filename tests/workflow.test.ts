import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import scenario from '../src/scenario.json' with { type: 'json' };
import manifest from '../src/asset-manifest.json' with { type: 'json' };
import { acceptsInput, currentTask, initialRun, runReducer, taskTimeline, TOTAL_SECONDS, WRONG_INPUT } from '../src/engine.ts';

const bytes = readFileSync(new URL(`../public/documents/${scenario.inputFile}`, import.meta.url));
function fakeFile(buffer: Uint8Array, name = 'renamed.docx') { return { name, size: buffer.length, async arrayBuffer() { return Uint8Array.from(buffer).buffer; } }; }
test('only the exact prepared bytes are accepted, regardless of filename', async () => {
  assert.equal(await acceptsInput(1, fakeFile(bytes), manifest.inputSha256), true);
  const changed = Uint8Array.from(bytes); changed[50] ^= 1;
  assert.equal(await acceptsInput(1, fakeFile(changed, scenario.inputFile), manifest.inputSha256), false);
  assert.equal(await acceptsInput(1, fakeFile(new TextEncoder().encode('wrong material')), manifest.inputSha256), false);
  assert.equal(await acceptsInput(1, fakeFile(new Uint8Array()), manifest.inputSha256), false);
  assert.equal(await acceptsInput(1, { size: 6 * 1024 * 1024, async arrayBuffer() { throw Error('must not read'); } }, manifest.inputSha256), false);
  assert.equal(await acceptsInput(1, { size: 100, async arrayBuffer() { throw Error('unreadable'); } }, manifest.inputSha256), false);
});
test('lines 2 and 3 reject the actual correct document without reading it', async () => {
  for (const line of [2, 3]) assert.equal(await acceptsInput(line, { size: bytes.length, async arrayBuffer() { throw Error('must not read'); } }, manifest.inputSha256), false);
  assert.equal(WRONG_INPUT, 'WRONG INPUT/CONTRACT MATERIAL - PROVIDE CORRECT VERSION.');
});
test('the timeline has 21 readable tasks and ends at 150 seconds', () => {
  assert.equal(TOTAL_SECONDS, 150); assert.equal(taskTimeline.length, 21);
  assert.deepEqual(scenario.stages.map(s => s.duration), [21,14,14,21,28,28,14,10]);
  let state = runReducer(runReducer(initialRun, { type: 'ACCEPT' }), { type: 'START' });
  const visited: string[] = [];
  for (const task of taskTimeline) {
    assert.equal(currentTask(state.elapsed).title, task.title); visited.push(task.title);
    assert.equal(task.end - task.start, task.stageIndex === 7 ? 10 : 7);
    state = runReducer(state, { type: 'TICK', delta: task.end - task.start });
  }
  assert.equal(new Set(visited).size, 21); assert.equal(state.mode, 'review'); assert.equal(state.elapsed, 150);
});
test('pauses, hidden tabs, late frames and reset cannot skip descriptions or progress without authority', () => {
  assert.equal(runReducer(initialRun, { type: 'START' }).mode, 'idle');
  let state = runReducer(runReducer(initialRun, { type: 'ACCEPT' }), { type: 'START' });
  state = runReducer(state, { type: 'TICK', delta: 100 }); assert.equal(state.elapsed, 7);
  state = runReducer(state, { type: 'HIDE' }); assert.equal(state.hiddenPause, true);
  assert.deepEqual(runReducer(state, { type: 'TICK', delta: 100 }), state);
  state = runReducer(state, { type: 'RESUME' }); assert.equal(state.hiddenPause, false);
  state = runReducer(state, { type: 'PAUSE' });
  assert.deepEqual(runReducer(state, { type: 'TICK', delta: 10 }), state);
  assert.equal(runReducer(state, { type: 'END' }).mode, 'paused');
  assert.deepEqual(runReducer(state, { type: 'RESET' }), initialRun);
});
test('both terminal choices use a terminal state that cannot tick or restart without reset', () => {
  const ended = runReducer({ mode: 'review', elapsed: 150, hiddenPause: false }, { type: 'END' });
  assert.equal(ended.mode, 'ended');
  assert.deepEqual(runReducer(ended, { type: 'TICK', delta: 10 }), ended);
  assert.deepEqual(runReducer(ended, { type: 'START' }), ended);
});
test('all tasks refer to defined requirements and the approval asset remains identical', () => {
  const ids = new Set(scenario.requirements.map(r => r.id));
  for (const task of taskTimeline) for (const ref of task.refs) assert.equal(ids.has(ref), true, ref);
  assert.equal(ids.size, 10);
  const report = readFileSync(new URL(`../public/documents/${scenario.approvalFile}`, import.meta.url));
  assert.equal(createHash('sha256').update(report).digest('hex'), manifest.approvalSha256);
  assert.equal(report.subarray(0, 5).toString(), '%PDF-');
  assert.equal(manifest.previewSourceSha256, manifest.approvalSha256);
  assert.equal(manifest.approvalPages.length, 7);
  for (const page of manifest.approvalPages) {
    const preview = readFileSync(new URL(`../public/documents/${page.file}`, import.meta.url));
    assert.equal(createHash('sha256').update(preview).digest('hex'), page.sha256);
  }
});
