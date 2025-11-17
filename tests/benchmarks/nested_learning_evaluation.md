# Nested Learning Model Evaluation Framework
**Version:** 1.0
**Created:** 2025-11-17
**Purpose:** Benchmark and validate nested learning implementation in Citation Integrity Platform
**Reference:** Behrouz et al., "Nested Learning", NeurIPS 2025

---

## Executive Summary

This evaluation framework provides **quantitative benchmarks** to validate that the Citation Integrity Platform's implementation matches Nested Learning theory claims. These tests are designed to measure:

1. **Update frequency hierarchy** enforcement (f_L0 > f_L1 > f_L2 > f_L3)
2. **Local Surprise Signal (LSS)** accuracy and trigger thresholds
3. **Context flow compression** ratios
4. **Memory consolidation** effectiveness
5. **Multi-level optimization** convergence rates

**Current Status:** ⚠️ **Implementation non-functional** (see Architecture Review). These benchmarks are designed for when core functionality is implemented.

---

## Part 1: Update Frequency Hierarchy Validation

### Theory Claim
**Behrouz et al.:** "Components ordered by update rate: fast weights (frequent updates) vs slow weights (rare updates)"

### Implementation Claim
**Multi-Level State Manager** enforces:
- Level 0 (Fast): f = 1.0 (every operation)
- Level 1 (Medium): f = 0.1 (every ~10 operations)
- Level 2 (Slow): f = 0.01 (every ~100 operations)
- Level 3 (Core): f = 0.001 (every ~1000 operations)

### Benchmark: Frequency Hierarchy Enforcement

**Test ID:** `NL-FREQ-001`
**File:** `tests/benchmarks/frequency_hierarchy.bench.ts`

```typescript
/**
 * Validate update frequency hierarchy over 10,000 operations
 *
 * Success Criteria:
 * - Level 0: 10,000 ± 0 updates (f=1.0)
 * - Level 1: 1,000 ± 10 updates (f=0.1)
 * - Level 2: 100 ± 5 updates (f=0.01)
 * - Level 3: 10 ± 2 updates (f=0.001)
 * - Hierarchy maintained: f_L0 > f_L1 > f_L2 > f_L3 (strict)
 */

interface FrequencyTestResult {
  operations: number;
  actualUpdates: [number, number, number, number]; // [L0, L1, L2, L3]
  expectedUpdates: [number, number, number, number];
  deviations: [number, number, number, number]; // % deviation
  hierarchyValid: boolean;
  passThreshold: boolean; // All deviations < 5%
}

async function benchmarkFrequencyHierarchy(
  operations: number = 10_000
): Promise<FrequencyTestResult> {
  // Implementation when platform is functional
  const mlState = new MultiLevelState(
    [null, null, null, null], // Initial memory
    DEFAULT_LEVEL_CONFIGS
  );

  // Simulate operations
  for (let i = 0; i < operations; i++) {
    mlState.recordOperation(0);
    mlState.recordOperation(1);
    mlState.recordOperation(2);
    mlState.recordOperation(3);

    // Trigger updates if due
    if (mlState.shouldUpdate(0)) mlState.update(0, null);
    if (mlState.shouldUpdate(1)) mlState.update(1, null);
    if (mlState.shouldUpdate(2)) mlState.update(2, null);
    if (mlState.shouldUpdate(3)) mlState.update(3, null);
  }

  const stats = mlState.getStats();

  return {
    operations,
    actualUpdates: [
      stats.levels[0].updateCount,
      stats.levels[1].updateCount,
      stats.levels[2].updateCount,
      stats.levels[3].updateCount,
    ],
    expectedUpdates: [
      operations * 1.0,
      operations * 0.1,
      operations * 0.01,
      operations * 0.001,
    ],
    deviations: [
      /* calculate % deviation */
    ],
    hierarchyValid: stats.hierarchyValid,
    passThreshold: /* all deviations < 5% */,
  };
}
```

**Acceptance Criteria:**
- ✅ All levels within 5% of expected update counts
- ✅ Hierarchy maintained for entire test duration
- ✅ No updates when `shouldUpdate()` returns false
- ✅ Updates occur within 1 operation of threshold

---

## Part 2: Local Surprise Signal (LSS) Accuracy

### Theory Claim
**Behrouz et al.:** "LSS quantifies deviation in representation space. Drives learning updates."

### Implementation Claim
**LSS Monitor** calculates:
- Parameter drift: `LSS = |current - cited| / cited`
- Thresholds: WARNING (0.2), ALERT (0.5), CRITICAL (1.0)

### Benchmark: LSS Drift Detection

**Test ID:** `NL-LSS-001`
**File:** `tests/benchmarks/lss_accuracy.bench.ts`

```typescript
/**
 * Validate LSS calculation accuracy across drift scenarios
 *
 * Success Criteria:
 * - LSS calculation matches formula within 0.1% error
 * - Threshold triggers occur at exact boundaries
 * - No false negatives (drift detected when present)
 * - No false positives (no alerts when drift < threshold)
 */

interface LSSTestCase {
  name: string;
  citedValue: number;
  currentValue: number;
  expectedLSS: number;
  expectedLevel: 'NONE' | 'WARNING' | 'ALERT' | 'CRITICAL';
}

const lssTestCases: LSSTestCase[] = [
  {
    name: 'No drift',
    citedValue: 1.8,
    currentValue: 1.8,
    expectedLSS: 0.0,
    expectedLevel: 'NONE',
  },
  {
    name: 'Small drift (under threshold)',
    citedValue: 1.8,
    currentValue: 1.9,
    expectedLSS: 0.0556, // (1.9-1.8)/1.8 = 5.56%
    expectedLevel: 'NONE',
  },
  {
    name: 'Warning threshold (exactly 20%)',
    citedValue: 1.8,
    currentValue: 2.16,
    expectedLSS: 0.2,
    expectedLevel: 'WARNING',
  },
  {
    name: 'Alert threshold (exactly 50%)',
    citedValue: 1.8,
    currentValue: 2.7,
    expectedLSS: 0.5,
    expectedLevel: 'ALERT',
  },
  {
    name: 'Critical threshold (100%+ drift)',
    citedValue: 1.8,
    currentValue: 3.6,
    expectedLSS: 1.0,
    expectedLevel: 'CRITICAL',
  },
  {
    name: 'Negative drift (value decreased)',
    citedValue: 2.0,
    currentValue: 1.0,
    expectedLSS: 0.5, // |1.0-2.0|/2.0 = 0.5
    expectedLevel: 'ALERT',
  },
];

async function benchmarkLSSAccuracy(): Promise<LSSTestResult[]> {
  const results: LSSTestResult[] = [];

  for (const testCase of lssTestCases) {
    const param: ParameterWithProvenance = {
      value: testCase.currentValue,
      type: 'VERIFIED',
      citedValue: testCase.citedValue,
    };

    const result = checkParameterDrift(param, {
      location: 'benchmarkLSSAccuracy',
      valueName: testCase.name,
    });

    results.push({
      name: testCase.name,
      expectedLSS: testCase.expectedLSS,
      actualLSS: result.lss,
      error: Math.abs(result.lss - testCase.expectedLSS),
      expectedLevel: testCase.expectedLevel,
      actualLevel: result.level,
      pass:
        Math.abs(result.lss - testCase.expectedLSS) < 0.001 &&
        result.level === testCase.expectedLevel,
    });
  }

  return results;
}
```

**Acceptance Criteria:**
- ✅ LSS calculation error < 0.1% for all test cases
- ✅ Threshold boundaries exact (no ±0.01 tolerance)
- ✅ 100% detection rate for drift ≥ WARNING threshold
- ✅ 0% false positive rate for drift < WARNING threshold

---

## Part 3: Context Flow Compression Ratio

### Theory Claim
**Behrouz et al.:** "Models learn by compressing their own context flow"

### Implementation Claim
**Multi-Level State Manager** achieves:
- Compression ratio >10:1 (Level 0 → Level 3)
- Information loss < 5% at each consolidation step

### Benchmark: Compression Effectiveness

**Test ID:** `NL-COMP-001`
**File:** `tests/benchmarks/compression_ratio.bench.ts`

```typescript
/**
 * Measure information compression across NL levels
 *
 * Success Criteria:
 * - Compression ratio L0→L3 > 10:1
 * - Information loss per level < 5%
 * - Lossless compression for critical metadata (DOI, citation)
 * - Lossy compression acceptable for non-critical (timestamps, counters)
 */

interface CompressionMetrics {
  level: NLLevel;
  rawSize: number; // bytes
  compressedSize: number; // bytes
  ratio: number; // rawSize / compressedSize
  informationLoss: number; // % of data discarded
  lossType: 'lossless' | 'lossy';
}

async function benchmarkCompressionRatio(): Promise<{
  perLevel: CompressionMetrics[];
  overall: {
    L0toL3Ratio: number;
    totalLoss: number;
    passThreshold: boolean;
  };
}> {
  // Simulate parameter consolidation across levels

  // Level 0: Raw parameter with full metadata
  const L0_data = {
    value: 1.8,
    type: 'PLACEHOLDER',
    timestamp: Date.now(),
    operationCount: 100,
    lastModified: Date.now(),
    validationAttempts: 5,
    history: [1.7, 1.75, 1.78, 1.8], // Full history
    metadata: { /* full provenance */ },
  };
  const L0_size = JSON.stringify(L0_data).length;

  // Level 1: Research-informed (drop operational metadata)
  const L1_data = {
    value: 1.8,
    type: 'INFORMED',
    doi: '10.1234/example',
    confidence: 0.7,
    history: [1.7, 1.8], // Compressed history (keep outliers)
  };
  const L1_size = JSON.stringify(L1_data).length;

  // Level 2: Research-verified (drop intermediates)
  const L2_data = {
    value: 1.8,
    type: 'VERIFIED',
    doi: '10.1234/example',
    citedValue: 1.8,
    lastValidated: Date.now(),
  };
  const L2_size = JSON.stringify(L2_data).length;

  // Level 3: Core knowledge (immutable)
  const L3_data = {
    value: 1.8,
    doi: '10.1234/example',
  };
  const L3_size = JSON.stringify(L3_data).length;

  return {
    perLevel: [
      {
        level: 0,
        rawSize: L0_size,
        compressedSize: L1_size,
        ratio: L0_size / L1_size,
        informationLoss: calculateLoss(L0_data, L1_data),
        lossType: 'lossy',
      },
      // ... similar for L1→L2, L2→L3
    ],
    overall: {
      L0toL3Ratio: L0_size / L3_size,
      totalLoss: calculateCumulativeLoss([L0_data, L1_data, L2_data, L3_data]),
      passThreshold: (L0_size / L3_size) > 10 && totalLoss < 0.05,
    },
  };
}
```

**Acceptance Criteria:**
- ✅ Overall compression ratio L0→L3 > 10:1
- ✅ Per-level information loss < 5%
- ✅ Critical metadata (DOI, value) preserved losslessly
- ✅ Non-critical metadata (timestamps, counters) allowed lossy compression

---

## Part 4: Memory Consolidation Effectiveness

### Theory Claim
**Behrouz et al.:** "Online consolidation (rapid during wakefulness), Offline consolidation (replay during sleep)"

### Implementation Claim
**Auto-Save Middleware** implements:
- Online: Save after every tool call (Level 0)
- Offline: Session summary extraction (Level 2)

### Benchmark: Consolidation Coverage

**Test ID:** `NL-CONS-001`
**File:** `tests/benchmarks/consolidation_coverage.bench.ts`

```typescript
/**
 * Validate memory consolidation across conversation lifecycle
 *
 * Success Criteria:
 * - 100% tool calls logged (online consolidation)
 * - Task detection rate > 95% (medium consolidation)
 * - Learning extraction rate > 80% (offline consolidation)
 * - Zero memory amnesia (all sessions retrievable)
 */

interface ConsolidationTest {
  totalToolCalls: number;
  loggedToolCalls: number; // Level 0 (fast)
  detectedTasks: number; // Level 1 (medium)
  extractedLearnings: number; // Level 2 (slow)
  coreMemoryUpdates: number; // Level 3 (core)
  amnesiaEvents: number; // Failed retrievals
}

async function benchmarkConsolidationEffectiveness(
  conversationLength: number = 100 // tool calls
): Promise<ConsolidationTest> {
  let logged = 0;
  let tasks = 0;
  let learnings = 0;
  let coreUpdates = 0;

  // Simulate conversation with agent memory system
  for (let i = 0; i < conversationLength; i++) {
    const toolCall = simulateToolCall();

    // Level 0: Immediate micro-save
    if (autoSaveMiddleware.handleToolCall(toolCall)) {
      logged++;
    }

    // Level 1: Task detection (every ~10 tool calls)
    if (i % 10 === 0 && taskDetector.detectTask(context)) {
      tasks++;
    }

    // Level 2: Learning extraction (every ~100 tool calls)
    if (i % 100 === 0 && learningExtractor.extract(history)) {
      learnings++;
    }

    // Level 3: Core memory update (every ~1000 tool calls)
    if (i % 1000 === 0 && coreMemory.shouldUpdate(insights)) {
      coreUpdates++;
    }
  }

  // Test retrieval (amnesia check)
  const amnesiaEvents = testMemoryRetrieval(conversationLength);

  return {
    totalToolCalls: conversationLength,
    loggedToolCalls: logged,
    detectedTasks: tasks,
    extractedLearnings: learnings,
    coreMemoryUpdates: coreUpdates,
    amnesiaEvents,
  };
}
```

**Acceptance Criteria:**
- ✅ Online consolidation: 100% coverage (all tool calls logged)
- ✅ Task detection: >95% recall
- ✅ Learning extraction: >80% of conversations yield insights
- ✅ Zero amnesia: All saved memories retrievable

---

## Part 5: Multi-Level Optimization Convergence

### Theory Claim
**Behrouz et al.:** "Each level has its own optimization objective"

### Implementation Claim
**Citation Integrity Platform** optimizes per-level:
- Level 0: Minimize latency (speed)
- Level 1: Minimize fabrication (accuracy)
- Level 2: Minimize variance (consistency)
- Level 3: Minimize drift (stability)

### Benchmark: Convergence Rates

**Test ID:** `NL-OPT-001`
**File:** `tests/benchmarks/optimization_convergence.bench.ts`

```typescript
/**
 * Measure convergence rates for each NL level's optimization objective
 *
 * Success Criteria:
 * - Level 0: Latency < 100ms by operation 100
 * - Level 1: Fabrication rate < 1% by operation 1000
 * - Level 2: Inter-rater variance < 0.05 by operation 10000
 * - Level 3: Parameter drift < 10% by operation 100000
 */

interface ConvergenceMetrics {
  level: NLLevel;
  objective: string;
  initialValue: number;
  finalValue: number;
  targetValue: number;
  convergedAt: number | null; // operation count when target reached
  convergenceRate: number; // improvement per operation
}

async function benchmarkConvergence(): Promise<ConvergenceMetrics[]> {
  return [
    {
      level: 0,
      objective: 'Latency minimization',
      initialValue: 500, // ms
      finalValue: measureLatency(100),
      targetValue: 100, // ms
      convergedAt: findConvergencePoint(latencyHistory, 100),
      convergenceRate: -4.0, // -4ms per operation
    },
    {
      level: 1,
      objective: 'Fabrication minimization',
      initialValue: 0.15, // 15% fabrication
      finalValue: measureFabricationRate(1000),
      targetValue: 0.01, // 1%
      convergedAt: findConvergencePoint(fabricationHistory, 0.01),
      convergenceRate: -0.00014, // -0.014% per operation
    },
    {
      level: 2,
      objective: 'Variance minimization',
      initialValue: 0.25, // High variance
      finalValue: measureInterRaterVariance(10000),
      targetValue: 0.05, // Low variance
      convergedAt: findConvergencePoint(varianceHistory, 0.05),
      convergenceRate: -0.00002, // -0.002 per operation
    },
    {
      level: 3,
      objective: 'Drift minimization',
      initialValue: 0.50, // 50% drift
      finalValue: measureParameterDrift(100000),
      targetValue: 0.10, // 10% drift
      convergedAt: findConvergencePoint(driftHistory, 0.10),
      convergenceRate: -0.000004, // -0.0004% per operation
    },
  ];
}
```

**Acceptance Criteria:**
- ✅ All objectives converge to target within specified operations
- ✅ No regression (monotonic improvement)
- ✅ Convergence rate matches theoretical predictions
- ✅ Cross-level independence (L0 optimization doesn't degrade L3)

---

## Part 6: End-to-End System Validation

### Integration Benchmark

**Test ID:** `NL-E2E-001`
**File:** `tests/benchmarks/e2e_validation.bench.ts`

```typescript
/**
 * Validate complete NL system across realistic workload
 *
 * Scenario: 1000 parameters consolidated from PLACEHOLDER → VERIFIED
 *
 * Success Criteria:
 * - 100% parameters reach VERIFIED status
 * - LSS monitoring detects all drift > 20%
 * - Memory consolidation: 0 amnesia events
 * - Performance: <10s p95 latency
 * - Compression: >10:1 ratio L0→L3
 */

interface E2EValidation {
  parametersProcessed: number;
  verified: number;
  placeholder: number;
  informed: number;
  driftDetected: number;
  amnesiaEvents: number;
  latencyP95: number;
  compressionRatio: number;
  overallPass: boolean;
}

async function runE2EValidation(
  parameterCount: number = 1000
): Promise<E2EValidation> {
  const parameters = generateTestParameters(parameterCount);

  const results = await processParametersWithNL(parameters);

  return {
    parametersProcessed: parameterCount,
    verified: results.filter(p => p.type === 'VERIFIED').length,
    placeholder: results.filter(p => p.type === 'PLACEHOLDER').length,
    informed: results.filter(p => p.type === 'INFORMED').length,
    driftDetected: results.filter(p => p.lss > 0.2).length,
    amnesiaEvents: countAmnesiaEvents(results),
    latencyP95: calculateP95(results.map(r => r.latency)),
    compressionRatio: calculateCompressionRatio(results),
    overallPass: validateAllCriteria(results),
  };
}
```

**Acceptance Criteria:**
- ✅ 100% parameters reach VERIFIED (no stuck in PLACEHOLDER)
- ✅ LSS detects all drift ≥ 20%
- ✅ Zero memory amnesia
- ✅ p95 latency < 10s
- ✅ Compression ratio > 10:1

---

## Part 7: Comparative Benchmarks (vs. Baseline)

### Control Group: Traditional Approach

**Test ID:** `NL-COMP-001`
**File:** `tests/benchmarks/nl_vs_traditional.bench.ts`

Compare Nested Learning implementation against traditional single-level approach:

| Metric | Traditional | Nested Learning | Improvement |
|--------|-------------|-----------------|-------------|
| **Parameters verified** | 60% | 100% (target) | +67% |
| **Fabrication detection** | 85% | 98.7% (claim) | +16% |
| **Memory amnesia rate** | 30% | 0% (target) | -100% |
| **Latency p95** | 15s | 8.2s (claim) | -45% |
| **Context compression** | 2:1 | 10:1 (target) | +400% |

**Benchmark Test:**
```typescript
async function comparativeAnalysis(): Promise<{
  traditional: SystemMetrics;
  nestedLearning: SystemMetrics;
  improvement: Record<string, number>;
}> {
  const traditionalResults = await runTraditionalApproach(1000);
  const nlResults = await runNestedLearningApproach(1000);

  return {
    traditional: traditionalResults,
    nestedLearning: nlResults,
    improvement: {
      verificationRate:
        (nlResults.verified - traditionalResults.verified) / traditionalResults.verified,
      fabricationDetection:
        (nlResults.detected - traditionalResults.detected) / traditionalResults.detected,
      amnesiaReduction:
        (traditionalResults.amnesia - nlResults.amnesia) / traditionalResults.amnesia,
      latencyReduction:
        (traditionalResults.latency - nlResults.latency) / traditionalResults.latency,
      compressionGain:
        (nlResults.compression - traditionalResults.compression) / traditionalResults.compression,
    },
  };
}
```

**Acceptance Criteria:**
- ✅ NL approach outperforms traditional on all metrics
- ✅ Improvements match theoretical predictions (±10%)
- ✅ No regressions on any dimension

---

## Part 8: Failure Mode Testing

### Robustness Benchmarks

**Test ID:** `NL-FAIL-001`
**File:** `tests/benchmarks/failure_modes.bench.ts`

Test NL system under adversarial conditions:

```typescript
/**
 * Failure mode scenarios:
 * 1. MCP server unavailable (50% uptime)
 * 2. Malformed citations (20% error rate)
 * 3. Massive drift (parameters change by 200%)
 * 4. Memory corruption (10% data loss)
 * 5. Concurrent updates (race conditions)
 */

interface FailureModeTest {
  scenario: string;
  expectedBehavior: string;
  actualBehavior: string;
  gracefulDegradation: boolean;
  dataLoss: number; // % of data lost
  recoveryTime: number; // ms
}

async function testFailureModes(): Promise<FailureModeTest[]> {
  return [
    await testMCPOutage(),
    await testMalformedCitations(),
    await testMassiveDrift(),
    await testMemoryCorruption(),
    await testConcurrentUpdates(),
  ];
}
```

**Acceptance Criteria:**
- ✅ Graceful degradation (system continues functioning)
- ✅ Data loss < 1% under all failure scenarios
- ✅ Recovery time < 5 seconds
- ✅ No cascading failures across NL levels

---

## Part 9: Benchmark Execution Guide

### Running All Benchmarks

```bash
# Install dependencies
npm install

# Run frequency hierarchy tests
npx tsx tests/benchmarks/frequency_hierarchy.bench.ts

# Run LSS accuracy tests
npx tsx tests/benchmarks/lss_accuracy.bench.ts

# Run compression ratio tests
npx tsx tests/benchmarks/compression_ratio.bench.ts

# Run consolidation coverage tests
npx tsx tests/benchmarks/consolidation_coverage.bench.ts

# Run optimization convergence tests
npx tsx tests/benchmarks/optimization_convergence.bench.ts

# Run end-to-end validation
npx tsx tests/benchmarks/e2e_validation.bench.ts

# Run comparative analysis
npx tsx tests/benchmarks/nl_vs_traditional.bench.ts

# Run failure mode tests
npx tsx tests/benchmarks/failure_modes.bench.ts

# Generate comprehensive report
npx tsx tests/benchmarks/generate_report.ts > benchmarks/nl_evaluation_report_$(date +%Y%m%d).md
```

### Continuous Benchmarking

Add to CI/CD pipeline:

```yaml
# .github/workflows/nl-benchmarks.yml
name: Nested Learning Benchmarks

on:
  pull_request:
    paths:
      - 'src/platform/**'
  schedule:
    - cron: '0 2 * * *' # Daily at 2 AM

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run NL benchmarks
        run: npm run benchmark:nl
      - name: Compare against baseline
        run: npm run benchmark:compare
      - name: Fail if regressions detected
        run: npm run benchmark:validate
```

---

## Part 10: Acceptance Thresholds

### Overall Platform Acceptance

The Nested Learning implementation is **production-ready** when:

| Benchmark | Threshold | Weight |
|-----------|-----------|--------|
| **Frequency hierarchy** | 100% valid | 10% |
| **LSS accuracy** | Error < 0.1% | 15% |
| **Compression ratio** | > 10:1 | 10% |
| **Consolidation coverage** | > 95% | 20% |
| **Convergence rates** | All objectives met | 15% |
| **E2E validation** | All criteria pass | 20% |
| **Comparative improvement** | All metrics better | 10% |

**Weighted Score Formula:**
```
Score = Σ (benchmark_i × weight_i)
Passing Score: ≥ 90%
```

**Current Status:** ⚠️ **0% - Implementation non-functional**

Per Architecture Review findings:
- Core verification stubbed (cannot run benchmarks)
- Database missing (cannot measure consolidation)
- No integration (cannot validate E2E)

**Estimated Implementation Timeline:**
- 3-4 weeks to implement core functionality
- 1 week to pass all benchmarks
- 1 week to optimize to production thresholds

---

## Appendix A: Theoretical Foundations

### Nested Learning Key Equations

1. **Update Frequency:** `f_L = updates per operation`
2. **LSS (Parameter):** `LSS = |current - cited| / cited`
3. **LSS (Claim):** `LSS = 1 - similarity(claim, source)`
4. **Compression Ratio:** `R = size(L0) / size(L3)`
5. **Information Loss:** `IL = 1 - |preserved_fields| / |total_fields|`

### References

- Behrouz et al., "Nested Learning: The Illusion of Deep Learning Architectures", NeurIPS 2025
- OWASP Top 10 (2021): https://owasp.org/Top10/
- Citation Integrity Platform Project Plan (this repo)

---

## Appendix B: Glossary

- **NL:** Nested Learning
- **LSS:** Local Surprise Signal (drift/deviation metric)
- **f_L:** Update frequency for level L
- **Consolidation:** Moving data from fast → slow memory
- **Context flow:** Data pipeline across NL levels
- **Provenance:** Citation metadata (DOI, confidence, validation status)
- **PLACEHOLDER:** Level 0 parameter (engineering guess)
- **INFORMED:** Level 1 parameter (research-backed estimate)
- **VERIFIED:** Level 2 parameter (peer-reviewed citation)

---

**End of Evaluation Framework**
