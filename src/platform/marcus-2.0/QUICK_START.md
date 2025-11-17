# Marcus 2.0 Quick Start Guide

## What Is Marcus 2.0?

**A platform engineer agent that models realistic engineering team behavior** using nested learning.

**One-Line Pitch:** "Study how platform engineering teams develop attribution cultures and accumulate technical debt over time."

---

## Quick Comparison

| Aspect | Marcus 1.0 (Citation Integrity) | Marcus 2.0 (Nested Learning) |
|--------|--------------------------------|------------------------------|
| **Role** | Build production systems | Model team behavior |
| **Input** | Task requirements | Team parameters |
| **Output** | Working code | Behavioral insights |
| **Focus** | Delivery | Research |
| **Timeframe** | Days | Months/Years |

---

## 5-Minute Tutorial

### 1. Install Dependencies
```bash
pip3 install numpy matplotlib seaborn
```

### 2. Run Basic Simulation
```bash
cd src/platform/marcus-2.0
python3 marcus_platform_sim.py
```

### 3. View Results
```bash
# Results saved to marcus_results.json
cat marcus_results.json | python3 -m json.tool | head -50
```

---

## What Does It Model?

### Engineering Attribution Strategies

```
PROPER_CREDIT    ████████░░ Quality: 10/10, Velocity: 8/10, Debt: 0/10
ADAPT_PATTERN    ███████░░░ Quality:  9/10, Velocity: 9/10, Debt: 1/10
COPY_PASTE       ██████░░░░ Quality:  6/10, Velocity: 10/10, Debt: 4/10
REINVENT_NIH     ███████░░░ Quality:  7/10, Velocity: 4/10, Debt: 3/10
CLAIM_ORIGINAL   ███░░░░░░░ Quality:  3/10, Velocity: 9/10, Debt: 8/10
```

### Multi-Level Memory

```
FAST (L1)  → Every commit     → "Does this compile?"
MEDIUM (L2) → Every sprint     → "Is this pattern good?"
SLOW (L3)   → Every quarter    → "What are our values?"
```

### Context-Aware Decisions

**Same engineer, different contexts:**
```
Deadline approaching  → Copy-paste (need velocity)
OSS contribution      → Proper credit (need reputation)
Internal tool         → Adapt pattern (balanced)
Major incident        → Reinvent wheel (NIH syndrome)
```

---

## Example Use Cases

### Use Case 1: Deadline Pressure
```python
from marcus_platform_sim import MarcusPlatformSimulation

# Simulate team under deadline pressure
sim = MarcusPlatformSimulation(
    num_engineers=20,
    deadline_pressure=0.9,  # High pressure
    team_culture="move_fast"
)

results = sim.run(num_sprints=24)  # 6 months
print(f"Technical debt accumulated: {results['debt']}")
print(f"Final quality score: {results['quality']}")
```

### Use Case 2: OSS Contribution
```python
# Simulate team contributing to open source
sim = MarcusPlatformSimulation(
    num_engineers=10,
    code_visibility=1.0,  # Fully public
    team_culture="quality_first"
)

results = sim.run(num_sprints=12)  # 3 months
print(f"Attribution patterns: {results['strategies']}")
```

### Use Case 3: Culture Formation
```python
# Watch team culture emerge from scratch
sim = MarcusPlatformSimulation(
    num_engineers=30,
    team_culture=None,  # No initial culture
    new_hire_rate=0.2   # 20% turnover
)

results = sim.run(num_sprints=100)  # 2 years
sim.plot_culture_evolution()
```

---

## Reading the Results

### Key Metrics

**Technical Debt Score:** Lower is better (0.0 = no debt, 1.0 = critical)
- Below 0.3: Healthy
- 0.3-0.6: Warning
- Above 0.6: Crisis

**Quality Score:** Higher is better (0.0 = broken, 1.0 = perfect)
- Above 0.8: Excellent
- 0.6-0.8: Good
- Below 0.6: Needs work

**Velocity-Quality Ratio:** Balance indicator
- 1.0: Perfect balance
- >1.5: Sacrificing quality for speed
- <0.7: Over-engineering

**Knowledge Concentration:** Bus factor indicator
- Below 0.3: Knowledge well-distributed
- 0.3-0.6: Some concentration
- Above 0.6: High risk (few key people)

---

## Common Patterns You'll See

### Pattern 1: The Death Spiral
```
High deadline pressure
  → More copy-paste
    → Rising technical debt
      → Slower velocity
        → More deadline pressure
          → Even more copy-paste
            → CRISIS
```

**Intervention:** Add slack time, mandate attribution

### Pattern 2: Quality Culture Emergence
```
Proper attribution leaders
  → New hires mimic behavior
    → Team norm forms
      → Peer pressure reinforces
        → Culture stabilizes
```

**Timeframe:** 6-12 months (Medium memory consolidation)

### Pattern 3: Context Collapse
```
Everything becomes "urgent"
  → Context signals degrade
    → Decision-making breaks
      → Random behavior
        → Quality collapse
```

**Intervention:** Better project management, realistic deadlines

---

## Quick Debugging

### Problem: Simulation crashes
**Solution:** Check numpy version (`pip3 install --upgrade numpy`)

### Problem: No strategy variation
**Solution:** Increase `exploration_rate` parameter

### Problem: Unrealistic results
**Solution:** Validate context parameters (0.0-1.0 range)

### Problem: Slow performance
**Solution:** Reduce `num_engineers` or `num_sprints`

---

## Next Steps

1. **Read the full plan:** `plans/MARCUS_2.0_NESTED_LEARNING_REMAKE.md`
2. **Explore examples:** `scripts/marcus_examples/`
3. **Check research:** `src/platform/marcus-2.0/RESEARCH_CITATIONS.md`
4. **Run experiments:** Try different team cultures

---

## Research Foundation

Based on peer-reviewed research:
- Behrouz et al. (2024) - Nested Learning
- Axelrod (1984) - Evolution of Cooperation
- Mockus et al. (2002) - OSS Development Studies
- Kruchten et al. (2012) - Technical Debt Theory

**Not speculation.** These patterns are observed in real engineering teams.

---

**Status:** 🎯 Planning Phase (See full plan for implementation timeline)
**Complexity:** High (5 weeks estimated)
**Priority:** MEDIUM
