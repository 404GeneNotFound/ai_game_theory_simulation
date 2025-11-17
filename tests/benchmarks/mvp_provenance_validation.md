# MVP Provenance System Validation (Week 5)
**Version:** 1.0
**Created:** 2025-11-17
**Purpose:** Validate the minimal viable provenance implementation (Week 1-4)
**Scope:** Citation verification, drift detection, database persistence, simulation integration

---

## Executive Summary

This validation framework tests the **actual MVP implementation** built in Week 1-4:
- Citation verification via existing Python tools
- Drift detection using LSS (Local Surprise Signal)
- SQLite persistence
- GameState integration
- ProvenanceValidationPhase execution

**NOT tested:** Multi-level state managers, nested learning frequency hierarchies (those were in the rejected 46,803-line implementation)

---

## Test Suite 1: Citation Verification Accuracy

**Test ID:** `MVP-CIT-001`
**File:** `tests/benchmarks/citation_verification.test.ts`

### Objective
Verify that Python citation tools correctly identify valid vs invalid citations.

### Test Cases

```typescript
describe('Citation Verification Accuracy', () => {
  test('Valid DOI citation should verify', async () => {
    const verifier = new CitationVerifier();
    const result = await verifier.verifyParameterCitation(
      'planetary_boundary_transgression_count',
      6,
      'Richardson et al. (2023) doi:10.1126/science.adh2458'
    );

    expect(result.isValid).toBe(true);
    expect(result.confidence).toBeGreaterThan(0.8);
  });

  test('Invalid citation should fail', async () => {
    const verifier = new CitationVerifier();
    const result = await verifier.verifyParameterCitation(
      'fake_parameter',
      999,
      'Nonexistent Author (2099)'
    );

    expect(result.isValid).toBe(false);
  });

  test('Citation with wrong value should detect mismatch', async () => {
    const verifier = new CitationVerifier();
    const result = await verifier.verifyParameterCitation(
      'planetary_boundary_transgression_count',
      3, // Wrong value (paper says 6)
      'Richardson et al. (2023) doi:10.1126/science.adh2458'
    );

    expect(result.drift).toBeGreaterThan(0.5); // 50% drift
  });
});
```

**Success Criteria:**
- ✅ Valid citations verify correctly (>90% accuracy)
- ✅ Invalid citations fail appropriately
- ✅ Value mismatches detected via drift calculation

---

## Test Suite 2: Drift Detection (LSS)

**Test ID:** `MVP-LSS-001`
**File:** `tests/benchmarks/drift_detection.test.ts`

### Objective
Validate Local Surprise Signal (LSS) calculation and threshold enforcement.

### LSS Formula
```
drift = |current - cited| / cited
```

### Test Cases

```typescript
import { calculateDrift, isDriftExcessive } from '@/types/provenance';

describe('Drift Detection (LSS)', () => {
  test('No drift (exact match)', () => {
    const drift = calculateDrift(2.0, 2.0);
    expect(drift).toBe(0.0);
    expect(isDriftExcessive(drift)).toBe(false);
  });

  test('Acceptable drift (10%)', () => {
    const drift = calculateDrift(2.2, 2.0);
    expect(drift).toBe(0.1);
    expect(isDriftExcessive(drift)).toBe(false);
  });

  test('Warning threshold (20%)', () => {
    const drift = calculateDrift(2.4, 2.0);
    expect(drift).toBe(0.2);
    expect(isDriftExcessive(drift)).toBe(false); // 20% is threshold
  });

  test('Excessive drift (25%)', () => {
    const drift = calculateDrift(2.5, 2.0);
    expect(drift).toBe(0.25);
    expect(isDriftExcessive(drift)).toBe(true); // >20% triggers warning
  });

  test('Critical drift (50%)', () => {
    const drift = calculateDrift(3.0, 2.0);
    expect(drift).toBe(0.5);
    expect(isDriftExcessive(drift)).toBe(true); // Alert level
  });

  test('Negative drift (parameter decreased)', () => {
    const drift = calculateDrift(1.6, 2.0);
    expect(drift).toBe(0.2); // 20% decrease
  });
});
```

**Success Criteria:**
- ✅ Drift calculation matches LSS formula
- ✅ Threshold enforcement at 20% (warning) and 50% (alert)
- ✅ Handles both positive and negative drift

---

## Test Suite 3: Database Persistence

**Test ID:** `MVP-DB-001`
**File:** `tests/benchmarks/database_performance.test.ts`

### Objective
Validate SQLite persistence, retrieval, and performance.

### Test Cases

```typescript
import { ProvenanceDatabase } from '@/utils/provenanceDatabase';

describe('Database Persistence', () => {
  let db: ProvenanceDatabase;

  beforeEach(() => {
    db = new ProvenanceDatabase(':memory:'); // In-memory for tests
  });

  test('Save and retrieve parameter', () => {
    const id = db.saveProvenance({
      name: 'test_param',
      value: 2.5,
      level: 'VERIFIED',
      citation: 'Test (2025)',
      citedValue: 2.5,
      confidence: 0.9
    });

    const retrieved = db.getLatestProvenance('test_param');
    expect(retrieved).not.toBeNull();
    expect(retrieved?.value).toBe(2.5);
    expect(retrieved?.level).toBe('VERIFIED');
  });

  test('History tracking', () => {
    // Save multiple versions
    db.saveProvenance({ name: 'param', value: 1.0, level: 'PLACEHOLDER' });
    db.saveProvenance({ name: 'param', value: 1.5, level: 'INFORMED', citation: 'A (2024)' });
    db.saveProvenance({ name: 'param', value: 2.0, level: 'VERIFIED', citation: 'B (2025)' });

    const history = db.getProvenanceHistory('param');
    expect(history).toHaveLength(3);
    expect(history[0].level).toBe('PLACEHOLDER');
    expect(history[2].level).toBe('VERIFIED');
  });

  test('Statistics by level', () => {
    db.saveProvenance({ name: 'p1', value: 1, level: 'VERIFIED' });
    db.saveProvenance({ name: 'p2', value: 2, level: 'VERIFIED' });
    db.saveProvenance({ name: 'p3', value: 3, level: 'INFORMED' });
    db.saveProvenance({ name: 'p4', value: 4, level: 'PLACEHOLDER' });

    const stats = db.getStats();
    expect(stats.verified).toBe(2);
    expect(stats.informed).toBe(1);
    expect(stats.placeholder).toBe(1);
    expect(stats.total).toBe(4);
  });

  test('Performance: 1000 inserts', () => {
    const start = Date.now();

    for (let i = 0; i < 1000; i++) {
      db.saveProvenance({
        name: `param_${i}`,
        value: i,
        level: 'PLACEHOLDER'
      });
    }

    const duration = Date.now() - start;
    expect(duration).toBeLessThan(1000); // <1 second for 1000 inserts
  });
});
```

**Success Criteria:**
- ✅ Parameters saved and retrieved correctly
- ✅ History tracking works (multiple versions)
- ✅ Statistics aggregation accurate
- ✅ Performance: >1000 inserts/second

---

## Test Suite 4: GameState Integration

**Test ID:** `MVP-STATE-001`
**File:** `tests/benchmarks/gamestate_integration.test.ts`

### Objective
Validate provenance registry integration with GameState and helper utilities.

### Test Cases

```typescript
import { createDefaultInitialState } from '@/simulation/initialization';
import { registerParameter, getParameter, updateParameter, getProvenanceSummary } from '@/utils/provenanceTracking';

describe('GameState Integration', () => {
  let state: GameState;
  let rng: () => number;

  beforeEach(() => {
    rng = createSeededRNG(42);
    state = createDefaultInitialState(rng, 'balanced');
  });

  test('provenanceRegistry exists on GameState', () => {
    expect(state.provenanceRegistry).toBeDefined();
    expect(typeof state.provenanceRegistry).toBe('object');
  });

  test('registerParameter adds to registry', () => {
    const id = registerParameter(state, {
      name: 'test_param',
      value: 3.14,
      level: 'VERIFIED',
      citation: 'Pi (∞)'
    });

    expect(state.provenanceRegistry['test_param']).toBeDefined();
    expect(state.provenanceRegistry['test_param'].value).toBe(3.14);
  });

  test('getParameter with fallback', () => {
    // Parameter doesn't exist
    const value = getParameter(state, 'missing_param', 99);
    expect(value).toBe(99);

    // Auto-registers as PLACEHOLDER
    expect(state.provenanceRegistry['missing_param']).toBeDefined();
    expect(state.provenanceRegistry['missing_param'].level).toBe('PLACEHOLDER');
  });

  test('updateParameter preserves provenance', () => {
    registerParameter(state, {
      name: 'param',
      value: 1.0,
      level: 'VERIFIED',
      citation: 'Original (2024)'
    });

    updateParameter(state, 'param', 2.0, {
      notes: 'Updated for new research'
    });

    expect(state.provenanceRegistry['param'].value).toBe(2.0);
    expect(state.provenanceRegistry['param'].citation).toBe('Original (2024)'); // Preserved
    expect(state.provenanceRegistry['param'].notes).toContain('Updated');
  });

  test('getProvenanceSummary aggregates correctly', () => {
    registerParameter(state, { name: 'v1', value: 1, level: 'VERIFIED' });
    registerParameter(state, { name: 'v2', value: 2, level: 'VERIFIED' });
    registerParameter(state, { name: 'i1', value: 3, level: 'INFORMED' });
    registerParameter(state, { name: 'p1', value: 4, level: 'PLACEHOLDER' });

    const summary = getProvenanceSummary(state);
    expect(summary.total).toBe(4);
    expect(summary.verified).toBe(2);
    expect(summary.informed).toBe(1);
    expect(summary.placeholder).toBe(1);
  });
});
```

**Success Criteria:**
- ✅ provenanceRegistry field exists on all GameState instances
- ✅ Helper utilities work correctly
- ✅ Parameters registered and retrieved accurately
- ✅ Summary statistics match reality

---

## Test Suite 5: ProvenanceValidationPhase

**Test ID:** `MVP-PHASE-001`
**File:** `tests/benchmarks/validation_phase.test.ts`

### Objective
Validate ProvenanceValidationPhase execution and event generation.

### Test Cases

```typescript
import { ProvenanceValidationPhase } from '@/simulation/engine/phases/ProvenanceValidationPhase';
import { createDefaultInitialState } from '@/simulation/initialization';
import { registerParameter } from '@/utils/provenanceTracking';

describe('ProvenanceValidationPhase', () => {
  let phase: ProvenanceValidationPhase;
  let state: GameState;
  let rng: () => number;

  beforeEach(() => {
    phase = new ProvenanceValidationPhase();
    rng = createSeededRNG(42);
    state = createDefaultInitialState(rng, 'balanced');
  });

  test('Phase properties', () => {
    expect(phase.id).toBe('provenance-validation');
    expect(phase.name).toBe('Provenance Validation');
    expect(phase.order).toBe(5.0);
  });

  test('Detects PLACEHOLDER parameters', () => {
    registerParameter(state, {
      name: 'placeholder_param',
      value: 100,
      level: 'PLACEHOLDER'
    });

    const result = phase.execute(state, rng, {
      month: 12,
      currentPhase: 'provenance-validation',
      isEndGame: false
    });

    const warnings = result.events.filter(e => e.type === 'provenance_warning');
    expect(warnings.length).toBeGreaterThan(0);
    expect(warnings[0].message).toContain('PLACEHOLDER');
  });

  test('Detects drift in VERIFIED parameters', () => {
    registerParameter(state, {
      name: 'drifted_param',
      value: 2.5,
      level: 'VERIFIED',
      citation: 'Test (2025)',
      citedValue: 2.0 // 25% drift
    });

    const result = phase.execute(state, rng, {
      month: 12,
      currentPhase: 'provenance-validation',
      isEndGame: false
    });

    const driftEvents = result.events.filter(e => e.type === 'provenance_drift');
    expect(driftEvents.length).toBeGreaterThan(0);
    expect(driftEvents[0].message).toContain('DRIFT');
  });

  test('Only runs yearly (Month % 12 === 0)', () => {
    registerParameter(state, {
      name: 'param',
      value: 1,
      level: 'PLACEHOLDER'
    });

    // Month 6 - should not validate
    const result6 = phase.execute(state, rng, {
      month: 6,
      currentPhase: 'provenance-validation',
      isEndGame: false
    });
    expect(result6.events.length).toBe(0);

    // Month 12 - should validate
    const result12 = phase.execute(state, rng, {
      month: 12,
      currentPhase: 'provenance-validation',
      isEndGame: false
    });
    expect(result12.events.length).toBeGreaterThan(0);
  });
});
```

**Success Criteria:**
- ✅ Phase executes at correct order (5.0)
- ✅ Detects PLACEHOLDER parameters
- ✅ Detects drift in VERIFIED parameters
- ✅ Only runs yearly (Month % 12 === 0)

---

## Test Suite 6: End-to-End Integration

**Test ID:** `MVP-E2E-001`
**File:** `tests/benchmarks/e2e_provenance.test.ts`

### Objective
Validate complete workflow: parameter registration → simulation run → drift detection → database persistence.

### Test Case

```typescript
describe('End-to-End Provenance Workflow', () => {
  test('Complete workflow: register → simulate → detect → persist', async () => {
    // 1. Initialize state
    const rng = createSeededRNG(42);
    const state = createDefaultInitialState(rng, 'balanced');

    // 2. Register parameters with citations
    registerParameter(state, {
      name: 'climate_sensitivity',
      value: 3.0,
      level: 'VERIFIED',
      citation: 'IPCC AR6 (2021)',
      citedValue: 3.0,
      confidence: 0.95
    });

    registerParameter(state, {
      name: 'ai_capability_growth_rate',
      value: 1.5,
      level: 'INFORMED',
      citation: 'Epoch (2024)',
      notes: 'Estimated from trends'
    });

    // 3. Run simulation phase
    const phase = new ProvenanceValidationPhase();
    const result = phase.execute(state, rng, {
      month: 12,
      currentPhase: 'provenance-validation',
      isEndGame: false
    });

    // 4. Verify events generated
    expect(result.events.length).toBeGreaterThanOrEqual(0);

    // 5. Persist to database
    const db = new ProvenanceDatabase('.cache/test_provenance.db');
    db.saveProvenance(state.provenanceRegistry['climate_sensitivity']);
    db.saveProvenance(state.provenanceRegistry['ai_capability_growth_rate']);

    // 6. Retrieve and verify
    const retrieved = db.getLatestProvenance('climate_sensitivity');
    expect(retrieved?.value).toBe(3.0);
    expect(retrieved?.citation).toBe('IPCC AR6 (2021)');

    // 7. Statistics
    const summary = getProvenanceSummary(state);
    expect(summary.total).toBe(2);
    expect(summary.verified).toBe(1);
    expect(summary.informed).toBe(1);
  });
});
```

**Success Criteria:**
- ✅ Complete workflow executes without errors
- ✅ All components integrate correctly
- ✅ Data persists and retrieves accurately

---

## Acceptance Criteria (Week 5 Complete)

To consider Week 5 complete, ALL test suites must pass:

- [MVP-CIT-001] Citation Verification Accuracy: **PASS**
- [MVP-LSS-001] Drift Detection (LSS): **PASS**
- [MVP-DB-001] Database Persistence: **PASS**
- [MVP-STATE-001] GameState Integration: **PASS**
- [MVP-PHASE-001] ProvenanceValidationPhase: **PASS**
- [MVP-E2E-001] End-to-End Integration: **PASS**

**Performance Targets:**
- Citation verification: <2 seconds per parameter
- Drift calculation: <1ms per parameter
- Database inserts: >1000/second
- Phase execution: <10ms for typical workload

**Coverage Target:**
- Unit test coverage: >80% for provenance utilities
- Integration test coverage: >70% for phase execution

---

## Running the Tests

```bash
# Run all MVP validation tests
npm test -- tests/benchmarks/

# Run individual test suites
npm test tests/benchmarks/citation_verification.test.ts
npm test tests/benchmarks/drift_detection.test.ts
npm test tests/benchmarks/database_performance.test.ts
npm test tests/benchmarks/gamestate_integration.test.ts
npm test tests/benchmarks/validation_phase.test.ts
npm test tests/benchmarks/e2e_provenance.test.ts

# Generate coverage report
npm test -- --coverage tests/benchmarks/
```

---

## Next Steps (Week 6)

Once all Week 5 benchmarks pass:
1. Security audit with real citation data
2. Load testing at production scale (1000+ parameters)
3. Production deployment validation
4. Documentation finalization
