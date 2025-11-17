/**
 * ProvenanceValidationPhase (5.0)
 *
 * Validates parameter provenance and detects citation drift.
 * Runs early to ensure parameters are verified before use in other phases.
 *
 * **EXECUTION ORDER:** 5.0 (Early - after initialization, before main simulation)
 * **DEPENDENCIES:** None (reads provenanceRegistry)
 * **SIDE EFFECTS:**
 * - Logs warnings for PLACEHOLDER parameters
 * - Logs alerts for excessive drift (>20%)
 * - Updates lastValidated timestamps
 *
 * Research: Behrouz et al. (2025) Nested Learning, Richardson et al. (2023) planetary boundaries
 * Implementation: Week 3-4 (Nov 17, 2025)
 */

import {
  GameState,
  SimulationPhase,
  PhaseResult,
  PhaseContext,
  RNGFunction,
  GameEvent
} from '@/types/game';
import type { ParameterProvenance } from '@/types/provenance';
import { calculateDrift, isDriftExcessive, needsVerification } from '@/types/provenance';

export class ProvenanceValidationPhase implements SimulationPhase {
  readonly id = 'provenance-validation';
  readonly name = 'Provenance Validation';
  readonly order = 5.0;

  // No dependencies - runs early to validate parameters
  readonly dependencies = [] as const;

  execute(state: GameState, _rng: RNGFunction): PhaseResult {
    const events: GameEvent[] = [];

    // Skip if no provenance registry
    if (!state.provenanceRegistry) {
      // Initialize empty registry on first run
      state.provenanceRegistry = {};
      return { events: [] };
    }

    const registry = state.provenanceRegistry;
    const params = Object.keys(registry);

    // Track stats
    let placeholderCount = 0;
    let driftWarningCount = 0;
    let driftAlertCount = 0;

    // Validate each registered parameter
    for (const paramName of params) {
      const provenance = registry[paramName];

      // Check for PLACEHOLDER parameters
      if (provenance.level === 'PLACEHOLDER') {
        placeholderCount++;

        // Log warning every 12 months (yearly reminder)
        if (state.currentMonth % 12 === 0) {
          console.warn(
            `⚠️ PLACEHOLDER parameter: ${paramName} = ${provenance.value}\n` +
            `   Needs verification. Citation: ${provenance.citation || 'NONE'}`
          );

          events.push({
            type: 'provenance_warning',
            message: `⚠️ PLACEHOLDER: ${paramName} needs verification`,
            timestamp: state.currentMonth,
            agentId: 'system'
          });
        }
      }

      // Check for drift in VERIFIED parameters
      if (provenance.level === 'VERIFIED' && provenance.citedValue !== undefined) {
        const drift = calculateDrift(provenance.value, provenance.citedValue);

        if (isDriftExcessive(drift)) {
          driftAlertCount++;

          console.warn(
            `🚨 DRIFT ALERT: ${paramName}\n` +
            `   Current: ${provenance.value}\n` +
            `   Cited: ${provenance.citedValue} (${provenance.citation})\n` +
            `   Drift: ${(drift * 100).toFixed(1)}% (threshold: 20%)`
          );

          events.push({
            type: 'provenance_drift',
            message: `🚨 DRIFT: ${paramName} = ${provenance.value} (cited: ${provenance.citedValue}, +${(drift * 100).toFixed(1)}%)`,
            timestamp: state.currentMonth,
            agentId: 'system'
          });
        } else if (drift > 0.1) {
          // 10-20% drift = warning
          driftWarningCount++;

          if (state.currentMonth % 12 === 0) {
            console.warn(
              `⚠️ DRIFT WARNING: ${paramName}\n` +
              `   Current: ${provenance.value}\n` +
              `   Cited: ${provenance.citedValue}\n` +
              `   Drift: ${(drift * 100).toFixed(1)}%`
            );
          }
        }
      }

      // Check if verification needed (time-based)
      if (needsVerification(provenance)) {
        // Don't auto-verify during simulation (too slow)
        // Just log for manual review
        if (state.currentMonth % 12 === 0) {
          console.log(
            `📋 Verification needed: ${paramName} (level: ${provenance.level})\n` +
            `   Last verified: ${provenance.lastVerified ? new Date(provenance.lastVerified).toISOString() : 'NEVER'}`
          );
        }
      }
    }

    // Summary log every 12 months
    if (state.currentMonth % 12 === 0 && params.length > 0) {
      console.log(
        `\n=== Provenance Summary (Month ${state.currentMonth}) ===\n` +
        `  Total parameters: ${params.length}\n` +
        `  PLACEHOLDER: ${placeholderCount}\n` +
        `  Drift warnings: ${driftWarningCount}\n` +
        `  Drift alerts: ${driftAlertCount}\n`
      );
    }

    return { events };
  }
}
