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

## Adding the Python Implementation

When you have the `nested_learning_enhanced.py` file from your Opus session, place it here:

```bash
# From the project root
mv ~/Downloads/nested_learning_enhanced.py src/platform/nested-learning-citation-study/

# Or any other Python files
mv ~/Downloads/enhanced_nest_learning.py src/platform/nested-learning-citation-study/
mv ~/Downloads/nest_learning_debug.py src/platform/nested-learning-citation-study/
```

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

## Quick Start (Once Python files are added)

```bash
# Run the simulation
python src/platform/nested-learning-citation-study/nested_learning_enhanced.py

# Or if it needs to be a module
cd src/platform/nested-learning-citation-study
python -m nested_learning_enhanced
```

## Documentation

- **Full Theory:** `docs/citations_and_integration.md`
- **Code Comparison:** `analysis/code_comparison_analysis.md`
- **Main Simulation Docs:** `../../docs/wiki/README.md`
