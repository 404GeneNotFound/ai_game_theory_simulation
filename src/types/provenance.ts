/**
 * Provenance Tracking Types
 *
 * Simple, minimal types for tracking parameter citations.
 * No over-engineering - just what's needed to prevent citation drift.
 */

/**
 * Provenance confidence level (matches Nested Learning hierarchy)
 */
export type ProvenanceLevel =
  | 'PLACEHOLDER' // Level 0: Engineering guess, needs verification
  | 'INFORMED' // Level 1: Research-backed estimate
  | 'VERIFIED'; // Level 2: Peer-reviewed citation

/**
 * Parameter provenance metadata
 */
export interface ParameterProvenance {
  /** Parameter name (e.g., "cascade_amplification_factor") */
  name: string;

  /** Current value */
  value: number;

  /** Provenance level */
  level: ProvenanceLevel;

  /** Citation (e.g., "Smith et al. (2023)") */
  citation?: string;

  /** DOI or file path to paper */
  source?: string;

  /** Cited value from paper (for drift detection) */
  citedValue?: number;

  /** When this was last verified */
  lastVerified?: number; // timestamp

  /** Confidence (0-1) from verification system */
  confidence?: number;

  /** Justification/notes */
  notes?: string;
}

/**
 * Verification result for a parameter
 */
export interface ParameterVerificationResult {
  parameter: string;
  verified: boolean;
  confidence: number;
  citation?: string;
  source?: string;
  drift?: number; // |current - cited| / cited
  suspicious: boolean;
  message: string;
}

/**
 * Provenance database entry (for persistence)
 */
export interface ProvenanceRecord {
  id?: number; // Auto-increment primary key
  parameterName: string;
  value: number;
  level: ProvenanceLevel;
  citation: string | null;
  source: string | null;
  citedValue: number | null;
  confidence: number | null;
  notes: string | null;
  verifiedAt: number; // timestamp
  createdAt: number; // timestamp
}

/**
 * Simple helper to check if parameter needs verification
 */
export function needsVerification(provenance: ParameterProvenance): boolean {
  // PLACEHOLDER always needs verification
  if (provenance.level === 'PLACEHOLDER') {
    return true;
  }

  // INFORMED should be verified periodically (every 30 days)
  if (provenance.level === 'INFORMED') {
    if (!provenance.lastVerified) {
      return true;
    }
    const daysSinceVerification =
      (Date.now() - provenance.lastVerified) / (1000 * 60 * 60 * 24);
    return daysSinceVerification > 30;
  }

  // VERIFIED should be checked for drift periodically (every 90 days)
  if (provenance.level === 'VERIFIED') {
    if (!provenance.lastVerified) {
      return true;
    }
    const daysSinceVerification =
      (Date.now() - provenance.lastVerified) / (1000 * 60 * 60 * 24);
    return daysSinceVerification > 90;
  }

  return false;
}

/**
 * Calculate drift from cited value
 */
export function calculateDrift(
  current: number,
  cited: number
): number {
  if (cited === 0) {
    return current === 0 ? 0 : Infinity;
  }
  return Math.abs(current - cited) / cited;
}

/**
 * Check if drift exceeds warning threshold
 */
export function isDriftExcessive(drift: number): boolean {
  return drift > 0.2; // 20% drift = warning threshold
}
