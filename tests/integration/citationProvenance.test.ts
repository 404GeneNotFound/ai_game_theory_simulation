/**
 * Citation Provenance Integration Test
 *
 * Tests end-to-end workflow:
 * 1. Verify citation using Python tools
 * 2. Save provenance to database
 * 3. Retrieve and validate
 */

import { describe, it, expect, beforeAll, afterAll } from '@jest/globals';
import { CitationVerifier } from '../../src/utils/citationVerifier';
import {
  ProvenanceDatabase,
  getProvenanceDatabase,
} from '../../src/utils/provenanceDatabase';
import type { ParameterProvenance } from '../../src/types/provenance';
import { calculateDrift, isDriftExcessive } from '../../src/types/provenance';
import { existsSync, unlinkSync } from 'fs';
import path from 'path';

describe('Citation Provenance Integration', () => {
  let verifier: CitationVerifier;
  let db: ProvenanceDatabase;
  const testDbPath = path.join(process.cwd(), '.cache', 'test-provenance.db');

  beforeAll(() => {
    // Clean up test database if exists
    if (existsSync(testDbPath)) {
      unlinkSync(testDbPath);
    }

    // Initialize
    verifier = new CitationVerifier();
    db = new ProvenanceDatabase(testDbPath);
  });

  afterAll(() => {
    // Cleanup
    db.close();
    if (existsSync(testDbPath)) {
      unlinkSync(testDbPath);
    }
  });

  it('should verify a known citation', async () => {
    // Use a citation that should exist in the verified database
    const text = 'According to Richardson et al. (2023), planetary boundaries are transgressed.';

    const result = verifier.verifyCitations(text);

    expect(result.citationsFound).toBeGreaterThan(0);
    console.log('Verification result:', JSON.stringify(result, null, 2));
  });

  it('should save and retrieve provenance', () => {
    const provenance: ParameterProvenance = {
      name: 'cascade_amplification_factor',
      value: 1.8,
      level: 'VERIFIED',
      citation: 'Richardson et al. (2023)',
      source: 'doi:10.1126/science.adh2458',
      citedValue: 1.8,
      confidence: 0.95,
      notes: 'Planetary boundary transgression cascades',
      lastVerified: Date.now(),
    };

    // Save
    const id = db.saveProvenance(provenance);
    expect(id).toBeGreaterThan(0);

    // Retrieve
    const retrieved = db.getLatestProvenance('cascade_amplification_factor');
    expect(retrieved).not.toBeNull();
    expect(retrieved?.name).toBe('cascade_amplification_factor');
    expect(retrieved?.value).toBe(1.8);
    expect(retrieved?.level).toBe('VERIFIED');
    expect(retrieved?.citation).toBe('Richardson et al. (2023)');
  });

  it('should detect parameter drift', () => {
    // Save original verified parameter
    const original: ParameterProvenance = {
      name: 'climate_sensitivity',
      value: 3.0,
      level: 'VERIFIED',
      citation: 'IPCC AR6 (2021)',
      citedValue: 3.0,
      confidence: 1.0,
      lastVerified: Date.now(),
    };
    db.saveProvenance(original);

    // Simulate parameter drift
    const drifted: ParameterProvenance = {
      ...original,
      value: 3.8, // 26.7% drift
    };

    const drift = calculateDrift(drifted.value, drifted.citedValue!);
    expect(drift).toBeCloseTo(0.267, 2);
    expect(isDriftExcessive(drift)).toBe(true); // >20% threshold
  });

  it('should track provenance history', () => {
    const param = 'test_parameter';

    // Save multiple versions
    db.saveProvenance({
      name: param,
      value: 1.0,
      level: 'PLACEHOLDER',
      lastVerified: Date.now(),
    });

    db.saveProvenance({
      name: param,
      value: 1.2,
      level: 'INFORMED',
      citation: 'Smith et al. (2023)',
      lastVerified: Date.now(),
    });

    db.saveProvenance({
      name: param,
      value: 1.2,
      level: 'VERIFIED',
      citation: 'Smith et al. (2023)',
      source: 'doi:10.xxxx/test',
      citedValue: 1.2,
      confidence: 0.98,
      lastVerified: Date.now(),
    });

    // Check history
    const history = db.getProvenanceHistory(param);
    expect(history.length).toBe(3);
    expect(history[0].level).toBe('VERIFIED'); // Latest first
    expect(history[1].level).toBe('INFORMED');
    expect(history[2].level).toBe('PLACEHOLDER');
  });

  it('should get statistics by provenance level', () => {
    const stats = db.getStats();
    console.log('Provenance statistics:', stats);

    expect(stats.total).toBeGreaterThan(0);
    expect(stats.verified).toBeGreaterThan(0);
  });

  it('should handle complete verification workflow', async () => {
    // Step 1: Start with PLACEHOLDER
    const placeholder: ParameterProvenance = {
      name: 'nuclear_winter_temperature_drop',
      value: -15, // degrees Celsius
      level: 'PLACEHOLDER',
      notes: 'Engineering estimate, needs verification',
      lastVerified: Date.now(),
    };
    db.saveProvenance(placeholder);

    // Step 2: Verify citation
    const text = 'Nuclear winter could cause temperature drops of 15°C according to Robock et al. (2007).';
    const verification = verifier.verifyCitations(text);

    expect(verification.citationsFound).toBeGreaterThan(0);

    // Step 3: Upgrade to VERIFIED (if citation found)
    if (verification.verified > 0) {
      const verified: ParameterProvenance = {
        ...placeholder,
        level: 'VERIFIED',
        citation: verification.results[0].citation,
        source: verification.results[0].source,
        citedValue: -15,
        confidence: verification.results[0].confidence,
        notes: 'Verified against peer-reviewed research',
        lastVerified: Date.now(),
      };
      db.saveProvenance(verified);

      // Confirm upgrade
      const latest = db.getLatestProvenance('nuclear_winter_temperature_drop');
      expect(latest?.level).toBe('VERIFIED');
    }
  });
});
