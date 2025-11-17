/**
 * Citation Verification Utility
 *
 * Minimal wrapper around existing Python citation verification tools.
 * Provides TypeScript interface to:
 * - CitationChecker.py (verify against database)
 * - verifyCitationWithAutoResearch.py (auto-research unverified)
 *
 * Design Philosophy: Build on existing infrastructure, don't reinvent.
 */

import { execSync } from 'child_process';
import { existsSync } from 'fs';
import path from 'path';

/**
 * Citation verification result
 */
export interface CitationVerificationResult {
  citation: string;
  verified: boolean;
  confidence: number; // 0-1
  source?: string; // File path or DOI
  suspicious: boolean;
  originalText: string;
}

/**
 * Verification summary
 */
export interface VerificationSummary {
  citationsFound: number;
  verified: number;
  unverified: number;
  suspicious: number;
  results: CitationVerificationResult[];
}

/**
 * Simple citation verifier using existing Python tools
 */
export class CitationVerifier {
  private scriptsDir: string;
  private citationCheckerPath: string;
  private autoResearchPath: string;

  constructor(repoRoot: string = process.cwd()) {
    this.scriptsDir = path.join(repoRoot, 'scripts');
    this.citationCheckerPath = path.join(this.scriptsDir, 'citationChecker.py');
    this.autoResearchPath = path.join(this.scriptsDir, 'verifyCitationWithAutoResearch.py');

    // Validate scripts exist
    if (!existsSync(this.citationCheckerPath)) {
      throw new Error(`❌ Citation checker not found: ${this.citationCheckerPath}`);
    }
    if (!existsSync(this.autoResearchPath)) {
      throw new Error(`❌ Auto-research script not found: ${this.autoResearchPath}`);
    }
  }

  /**
   * Verify citations in text (quick check against database)
   *
   * @param text - Text containing citations
   * @returns Verification summary
   */
  public verifyCitations(text: string): VerificationSummary {
    try {
      // Call Python citation checker (with --json flag)
      const result = execSync(
        `python3 "${this.citationCheckerPath}" --json --text "${this.escapeBash(text)}"`,
        {
          cwd: this.scriptsDir,
          encoding: 'utf-8',
          maxBuffer: 10 * 1024 * 1024, // 10MB buffer
        }
      );

      // Parse JSON response
      const parsed = JSON.parse(result);

      return {
        citationsFound: parsed.citations_found || 0,
        verified: parsed.verified || 0,
        unverified: parsed.unverified || 0,
        suspicious: parsed.suspicious || 0,
        results: (parsed.results || []).map((r: any) => ({
          citation: r.citation,
          verified: r.verified,
          confidence: r.verified ? 1.0 : 0.0,
          source: r.source,
          suspicious: r.suspicious || false,
          originalText: r.original_text,
        })),
      };
    } catch (error) {
      console.error('❌ Citation verification failed:', error);
      throw new Error(`Citation verification failed: ${error}`);
    }
  }

  /**
   * Verify with auto-research (searches for unverified citations)
   *
   * @param text - Text containing citations
   * @param autoResearch - If true, auto-search for unverified (default: true)
   * @param downloadPDFs - If true, download PDFs (default: false)
   * @returns Verification summary with research results
   */
  public async verifyWithResearch(
    text: string,
    autoResearch: boolean = true,
    downloadPDFs: boolean = false
  ): Promise<VerificationSummary> {
    try {
      // Build command (with --json flag)
      const cmd = [
        `python3 "${this.autoResearchPath}"`,
        `--json`,
        `--text "${this.escapeBash(text)}"`,
        autoResearch ? '' : '--no-auto-research',
        downloadPDFs ? '--download-pdfs' : '',
      ]
        .filter(Boolean)
        .join(' ');

      // Execute (async via Promise wrapper)
      const result = await this.execAsync(cmd, {
        cwd: this.scriptsDir,
        maxBuffer: 10 * 1024 * 1024,
      });

      // Parse JSON response
      const parsed = JSON.parse(result);

      return {
        citationsFound: parsed.citations_found || 0,
        verified: parsed.verified || 0,
        unverified: parsed.unverified || 0,
        suspicious: parsed.suspicious || 0,
        results: (parsed.results || []).map((r: any) => ({
          citation: r.citation,
          verified: r.verified,
          confidence: r.confidence || (r.verified ? 1.0 : 0.0),
          source: r.source,
          suspicious: r.suspicious || false,
          originalText: r.original_text,
        })),
      };
    } catch (error) {
      console.error('❌ Citation research failed:', error);
      throw new Error(`Citation research failed: ${error}`);
    }
  }

  /**
   * Verify a single parameter citation
   *
   * @param paramName - Parameter name
   * @param value - Parameter value
   * @param citation - Citation text (e.g., "Smith et al. (2023)")
   * @returns Verification result
   */
  public async verifyParameterCitation(
    paramName: string,
    value: number,
    citation: string
  ): Promise<CitationVerificationResult> {
    const text = `Parameter ${paramName}=${value} from ${citation}`;
    const summary = await this.verifyWithResearch(text, true, false);

    if (summary.results.length === 0) {
      return {
        citation,
        verified: false,
        confidence: 0,
        suspicious: false,
        originalText: text,
      };
    }

    return summary.results[0];
  }

  /**
   * Escape bash special characters
   */
  private escapeBash(str: string): string {
    return str.replace(/"/g, '\\"').replace(/\$/g, '\\$').replace(/`/g, '\\`');
  }

  /**
   * Async wrapper for execSync
   */
  private execAsync(
    command: string,
    options: any
  ): Promise<string> {
    return new Promise((resolve, reject) => {
      try {
        const result = execSync(command, {
          ...options,
          encoding: 'utf-8',
        });
        resolve(result);
      } catch (error) {
        reject(error);
      }
    });
  }
}

/**
 * Singleton instance for convenience
 */
let _verifierInstance: CitationVerifier | null = null;

export function getCitationVerifier(): CitationVerifier {
  if (!_verifierInstance) {
    _verifierInstance = new CitationVerifier();
  }
  return _verifierInstance;
}
