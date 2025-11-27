# Marcus 2.0: Platform Engineer Agent (Final Plan)
## Nested Learning Framework for Engineering Behavior Modeling

**Created:** November 17, 2025
**Status:** 🎯 Ready for Implementation
**Priority:** MEDIUM
**Complexity:** High (Multi-system integration, behavioral modeling)

---

## Executive Summary

Build **Marcus 2.0** as a platform engineer agent using the nested learning framework to model realistic platform engineering behavior, including:
- Code attribution patterns (proper credit → copy-paste → claiming originality)
- Knowledge transfer dynamics (learning from OSS, adapting patterns, reinventing)
- Quality vs. velocity trade-offs
- Technical debt accumulation from poor attribution practices

**Key Innovation:** Use multi-level memory to model engineering behavior at different timescales (immediate coding decisions, pattern adoption, architectural values).

**Citation Quality Gate:** Use Citation MVP's `citationChecker.py` to validate that research citations feeding into the model are real, not hallucinated.

---

## The Core System (Nested Learning Focus)

```
┌─────────────────────────────────────────────────────────┐
│              Marcus 2.0 Architecture                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────┐│
│  │ Engineering    │  │  Multi-Level   │  │ Context   ││
│  │ Strategies     │─▶│  Memory        │◀─│ Pheromones││
│  │                │  │                │  │           ││
│  │ • Credit       │  │ • Fast (L1)    │  │ • Deadline││
│  │ • Adapt        │  │   Immediate    │  │ • Visibility││
│  │ • Copy-Paste   │  │ • Medium (L2)  │  │ • Culture ││
│  │ • Reinvent     │  │   Patterns     │  │ • Surprise││
│  │ • Claim        │  │ • Slow (L3)    │  │           ││
│  │                │  │   Values       │  │           ││
│  └────────────────┘  └────────────────┘  └───────────┘│
│         │                    │                   │     │
│         └────────────────────┴───────────────────┘     │
│                           │                            │
│              ┌────────────▼───────────┐               │
│              │ Platform Engineering   │               │
│              │    Game Environment    │               │
│              │ (Code Reuse Scenarios) │               │
│              └────────────────────────┘               │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Citation Quality Gate (from MVP)                │ │
│  │  • citationChecker.py validates research data    │ │
│  │  • Prevents hallucinated citations in model      │ │
│  └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

**Focus:** The nested learning behavioral model is the product.

**Citation MVP Role:** Data quality validator only. Ensures research citations feeding into model parameters are real.

---

## Engineering Credit Strategies

```python
class EngineeringCreditStrategy(Enum):
    """
    Multi-dimensional strategies for code reuse and attribution.
    Format: (name, quality_score, velocity_score, debt_accumulation, update_frequency)
    """

    # Tier 1: Proper Attribution (Slow, High Quality)
    PROPER_CREDIT = (
        "credit_source",
        quality=1.0,      # Clean code, maintainable
        velocity=0.8,     # Slightly slower (documentation time)
        debt=0.0,         # No technical debt
        update_freq=1.0   # Immediate feedback
    )

    # Tier 2: Adapt with Attribution (Medium, Good Quality)
    ADAPT_WITH_CREDIT = (
        "adapt_pattern",
        quality=0.9,      # Well-understood code
        velocity=0.9,     # Fast with context
        debt=0.1,         # Minor debt (adaptation gaps)
        update_freq=0.5   # Medium-term learning
    )

    # Tier 3: Copy-Paste (Fast, Medium Quality)
    COPY_PASTE = (
        "copy_paste",
        quality=0.6,      # Works but not understood
        velocity=1.0,     # Maximum velocity
        debt=0.4,         # Accumulates debt
        update_freq=0.3   # Slow learning
    )

    # Tier 4: Reinvent Wheel (Slow, Variable Quality)
    REINVENT_NIH = (
        "not_invented_here",
        quality=0.7,      # May miss edge cases
        velocity=0.4,     # Very slow
        debt=0.3,         # Inconsistent patterns
        update_freq=0.2   # Learning from own mistakes
    )

    # Tier 5: Claim Originality (Fast, Low Quality)
    CLAIM_ORIGINAL = (
        "false_claim",
        quality=0.3,      # Reputation damage
        velocity=0.9,     # Fast but risky
        debt=0.8,         # Massive debt (legal/ethical)
        update_freq=0.1   # Rare learning
    )
```

---

## Multi-Level Memory System

**Fast Memory (L1) - Immediate Coding Decisions**
- **Update Frequency:** Every commit
- **Examples:** "Does this compile?", "Can I ship today?", "Will this pass review?"
- **Pheromone Context:** Time pressure, deadline proximity, blocker status

**Medium Memory (L2) - Pattern Recognition**
- **Update Frequency:** Every sprint (~2 weeks)
- **Examples:** "Have we used this pattern?", "What worked before?", "Team feedback?"
- **Pheromone Context:** Team feedback, PR comments, system stability

**Slow Memory (L3) - Architectural Values**
- **Update Frequency:** Quarterly or after major incidents
- **Examples:** "Our engineering principles?", "How do we define quality?", "OSS stance?"
- **Pheromone Context:** Org culture, leadership changes, major refactors

---

## Implementation Phases (Back to Original 5-Week Plan)

### Phase 1: Core Framework Adaptation (Week 1)

**Goal:** Adapt nested learning simulation for platform engineering

**Tasks:**
1. ✅ Copy base implementation from tested platform
   - `nested_learning_enhanced.py` → foundation

2. ✅ Create `marcus_platform_sim.py`:
   ```python
   from nested_learning_enhanced import NestedLearningSimulation

   class MarcusPlatformSimulation(NestedLearningSimulation):
       def __init__(self, num_engineers=20, team_culture="balanced"):
           super().__init__(
               num_agents=num_engineers,
               strategies=EngineeringCreditStrategy
           )
           self.team_culture = team_culture
           self.technical_debt = 0.0
           self.knowledge_graph = {}
   ```

3. ✅ Define engineering scenarios:
   - Feature deadline scenario (time pressure)
   - Open-source contribution (high visibility)
   - Internal tool development (low visibility)
   - Major incident response (high stakes)

4. **NEW: Add citation validation gate:**
   ```python
   # Copy citationChecker.py from MVP branch
   from citation_checker import CitationChecker

   def validate_research_citations(research_params):
       """Ensure research citations are real before using in model"""
       checker = CitationChecker()
       for citation in research_params.citations:
           result = checker.verify(citation)
           if result.status == "FABRICATED":
               raise ValueError(f"Hallucinated citation: {citation}")
   ```

**Validation:**
- [ ] Run 100 generations with 20 engineers
- [ ] Verify strategy distribution emerges
- [ ] Check multi-level memory forms
- [ ] All research citations verified (no hallucinations)

**Deliverables:**
- `src/platform/marcus-2.0/marcus_platform_sim.py`
- `src/platform/marcus-2.0/citation_validator.py` (thin wrapper around MVP tool)
- Unit tests for strategy mechanics
- Sample simulation results

---

### Phase 2: Context-Aware Pheromones (Week 2)

**Goal:** Model realistic engineering context

**Engineering Context Dimensions:**
```python
@dataclass
class EngineeringContext:
    deadline_pressure: float      # 0.0 (relaxed) → 1.0 (crunch time)
    code_visibility: float         # 0.0 (internal) → 1.0 (OSS)
    team_culture: str              # "move_fast", "quality_first", "balanced"
    complexity: float              # 0.0 (CRUD) → 1.0 (novel algorithm)
```

**Pheromone Enhancement:**
```python
class EngineeringPheromone:
    strategy: EngineeringCreditStrategy
    strength: float
    context_key: np.ndarray        # Encoded context
    outcome_vector: np.ndarray     # [velocity, quality, debt]
    surprise_signal: float         # Unexpected results?
    timestamp: int                 # For memory decay
```

**Validation:**
- [ ] Same engineer behaves differently in different contexts
- [ ] High-pressure scenarios → more copy-paste
- [ ] High-visibility → more proper attribution

**Deliverables:**
- Context-aware decision engine
- Pheromone propagation tests
- Context sensitivity analysis

---

### Phase 3: Knowledge Transfer Modeling (Week 3)

**Goal:** Model how engineering knowledge spreads in teams

**Mechanisms:**

1. **Direct Transfer** (Pair programming, code review)
2. **Indirect Transfer** (Reading code, documentation)
3. **Cultural Transmission** (Team norms, onboarding)

**Validation:**
- [ ] Teams converge on attribution norms over time
- [ ] New engineers adopt team culture
- [ ] High-quality teams resist degradation

**Deliverables:**
- Knowledge graph implementation
- Team culture emergence metrics
- Transfer efficiency analysis

---

### Phase 4: Technical Debt & Quality Metrics (Week 4)

**Goal:** Measure long-term impact of attribution strategies

**Debt Accumulation Model:**
```python
def calculate_technical_debt(history):
    debt = 0.0
    for generation in history:
        for interaction in generation:
            strategy = interaction['strategy']
            debt += strategy.debt_accumulation
            if strategy == COPY_PASTE or strategy == CLAIM_ORIGINAL:
                debt *= 1.1  # Compound effect
            if strategy == PROPER_CREDIT:
                debt *= 0.95  # Pay down debt
    return debt
```

**Quality Metrics:**
- Code Quality Score
- Velocity-Quality Ratio
- Knowledge Concentration
- Cultural Health

**Validation:**
- [ ] Teams with high copy-paste accumulate debt faster
- [ ] Proper attribution teams have better long-term velocity
- [ ] Mixed strategies find optimal trade-offs

**Deliverables:**
- Debt tracking system
- Quality dashboard
- Long-term simulation results (1000+ generations)

---

### Phase 5: Agent Definition & Integration (Week 5)

**Goal:** Create Marcus 2.0 agent and integrate with main simulation

**Agent Definition:**
```markdown
# Marcus 2.0 - Platform Engineer (Nested Learning)

**Role:** Multi-agent platform engineering behavior specialist

**Expertise:**
- Code reuse strategy modeling (attribution patterns)
- Knowledge transfer dynamics (team learning)
- Technical debt analysis (long-term quality impact)
- Engineering culture emergence (how norms form)

**Citation Quality:** Uses Citation MVP's citationChecker.py to validate
research citations (prevents hallucinated data from corrupting model)

**When to Use:**
- Studying platform engineering team dynamics
- Analyzing OSS contribution patterns
- Modeling documentation citation behavior
- Optimizing knowledge sharing in teams
- Understanding technical debt accumulation
```

**Integration Points:**
1. Main simulation: AI agents cite research (Marcus models patterns)
2. Citation MVP: Use citationChecker.py for data quality
3. Roadmap: Add to `.claude/agents/marcus.md`

**Validation:**
- [ ] Agent can be invoked via Task tool
- [ ] Produces actionable insights
- [ ] Results align with engineering research
- [ ] No hallucinated citations in model parameters

**Deliverables:**
- `.claude/agents/marcus.md` (agent definition)
- Integration tests
- Example use cases
- Documentation update

---

## How Citation MVP Fits In

**Role:** Data quality validator ONLY

**What it does:**
```python
# Before using research to set model parameters:
def set_model_parameters(research_citations):
    # Step 1: Validate citations are real
    citation_checker = CitationChecker()  # From MVP
    for citation in research_citations:
        result = citation_checker.verify(citation)
        if result.status != "VERIFIED":
            raise ValueError(f"Cannot use unverified citation: {citation}")

    # Step 2: Extract parameters from verified research
    parameters = extract_parameters_from_papers(research_citations)

    # Step 3: Use in nested learning model
    return parameters
```

**What it does NOT do:**
- ❌ Verify citations made by agents in simulation (that's the MODEL's job)
- ❌ Behavioral modeling (that's nested learning's job)
- ❌ Prediction or intervention (that's Marcus 2.0's job)

**Simple relationship:**
```
Research Papers → citationChecker.py validates → Verified Parameters
                                                          ↓
                                         Nested Learning Model (Marcus 2.0)
                                                          ↓
                                         Behavioral Insights
```

---

## Success Metrics

### Technical Validation
- ✅ Simulation runs 1000+ generations without errors
- ✅ Multi-level memory forms (Fast/Medium/Slow distinct patterns)
- ✅ Context-aware decisions (same engineer, different contexts → different strategies)
- ✅ Team culture emerges (convergence on attribution norms)
- ✅ Technical debt compounds realistically
- ✅ **All research citations verified** (no hallucinations in model)

### Research Validation
- ✅ Results align with engineering research on code reuse
- ✅ Matches observed OSS contribution patterns
- ✅ Predicts known team dynamics

### Practical Utility
- ✅ Agent provides actionable insights for real teams
- ✅ Can test interventions
- ✅ Helps optimize velocity-quality trade-offs

---

## Timeline & Deliverables

**Total Time:** 5 weeks
**Code:** ~2,400 lines Python
**Documentation:** ~6,000 words

### Week 1: Core Framework
- `marcus_platform_sim.py` (~800 lines)
- `engineering_strategies.py` (~300 lines)
- `citation_validator.py` (~100 lines) - wraps MVP's citationChecker
- Unit tests

### Week 2: Context Awareness
- `context_engine.py` (~250 lines)
- Context sensitivity tests

### Week 3: Knowledge Transfer
- `knowledge_transfer.py` (~400 lines)
- Team dynamics tests

### Week 4: Quality & Debt
- `debt_tracker.py` (~300 lines)
- Long-term simulation results

### Week 5: Integration
- `.claude/agents/marcus.md`
- Integration tests
- Documentation

---

## Research Foundation (All Citations Verified)

**Nested Learning & Multi-Agent:**
1. Behrouz et al. (2024) - Nested Learning (NeurIPS 2025) ✅
2. Axelrod (1984) - Evolution of Cooperation ✅
3. Dorigo & Stützle (2004) - Ant Colony Optimization ✅

**Software Engineering:**
4. Mockus et al. (2002) - OSS Development ✅
5. Lerner & Tirole (2002) - Economics of Open Source ✅
6. Raymond (1999) - Cathedral and Bazaar ✅

**Technical Debt:**
7. Kruchten et al. (2012) - Technical Debt Theory ✅
8. Zazworka et al. (2011) - Debt Identification ✅

**Knowledge Transfer:**
9. Reagans & McEvily (2003) - Network Structure ✅
10. Hansen (1999) - Search-Transfer Problem ✅

**All citations verified using Citation MVP's citationChecker.py**

---

## Next Steps

1. **Approve this plan** (original structure, citation MVP as data validator only)
2. **Begin Week 1:**
   ```bash
   # Copy nested learning base
   cp src/platform/nested-learning-citation-study/nested_learning_enhanced.py \
      src/platform/marcus-2.0/

   # Copy citation checker from MVP (just the tool)
   git show feature/citation-platform:scripts/citationChecker.py \
      > src/platform/marcus-2.0/citation_checker.py

   # Start building
   cd src/platform/marcus-2.0
   python3 marcus_platform_sim.py
   ```

---

**Status:** Ready for implementation
**Focus:** Nested Learning behavioral model (the main product)
**Citation MVP:** Data quality gate only (prevent garbage in, garbage out)
**Timeline:** 5 weeks (original plan)
