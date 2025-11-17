/**
 * MVP-PHASE-001: ProvenanceValidationPhase Test Suite
 *
 * Validates ProvenanceValidationPhase execution and event generation.
 *
 * Tests:
 * - Phase properties (id, name, order)
 * - Detects PLACEHOLDER parameters
 * - Detects drift in VERIFIED parameters
 * - Only runs yearly (Month % 12 === 0)
 *
 * Week 5 Benchmark (Nov 17, 2025)
 */

import { test, describe } from 'node:test';
import assert from 'node:assert';
import { ProvenanceValidationPhase } from '../../src/simulation/engine/phases/ProvenanceValidationPhase';
import { createDefaultInitialState } from '../../src/simulation/initialization';
import { registerParameter } from '../../src/utils/provenanceTracking';
import type { GameState } from '../../src/types/game';

/**
 * Simple seeded RNG for deterministic tests
 */
function createSeededRNG(seed: number): () => number {
  let state = seed;
  return () => {
    state = (state * 1103515245 + 12345) & 0x7fffffff;
    return state / 0x7fffffff;
  };
}

describe('MVP-PHASE-001: ProvenanceValidationPhase', () => {
  let phase: ProvenanceValidationPhase;
  let state: GameState;
  let rng: () => number;

  test('Setup: Create phase and state', () => {
    phase = new ProvenanceValidationPhase();
    rng = createSeededRNG(42);
    state = createDefaultInitialState(rng, 'balanced');
  });

  test('Phase properties: id', () => {
    assert.strictEqual(phase.id, 'provenance-validation');
  });

  test('Phase properties: name', () => {
    assert.strictEqual(phase.name, 'Provenance Validation');
  });

  test('Phase properties: order', () => {
    assert.strictEqual(phase.order, 5.0);
  });

  test('Detects PLACEHOLDER parameters (Month 12)', () => {
    // Clear registry
    state.provenanceRegistry = {};
    state.currentMonth = 12;

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
    assert.ok(warnings.length > 0, 'Should generate warning for PLACEHOLDER');
    assert.ok(warnings[0].message.includes('PLACEHOLDER'), 'Warning should mention PLACEHOLDER');
  });

  test('Detects drift in VERIFIED parameters (Month 12)', () => {
    // Clear registry
    state.provenanceRegistry = {};
    state.currentMonth = 12;

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
    assert.ok(driftEvents.length > 0, 'Should generate drift event');
    assert.ok(driftEvents[0].message.includes('DRIFT'), 'Event should mention DRIFT');
  });

  test('Does not run on non-yearly months (Month 6)', () => {
    // Clear registry
    state.provenanceRegistry = {};
    // CRITICAL FIX: Set state.currentMonth (phase reads from state, not context)
    state.currentMonth = 6;

    registerParameter(state, {
      name: 'param',
      value: 1,
      level: 'PLACEHOLDER'
    });

    const result = phase.execute(state, rng, {
      month: 6,
      currentPhase: 'provenance-validation',
      isEndGame: false
    });

    assert.strictEqual(result.events.length, 0, 'Should not generate events on Month 6');
  });

  test('Runs on Month 0 (game start)', () => {
    // Clear registry
    state.provenanceRegistry = {};
    state.currentMonth = 0;

    registerParameter(state, {
      name: 'param',
      value: 1,
      level: 'PLACEHOLDER'
    });

    const result = phase.execute(state, rng, {
      month: 0,
      currentPhase: 'provenance-validation',
      isEndGame: false
    });

    assert.ok(result.events.length > 0, 'Should run on Month 0');
  });

  test('Runs on Month 24 (2 years)', () => {
    // Clear registry
    state.provenanceRegistry = {};
    state.currentMonth = 24;

    registerParameter(state, {
      name: 'param',
      value: 1,
      level: 'PLACEHOLDER'
    });

    const result = phase.execute(state, rng, {
      month: 24,
      currentPhase: 'provenance-validation',
      isEndGame: false
    });

    assert.ok(result.events.length > 0, 'Should run on Month 24');
  });

  test('Multiple PLACEHOLDER parameters detected', () => {
    // Clear registry
    state.provenanceRegistry = {};
    state.currentMonth = 12;

    registerParameter(state, { name: 'p1', value: 1, level: 'PLACEHOLDER' });
    registerParameter(state, { name: 'p2', value: 2, level: 'PLACEHOLDER' });
    registerParameter(state, { name: 'p3', value: 3, level: 'PLACEHOLDER' });

    const result = phase.execute(state, rng, {
      month: 12,
      currentPhase: 'provenance-validation',
      isEndGame: false
    });

    const warnings = result.events.filter(e => e.type === 'provenance_warning');
    assert.ok(warnings.length >= 3, 'Should detect all 3 PLACEHOLDER parameters');
  });

  test('Ignores INFORMED parameters (no drift)', () => {
    // Clear registry
    state.provenanceRegistry = {};
    state.currentMonth = 12;

    registerParameter(state, {
      name: 'informed_param',
      value: 5.0,
      level: 'INFORMED',
      citation: 'Estimate (2024)'
    });

    const result = phase.execute(state, rng, {
      month: 12,
      currentPhase: 'provenance-validation',
      isEndGame: false
    });

    const driftEvents = result.events.filter(e => e.type === 'provenance_drift');
    assert.strictEqual(driftEvents.length, 0, 'INFORMED parameters without citedValue should not trigger drift');
  });

  test('VERIFIED parameter with no drift', () => {
    // Clear registry
    state.provenanceRegistry = {};
    state.currentMonth = 12;

    registerParameter(state, {
      name: 'no_drift_param',
      value: 3.0,
      level: 'VERIFIED',
      citation: 'Test (2025)',
      citedValue: 3.0 // No drift
    });

    const result = phase.execute(state, rng, {
      month: 12,
      currentPhase: 'provenance-validation',
      isEndGame: false
    });

    const driftEvents = result.events.filter(e => e.type === 'provenance_drift');
    assert.strictEqual(driftEvents.length, 0, 'Should not generate drift event for 0% drift');
  });

  test('VERIFIED parameter with acceptable drift (10%)', () => {
    // Clear registry
    state.provenanceRegistry = {};
    state.currentMonth = 12;

    registerParameter(state, {
      name: 'small_drift_param',
      value: 2.2,
      level: 'VERIFIED',
      citation: 'Test (2025)',
      citedValue: 2.0 // 10% drift (acceptable)
    });

    const result = phase.execute(state, rng, {
      month: 12,
      currentPhase: 'provenance-validation',
      isEndGame: false
    });

    const driftEvents = result.events.filter(e => e.type === 'provenance_drift');
    assert.strictEqual(driftEvents.length, 0, 'Should not generate drift event for 10% drift (below 20% threshold)');
  });

  test('Empty registry generates no events', () => {
    // Clear registry
    state.provenanceRegistry = {};
    state.currentMonth = 12;

    const result = phase.execute(state, rng, {
      month: 12,
      currentPhase: 'provenance-validation',
      isEndGame: false
    });

    assert.strictEqual(result.events.length, 0, 'Empty registry should generate no events');
  });

  test('Mixed parameters: VERIFIED, INFORMED, PLACEHOLDER', () => {
    // Clear registry
    state.provenanceRegistry = {};
    state.currentMonth = 12;

    registerParameter(state, {
      name: 'verified_ok',
      value: 1.0,
      level: 'VERIFIED',
      citation: 'A (2020)',
      citedValue: 1.0
    });

    registerParameter(state, {
      name: 'verified_drift',
      value: 3.0,
      level: 'VERIFIED',
      citation: 'B (2021)',
      citedValue: 2.0 // 50% drift
    });

    registerParameter(state, {
      name: 'informed_ok',
      value: 5.0,
      level: 'INFORMED',
      citation: 'C (2022)'
    });

    registerParameter(state, {
      name: 'placeholder_bad',
      value: 10.0,
      level: 'PLACEHOLDER'
    });

    const result = phase.execute(state, rng, {
      month: 12,
      currentPhase: 'provenance-validation',
      isEndGame: false
    });

    const driftEvents = result.events.filter(e => e.type === 'provenance_drift');
    const warningEvents = result.events.filter(e => e.type === 'provenance_warning');

    assert.strictEqual(driftEvents.length, 1, 'Should detect 1 drift event');
    assert.ok(warningEvents.length >= 1, 'Should detect at least 1 PLACEHOLDER warning');
  });
});
