import { test } from 'node:test';
import assert from 'node:assert/strict';
import scenario from '../src/scenario.json' with { type: 'json' };
import { selectTests } from '../src/test-selection.ts';

test('confirmed intake selects the required KB and owner tests, preserving explicit exclusions', () => {
  const selected = selectTests(scenario.intake.facts, scenario.testCatalog, scenario.additionalTests);
  assert.equal(selected.length, 26);
  assert.deepEqual(selected.map(x => x.id), scenario.selectedTestIds);
  assert.equal(selected.some(x => x.id === 'SAE-TST-08'), false);
  assert.equal(selected.filter(x => x.source === 'Additional Tests').length, 3);
  const changed = selectTests({ ...scenario.intake.facts, containerTarget: true }, scenario.testCatalog, scenario.additionalTests);
  assert.equal(changed.find(x => x.id === 'SAE-TST-08')?.mandatory, true);
  assert.deepEqual(selectTests({}, scenario.testCatalog, scenario.additionalTests), []);
  assert.throws(() => selectTests(scenario.intake.facts, scenario.testCatalog, [scenario.testCatalog[0]]), /Duplicate verification identity/);
});

test('every selected test and workflow reference retains intake and requirement traceability', () => {
  const ids = new Set(scenario.requirements.map(x => x.id));
  const tests = [...scenario.testCatalog, ...scenario.additionalTests];
  const testIds = new Set(tests.map(x => x.id));
  assert.equal(testIds.size, 27);
  for (const check of tests) {
    for (const fact of check.when) assert.equal(Object.hasOwn(scenario.intake.facts, fact), true);
    for (const req of check.requirements) assert.equal(ids.has(req), true);
    assert.ok(check.procedure && check.acceptance && check.record && check.evidenceId);
    assert.equal(check.mandatory, true);
  }
  for (const stage of scenario.stages) for (const task of stage.tasks) for (const id of task.testRefs) assert.equal(testIds.has(id), true, id);
  for (const req of ids) assert.ok(tests.some(x => x.requirements.includes(req)), req);
  assert.deepEqual([...new Set(scenario.testCatalog.map(x => x.blueprintNode))].sort(), ['12','13','14','15','16','17']);
  for (const boundary of scenario.contractBasis.boundaries) {
    for (const req of boundary.requirements) assert.ok(ids.has(req), req);
    for (const check of boundary.tests) {
      assert.ok(scenario.selectedTestIds.includes(check), check);
      assert.ok(tests.some(x => x.id === check && x.requirements.some(r => boundary.requirements.includes(r))), check);
    }
  }
  assert.ok(scenario.contractBasis.decisions.some(x => x.gate === 'Before executable contract'));
});
