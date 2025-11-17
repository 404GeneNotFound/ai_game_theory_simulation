# Nested Learning Citation Study Platform

## Overview

This is a **separate platform** from the main simulation for studying citation behavior using Nested Learning multi-agent systems. This is based on the NeurIPS 2025 paper "Nested Learning: The Illusion of Deep Learning Architectures" by Behrouz et al. (2024).

## What This Platform Does

This platform models **citation behavior as a multi-agent game** where:
- Agents represent researchers making citation decisions
- Strategies include proper citation, selective citation, plagiarism, etc.
- Learning happens at multiple timescales (fast/medium/slow memory)
- Pheromone-based communication models academic influence
- Agents self-modify their citation strategies based on outcomes

## Directory Structure

```
src/platform/nested-learning-citation-study/
├── README.md (this file)
├── docs/
│   └── citations_and_integration.md  # Complete citations and theory
├── analysis/
│   └── code_comparison_analysis.md   # Comparison with other approaches
└── (Python implementation files go here)
```

## Distinction from Citation-Integrity MVP

**IMPORTANT:** This is NOT the same as the `claude/citation-integrity-mvp-0131dmgaZK6S4Qvsaj7ZzbhE` branch.

### Citation-Integrity MVP Branch
- **Purpose:** Verifies citations in the simulation's own research documentation
- **What it does:** Checks if papers cited in the simulation are real and accurately represented
- **Tools:** PDF downloaders, citation extractors, verification scripts
- **Location:** `.claude/agents/citation-verifier.md`, `scripts/citationChecker.py`

### Nested Learning Platform (This)
- **Purpose:** Studies citation behavior as a game-theoretic system
- **What it does:** Models how citation strategies evolve in academic communities
- **Tools:** Multi-agent simulation, nested learning algorithms, swarm intelligence
- **Location:** `src/platform/nested-learning-citation-study/`

**You need BOTH:**
- Citation-Integrity MVP: To ensure the simulation uses accurate research
- Nested Learning Platform: To study citation behavior patterns

## Implementation Files

✅ **All files added!** The platform now includes:

### Standalone Python Implementation
- **`nested_learning_enhanced.py`** (31KB) - Full implementation with all nested learning concepts
- **`enhanced_nest_learning.py`** (21KB) - Production-ready version
- **`nest_learning_debug.py`** (30KB) - Testing and debugging tools
- **`nested_learning_results.json`** (39KB) - Sample simulation results

### TypeScript/Python Integration Bridge
- **`integration/citation_integrity_agent.py`** (28KB) - Production agent with DB/Redis integration
- **`integration/citationAgentIntegration.ts`** (19KB) - TypeScript bridge for platform integration
- **`integration/citation_evaluation_benchmarks.py`** (54KB) - Comprehensive benchmarking suite
- **`integration/COMPLETE_AGENT_DOCUMENTATION.md`** (8.8KB) - Full integration documentation
- **`integration/README.md`** - Integration layer guide

## Key Features (from the documentation)

1. **Multi-Level Memory System**
   - Fast memory (updates every step)
   - Medium memory (updates every 10 steps)
   - Slow memory (updates every 50 steps)

2. **Associative Memory Pheromones**
   - Context-aware signaling between agents
   - Maps research contexts to citation strategies
   - Uses Local Surprise Signals for adaptation

3. **Deep Momentum Optimizer**
   - Neural network-based momentum
   - Adaptive learning rates
   - Newton-Schulz iterations

4. **Self-Modifying Agents**
   - Agents learn their own learning rules
   - Dynamic strategy adaptation
   - Context-aware decision making

## Citation Strategies

From the code comparison document:

```python
class CitationStrategy(Enum):
    PROPER_CITE = ("proper_cite", 1.0, 1.0)      # Always cite properly
    SELECTIVE_CITE = ("selective_cite", 0.8, 0.5) # Cherry-pick citations
    OVER_CITE = ("over_cite", 0.7, 0.3)          # Excessive self-citation
    UNDER_CITE = ("under_cite", 0.6, 0.2)        # Minimal citations
    FABRICATE = ("fabricate", 0.3, 0.1)          # Make up citations
```

## Integration with Main Simulation

This platform can:
1. Run standalone to study citation dynamics
2. Provide insights for the main simulation's academic modeling
3. Test hypotheses about research integrity
4. Generate data on emergent citation patterns

## Next Steps

1. **Add Python files** from your Opus session
2. **Test the implementation** standalone
3. **Compare with citation-integrity MVP** (different purposes)
4. **Consider integration points** with main simulation
5. **Build Marcus 2.0** using this framework

## Building Marcus 2.0 (Platform-Engineer)

Based on the nested learning framework, Marcus 2.0 could:
- Model software engineering citation patterns (library attribution)
- Study open-source contribution credit
- Analyze documentation citation practices
- Track knowledge transfer in engineering teams

## References

See `docs/citations_and_integration.md` for complete academic citations including:
- Behrouz et al. (2024) - Nested Learning paper
- Dorigo & Stützle (2004) - Ant Colony Optimization
- Hopfield (1982) - Associative Memory Networks
- Axelrod (1984) - Evolution of Cooperation
- And 10+ more foundational papers

## Quick Start

### Option 1: Standalone Simulation

```bash
# From project root
cd src/platform/nested-learning-citation-study

# Run the enhanced implementation
python3 nested_learning_enhanced.py

# Or use the production version
python3 enhanced_nest_learning.py

# Run with debugging
python3 nest_learning_debug.py
```

### Option 2: Integrated with TypeScript Platform

```bash
# See integration/README.md for complete setup

# Install dependencies
pip3 install numpy redis psycopg2-binary requests
npm install ioredis pg axios pino

# Start the integrated system
npm run agent:bridge
```

### Basic Usage Example

```python
from nested_learning_enhanced import NestedLearningSimulation, Strategy

# Create simulation
sim = NestedLearningSimulation(num_agents=20, num_generations=100)

# Run simulation
results = sim.run()

# Analyze results
print(f"Final cooperation rate: {results['cooperation_rate']}")
print(f"Strategy distribution: {results['strategy_distribution']}")

# View results
sim.plot_results()  # If matplotlib available
```

### Sample Results

See `nested_learning_results.json` for example output showing:
- Generation-by-generation strategy evolution
- Memory level distributions
- Cooperation rates over time
- Convergence metrics

## Documentation

### Platform Documentation
- **Full Theory:** `docs/citations_and_integration.md` - Complete academic citations and theory
- **Integration Guide:** `docs/integration_guide_continued.md` - Citation platform integration
- **TypeScript Integration:** `integration/README.md` - Production integration with TypeScript platform
- **Complete Agent Docs:** `integration/COMPLETE_AGENT_DOCUMENTATION.md` - Full system architecture
- **Code Comparison:** `analysis/code_comparison_analysis.md` - Implementation details
- **Branch Comparison:** `analysis/branch_comparison.md` - MVP vs Platform comparison

### Main Simulation Documentation
- **Main Simulation Docs:** `../../docs/wiki/README.md`
- **Development Workflow:** `../../docs/DEVELOPMENT_WORKFLOW.md`

## Testing

### Basic Testing
```bash
# Syntax check
python3 -m py_compile nested_learning_enhanced.py

# Run basic test
python3 nested_learning_debug.py

# Run full simulation (100 generations)
python3 nested_learning_enhanced.py --generations 100 --agents 20

# Compare with baseline
python3 enhanced_nest_learning.py --compare-baseline
```

### Comprehensive Benchmarking
```bash
cd integration

# Install benchmark dependencies
pip3 install pandas matplotlib seaborn scikit-learn

# Run full benchmark suite
python3 citation_evaluation_benchmarks.py

# Compare against baselines (Random Forest, SVM, Neural Net)
python3 citation_evaluation_benchmarks.py --baseline-comparison

# Performance profiling (latency, throughput)
python3 citation_evaluation_benchmarks.py --performance-profile

# Cross-validation (K-fold)
python3 citation_evaluation_benchmarks.py --cross-validation
```

**Benchmark Output:**
- JSON results with all metrics
- HTML reports with visualizations
- Comparison charts (Nested Learning vs baselines)
- Performance profiles (latency distributions, throughput)
