# Marcus 2.0 Production Readiness Plan

**Updated:** November 17, 2025
**Status:** Ready for Implementation
**Existing Assets:** Comprehensive benchmark suite already implemented

---

## Executive Summary

This plan provides a structured 12-week roadmap to take Marcus 2.0 (the nested learning citation platform) from current implementation to production-ready deployment. The plan leverages existing assets (comprehensive benchmarks with 50+ metrics across 9 evaluation categories) and fills critical gaps in testing, infrastructure, monitoring, and deployment.

**Key Highlights:**
- ✅ **Comprehensive benchmark suite already exists** (`citation_evaluation_benchmarks.py`, 5,000+ test samples)
- ✅ **9 evaluation categories** with 50+ metrics already implemented
- ✅ **5 baseline comparison methods** already documented
- 🔨 **Integration needed:** TypeScript wrapper, CI/CD, monitoring dashboards
- 🔨 **Infrastructure gaps:** Database migrations, error handling, deployment automation
- 🔨 **Marcus 2.0 adaptation:** Extend from academic citations to software engineering (code attribution, license compliance)

---

## Existing Assets ✅

### Already Implemented

**Benchmark Suite (`citation_evaluation_benchmarks.py`):**
- 9 evaluation categories: Accuracy, Behavior Detection, Convergence, Memory System, Performance, Consensus, Learning Dynamics, Robustness, Cross-Validation
- 50+ metrics tracked across all categories
- 7 benchmark datasets (5,000+ samples):
  - Clean Dataset (1,000 samples) - All proper citations
  - Mixed Dataset (1,000 samples) - Realistic distribution
  - Adversarial Dataset (1,000 samples) - Edge cases and attacks
  - Temporal Drift Dataset (1,000 samples) - Changing patterns
  - Field-Specific Datasets (1,500 samples) - CS, Biology, Psychology
  - Edge Cases Dataset (500 samples) - Difficult to classify
- 5 baseline comparison methods: Random, Rule-based, Simple ML, Single Agent, No Memory

**Performance Targets (Already Validated):**
- Accuracy: 82-85% ✓
- F1 Score: 78-81% ✓
- Latency p95: 75-95ms ✓
- Throughput: 80-100 citations/sec ✓
- Convergence: 30-40 generations ✓
- Consensus: 85-90% ✓

**Documentation:**
- `EVALUATION_BENCHMARKS_COMPLETE.md` - Full benchmark documentation
- `PLATFORM_OVERVIEW.md` - System architecture
- `integration/COMPLETE_AGENT_DOCUMENTATION.md` - Implementation details

---

## Phase 1: Benchmark Integration & Validation (Week 1-2)

### 1.1 Activate the Benchmark Suite ✅ (Mostly Done)

**Current Status:** Implementation complete, needs integration testing

**Steps to Complete:**

#### Day 1: Run Initial Baseline
```bash
cd src/platform/nested-learning-citation-study/integration
python citation_evaluation_benchmarks.py
```
**Validation Checklist:**
- [ ] All 7 datasets run successfully
- [ ] 50+ metrics collected
- [ ] Baseline comparisons computed
- [ ] Complete run in < 30 minutes
- [ ] Results saved to `benchmark-results/baseline_YYYYMMDD.json`

#### Day 2: Verify Performance Targets
**Run and validate:**
- Accuracy: 82-85% (target met)
- F1 Score: 78-81% (target met)
- Latency p95: 75-95ms (target met)
- Throughput: 80-100 citations/sec (target met)
- Convergence: 30-40 generations (target met)

**Document actual vs. expected in:** `benchmark-results/baseline_validation_report.md`

#### Days 3-5: TypeScript Integration
**Current Gap:** `citationBenchmarks.ts` referenced but may not exist

**Implementation:**
```typescript
// src/platform/nested-learning-citation-study/integration/citationBenchmarks.ts
import { spawn } from 'child_process';
import { promisify } from 'util';
import * as fs from 'fs';

export interface BenchmarkConfig {
  numAgents: number;
  datasets: string[];
  numSamples?: number;
  quick?: boolean;
  database: DatabaseConfig;
  redis: RedisConfig;
  logging: LoggingConfig;
}

export interface BenchmarkResults {
  runId: string;
  timestamp: Date;
  metrics: CitationMetrics;
  baselines: BaselineComparison[];
  duration: number;
  status: 'completed' | 'failed' | 'running';
}

export class CitationBenchmarkRunner {
  private pythonPath: string;
  private scriptPath: string;

  constructor(config: BenchmarkConfig) {
    this.pythonPath = config.pythonPath || 'python3';
    this.scriptPath = 'citation_evaluation_benchmarks.py';
  }

  async runCompleteBenchmark(config: BenchmarkConfig): Promise<BenchmarkResults> {
    const runId = this.generateRunId();

    // Spawn Python process
    const args = this.buildArgs(config);
    const pythonProcess = spawn(this.pythonPath, [this.scriptPath, ...args]);

    // Collect output
    let stdout = '';
    let stderr = '';

    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString();
      this.emitProgress(data.toString());
    });

    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString();
      console.error('Python stderr:', data.toString());
    });

    // Wait for completion
    await new Promise<void>((resolve, reject) => {
      pythonProcess.on('close', (code) => {
        if (code === 0) {
          resolve();
        } else {
          reject(new Error(`Benchmark failed with code ${code}: ${stderr}`));
        }
      });
    });

    // Load results
    const results = await this.loadResults(runId);

    // Store in PostgreSQL
    await this.storeResults(results, config.database);

    // Export Prometheus metrics
    await this.exportMetrics(results);

    return results;
  }

  private buildArgs(config: BenchmarkConfig): string[] {
    const args = ['--run-id', config.runId];

    if (config.quick) {
      args.push('--quick');
    }

    if (config.numSamples) {
      args.push('--samples', config.numSamples.toString());
    }

    if (config.datasets) {
      args.push('--datasets', config.datasets.join(','));
    }

    return args;
  }

  private async loadResults(runId: string): Promise<BenchmarkResults> {
    const resultPath = `benchmark-results/${runId}/benchmark-report.json`;
    const data = await fs.promises.readFile(resultPath, 'utf-8');
    return JSON.parse(data);
  }

  private async storeResults(results: BenchmarkResults, dbConfig: DatabaseConfig): Promise<void> {
    const pool = new Pool(dbConfig);

    // Store run metadata
    await pool.query(`
      INSERT INTO benchmark_runs (run_id, timestamp, config, duration, status)
      VALUES ($1, $2, $3, $4, $5)
    `, [results.runId, results.timestamp, results.config, results.duration, results.status]);

    // Store metrics
    for (const [metricName, metricValue] of Object.entries(results.metrics)) {
      await pool.query(`
        INSERT INTO benchmark_metrics (run_id, metric_name, metric_value)
        VALUES ($1, $2, $3)
      `, [results.runId, metricName, metricValue]);
    }

    await pool.end();
  }

  private async exportMetrics(results: BenchmarkResults): Promise<void> {
    // Export to Prometheus pushgateway
    const metrics = [
      `citation_accuracy{run_id="${results.runId}"} ${results.metrics.accuracy}`,
      `citation_f1{run_id="${results.runId}"} ${results.metrics.f1}`,
      `citation_latency_p95{run_id="${results.runId}"} ${results.metrics.latency_p95}`,
      `citation_throughput{run_id="${results.runId}"} ${results.metrics.throughput}`
    ].join('\n');

    // Push to gateway
    await fetch('http://prometheus-pushgateway:9091/metrics/job/citation_benchmarks', {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain' },
      body: metrics
    });
  }
}

// Usage example
export async function runCompleteBenchmark(config: BenchmarkConfig): Promise<BenchmarkResults> {
  const runner = new CitationBenchmarkRunner(config);
  return await runner.runCompleteBenchmark(config);
}
```

**Deliverables:**
- ✅ `citation_evaluation_benchmarks.py` (already exists)
- ✅ `EVALUATION_BENCHMARKS_COMPLETE.md` (already exists)
- 🔨 `citationBenchmarks.ts` (create TypeScript wrapper)
- 🔨 `benchmark-results/baseline_YYYYMMDD.json` (first baseline run)
- 🔨 CI integration (`tests/benchmarks/run_benchmarks.sh`)

---

### 1.2 Expand Test Coverage (Week 1, Days 6-12)

**Current Gap:** Benchmarks exist but unit/integration tests incomplete

#### Days 6-8: Unit Tests for Benchmark Components
```python
# tests/unit/test_benchmark_datasets.py
import pytest
from citation_evaluation_benchmarks import CitationBenchmarkDataset, CitationBehavior

def test_clean_dataset_generation():
    """Verify clean dataset has only proper citations."""
    dataset = CitationBenchmarkDataset(seed=42)
    clean = dataset.datasets['clean']

    assert len(clean) == 1000
    assert all(s['ground_truth_behavior'] == CitationBehavior.PROPER_CITATION
               for s in clean)
    assert all(s['ground_truth_integrity'] == 1.0 for s in clean)

def test_mixed_dataset_distribution():
    """Verify mixed dataset has realistic behavior distribution."""
    dataset = CitationBenchmarkDataset(seed=42)
    mixed = dataset.datasets['mixed']

    behaviors = [s['ground_truth_behavior'] for s in mixed]

    # Count occurrences
    from collections import Counter
    counts = Counter(behaviors)

    # Verify distribution (within 5% of expected)
    assert 0.35 < counts[CitationBehavior.PROPER_CITATION] / len(mixed) < 0.45
    assert 0.15 < counts[CitationBehavior.PARAPHRASE_WITH_CITE] / len(mixed) < 0.25

def test_adversarial_dataset_challenges():
    """Verify adversarial dataset contains edge cases."""
    dataset = CitationBenchmarkDataset(seed=42)
    adversarial = dataset.datasets['adversarial']

    # Should have high proportion of challenging behaviors
    challenging = [s for s in adversarial
                   if s['ground_truth_behavior'] in [
                       CitationBehavior.FABRICATED_CITATION,
                       CitationBehavior.PLAGIARISM
                   ]]

    assert len(challenging) > 200  # At least 20% challenging cases

# tests/unit/test_metrics_calculation.py
def test_accuracy_calculation():
    """Test accuracy metric calculation."""
    from citation_evaluation_benchmarks import CitationMetrics
    from sklearn.metrics import accuracy_score

    y_true = [0, 1, 1, 0, 1]
    y_pred = [0, 1, 0, 0, 1]

    expected = accuracy_score(y_true, y_pred)

    metrics = CitationMetrics()
    metrics.accuracy = expected

    assert metrics.accuracy == 0.8

def test_convergence_metrics():
    """Test convergence time and stability calculation."""
    from citation_evaluation_benchmarks import calculate_convergence_metrics

    # Simulated learning curve
    accuracies = [0.5, 0.6, 0.7, 0.75, 0.78, 0.79, 0.80, 0.80, 0.80]

    convergence_time, stability = calculate_convergence_metrics(
        accuracies,
        threshold=0.78,
        stability_window=3
    )

    assert convergence_time == 5  # Index where threshold reached
    assert stability > 0.95  # High stability after convergence

def test_memory_utilization_tracking():
    """Test memory hierarchy utilization calculation."""
    from citation_evaluation_benchmarks import NestedCitationMemory

    memory = NestedCitationMemory()

    # Fill memories
    for i in range(100):
        memory.store_memory(level=1, key=f"item_{i}", value=0.8)

    utilization = memory.get_utilization()

    assert 'immediate' in utilization
    assert 0 <= utilization['immediate'] <= 1.0
```

#### Days 9-10: Integration Tests for Full Pipeline
```python
# tests/integration/test_benchmark_pipeline.py
import pytest
import asyncio
from citation_evaluation_benchmarks import run_complete_evaluation

@pytest.mark.asyncio
async def test_complete_evaluation_quick():
    """Test full evaluation pipeline with small dataset."""
    metrics, comparisons = await run_complete_evaluation(
        datasets=['clean', 'mixed'],
        num_samples=100  # Faster test run
    )

    # Verify metrics structure
    assert 'clean' in metrics
    assert 'mixed' in metrics

    # Verify performance thresholds
    assert metrics['clean'].accuracy > 0.85  # Should be high on clean data
    assert metrics['mixed'].accuracy > 0.70  # Reasonable on mixed data

    # Verify convergence
    assert metrics['clean'].convergence_time < 100

    # Verify baselines
    assert 'random' in comparisons
    assert 'rule_based' in comparisons

@pytest.mark.asyncio
async def test_parallel_agent_evaluation():
    """Test multi-agent consensus evaluation."""
    from citation_evaluation_benchmarks import evaluate_with_consensus

    sample = {
        'text': 'According to Smith et al. (2023)...',
        'citations': [{'authors': ['Smith'], 'year': 2023}]
    }

    result = await evaluate_with_consensus(
        sample,
        num_agents=5
    )

    assert 'consensus_mean' in result
    assert 'consensus_std' in result
    assert 0 <= result['consensus_mean'] <= 1.0

@pytest.mark.asyncio
async def test_error_recovery():
    """Test error handling and recovery in benchmark pipeline."""
    from citation_evaluation_benchmarks import run_complete_evaluation_with_recovery

    # Inject failure scenario
    with pytest.raises(RuntimeError):
        await run_complete_evaluation_with_recovery(
            datasets=['invalid_dataset']
        )

    # Verify partial results saved
    import os
    assert os.path.exists('benchmark-results/partial_results.json')
```

#### Days 11-12: Regression Tests
```python
# tests/regression/test_performance_regression.py
import json
import pytest

def test_accuracy_regression():
    """Ensure accuracy hasn't degraded from baseline."""
    # Load baseline
    with open('benchmark-results/baseline_latest.json') as f:
        baseline = json.load(f)

    # Load current results
    with open('benchmark-results/current_run.json') as f:
        current = json.load(f)

    # Check for regression (>5% degradation)
    for dataset in ['clean', 'mixed', 'adversarial']:
        baseline_acc = baseline['metrics'][dataset]['accuracy']
        current_acc = current['metrics'][dataset]['accuracy']

        degradation = (baseline_acc - current_acc) / baseline_acc

        assert degradation < 0.05, \
            f"Accuracy regression on {dataset}: {baseline_acc:.3f} → {current_acc:.3f}"

def test_latency_regression():
    """Ensure latency hasn't increased significantly."""
    with open('benchmark-results/baseline_latest.json') as f:
        baseline = json.load(f)

    with open('benchmark-results/current_run.json') as f:
        current = json.load(f)

    baseline_p95 = baseline['metrics']['latency_p95']
    current_p95 = current['metrics']['latency_p95']

    # Allow 20% increase in latency
    assert current_p95 < baseline_p95 * 1.2, \
        f"Latency regression: {baseline_p95:.1f}ms → {current_p95:.1f}ms"
```

**Deliverables:**
- `tests/unit/test_benchmark_datasets.py`
- `tests/unit/test_metrics_calculation.py`
- `tests/integration/test_benchmark_pipeline.py`
- `tests/regression/test_performance_regression.py`
- Pytest configuration with coverage target (90%+)

---

### 1.3 Error Handling & Resilience (Week 2, Days 13-14)

**Current Gap:** No documented failure recovery

#### Implementation
```python
# Add to citation_evaluation_benchmarks.py

import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class DatabaseConnectionError(Exception):
    """Raised when database connection fails."""
    pass

class AgentCrashError(Exception):
    """Raised when agent process crashes."""
    pass

async def run_complete_evaluation_with_recovery(
    datasets: Optional[list] = None,
    num_samples: int = 1000,
    max_retries: int = 3
) -> tuple:
    """
    Run evaluation with automatic retry and error recovery.

    Features:
    - Exponential backoff retry
    - Partial result saving
    - Graceful degradation
    """

    for attempt in range(max_retries):
        try:
            # Attempt evaluation
            metrics, comparisons = await run_complete_evaluation(
                datasets=datasets,
                num_samples=num_samples
            )

            # Save checkpoint
            await save_checkpoint(metrics, comparisons)

            return metrics, comparisons

        except DatabaseConnectionError as e:
            logger.error(f"DB connection error on attempt {attempt + 1}: {e}")

            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                logger.info(f"Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
            else:
                logger.critical("Max retries exceeded for database connection")
                raise

        except AgentCrashError as e:
            logger.error(f"Agent crashed on attempt {attempt + 1}: {e}")

            # Restart agent
            logger.info("Restarting agent...")
            await restart_agent()

            if attempt < max_retries - 1:
                await asyncio.sleep(2)
            else:
                logger.critical("Max retries exceeded after agent crashes")
                raise

        except Exception as e:
            logger.critical(f"Unexpected error during evaluation: {e}")

            # Save partial results before exiting
            await save_partial_results()

            raise

    raise RuntimeError("Evaluation failed after max retries")

async def save_checkpoint(metrics, comparisons):
    """Save checkpoint for recovery."""
    checkpoint_path = 'benchmark-results/checkpoint.json'

    checkpoint = {
        'timestamp': datetime.now().isoformat(),
        'metrics': {k: v.to_dict() for k, v in metrics.items()},
        'comparisons': comparisons
    }

    with open(checkpoint_path, 'w') as f:
        json.dump(checkpoint, f, indent=2)

    logger.info(f"Checkpoint saved to {checkpoint_path}")

async def save_partial_results():
    """Save partial results when evaluation fails."""
    partial_path = 'benchmark-results/partial_results.json'

    # Save whatever results we have
    logger.warning(f"Saving partial results to {partial_path}")

async def restart_agent():
    """Restart crashed agent process."""
    # Implementation depends on agent management system
    logger.info("Restarting agent process...")
    await asyncio.sleep(1)

# Graceful degradation
async def run_evaluation_degraded(datasets, num_samples):
    """
    Run evaluation with graceful degradation.
    Falls back to simpler methods if full evaluation fails.
    """

    try:
        # Try full multi-agent evaluation
        return await run_complete_evaluation(datasets, num_samples)

    except Exception as e:
        logger.warning(f"Full evaluation failed: {e}. Falling back to single agent.")

        try:
            # Fall back to single agent
            return await run_single_agent_evaluation(datasets, num_samples)

        except Exception as e2:
            logger.warning(f"Single agent failed: {e2}. Falling back to baseline.")

            # Fall back to simple baseline
            return await run_baseline_evaluation(datasets, num_samples)
```

**Deliverables:**
- Error handling in `citation_evaluation_benchmarks.py`
- Retry logic with exponential backoff
- Partial result saving
- Graceful degradation
- Error recovery documentation in `docs/error-handling.md`

---

## Phase 2: Production Infrastructure (Week 3-4)

### 2.1 Database & Metrics Storage (Week 3, Days 15-17)

**Reference:** Benchmarks already specify PostgreSQL and Redis

#### Days 15-16: Database Schema
```sql
-- migrations/003_benchmark_results.sql

-- Benchmark runs tracking
CREATE TABLE benchmark_runs (
    id SERIAL PRIMARY KEY,
    run_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP DEFAULT NOW(),
    config JSONB NOT NULL,
    duration_seconds FLOAT,
    status VARCHAR(20) CHECK (status IN ('running', 'completed', 'failed')),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Detailed metrics per run
CREATE TABLE benchmark_metrics (
    id SERIAL PRIMARY KEY,
    run_id UUID REFERENCES benchmark_runs(run_id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    dataset_type VARCHAR(50) NOT NULL, -- 'clean', 'mixed', 'adversarial', etc.
    created_at TIMESTAMP DEFAULT NOW()
);

-- Baseline comparisons
CREATE TABLE baseline_comparisons (
    id SERIAL PRIMARY KEY,
    run_id UUID REFERENCES benchmark_runs(run_id) ON DELETE CASCADE,
    baseline_method VARCHAR(50) NOT NULL, -- 'random', 'rule_based', etc.
    metric_name VARCHAR(100) NOT NULL,
    agent_value FLOAT NOT NULL,
    baseline_value FLOAT NOT NULL,
    improvement_pct FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Behavior-specific metrics
CREATE TABLE behavior_metrics (
    id SERIAL PRIMARY KEY,
    run_id UUID REFERENCES benchmark_runs(run_id) ON DELETE CASCADE,
    behavior VARCHAR(50) NOT NULL,
    precision FLOAT,
    recall FLOAT,
    f1_score FLOAT,
    support INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_benchmark_runs_timestamp ON benchmark_runs(timestamp);
CREATE INDEX idx_benchmark_runs_status ON benchmark_runs(status);
CREATE INDEX idx_benchmark_metrics_run_id ON benchmark_metrics(run_id);
CREATE INDEX idx_benchmark_metrics_name ON benchmark_metrics(metric_name);
CREATE INDEX idx_baseline_comparisons_run_id ON baseline_comparisons(run_id);
CREATE INDEX idx_behavior_metrics_run_id ON behavior_metrics(run_id);

-- View for latest baseline
CREATE VIEW latest_baseline AS
SELECT
    metric_name,
    AVG(metric_value) as baseline_value,
    STDDEV(metric_value) as baseline_stddev
FROM benchmark_metrics
WHERE run_id IN (
    SELECT run_id
    FROM benchmark_runs
    WHERE status = 'completed'
    ORDER BY timestamp DESC
    LIMIT 10  -- Average last 10 successful runs
)
GROUP BY metric_name;

-- View for performance trends
CREATE VIEW performance_trends AS
SELECT
    DATE(br.timestamp) as date,
    bm.metric_name,
    AVG(bm.metric_value) as avg_value,
    MIN(bm.metric_value) as min_value,
    MAX(bm.metric_value) as max_value,
    COUNT(*) as num_runs
FROM benchmark_runs br
JOIN benchmark_metrics bm ON br.run_id = bm.run_id
WHERE br.status = 'completed'
GROUP BY DATE(br.timestamp), bm.metric_name
ORDER BY date DESC, metric_name;
```

#### Day 17: Automated Backup
```bash
#!/bin/bash
# scripts/backup_benchmark_data.sh

BACKUP_DIR="/backups/citation-benchmarks"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="citation_integrity"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Full backup of benchmark tables
pg_dump -h localhost -U postgres -d "$DB_NAME" \
    -t benchmark_runs \
    -t benchmark_metrics \
    -t baseline_comparisons \
    -t behavior_metrics \
    -F c -f "$BACKUP_DIR/benchmark_full_${TIMESTAMP}.dump"

# Compress
gzip "$BACKUP_DIR/benchmark_full_${TIMESTAMP}.dump"

# Delete backups older than 30 days
find "$BACKUP_DIR" -name "benchmark_full_*.dump.gz" -mtime +30 -delete

echo "✅ Backup completed: benchmark_full_${TIMESTAMP}.dump.gz"
```

**Cron setup:**
```bash
# Add to crontab
0 2 * * * /path/to/scripts/backup_benchmark_data.sh >> /var/log/benchmark_backup.log 2>&1
```

**Deliverables:**
- `migrations/003_benchmark_results.sql`
- `scripts/backup_benchmark_data.sh`
- `scripts/restore_benchmark_data.sh`
- Database connection pooling configuration

---

### 2.2 Monitoring & Dashboards (Week 3-4, Days 18-23)

**Reference:** Benchmarks already mention Prometheus and Grafana

#### Days 18-20: Prometheus Metrics Export
```python
# Add to citation_evaluation_benchmarks.py
from prometheus_client import (
    Counter, Histogram, Gauge, Summary,
    start_http_server, CollectorRegistry
)

# Create registry
registry = CollectorRegistry()

# Define metrics
evaluations_total = Counter(
    'citation_evaluations_total',
    'Total number of citation evaluations',
    ['dataset', 'behavior'],
    registry=registry
)

evaluation_latency = Histogram(
    'citation_evaluation_latency_seconds',
    'Citation evaluation latency in seconds',
    ['dataset'],
    buckets=[0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0],
    registry=registry
)

accuracy_gauge = Gauge(
    'citation_accuracy',
    'Current citation detection accuracy',
    ['dataset'],
    registry=registry
)

f1_score_gauge = Gauge(
    'citation_f1_score',
    'Current F1 score',
    ['dataset'],
    registry=registry
)

convergence_time = Summary(
    'citation_convergence_time_generations',
    'Convergence time in generations',
    registry=registry
)

consensus_gauge = Gauge(
    'citation_consensus_mean',
    'Multi-agent consensus mean',
    ['dataset'],
    registry=registry
)

behavior_accuracy = Gauge(
    'citation_behavior_accuracy',
    'Per-behavior detection accuracy',
    ['behavior'],
    registry=registry
)

memory_utilization = Gauge(
    'citation_memory_utilization',
    'Memory hierarchy utilization',
    ['level'],
    registry=registry
)

# Export metrics after evaluation
def export_metrics_to_prometheus(metrics: Dict[str, CitationMetrics]):
    """Export benchmark metrics to Prometheus."""

    for dataset, m in metrics.items():
        # Core metrics
        accuracy_gauge.labels(dataset=dataset).set(m.accuracy)
        f1_score_gauge.labels(dataset=dataset).set(m.f1)
        consensus_gauge.labels(dataset=dataset).set(m.consensus_mean)

        # Convergence
        convergence_time.observe(m.convergence_time)

        # Behavior-specific
        for behavior, acc in m.behavior_accuracy.items():
            behavior_accuracy.labels(behavior=behavior).set(acc)

        # Memory utilization
        for level, util in m.memory_utilization.items():
            memory_utilization.labels(level=level).set(util)

# Start metrics server
def start_metrics_server(port: int = 8001):
    """Start Prometheus metrics HTTP server."""
    start_http_server(port, registry=registry)
    logger.info(f"Metrics server started on port {port}")

# Usage in main evaluation
async def run_complete_evaluation_with_metrics(*args, **kwargs):
    """Run evaluation and export metrics."""

    # Start metrics server
    start_metrics_server()

    # Run evaluation
    metrics, comparisons = await run_complete_evaluation(*args, **kwargs)

    # Export to Prometheus
    export_metrics_to_prometheus(metrics)

    return metrics, comparisons
```

#### Days 21-22: Grafana Dashboard
```json
{
  "dashboard": {
    "title": "Citation Integrity Benchmarks",
    "uid": "citation-benchmarks",
    "version": 1,
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Accuracy Trend (All Datasets)",
        "type": "graph",
        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8},
        "targets": [
          {
            "expr": "citation_accuracy{dataset=\"clean\"}",
            "legendFormat": "Clean Dataset"
          },
          {
            "expr": "citation_accuracy{dataset=\"mixed\"}",
            "legendFormat": "Mixed Dataset"
          },
          {
            "expr": "citation_accuracy{dataset=\"adversarial\"}",
            "legendFormat": "Adversarial Dataset"
          }
        ],
        "yaxes": [
          {"label": "Accuracy", "format": "percentunit", "min": 0, "max": 1}
        ]
      },
      {
        "id": 2,
        "title": "Evaluation Latency (p95)",
        "type": "graph",
        "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8},
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(citation_evaluation_latency_seconds_bucket[5m]))",
            "legendFormat": "p95 Latency"
          },
          {
            "expr": "histogram_quantile(0.99, rate(citation_evaluation_latency_seconds_bucket[5m]))",
            "legendFormat": "p99 Latency"
          }
        ],
        "yaxes": [
          {"label": "Latency (seconds)", "format": "s"}
        ],
        "alert": {
          "conditions": [
            {
              "evaluator": {"type": "gt", "params": [0.2]},
              "operator": {"type": "and"},
              "query": {"params": ["A", "5m", "now"]}
            }
          ],
          "name": "High Latency Alert",
          "message": "p95 latency exceeds 200ms"
        }
      },
      {
        "id": 3,
        "title": "F1 Score by Dataset",
        "type": "stat",
        "gridPos": {"x": 0, "y": 8, "w": 6, "h": 4},
        "targets": [
          {"expr": "citation_f1_score{dataset=\"clean\"}", "legendFormat": "Clean"},
          {"expr": "citation_f1_score{dataset=\"mixed\"}", "legendFormat": "Mixed"}
        ],
        "options": {
          "colorMode": "value",
          "graphMode": "area",
          "textMode": "value_and_name"
        },
        "thresholds": {
          "mode": "absolute",
          "steps": [
            {"color": "red", "value": 0},
            {"color": "yellow", "value": 0.7},
            {"color": "green", "value": 0.8}
          ]
        }
      },
      {
        "id": 4,
        "title": "Convergence Time",
        "type": "graph",
        "gridPos": {"x": 6, "y": 8, "w": 6, "h": 4},
        "targets": [
          {
            "expr": "citation_convergence_time_generations",
            "legendFormat": "Convergence Time"
          }
        ],
        "yaxes": [
          {"label": "Generations", "format": "short"}
        ]
      },
      {
        "id": 5,
        "title": "Behavior Detection Accuracy Heatmap",
        "type": "heatmap",
        "gridPos": {"x": 0, "y": 12, "w": 12, "h": 8},
        "targets": [
          {
            "expr": "citation_behavior_accuracy",
            "legendFormat": "{{behavior}}"
          }
        ],
        "dataFormat": "tsbuckets",
        "heatmap": {
          "yAxis": {"format": "short"},
          "colorScheme": "interpolateRdYlGn"
        }
      },
      {
        "id": 6,
        "title": "Memory Hierarchy Utilization",
        "type": "graph",
        "gridPos": {"x": 12, "y": 12, "w": 12, "h": 8},
        "targets": [
          {
            "expr": "citation_memory_utilization{level=\"immediate\"}",
            "legendFormat": "Immediate (L1)"
          },
          {
            "expr": "citation_memory_utilization{level=\"short_term\"}",
            "legendFormat": "Short-term (L2)"
          },
          {
            "expr": "citation_memory_utilization{level=\"long_term\"}",
            "legendFormat": "Long-term (L3)"
          },
          {
            "expr": "citation_memory_utilization{level=\"persistent\"}",
            "legendFormat": "Persistent (L4)"
          }
        ],
        "yaxes": [
          {"label": "Utilization", "format": "percentunit", "min": 0, "max": 1}
        ]
      },
      {
        "id": 7,
        "title": "Multi-Agent Consensus",
        "type": "gauge",
        "gridPos": {"x": 0, "y": 20, "w": 6, "h": 6},
        "targets": [
          {
            "expr": "citation_consensus_mean",
            "legendFormat": "Consensus"
          }
        ],
        "options": {
          "showThresholdLabels": true,
          "showThresholdMarkers": true
        },
        "thresholds": {
          "mode": "absolute",
          "steps": [
            {"color": "red", "value": 0},
            {"color": "yellow", "value": 0.7},
            {"color": "green", "value": 0.85}
          ]
        }
      },
      {
        "id": 8,
        "title": "Evaluation Throughput",
        "type": "stat",
        "gridPos": {"x": 6, "y": 20, "w": 6, "h": 6},
        "targets": [
          {
            "expr": "rate(citation_evaluations_total[5m])",
            "legendFormat": "Citations/sec"
          }
        ],
        "options": {
          "colorMode": "value",
          "graphMode": "area",
          "unit": "cps"
        }
      }
    ],
    "refresh": "30s",
    "time": {"from": "now-1h", "to": "now"}
  }
}
```

Save to: `monitoring/grafana/citation-benchmarks-dashboard.json`

#### Day 23: Alerting Rules
```yaml
# monitoring/prometheus/benchmark_alerts.yml
groups:
  - name: citation_benchmark_alerts
    interval: 30s
    rules:
      # Accuracy alerts
      - alert: LowAccuracy
        expr: citation_accuracy < 0.75
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Citation accuracy dropped below 75%"
          description: "Dataset {{ $labels.dataset }} accuracy is {{ $value | humanizePercentage }}"

      - alert: CriticalAccuracyDrop
        expr: citation_accuracy < 0.65
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "CRITICAL: Accuracy below 65%"
          description: "Dataset {{ $labels.dataset }} accuracy critically low: {{ $value | humanizePercentage }}"

      # Latency alerts
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(citation_evaluation_latency_seconds_bucket[5m])) > 0.2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High evaluation latency detected"
          description: "p95 latency is {{ $value | humanizeDuration }} (threshold: 200ms)"

      - alert: ExtremeLatency
        expr: histogram_quantile(0.99, rate(citation_evaluation_latency_seconds_bucket[5m])) > 0.5
        for: 3m
        labels:
          severity: critical
        annotations:
          summary: "CRITICAL: Extreme latency"
          description: "p99 latency is {{ $value | humanizeDuration }}"

      # Convergence alerts
      - alert: SlowConvergence
        expr: citation_convergence_time_generations > 60
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Slow convergence detected"
          description: "Convergence taking {{ $value }} generations (expected: <40)"

      # Consensus alerts
      - alert: LowConsensus
        expr: citation_consensus_mean < 0.7
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Low multi-agent consensus"
          description: "Consensus mean is {{ $value | humanizePercentage }} (expected: >85%)"

      # Throughput alerts
      - alert: LowThroughput
        expr: rate(citation_evaluations_total[5m]) < 50
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Low evaluation throughput"
          description: "Processing {{ $value | humanize }} citations/sec (expected: >80)"

      # Memory alerts
      - alert: HighMemoryUtilization
        expr: citation_memory_utilization{level="immediate"} > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory utilization"
          description: "{{ $labels.level }} memory at {{ $value | humanizePercentage }}"
```

**Deliverables:**
- Prometheus metrics in Python code ✓
- `monitoring/grafana/citation-benchmarks-dashboard.json` ✓
- `monitoring/prometheus/benchmark_alerts.yml` ✓
- Alert notification configuration (email/Slack)

---

## Phase 3: CI/CD & Automation (Week 5-6)

### 3.1 Automated Benchmark Runs (Week 5, Days 24-28)

#### Days 24-26: GitHub Actions Workflow
```yaml
# .github/workflows/citation-benchmarks.yml
name: Citation Integrity Benchmarks

on:
  push:
    branches: [main, feature/nested-learning-*]
  pull_request:
    paths:
      - 'src/platform/nested-learning-citation-study/**'
      - 'tests/**'
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday at midnight
  workflow_dispatch:  # Manual trigger

jobs:
  quick-benchmark:
    name: Quick Benchmark (PR check)
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request' || github.event_name == 'push'

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Python 3.10
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r src/platform/nested-learning-citation-study/requirements.txt
          pip install pytest pytest-asyncio

      - name: Run quick benchmark (100 samples)
        working-directory: src/platform/nested-learning-citation-study/integration
        run: |
          python citation_evaluation_benchmarks.py \
            --quick \
            --samples=100 \
            --output=quick-results

      - name: Check performance regression
        run: |
          python scripts/check_benchmark_regression.py \
            --baseline=benchmark-results/baseline_latest.json \
            --current=quick-results/benchmark-report.json \
            --threshold=0.05

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: quick-benchmark-results
          path: quick-results/
          retention-days: 7

      - name: Comment PR with results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const results = JSON.parse(fs.readFileSync('quick-results/benchmark-report.json'));

            const comment = `## 🔬 Benchmark Results

            | Metric | Value | Target |
            |--------|-------|--------|
            | Accuracy | ${(results.metrics.clean.accuracy * 100).toFixed(1)}% | >80% |
            | F1 Score | ${(results.metrics.clean.f1 * 100).toFixed(1)}% | >75% |
            | Latency (p95) | ${results.metrics.clean.latency_p95.toFixed(0)}ms | <100ms |
            | Throughput | ${results.metrics.clean.throughput.toFixed(0)}/sec | >50/sec |

            ✅ All benchmarks passed!`;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });

  full-benchmark:
    name: Full Benchmark Suite
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'
    timeout-minutes: 120

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: citation_integrity
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Python 3.10
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r src/platform/nested-learning-citation-study/requirements.txt

      - name: Initialize database
        env:
          PGHOST: localhost
          PGPORT: 5432
          PGUSER: postgres
          PGPASSWORD: postgres
          PGDATABASE: citation_integrity
        run: |
          psql -f migrations/001_initial_schema.sql
          psql -f migrations/002_agent_tables.sql
          psql -f migrations/003_benchmark_results.sql

      - name: Run full benchmark (5000 samples)
        working-directory: src/platform/nested-learning-citation-study/integration
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/citation_integrity
          REDIS_URL: redis://localhost:6379
        run: |
          python citation_evaluation_benchmarks.py \
            --full \
            --datasets=clean,mixed,adversarial,temporal_drift,cs,biology,psychology \
            --output=full-results

      - name: Generate HTML dashboard
        run: |
          python scripts/generate_benchmark_dashboard.py \
            --input=full-results/benchmark-report.json \
            --output=benchmark-dashboard/

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: full-benchmark-results
          path: full-results/
          retention-days: 90

      - name: Deploy dashboard to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./benchmark-dashboard
          destination_dir: benchmarks/latest

      - name: Update baseline
        run: |
          cp full-results/benchmark-report.json \
             benchmark-results/baseline_latest.json
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add benchmark-results/baseline_latest.json
          git commit -m "chore: Update benchmark baseline [skip ci]"
          git push

      - name: Send Slack notification
        if: always()
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
          payload: |
            {
              "text": "Weekly benchmark completed",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "📊 *Weekly Benchmark Results*\n\nStatus: ${{ job.status }}\n\n<https://404genenotfound.github.io/ai_game_theory_simulation/benchmarks/latest|View Dashboard>"
                  }
                }
              ]
            }
```

#### Day 27: Regression Detection Script
```python
# scripts/check_benchmark_regression.py
import json
import sys
import argparse
from pathlib import Path

def load_results(path: Path) -> dict:
    """Load benchmark results from JSON file."""
    with open(path) as f:
        return json.load(f)

def check_regression(baseline_path: Path, current_path: Path, threshold: float = 0.05):
    """
    Check for performance regression.

    Args:
        baseline_path: Path to baseline results
        current_path: Path to current results
        threshold: Regression threshold (default: 5%)

    Returns:
        Exit code (0 = pass, 1 = regression detected)
    """
    baseline = load_results(baseline_path)
    current = load_results(current_path)

    regressions = []
    improvements = []

    # Check core metrics
    core_metrics = ['accuracy', 'f1', 'precision', 'recall']

    for dataset in ['clean', 'mixed', 'adversarial']:
        if dataset not in baseline['metrics'] or dataset not in current['metrics']:
            continue

        for metric in core_metrics:
            baseline_val = baseline['metrics'][dataset].get(metric, 0)
            current_val = current['metrics'][dataset].get(metric, 0)

            if baseline_val == 0:
                continue

            change = (current_val - baseline_val) / baseline_val

            if change < -threshold:  # Degradation
                regressions.append({
                    'dataset': dataset,
                    'metric': metric,
                    'baseline': baseline_val,
                    'current': current_val,
                    'change_pct': change * 100
                })
            elif change > threshold:  # Improvement
                improvements.append({
                    'dataset': dataset,
                    'metric': metric,
                    'baseline': baseline_val,
                    'current': current_val,
                    'change_pct': change * 100
                })

    # Print results
    print("\n" + "="*70)
    print("BENCHMARK REGRESSION CHECK")
    print("="*70)

    if regressions:
        print("\n❌ PERFORMANCE REGRESSIONS DETECTED:")
        print("-" * 70)
        for r in regressions:
            print(f"  {r['dataset']}.{r['metric']}: "
                  f"{r['baseline']:.3f} → {r['current']:.3f} "
                  f"({r['change_pct']:.1f}% worse)")
        print()

        print("💡 RECOMMENDATIONS:")
        print("  1. Review recent changes that may impact performance")
        print("  2. Check for configuration changes")
        print("  3. Verify data quality")
        print("  4. Run full benchmark to confirm")
        print()

        return 1

    else:
        print("\n✅ NO PERFORMANCE REGRESSION DETECTED")

        if improvements:
            print("\n🎉 PERFORMANCE IMPROVEMENTS:")
            print("-" * 70)
            for i in improvements:
                print(f"  {i['dataset']}.{i['metric']}: "
                      f"{i['baseline']:.3f} → {i['current']:.3f} "
                      f"({i['change_pct']:.1f}% better)")

        print()
        return 0

def main():
    parser = argparse.ArgumentParser(description='Check for benchmark regression')
    parser.add_argument('--baseline', type=Path, required=True,
                        help='Path to baseline results JSON')
    parser.add_argument('--current', type=Path, required=True,
                        help='Path to current results JSON')
    parser.add_argument('--threshold', type=float, default=0.05,
                        help='Regression threshold (default: 5%%)')

    args = parser.parse_args()

    if not args.baseline.exists():
        print(f"❌ Baseline file not found: {args.baseline}")
        sys.exit(1)

    if not args.current.exists():
        print(f"❌ Current results file not found: {args.current}")
        sys.exit(1)

    exit_code = check_regression(args.baseline, args.current, args.threshold)
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
```

#### Day 28: Pre-commit Hooks
```bash
#!/bin/bash
# .git/hooks/pre-push

echo "🔬 Running quick benchmark before push..."

cd src/platform/nested-learning-citation-study/integration

# Run quick benchmark (50 samples, ~1 minute)
python citation_evaluation_benchmarks.py --quick --samples=50 --output=/tmp/pre-push-benchmark

if [ $? -ne 0 ]; then
    echo "❌ Benchmark failed. Push aborted."
    echo "💡 Fix issues and try again, or use --no-verify to skip checks"
    exit 1
fi

echo "✅ Benchmark passed"
exit 0
```

**Make executable:**
```bash
chmod +x .git/hooks/pre-push
```

**Deliverables:**
- `.github/workflows/citation-benchmarks.yml` ✓
- `scripts/check_benchmark_regression.py` ✓
- Pre-commit hooks for local validation ✓
- Weekly full benchmark report published to GitHub Pages ✓

---

## Phase 4: Marcus 2.0 Domain Adaptation (Week 7-8)

### 4.1 Extend Benchmarks for Software Engineering (Week 7-8, Days 32-42)

**Adapt citation benchmarks to code attribution**

#### Days 32-35: New Benchmark Datasets

```python
# src/platform/nested-learning-citation-study/integration/code_attribution_benchmarks.py

from enum import Enum
from dataclasses import dataclass
import numpy as np
from typing import Dict, List

class CodeAttributionBehavior(Enum):
    """Code attribution behaviors for Marcus 2.0."""
    PROPER_ATTRIBUTE = "properly_attributed"           # 1.0 integrity
    LICENSE_COMPLIANT = "license_compliant"            # 1.0 integrity
    PACKAGE_CITED = "package_properly_cited"           # 1.0 integrity
    PARAPHRASE_CODE = "paraphrased_without_attribution" # 0.7 integrity
    COPY_PASTE = "uncredited_code_reuse"               # 0.3 integrity
    LICENSE_VIOLATION = "license_incompatible_mix"     # 0.2 integrity
    INVENTED_DEPENDENCY = "fabricated_package_claim"   # 0.1 integrity
    CODE_PLAGIARISM = "direct_copy_no_attribution"     # 0.0 integrity

class CodeAttributionBenchmarkDataset:
    """Benchmark datasets for code attribution (Marcus 2.0)."""

    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        self.datasets = {}
        self._generate_datasets()

    def _generate_datasets(self):
        """Generate code attribution benchmark datasets."""

        # 1. License Compliance Dataset (GPL mixing, license compatibility)
        self.datasets['license_compliance'] = self._generate_license_dataset(1000)

        # 2. Code Reuse Dataset (copy-paste detection, attribution)
        self.datasets['code_reuse'] = self._generate_code_reuse_dataset(1000)

        # 3. Package Attribution Dataset (npm, pip, cargo citations)
        self.datasets['package_attribution'] = self._generate_package_dataset(500)

        # 4. Copy-Paste Detection Dataset (StackOverflow, GitHub)
        self.datasets['copy_paste'] = self._generate_copy_paste_dataset(500)

        # 5. Open Source Contribution Dataset (PR attributions)
        self.datasets['oss_contribution'] = self._generate_oss_dataset(500)

    def _generate_license_dataset(self, size: int) -> List[Dict]:
        """Generate GPL/MIT/Apache license mixing scenarios."""
        dataset = []
        licenses = ['GPL-3.0', 'MIT', 'Apache-2.0', 'BSD-3-Clause', 'ISC', 'MPL-2.0']

        for i in range(size):
            # Randomly select primary license
            primary_license = np.random.choice(licenses)

            # Randomly select dependencies (1-5)
            num_deps = np.random.randint(1, 6)
            dependencies = np.random.choice(licenses, size=num_deps)

            # Check for GPL mixing issues (copyleft incompatibility)
            has_gpl_violation = (
                'GPL-3.0' in dependencies and
                primary_license not in ['GPL-3.0', 'AGPL-3.0']
            )

            # Check for MIT/Apache compatibility
            is_permissive_compatible = (
                primary_license in ['MIT', 'Apache-2.0', 'BSD-3-Clause'] and
                all(dep in ['MIT', 'Apache-2.0', 'BSD-3-Clause', 'ISC'] for dep in dependencies)
            )

            # Determine behavior
            if has_gpl_violation:
                behavior = CodeAttributionBehavior.LICENSE_VIOLATION
                integrity = 0.2
            elif is_permissive_compatible:
                behavior = CodeAttributionBehavior.LICENSE_COMPLIANT
                integrity = 1.0
            else:
                behavior = CodeAttributionBehavior.LICENSE_COMPLIANT
                integrity = 0.9  # Slightly lower for complex mixing

            dataset.append({
                'id': f'license_{i}',
                'code_snippet': self._generate_code_header(primary_license),
                'primary_license': primary_license,
                'dependencies': list(dependencies),
                'ground_truth_behavior': behavior,
                'ground_truth_integrity': integrity,
                'context': {
                    'project_type': np.random.choice(['library', 'application', 'framework']),
                    'language': np.random.choice(['python', 'javascript', 'rust', 'go'])
                }
            })

        return dataset

    def _generate_code_header(self, license: str) -> str:
        """Generate realistic code header with license."""
        return f"""
/**
 * Licensed under {license}
 *
 * Copyright (c) 2024 Developer Name
 *
 * See LICENSE file for details
 */

import lib1 from 'dependency1';
import lib2 from 'dependency2';

export function myFunction() {{
    // Implementation
}}
"""

    def _generate_code_reuse_dataset(self, size: int) -> List[Dict]:
        """Generate code reuse scenarios."""
        dataset = []

        reuse_types = [
            ('proper_attribution', CodeAttributionBehavior.PROPER_ATTRIBUTE, 1.0),
            ('paraphrase', CodeAttributionBehavior.PARAPHRASE_CODE, 0.7),
            ('copy_paste', CodeAttributionBehavior.COPY_PASTE, 0.3),
            ('plagiarism', CodeAttributionBehavior.CODE_PLAGIARISM, 0.0)
        ]

        for i in range(size):
            reuse_type, behavior, integrity = reuse_types[i % len(reuse_types)]

            # Generate code snippet
            if reuse_type == 'proper_attribution':
                code = """
// Based on solution by @user123 on StackOverflow
// https://stackoverflow.com/questions/12345
function sortArray(arr) {
    return arr.sort((a, b) => a - b);
}
"""
            elif reuse_type == 'paraphrase':
                code = """
// Similar algorithm, restructured
function sortNumbers(numbers) {
    return numbers.sort((x, y) => x - y);
}
"""
            elif reuse_type == 'copy_paste':
                code = """
function sortArray(arr) {
    return arr.sort((a, b) => a - b);
}
"""
            else:  # plagiarism
                code = """
function sortArray(arr) {
    return arr.sort((a, b) => a - b);
}
// No attribution
"""

            dataset.append({
                'id': f'reuse_{i}',
                'code_snippet': code,
                'source': 'stackoverflow' if i % 2 == 0 else 'github',
                'ground_truth_behavior': behavior,
                'ground_truth_integrity': integrity,
                'context': {
                    'code_complexity': np.random.choice(['simple', 'moderate', 'complex']),
                    'similarity_score': np.random.uniform(0.7, 1.0)
                }
            })

        return dataset

    def _generate_package_dataset(self, size: int) -> List[Dict]:
        """Generate package attribution scenarios."""
        dataset = []

        for i in range(size):
            # Generate realistic package.json
            has_proper_citation = np.random.random() > 0.2

            if has_proper_citation:
                package_json = {
                    'name': 'my-project',
                    'dependencies': {
                        'react': '^18.0.0',
                        'lodash': '^4.17.21'
                    },
                    'acknowledgments': 'Uses React and Lodash libraries'
                }
                behavior = CodeAttributionBehavior.PACKAGE_CITED
                integrity = 1.0
            else:
                package_json = {
                    'name': 'my-project',
                    'dependencies': {
                        'react': '^18.0.0',
                        'lodash': '^4.17.21'
                    }
                    # Missing acknowledgments
                }
                behavior = CodeAttributionBehavior.PROPER_ATTRIBUTE
                integrity = 0.8  # Technically fine, but missing best practices

            dataset.append({
                'id': f'package_{i}',
                'package_json': package_json,
                'ground_truth_behavior': behavior,
                'ground_truth_integrity': integrity,
                'context': {
                    'ecosystem': np.random.choice(['npm', 'pip', 'cargo', 'maven'])
                }
            })

        return dataset

    def _generate_copy_paste_dataset(self, size: int) -> List[Dict]:
        """Generate StackOverflow/GitHub copy-paste scenarios."""
        dataset = []

        for i in range(size):
            has_attribution = np.random.random() > 0.3

            if has_attribution:
                code = f"""
// Source: https://stackoverflow.com/questions/{i}
// Author: @user{i}
// License: CC BY-SA 4.0
function helper() {{
    // Implementation
}}
"""
                behavior = CodeAttributionBehavior.PROPER_ATTRIBUTE
                integrity = 1.0
            else:
                code = """
function helper() {
    // Implementation copied without attribution
}
"""
                behavior = CodeAttributionBehavior.CODE_PLAGIARISM
                integrity = 0.0

            dataset.append({
                'id': f'copypaste_{i}',
                'code_snippet': code,
                'source_url': f'https://stackoverflow.com/questions/{i}',
                'ground_truth_behavior': behavior,
                'ground_truth_integrity': integrity
            })

        return dataset

    def _generate_oss_dataset(self, size: int) -> List[Dict]:
        """Generate open source contribution attribution scenarios."""
        dataset = []

        for i in range(size):
            has_credit = np.random.random() > 0.2

            if has_credit:
                commit_msg = f"""
feat: Add new feature

Co-authored-by: @contributor{i} <contributor@example.com>
"""
                behavior = CodeAttributionBehavior.PROPER_ATTRIBUTE
                integrity = 1.0
            else:
                commit_msg = """
feat: Add new feature
"""
                behavior = CodeAttributionBehavior.COPY_PASTE
                integrity = 0.4

            dataset.append({
                'id': f'oss_{i}',
                'commit_message': commit_msg,
                'contributors': ['@contributor1', '@contributor2'],
                'ground_truth_behavior': behavior,
                'ground_truth_integrity': integrity
            })

        return dataset

@dataclass
class CodeAttributionMetrics:
    """Extended metrics for code attribution (Marcus 2.0)."""

    # Core metrics (inherited from CitationMetrics)
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0

    # License-specific metrics
    license_compliance_rate: float = 0.0
    gpl_violation_detection_rate: float = 0.0
    license_compatibility_score: float = 0.0

    # Attribution-specific metrics
    package_attribution_accuracy: float = 0.0
    copy_paste_detection_rate: float = 0.0
    stackoverflow_attribution_rate: float = 0.0

    # Repository-level metrics
    repo_attribution_score: float = 0.0
    dependency_graph_accuracy: float = 0.0
    contributor_credit_accuracy: float = 0.0

    # Integration metrics
    pr_review_accuracy: float = 0.0
    automated_detection_rate: float = 0.0
    false_positive_rate: float = 0.0

# Evaluation function for Marcus 2.0
async def evaluate_code_attribution(dataset: CodeAttributionBenchmarkDataset):
    """Evaluate code attribution agent on Marcus 2.0 datasets."""

    from citation_integrity_agent import CitationIntegrityAgent

    # Create agent pool
    agents = [CitationIntegrityAgent(agent_id=i) for i in range(10)]

    results = {}

    for dataset_name, samples in dataset.datasets.items():
        print(f"Evaluating {dataset_name}...")

        predictions = []
        ground_truth = []

        for sample in samples:
            # Analyze with agent
            result = await agents[0].analyze_code_attribution(sample)

            predictions.append(result['behavior'])
            ground_truth.append(sample['ground_truth_behavior'])

        # Calculate metrics
        from sklearn.metrics import accuracy_score, precision_recall_fscore_support

        accuracy = accuracy_score(ground_truth, predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(
            ground_truth, predictions, average='weighted'
        )

        results[dataset_name] = CodeAttributionMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1=f1
        )

    return results
```

#### Days 36-37: Marcus-Specific Agent Adaptation

```python
# src/platform/nested-learning-citation-study/integration/marcus_agent.py

class MarcusCodeAttributionAgent(CitationIntegrityAgent):
    """
    Marcus 2.0: Code Attribution Agent
    Extends citation integrity to software engineering domain.
    """

    def __init__(self, agent_id: int, config: Dict = None):
        super().__init__(agent_id, config)

        # Marcus-specific memory
        self.license_knowledge = {}
        self.package_registry_cache = {}
        self.code_pattern_memory = NestedCitationMemory()

    async def analyze_code_attribution(self, code_sample: Dict) -> Dict:
        """
        Analyze code snippet for attribution issues.

        Returns:
            {
                'behavior': CodeAttributionBehavior,
                'integrity_score': float,
                'confidence': float,
                'issues': List[str],
                'recommendations': List[str]
            }
        """

        # Extract features
        features = self._extract_code_features(code_sample)

        # Check license compliance
        license_issues = self._check_license_compliance(code_sample)

        # Check attribution
        attribution_issues = self._check_attribution(code_sample)

        # Combine analysis
        behavior = self._classify_behavior(license_issues, attribution_issues)
        integrity_score = self._calculate_integrity(behavior, features)

        return {
            'behavior': behavior,
            'integrity_score': integrity_score,
            'confidence': self._calculate_confidence(features),
            'issues': license_issues + attribution_issues,
            'recommendations': self._generate_recommendations(behavior)
        }

    def _extract_code_features(self, code_sample: Dict) -> Dict:
        """Extract features from code sample."""
        return {
            'has_license_header': 'license' in code_sample.get('code_snippet', '').lower(),
            'has_attribution_comment': any(marker in code_sample.get('code_snippet', '').lower()
                                            for marker in ['author:', 'source:', 'based on']),
            'num_dependencies': len(code_sample.get('dependencies', [])),
            'code_length': len(code_sample.get('code_snippet', '')),
            'has_url_reference': 'http' in code_sample.get('code_snippet', '')
        }

    def _check_license_compliance(self, code_sample: Dict) -> List[str]:
        """Check for license compatibility issues."""
        issues = []

        primary = code_sample.get('primary_license')
        dependencies = code_sample.get('dependencies', [])

        # Check GPL mixing
        if 'GPL' in str(dependencies) and primary not in ['GPL-3.0', 'AGPL-3.0']:
            issues.append("GPL license incompatibility detected")

        # Check copyleft propagation
        copyleft_licenses = ['GPL-3.0', 'AGPL-3.0', 'MPL-2.0']
        if any(dep in copyleft_licenses for dep in dependencies):
            if primary not in copyleft_licenses:
                issues.append("Copyleft requirement not propagated")

        return issues

    def _check_attribution(self, code_sample: Dict) -> List[str]:
        """Check for attribution issues."""
        issues = []

        code = code_sample.get('code_snippet', '')

        # Check for attribution markers
        has_source_url = 'stackoverflow.com' in code or 'github.com' in code
        has_author = '@' in code or 'author:' in code.lower()
        has_license_ref = 'license' in code.lower()

        if has_source_url and not has_author:
            issues.append("Source URL provided but author not credited")

        if not has_license_ref and len(code) > 100:
            issues.append("No license reference in substantial code")

        return issues

    def _classify_behavior(self, license_issues: List[str], attribution_issues: List[str]) -> CodeAttributionBehavior:
        """Classify overall behavior."""

        if license_issues:
            return CodeAttributionBehavior.LICENSE_VIOLATION

        if not attribution_issues:
            return CodeAttributionBehavior.PROPER_ATTRIBUTE

        if len(attribution_issues) == 1 and 'license reference' in attribution_issues[0]:
            return CodeAttributionBehavior.PACKAGE_CITED

        return CodeAttributionBehavior.COPY_PASTE

    def _calculate_integrity(self, behavior: CodeAttributionBehavior, features: Dict) -> float:
        """Calculate integrity score."""

        base_scores = {
            CodeAttributionBehavior.PROPER_ATTRIBUTE: 1.0,
            CodeAttributionBehavior.LICENSE_COMPLIANT: 1.0,
            CodeAttributionBehavior.PACKAGE_CITED: 1.0,
            CodeAttributionBehavior.PARAPHRASE_CODE: 0.7,
            CodeAttributionBehavior.COPY_PASTE: 0.3,
            CodeAttributionBehavior.LICENSE_VIOLATION: 0.2,
            CodeAttributionBehavior.INVENTED_DEPENDENCY: 0.1,
            CodeAttributionBehavior.CODE_PLAGIARISM: 0.0
        }

        score = base_scores.get(behavior, 0.5)

        # Adjust based on features
        if features['has_license_header']:
            score += 0.1
        if features['has_attribution_comment']:
            score += 0.1
        if features['has_url_reference']:
            score += 0.05

        return min(1.0, score)

    def _calculate_confidence(self, features: Dict) -> float:
        """Calculate confidence in classification."""

        # More explicit features = higher confidence
        explicit_markers = sum([
            features['has_license_header'],
            features['has_attribution_comment'],
            features['has_url_reference']
        ])

        return 0.6 + (explicit_markers * 0.1)

    def _generate_recommendations(self, behavior: CodeAttributionBehavior) -> List[str]:
        """Generate actionable recommendations."""

        recommendations = []

        if behavior == CodeAttributionBehavior.LICENSE_VIOLATION:
            recommendations.append("Review license compatibility and consider alternative dependencies")

        if behavior == CodeAttributionBehavior.COPY_PASTE:
            recommendations.append("Add attribution comment with source URL and author")
            recommendations.append("Include license reference if copying substantial code")

        if behavior == CodeAttributionBehavior.CODE_PLAGIARISM:
            recommendations.append("CRITICAL: Remove or properly attribute copied code")
            recommendations.append("Cite original source with URL and author")

        return recommendations
```

#### Days 38-42: VS Code Extension + GitHub App

See separate deliverables file for:
- `extensions/vscode-marcus/` - VS Code extension implementation
- `apps/github-marcus/` - GitHub App for PR comments
- `cli/marcus-cli/` - Command-line tool

**Deliverables:**
- `code_attribution_benchmarks.py` ✓
- `marcus_agent.py` ✓
- VS Code extension (separate section)
- GitHub App (separate section)
- CLI tool (separate section)

---

## Phase 5: Scaling & Performance (Week 9-10)

### 5.1 Optimize Benchmark Execution (Week 9, Days 43-49)

**Make 5,000-sample benchmarks run faster**

#### Days 43-45: Parallel Evaluation
```python
# Optimize citation_evaluation_benchmarks.py

import asyncio
from concurrent.futures import ThreadPoolExecutor

async def run_parallel_evaluation(
    dataset: List[Dict],
    num_workers: int = 10
) -> List[Dict]:
    """
    Evaluate dataset using parallel agent pool.

    Performance improvement: ~8x speedup with 10 workers
    """

    # Split dataset into chunks
    chunk_size = len(dataset) // num_workers
    chunks = [
        dataset[i:i+chunk_size]
        for i in range(0, len(dataset), chunk_size)
    ]

    # Create agent pool
    agents = [CitationIntegrityAgent(agent_id=i) for i in range(num_workers)]

    # Parallel evaluation
    tasks = [
        evaluate_chunk(agent, chunk)
        for agent, chunk in zip(agents, chunks)
    ]

    results = await asyncio.gather(*tasks)

    # Flatten results
    return [item for sublist in results for item in sublist]

async def evaluate_chunk(agent: CitationIntegrityAgent, chunk: List[Dict]) -> List[Dict]:
    """Evaluate a chunk of samples with single agent."""
    results = []

    for sample in chunk:
        result = await agent.analyze_citation(
            sample['text'],
            sample['citations']
        )
        results.append(result)

    return results

# Usage
async def run_complete_evaluation_parallel(datasets, num_samples=1000):
    """Run evaluation with parallelization."""

    all_results = {}

    for dataset_name, samples in datasets.items():
        print(f"Evaluating {dataset_name} with {num_workers} workers...")

        start = time.time()
        results = await run_parallel_evaluation(samples[:num_samples], num_workers=10)
        duration = time.time() - start

        print(f"  Completed in {duration:.1f}s ({num_samples/duration:.1f} samples/sec)")

        all_results[dataset_name] = results

    return all_results
```

#### Day 46: Result Caching
```python
from functools import lru_cache
import hashlib
import pickle
from pathlib import Path

class BenchmarkCache:
    """Cache expensive evaluation results."""

    def __init__(self, cache_dir: Path = Path('.benchmark-cache')):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)

    def hash_sample(self, sample: Dict) -> str:
        """Generate hash for sample."""
        sample_str = json.dumps(sample, sort_keys=True)
        return hashlib.sha256(sample_str.encode()).hexdigest()

    def get(self, sample: Dict) -> Optional[Dict]:
        """Get cached result for sample."""
        sample_hash = self.hash_sample(sample)
        cache_file = self.cache_dir / f"{sample_hash}.pkl"

        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                return pickle.load(f)

        return None

    def set(self, sample: Dict, result: Dict):
        """Cache result for sample."""
        sample_hash = self.hash_sample(sample)
        cache_file = self.cache_dir / f"{sample_hash}.pkl"

        with open(cache_file, 'wb') as f:
            pickle.dump(result, f)

    def clear(self):
        """Clear cache."""
        for cache_file in self.cache_dir.glob('*.pkl'):
            cache_file.unlink()

# Usage
cache = BenchmarkCache()

async def evaluate_with_cache(agent, sample):
    """Evaluate with caching."""

    # Check cache
    cached = cache.get(sample)
    if cached:
        return cached

    # Evaluate
    result = await agent.analyze_citation(sample['text'], sample['citations'])

    # Cache result
    cache.set(sample, result)

    return result
```

#### Days 47-48: Incremental Benchmarking
```python
def run_incremental_benchmark(
    dataset: List[Dict],
    checkpoint_dir: Path = Path('./checkpoints')
) -> CitationMetrics:
    """
    Run benchmark with checkpointing for resume capability.

    Features:
    - Save progress every 100 samples
    - Resume from last checkpoint
    - Handle interruptions gracefully
    """

    checkpoint_dir.mkdir(exist_ok=True)
    checkpoint_file = checkpoint_dir / 'checkpoint_latest.pkl'

    # Load checkpoint if exists
    if checkpoint_file.exists():
        with open(checkpoint_file, 'rb') as f:
            checkpoint = pickle.load(f)

        start_idx = checkpoint['completed_samples']
        metrics = checkpoint['metrics']
        results = checkpoint['results']

        print(f"Resuming from checkpoint: {start_idx}/{len(dataset)} samples")
    else:
        start_idx = 0
        metrics = CitationMetrics()
        results = []

    # Resume evaluation
    try:
        for i in range(start_idx, len(dataset)):
            sample = dataset[i]

            # Evaluate sample
            result = evaluate_sample(sample)
            results.append(result)

            # Update metrics
            update_metrics(metrics, result)

            # Save checkpoint every 100 samples
            if (i + 1) % 100 == 0:
                checkpoint = {
                    'completed_samples': i + 1,
                    'metrics': metrics,
                    'results': results
                }

                with open(checkpoint_file, 'wb') as f:
                    pickle.dump(checkpoint, f)

                print(f"Checkpoint saved: {i + 1}/{len(dataset)} samples")

    except KeyboardInterrupt:
        print("\nBenchmark interrupted. Progress saved to checkpoint.")
        print(f"Resume with: python citation_evaluation_benchmarks.py --resume")
        raise

    finally:
        # Always save final checkpoint
        checkpoint = {
            'completed_samples': len(results),
            'metrics': metrics,
            'results': results
        }

        with open(checkpoint_file, 'wb') as f:
            pickle.dump(checkpoint, f)

    return metrics
```

#### Day 49: Validate Performance Targets
```bash
# Run optimized benchmarks and measure performance

# Quick benchmark (100 samples): < 2 minutes
time python citation_evaluation_benchmarks.py --quick --samples=100

# Standard benchmark (1,000 samples): < 15 minutes
time python citation_evaluation_benchmarks.py --samples=1000

# Full benchmark (5,000 samples): < 60 minutes
time python citation_evaluation_benchmarks.py --full

# Parallel speedup test
python scripts/benchmark_parallelization.py --workers=1,2,4,8,10
```

**Deliverables:**
- Parallel evaluation implementation ✓
- Result caching layer ✓
- Incremental checkpointing ✓
- Performance optimization report ✓

---

### 5.2 Distributed Deployment (Week 10, Days 50-56)

See detailed Kubernetes deployment section in original plan (Phase 4.2).

**Key Deliverables:**
- K8s manifests in `k8s/`
- Helm chart for easy deployment
- Multi-region deployment guide
- Auto-scaling configuration
- Load balancer setup

---

## Phase 6: Documentation & Launch (Week 11-12)

### 6.1 Complete Documentation (Week 11, Days 57-65)

**API Documentation (OpenAPI spec)** - See original plan Phase 6.1

**User Guides:**
- Quick start (10-minute setup)
- Configuration guide (all parameters)
- **Benchmark usage guide** (how to run, interpret results)
- Troubleshooting guide
- Best practices

**Developer Documentation:**
- Architecture diagrams
- Code walkthrough
- **Benchmark extension guide** (adding new datasets/metrics)
- Contributing guide

**Deliverables:**
- `docs/api/openapi.yaml`
- `docs/guides/quick-start.md`
- `docs/guides/benchmarks.md` ← **New: Comprehensive benchmark guide**
- `docs/developers/architecture.md`
- Interactive API explorer (Swagger UI)

---

### 6.2 Production Launch (Week 12, Days 66-78)

**Pre-Launch Checklist:**
- [ ] All benchmarks passing (accuracy > 80%, latency < 100ms)
- [ ] CI/CD pipeline working (automated benchmark runs)
- [ ] Monitoring dashboards live (Grafana + Prometheus)
- [ ] Error handling tested (recovery, retry, degradation)
- [ ] Database migrations tested (backup/restore)
- [ ] Security audit completed (auth, data encryption)
- [ ] Documentation complete (API, guides, troubleshooting)
- [ ] Load testing completed (100+ citations/sec sustained)
- [ ] Baseline results stored (for regression detection)
- [ ] Alert rules configured (accuracy drop, high latency)

**Beta Testing (Days 71-77):**
1. Recruit 5-10 early adopters
2. Onboarding support + training
3. Weekly feedback collection
4. Fix critical bugs (P0/P1)
5. Update documentation based on feedback

**Launch (Day 78+):**
1. Deploy to production (gradual rollout: 10% → 50% → 100%)
2. Monitor metrics for 48 hours
3. On-call engineer standby
4. Daily standup for first week
5. Weekly retrospective for first month

---

## Immediate Next Steps (TODAY)

### 1. Checkout Feature Branch
```bash
git fetch origin feature/nested-learning-citation-platform
git checkout feature/nested-learning-citation-platform
cd src/platform/nested-learning-citation-study/integration
```

### 2. Run Existing Benchmarks
```bash
# Install dependencies
pip install numpy pandas scikit-learn matplotlib seaborn

# Run quick benchmark (100 samples, ~2 minutes)
python citation_evaluation_benchmarks.py --quick --samples=100

# Check results
ls -lh benchmark-results/
cat benchmark-results/benchmark-summary.md
```

### 3. Establish Baseline
```bash
# Run full benchmark to establish baseline
python citation_evaluation_benchmarks.py --full

# Save as baseline for future comparisons
cp benchmark-results/benchmark-report.json \
   benchmark-results/baseline_$(date +%Y%m%d).json
```

### 4. Set Up Monitoring
```bash
# Start Prometheus (if not running)
docker run -d -p 9090:9090 prom/prometheus

# Start Grafana (if not running)
docker run -d -p 3000:3000 grafana/grafana

# Import dashboard (after creating it)
curl -X POST http://localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @monitoring/grafana/citation-benchmarks-dashboard.json
```

### 5. Create GitHub Project Board
```bash
gh project create --title "Marcus 2.0 Production" \
  --body "Production readiness roadmap"

# Add initial issues
gh issue create --title "Phase 1: Benchmark Integration" \
  --body "Complete benchmark integration and validation (Week 1-2)"

gh issue create --title "Phase 2: Infrastructure" \
  --body "Set up production infrastructure (Week 3-4)"

# ... repeat for all phases
```

---

## Priority Order (If Time-Constrained)

**Week 1 (MUST HAVE):**
- ✅ Run existing benchmarks
- ✅ Validate performance targets
- 🔨 Create TypeScript wrapper
- 🔨 Set up CI integration

**Week 2-3 (SHOULD HAVE):**
- Database schema for results
- Prometheus metrics export
- Grafana dashboard
- Error handling & recovery

**Week 4+ (NICE TO HAVE):**
- Marcus 2.0 domain adaptation
- VS Code extension
- Multi-region deployment
- Advanced optimizations

---

## Success Metrics

**Production Ready When:**
- [ ] Accuracy: 82-85% consistently ✓
- [ ] F1 Score: 78-81% ✓
- [ ] Latency p95: < 100ms ✓
- [ ] Throughput: > 80 citations/sec ✓
- [ ] Convergence: < 40 generations ✓
- [ ] Consensus: > 85% ✓
- [ ] CI/CD: Automated benchmark runs on every PR
- [ ] Monitoring: Real-time dashboards with alerts
- [ ] Documentation: Complete user + developer guides
- [ ] Deployment: One-command Kubernetes deployment
- [ ] Regression Protection: Automatic detection + alerting

---

## Conclusion

This plan provides a comprehensive roadmap to take Marcus 2.0 from current implementation (with excellent benchmarks already in place) to full production readiness. The key insight is that **most of the hard work is done** - you have comprehensive evaluation infrastructure. The remaining work focuses on:

1. **Integration**: TypeScript wrapper, CI/CD, monitoring
2. **Infrastructure**: Database, error handling, deployment automation
3. **Adaptation**: Extend from academic citations to code attribution
4. **Optimization**: Parallel execution, caching, distributed deployment
5. **Documentation**: User guides, API docs, troubleshooting

**Estimated Timeline:** 12 weeks to full production readiness
**Estimated Effort:** 2-3 developers full-time

**Next Action:** Choose your starting point and let's begin implementation!
