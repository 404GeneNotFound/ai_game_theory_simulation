/**
 * MVP-STATE-001: GameState Integration Test Suite
 *
 * Validates provenance registry integration with GameState and helper utilities.
 *
 * Tests:
 * - provenanceRegistry field exists
 * - registerParameter adds to registry
 * - getParameter with fallback
 * - updateParameter preserves provenance
 * - getProvenanceSummary aggregates correctly
 *
 * Week 5 Benchmark (Nov 17, 2025)
 */

import { test, describe } from 'node:test';
import assert from 'node:assert';
import { createDefaultInitialState } from '../../src/simulation/initialization';
import {
  registerParameter,
  getParameter,
  updateParameter,
  getProvenanceSummary,
  batchRegisterParameters
} from '../../src/utils/provenanceTracking';
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

describe('MVP-STATE-001: GameState Integration', () => {
  let state: GameState;
  let rng: () => number;

  // Before each test, create a fresh GameState
  test('Setup: Create GameState', () => {
    rng = createSeededRNG(42);
    state = createDefaultInitialState(rng, 'balanced');
  });

  test('provenanceRegistry exists on GameState', () => {
    assert.ok(state.provenanceRegistry !== undefined);
    assert.strictEqual(typeof state.provenanceRegistry, 'object');
  });

  test('registerParameter adds to registry', () => {
    const id = registerParameter(state, {
      name: 'test_param',
      value: 3.14,
      level: 'VERIFIED',
      citation: 'Pi (∞)'
    });

    assert.ok(state.provenanceRegistry['test_param'] !== undefined);
    assert.strictEqual(state.provenanceRegistry['test_param'].value, 3.14);
    assert.strictEqual(state.provenanceRegistry['test_param'].level, 'VERIFIED');
    assert.strictEqual(state.provenanceRegistry['test_param'].citation, 'Pi (∞)');
  });

  test('registerParameter with full metadata', () => {
    registerParameter(state, {
      name: 'climate_sensitivity',
      value: 3.0,
      level: 'VERIFIED',
      citation: 'IPCC AR6 (2021)',
      source: 'doi:10.1017/9781009157896',
      citedValue: 3.0,
      confidence: 0.95,
      notes: 'Central estimate of equilibrium climate sensitivity'
    });

    const param = state.provenanceRegistry['climate_sensitivity'];
    assert.strictEqual(param.value, 3.0);
    assert.strictEqual(param.level, 'VERIFIED');
    assert.strictEqual(param.citation, 'IPCC AR6 (2021)');
    assert.strictEqual(param.source, 'doi:10.1017/9781009157896');
    assert.strictEqual(param.citedValue, 3.0);
    assert.strictEqual(param.confidence, 0.95);
    assert.ok(param.notes?.includes('equilibrium climate sensitivity'));
  });

  test('getParameter returns existing value', () => {
    registerParameter(state, {
      name: 'existing_param',
      value: 42,
      level: 'INFORMED'
    });

    const value = getParameter(state, 'existing_param', 999);
    assert.strictEqual(value, 42);
  });

  test('getParameter with fallback for missing parameter', () => {
    // Parameter doesn't exist
    const value = getParameter(state, 'missing_param', 99);
    assert.strictEqual(value, 99);

    // Auto-registers as PLACEHOLDER
    assert.ok(state.provenanceRegistry['missing_param'] !== undefined);
    assert.strictEqual(state.provenanceRegistry['missing_param'].level, 'PLACEHOLDER');
    assert.strictEqual(state.provenanceRegistry['missing_param'].value, 99);
  });

  test('getParameter with metadata auto-registration', () => {
    const value = getParameter(state, 'auto_param', 123, {
      level: 'INFORMED',
      notes: 'Auto-registered with metadata'
    });

    assert.strictEqual(value, 123);
    assert.strictEqual(state.provenanceRegistry['auto_param'].level, 'INFORMED');
    assert.ok(state.provenanceRegistry['auto_param'].notes?.includes('Auto-registered'));
  });

  test('updateParameter modifies value', () => {
    registerParameter(state, {
      name: 'update_test',
      value: 1.0,
      level: 'VERIFIED',
      citation: 'Original (2024)'
    });

    updateParameter(state, 'update_test', 2.0);

    assert.strictEqual(state.provenanceRegistry['update_test'].value, 2.0);
  });

  test('updateParameter preserves provenance metadata', () => {
    registerParameter(state, {
      name: 'param_to_update',
      value: 1.0,
      level: 'VERIFIED',
      citation: 'Original (2024)',
      citedValue: 1.0,
      confidence: 0.9
    });

    updateParameter(state, 'param_to_update', 2.0, {
      notes: 'Updated for new research'
    });

    // Value updated
    assert.strictEqual(state.provenanceRegistry['param_to_update'].value, 2.0);

    // Original metadata preserved
    assert.strictEqual(state.provenanceRegistry['param_to_update'].level, 'VERIFIED');
    assert.strictEqual(state.provenanceRegistry['param_to_update'].citation, 'Original (2024)');
    assert.strictEqual(state.provenanceRegistry['param_to_update'].citedValue, 1.0);
    assert.strictEqual(state.provenanceRegistry['param_to_update'].confidence, 0.9);

    // Notes updated
    assert.ok(state.provenanceRegistry['param_to_update'].notes?.includes('Updated'));
  });

  test('batchRegisterParameters registers multiple', () => {
    const paramCount = Object.keys(state.provenanceRegistry).length;

    batchRegisterParameters(state, {
      'batch_param_1': {
        value: 1.0,
        level: 'VERIFIED',
        citation: 'Paper A (2023)'
      },
      'batch_param_2': {
        value: 2.0,
        level: 'INFORMED',
        citation: 'Paper B (2024)'
      },
      'batch_param_3': {
        value: 3.0,
        level: 'PLACEHOLDER'
      }
    });

    assert.strictEqual(Object.keys(state.provenanceRegistry).length, paramCount + 3);
    assert.strictEqual(state.provenanceRegistry['batch_param_1'].value, 1.0);
    assert.strictEqual(state.provenanceRegistry['batch_param_2'].value, 2.0);
    assert.strictEqual(state.provenanceRegistry['batch_param_3'].value, 3.0);
  });

  test('getProvenanceSummary aggregates correctly', () => {
    // Clear registry
    state.provenanceRegistry = {};

    // Add test parameters
    registerParameter(state, { name: 'v1', value: 1, level: 'VERIFIED' });
    registerParameter(state, { name: 'v2', value: 2, level: 'VERIFIED' });
    registerParameter(state, { name: 'i1', value: 3, level: 'INFORMED' });
    registerParameter(state, { name: 'p1', value: 4, level: 'PLACEHOLDER' });

    const summary = getProvenanceSummary(state);

    assert.strictEqual(summary.total, 4);
    assert.strictEqual(summary.verified, 2);
    assert.strictEqual(summary.informed, 1);
    assert.strictEqual(summary.placeholder, 1);
  });

  test('getProvenanceSummary includes parameter names', () => {
    // Clear registry
    state.provenanceRegistry = {};

    registerParameter(state, { name: 'verified_a', value: 1, level: 'VERIFIED' });
    registerParameter(state, { name: 'verified_b', value: 2, level: 'VERIFIED' });
    registerParameter(state, { name: 'informed_a', value: 3, level: 'INFORMED' });
    registerParameter(state, { name: 'placeholder_a', value: 4, level: 'PLACEHOLDER' });

    const summary = getProvenanceSummary(state);

    assert.ok(summary.parameters.VERIFIED.includes('verified_a'));
    assert.ok(summary.parameters.VERIFIED.includes('verified_b'));
    assert.ok(summary.parameters.INFORMED.includes('informed_a'));
    assert.ok(summary.parameters.PLACEHOLDER.includes('placeholder_a'));
  });

  test('Empty registry returns zero counts', () => {
    state.provenanceRegistry = {};

    const summary = getProvenanceSummary(state);

    assert.strictEqual(summary.total, 0);
    assert.strictEqual(summary.verified, 0);
    assert.strictEqual(summary.informed, 0);
    assert.strictEqual(summary.placeholder, 0);
  });

  test('Registry persists across state mutations', () => {
    registerParameter(state, {
      name: 'persistent_param',
      value: 100,
      level: 'VERIFIED',
      citation: 'Test (2025)'
    });

    // Simulate state mutation (normal simulation operation)
    state.currentMonth++;

    // Parameter should still exist
    assert.ok(state.provenanceRegistry['persistent_param'] !== undefined);
    assert.strictEqual(state.provenanceRegistry['persistent_param'].value, 100);
  });

  test('Multiple parameters with same value but different metadata', () => {
    registerParameter(state, {
      name: 'param_A',
      value: 5.0,
      level: 'VERIFIED',
      citation: 'Source A (2020)'
    });

    registerParameter(state, {
      name: 'param_B',
      value: 5.0,
      level: 'INFORMED',
      citation: 'Source B (2021)'
    });

    // Same value, different provenance
    assert.strictEqual(state.provenanceRegistry['param_A'].value, 5.0);
    assert.strictEqual(state.provenanceRegistry['param_B'].value, 5.0);
    assert.strictEqual(state.provenanceRegistry['param_A'].level, 'VERIFIED');
    assert.strictEqual(state.provenanceRegistry['param_B'].level, 'INFORMED');
    assert.notStrictEqual(state.provenanceRegistry['param_A'].citation, state.provenanceRegistry['param_B'].citation);
  });
});
