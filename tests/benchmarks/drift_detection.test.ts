/**
 * MVP-LSS-001: Drift Detection (LSS) Test Suite
 *
 * Validates Local Surprise Signal (LSS) calculation and threshold enforcement.
 *
 * LSS Formula: drift = |current - cited| / cited
 *
 * Thresholds:
 * - Warning: 20% drift
 * - Alert: 50% drift
 *
 * Week 5 Benchmark (Nov 17, 2025)
 */

import { test, describe } from 'node:test';
import assert from 'node:assert';
import { calculateDrift, isDriftExcessive } from '../../src/types/provenance';

describe('MVP-LSS-001: Drift Detection (LSS)', () => {
  test('No drift (exact match)', () => {
    const drift = calculateDrift(2.0, 2.0);
    assert.strictEqual(drift, 0.0);
    assert.strictEqual(isDriftExcessive(drift), false);
  });

  test('Acceptable drift (10%)', () => {
    const drift = calculateDrift(2.2, 2.0);
    assert.ok(Math.abs(drift - 0.1) < 0.001); // Allow floating-point tolerance
    assert.strictEqual(isDriftExcessive(drift), false);
  });

  test('Warning threshold (20%)', () => {
    const drift = calculateDrift(2.4, 2.0);
    assert.ok(Math.abs(drift - 0.2) < 0.001); // Allow floating-point tolerance
    assert.strictEqual(isDriftExcessive(drift), false); // 20% is threshold (not exceeded)
  });

  test('Just above warning threshold (20.1%)', () => {
    const drift = calculateDrift(2.402, 2.0);
    assert.ok(drift > 0.2 && drift < 0.21);
    assert.strictEqual(isDriftExcessive(drift), true); // >20% triggers warning
  });

  test('Excessive drift (25%)', () => {
    const drift = calculateDrift(2.5, 2.0);
    assert.strictEqual(drift, 0.25);
    assert.strictEqual(isDriftExcessive(drift), true); // >20% triggers warning
  });

  test('Critical drift (50%)', () => {
    const drift = calculateDrift(3.0, 2.0);
    assert.strictEqual(drift, 0.5);
    assert.strictEqual(isDriftExcessive(drift), true); // Alert level
  });

  test('Extreme drift (100%)', () => {
    const drift = calculateDrift(4.0, 2.0);
    assert.strictEqual(drift, 1.0);
    assert.strictEqual(isDriftExcessive(drift), true);
  });

  test('Negative drift (parameter decreased by 10%)', () => {
    const drift = calculateDrift(1.8, 2.0);
    assert.ok(Math.abs(drift - 0.1) < 0.001); // 10% decrease (allow tolerance)
    assert.strictEqual(isDriftExcessive(drift), false);
  });

  test('Negative drift (parameter decreased by 25%)', () => {
    const drift = calculateDrift(1.5, 2.0);
    assert.strictEqual(drift, 0.25); // 25% decrease
    assert.strictEqual(isDriftExcessive(drift), true);
  });

  test('Small values (avoiding divide-by-zero)', () => {
    const drift = calculateDrift(0.002, 0.001);
    assert.strictEqual(drift, 1.0); // 100% drift
    assert.strictEqual(isDriftExcessive(drift), true);
  });

  test('Zero cited value (edge case)', () => {
    // Should handle gracefully (or throw - depends on implementation)
    try {
      const drift = calculateDrift(1.0, 0);
      // If it returns a value, it should be Infinity or very large
      assert.ok(drift === Infinity || drift > 100);
    } catch (e) {
      // If it throws, that's also acceptable
      assert.ok(e instanceof Error);
    }
  });

  test('Both zero (edge case)', () => {
    const drift = calculateDrift(0, 0);
    // No drift if both are zero
    assert.strictEqual(drift, 0);
  });

  test('Precision: small drift percentages', () => {
    const drift = calculateDrift(2.01, 2.0);
    assert.ok(drift >= 0.004 && drift <= 0.006); // ~0.5% drift
    assert.strictEqual(isDriftExcessive(drift), false);
  });

  test('Precision: boundary testing at 20%', () => {
    // Just below threshold
    const drift1 = calculateDrift(2.399, 2.0);
    assert.ok(drift1 < 0.2);
    assert.strictEqual(isDriftExcessive(drift1), false);

    // Just above threshold
    const drift2 = calculateDrift(2.401, 2.0);
    assert.ok(drift2 > 0.2);
    assert.strictEqual(isDriftExcessive(drift2), true);
  });
});
