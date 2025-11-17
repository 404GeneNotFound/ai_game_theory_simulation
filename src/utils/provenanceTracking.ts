/**
 * Provenance Tracking Utilities
 *
 * Helper functions for tracking parameter citations in the simulation.
 * Makes it easy to declare provenance at point of use.
 *
 * Week 3-4 (Nov 17, 2025)
 */

import type { GameState } from '@/types/game';
import type { ParameterProvenance, ProvenanceLevel } from '@/types/provenance';

/**
 * Register a parameter with its provenance
 *
 * @example
 * ```typescript
 * // PLACEHOLDER parameter (needs verification)
 * const cascadeAmp = registerParameter(state, {
 *   name: 'cascade_amplification_factor',
 *   value: 1.8,
 *   level: 'PLACEHOLDER',
 *   notes: 'Engineering estimate, needs verification'
 * });
 *
 * // VERIFIED parameter (from research)
 * const temp_sensitivity = registerParameter(state, {
 *   name: 'climate_sensitivity',
 *   value: 3.0,
 *   level: 'VERIFIED',
 *   citation: 'IPCC AR6 (2021)',
 *   source: 'doi:10.1017/9781009157896',
 *   citedValue: 3.0,
 *   confidence: 0.95,
 *   notes: 'Equilibrium climate sensitivity (ECS)'
 * });
 * ```
 */
export function registerParameter(
  state: GameState,
  provenance: ParameterProvenance
): number {
  // Initialize registry if needed
  if (!state.provenanceRegistry) {
    state.provenanceRegistry = {};
  }

  // Add timestamp if not provided
  if (!provenance.lastVerified) {
    provenance.lastVerified = Date.now();
  }

  // Register or update
  state.provenanceRegistry[provenance.name] = provenance;

  // Return value for convenient inline use
  return provenance.value;
}

/**
 * Get parameter value with provenance tracking
 *
 * If parameter not registered, logs warning and registers as PLACEHOLDER.
 *
 * @example
 * ```typescript
 * const cascadeAmp = getParameter(state, 'cascade_amplification_factor', 1.8, {
 *   citation: 'Richardson et al. (2023)',
 *   level: 'VERIFIED'
 * });
 * ```
 */
export function getParameter(
  state: GameState,
  name: string,
  defaultValue: number,
  metadata?: Partial<ParameterProvenance>
): number {
  // Initialize registry if needed
  if (!state.provenanceRegistry) {
    state.provenanceRegistry = {};
  }

  const existing = state.provenanceRegistry[name];

  if (existing) {
    return existing.value;
  }

  // Not registered - create PLACEHOLDER
  const level: ProvenanceLevel = metadata?.level || 'PLACEHOLDER';

  console.warn(
    `⚠️ Parameter "${name}" not registered. Creating ${level} entry with value ${defaultValue}`
  );

  const provenance: ParameterProvenance = {
    name,
    value: defaultValue,
    level,
    citation: metadata?.citation,
    source: metadata?.source,
    citedValue: metadata?.citedValue,
    confidence: metadata?.confidence,
    notes: metadata?.notes || 'Auto-registered on first use',
    lastVerified: Date.now(),
  };

  state.provenanceRegistry[name] = provenance;

  return defaultValue;
}

/**
 * Update parameter value (with drift check)
 *
 * @example
 * ```typescript
 * updateParameter(state, 'cascade_amplification_factor', 2.0, {
 *   notes: 'Updated based on new simulation results'
 * });
 * ```
 */
export function updateParameter(
  state: GameState,
  name: string,
  newValue: number,
  metadata?: Partial<ParameterProvenance>
): void {
  if (!state.provenanceRegistry) {
    state.provenanceRegistry = {};
  }

  const existing = state.provenanceRegistry[name];

  if (!existing) {
    console.warn(
      `⚠️ Updating unregistered parameter "${name}". Consider using registerParameter() first.`
    );

    state.provenanceRegistry[name] = {
      name,
      value: newValue,
      level: 'PLACEHOLDER',
      notes: 'Created via updateParameter',
      lastVerified: Date.now(),
      ...metadata,
    };
    return;
  }

  // Update value
  existing.value = newValue;

  // Update metadata if provided
  if (metadata) {
    if (metadata.level) existing.level = metadata.level;
    if (metadata.citation) existing.citation = metadata.citation;
    if (metadata.source) existing.source = metadata.source;
    if (metadata.citedValue !== undefined) existing.citedValue = metadata.citedValue;
    if (metadata.confidence !== undefined) existing.confidence = metadata.confidence;
    if (metadata.notes) existing.notes = metadata.notes;
  }
}

/**
 * Batch register parameters from an object
 *
 * Convenient for initializing multiple parameters at once.
 *
 * @example
 * ```typescript
 * batchRegisterParameters(state, {
 *   climate_sensitivity: {
 *     value: 3.0,
 *     level: 'VERIFIED',
 *     citation: 'IPCC AR6 (2021)',
 *     citedValue: 3.0
 *   },
 *   cascade_amplification: {
 *     value: 1.8,
 *     level: 'PLACEHOLDER',
 *     notes: 'Needs verification'
 *   }
 * });
 * ```
 */
export function batchRegisterParameters(
  state: GameState,
  parameters: Record<string, Omit<ParameterProvenance, 'name'>>
): void {
  for (const [name, metadata] of Object.entries(parameters)) {
    registerParameter(state, {
      name,
      ...metadata,
    });
  }
}

/**
 * Get provenance summary for reporting
 */
export function getProvenanceSummary(state: GameState): {
  total: number;
  placeholder: number;
  informed: number;
  verified: number;
  parameters: Record<ProvenanceLevel, string[]>;
} {
  if (!state.provenanceRegistry) {
    return {
      total: 0,
      placeholder: 0,
      informed: 0,
      verified: 0,
      parameters: { PLACEHOLDER: [], INFORMED: [], VERIFIED: [] },
    };
  }

  const params = Object.values(state.provenanceRegistry);

  return {
    total: params.length,
    placeholder: params.filter((p) => p.level === 'PLACEHOLDER').length,
    informed: params.filter((p) => p.level === 'INFORMED').length,
    verified: params.filter((p) => p.level === 'VERIFIED').length,
    parameters: {
      PLACEHOLDER: params.filter((p) => p.level === 'PLACEHOLDER').map((p) => p.name),
      INFORMED: params.filter((p) => p.level === 'INFORMED').map((p) => p.name),
      VERIFIED: params.filter((p) => p.level === 'VERIFIED').map((p) => p.name),
    },
  };
}
