import assert from 'node:assert/strict';

/** Retain native tool and command rows while the managed profile owns compaction. */
export function adaptDailyPresets(input) {
  assert.equal(input.length, 4);
  assert.deepEqual(input.map(row => row.id).sort(), ['preset-cordis', 'preset-minimal', 'preset-ptc', 'preset-standard']);
  return input.map(row => {
    assert.equal(row.name, '@deepseek-ai/dsh-agent-preset');
    const config = structuredClone(row.config);
    assert.equal(row.id, 'preset-' + config.id);
    const groups = config.plugins.filter(row => row.id === 'compaction');
    assert.equal(groups.length, 1);
    const [group] = groups;
    assert.equal(group.name, 'cordis:group');
    assert.equal(group.group, true);
    assert.equal(group.isolate?.compaction, true);
    const engines = group.config.filter(row => row.id === 'compaction-basic');
    assert.equal(engines.length, 1);
    assert.equal(engines[0].name, '@deepseek-ai/dsh-compaction-basic');
    assert.notEqual(engines[0].disabled, true);
    group.config = group.config.filter(row => row.id !== 'compaction-basic');
    delete group.isolate.compaction;
    return { id: row.id, config };
  });
}
