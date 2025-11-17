/**
 * Provenance Database (Simple SQLite)
 *
 * Minimal persistence for parameter citations.
 * Uses SQLite (no external database required).
 */

import Database from 'better-sqlite3';
import path from 'path';
import { existsSync, mkdirSync } from 'fs';
import type {
  ParameterProvenance,
  ProvenanceRecord,
  ProvenanceLevel,
} from '../types/provenance';

/**
 * Simple SQLite database for provenance tracking
 */
export class ProvenanceDatabase {
  private db: Database.Database;

  constructor(dbPath?: string) {
    // Default: .cache/provenance.db
    const defaultPath = path.join(process.cwd(), '.cache', 'provenance.db');
    const finalPath = dbPath || defaultPath;

    // Ensure directory exists
    const dir = path.dirname(finalPath);
    if (!existsSync(dir)) {
      mkdirSync(dir, { recursive: true });
    }

    // Open database
    this.db = new Database(finalPath);
    this.initializeSchema();
  }

  /**
   * Initialize database schema
   */
  private initializeSchema(): void {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS provenance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        parameter_name TEXT NOT NULL,
        value REAL NOT NULL,
        level TEXT NOT NULL CHECK(level IN ('PLACEHOLDER', 'INFORMED', 'VERIFIED')),
        citation TEXT,
        source TEXT,
        cited_value REAL,
        confidence REAL,
        notes TEXT,
        verified_at INTEGER NOT NULL,
        created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000)
      );

      CREATE INDEX IF NOT EXISTS idx_parameter_name ON provenance(parameter_name);
      CREATE INDEX IF NOT EXISTS idx_level ON provenance(level);
      CREATE INDEX IF NOT EXISTS idx_verified_at ON provenance(verified_at);
    `);
  }

  /**
   * Save provenance record (uses millisecond-precision timestamps)
   */
  public saveProvenance(provenance: ParameterProvenance): number {
    const stmt = this.db.prepare(`
      INSERT INTO provenance (
        parameter_name, value, level, citation, source,
        cited_value, confidence, notes, verified_at, created_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);

    const now = Date.now();
    const result = stmt.run(
      provenance.name,
      provenance.value,
      provenance.level,
      provenance.citation || null,
      provenance.source || null,
      provenance.citedValue || null,
      provenance.confidence || null,
      provenance.notes || null,
      provenance.lastVerified || now,
      now // Explicit millisecond-precision timestamp
    );

    return result.lastInsertRowid as number;
  }

  /**
   * Get latest provenance for a parameter
   */
  public getLatestProvenance(parameterName: string): ParameterProvenance | null {
    const stmt = this.db.prepare(`
      SELECT * FROM provenance
      WHERE parameter_name = ?
      ORDER BY created_at DESC
      LIMIT 1
    `);

    const row = stmt.get(parameterName) as any;
    if (!row) {
      return null;
    }

    return this.rowToProvenance(row);
  }

  /**
   * Get all provenance records for a parameter (chronological order, oldest first)
   */
  public getProvenanceHistory(parameterName: string): ParameterProvenance[] {
    const stmt = this.db.prepare(`
      SELECT * FROM provenance
      WHERE parameter_name = ?
      ORDER BY created_at ASC
    `);

    const rows = stmt.all(parameterName) as any[];
    return rows.map((row) => this.rowToProvenance(row));
  }

  /**
   * Get all parameters by level
   */
  public getParametersByLevel(level: ProvenanceLevel): ParameterProvenance[] {
    const stmt = this.db.prepare(`
      SELECT * FROM provenance
      WHERE level = ?
      GROUP BY parameter_name
      HAVING created_at = MAX(created_at)
      ORDER BY parameter_name
    `);

    const rows = stmt.all(level) as any[];
    return rows.map((row) => this.rowToProvenance(row));
  }

  /**
   * Get statistics (returns 0 for empty database, not NULL)
   */
  public getStats(): {
    total: number;
    placeholder: number;
    informed: number;
    verified: number;
  } {
    const stmt = this.db.prepare(`
      SELECT
        COUNT(DISTINCT parameter_name) as total,
        COALESCE(SUM(CASE WHEN level = 'PLACEHOLDER' THEN 1 ELSE 0 END), 0) as placeholder,
        COALESCE(SUM(CASE WHEN level = 'INFORMED' THEN 1 ELSE 0 END), 0) as informed,
        COALESCE(SUM(CASE WHEN level = 'VERIFIED' THEN 1 ELSE 0 END), 0) as verified
      FROM (
        SELECT parameter_name, level
        FROM provenance
        GROUP BY parameter_name
        HAVING created_at = MAX(created_at)
      )
    `);

    return stmt.get() as any;
  }

  /**
   * Convert database row to ParameterProvenance
   */
  private rowToProvenance(row: any): ParameterProvenance {
    return {
      name: row.parameter_name,
      value: row.value,
      level: row.level as ProvenanceLevel,
      citation: row.citation || undefined,
      source: row.source || undefined,
      citedValue: row.cited_value || undefined,
      confidence: row.confidence || undefined,
      notes: row.notes || undefined,
      lastVerified: row.verified_at,
    };
  }

  /**
   * Close database connection
   */
  public close(): void {
    this.db.close();
  }
}

/**
 * Singleton instance
 */
let _dbInstance: ProvenanceDatabase | null = null;

export function getProvenanceDatabase(): ProvenanceDatabase {
  if (!_dbInstance) {
    _dbInstance = new ProvenanceDatabase();
  }
  return _dbInstance;
}
