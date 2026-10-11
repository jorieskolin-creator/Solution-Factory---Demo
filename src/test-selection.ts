export type TestRule = { id: string; when: readonly string[] };

/** Missing or unknown intake facts never imply applicability. */
export function selectTests<T extends TestRule>(facts: Record<string, boolean>, catalog: readonly T[], additions: readonly T[]): T[] {
  const unique = new Map<string, T>();
  for (const test of [...catalog, ...additions]) {
    if (unique.has(test.id)) throw new Error(`Duplicate verification identity: ${test.id}`);
    unique.set(test.id, test);
  }
  return [...unique.values()].filter(test => test.when.every(field => facts[field] === true));
}
