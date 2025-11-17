# Marcus 2.0: Platform Engineer Agent Remake
## Using Nested Learning Framework for Engineering Behavior Modeling

**Created:** November 17, 2025
**Status:** 🎯 Planning Phase
**Priority:** MEDIUM
**Complexity:** High (Multi-system integration, behavioral modeling)

---

## Executive Summary

Remake **Marcus** (platform-engineer agent) using the nested learning framework to model realistic platform engineering behavior, including:
- Code attribution patterns (proper credit → copy-paste → claiming originality)
- Knowledge transfer dynamics (learning from OSS, adapting patterns, reinventing)
- Quality vs. velocity trade-offs
- Technical debt accumulation from poor attribution practices

**Key Innovation:** Use multi-level memory to model engineering behavior at different timescales (immediate coding decisions, pattern adoption, architectural values).

---

## 1. Background & Motivation

### Marcus 1.0 (Citation Integrity Project)
- **Role:** Platform engineer who delivered full production systems
- **Achievements:**
  - 32,853 lines of code in 2 days
  - 94.2% test coverage (187+ tests)
  - 96% reduction in citation fabrication
  - Zero critical security vulnerabilities
  - Complete Kubernetes deployment infrastructure

**Limitation:** Marcus 1.0 was task-focused (build a system) but didn't model *how* platform engineers actually behave regarding code reuse, attribution, and knowledge transfer.

### Why Remake with Nested Learning?

**Current Reality in Platform Engineering:**
1. **Attribution varies wildly:**
   - Some engineers credit every StackOverflow answer
   - Others copy-paste entire libraries without attribution
   - Some reinvent wheels (NIH syndrome)

2. **Multi-timescale decisions:**
   - **Fast (L1):** "Does this code snippet work?" (immediate)
   - **Medium (L2):** "Is this pattern appropriate for our stack?" (pattern recognition)
   - **Slow (L3):** "What are our architectural principles?" (long-term values)

3. **Context-dependent behavior:**
   - Same engineer may credit differently based on:
     - Time pressure (deadline approaching?)
     - Code visibility (open-source vs. internal?)
     - Team culture (documentation-heavy vs. move-fast?)
     - Personal reputation stake

**Marcus 2.0 Goal:** Model these realistic behaviors to study:
- How attribution cultures emerge in engineering teams
- Impact of code reuse strategies on velocity vs. quality
- Knowledge transfer patterns in platform engineering
- Technical debt from poorly attributed code

---

## 2. Architecture Design

### 2.1 Core Components

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
└─────────────────────────────────────────────────────────┘
```

### 2.2 Engineering Credit Strategies

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

### 2.3 Multi-Level Memory System

**Fast Memory (L1) - Immediate Coding Decisions**
- **Update Frequency:** Every commit
- **Examples:**
  - "Does this snippet compile?"
  - "Can I ship this today?"
  - "Will this pass code review?"
- **Pheromone Context:** Time pressure, deadline proximity, blocker status

**Medium Memory (L2) - Pattern Recognition**
- **Update Frequency:** Every sprint (~2 weeks)
- **Examples:**
  - "Have we used this pattern before?"
  - "What worked in similar situations?"
  - "How did team react to this approach?"
- **Pheromone Context:** Team feedback, PR comments, system stability

**Slow Memory (L3) - Architectural Values**
- **Update Frequency:** Quarterly or after major incidents
- **Examples:**
  - "What are our engineering principles?"
  - "How do we define code quality?"
  - "What's our stance on OSS contribution?"
- **Pheromone Context:** Org culture, leadership changes, major refactors

---

## 3. Implementation Phases

### Phase 1: Core Framework Adaptation (Week 1)
**Goal:** Adapt nested learning simulation for platform engineering

**Tasks:**
1. ✅ **Copy base implementation** (DONE)
   - `nested_learning_enhanced.py` → platform foundation

2. **Create `marcus_platform_sim.py`:**
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

3. **Define engineering scenarios:**
   - Feature deadline scenario (time pressure)
   - Open-source contribution (high visibility)
   - Internal tool development (low visibility)
   - Major incident response (high stakes)

**Validation:**
- Run 100 generations with 20 engineers
- Verify strategy distribution emerges
- Check multi-level memory forms

**Deliverables:**
- `src/platform/marcus-2.0/marcus_platform_sim.py`
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
    reputation_stake: float        # 0.0 (junior IC) → 1.0 (staff+)
    complexity: float              # 0.0 (CRUD) → 1.0 (novel algorithm)
    prior_art_available: float     # 0.0 (novel) → 1.0 (well-trodden)
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
- Same engineer behaves differently in different contexts
- High-pressure scenarios → more copy-paste
- High-visibility → more proper attribution

**Deliverables:**
- Context-aware decision engine
- Pheromone propagation tests
- Context sensitivity analysis

---

### Phase 3: Knowledge Transfer Modeling (Week 3)
**Goal:** Model how engineering knowledge spreads in teams

**Mechanisms:**
1. **Direct Transfer** (Pair programming, code review)
   ```python
   def pair_program(engineer_a, engineer_b, task):
       # Engineer B learns from Engineer A's attribution strategy
       knowledge_transfer = engineer_a.strategy.quality * 0.7
       engineer_b.update_medium_memory(knowledge_transfer)
   ```

2. **Indirect Transfer** (Reading code, documentation)
   ```python
   def read_codebase(engineer, codebase):
       # Learn from attribution patterns in existing code
       pattern_strength = count_attribution_comments(codebase)
       engineer.update_slow_memory(pattern_strength)
   ```

3. **Cultural Transmission** (Team norms, onboarding)
   ```python
   def onboard_engineer(new_engineer, team):
       # New engineers adopt team culture
       culture_signal = team.average_attribution_strategy()
       new_engineer.initialize_memory(culture_signal)
   ```

**Validation:**
- Teams converge on attribution norms over time
- New engineers adopt team culture
- High-quality teams resist degradation

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
            # Debt compounds over time
            debt += strategy.debt_accumulation
            # Poor attribution makes future work harder
            if strategy == COPY_PASTE or strategy == CLAIM_ORIGINAL:
                debt *= 1.1  # Compound effect
            # Good attribution reduces debt
            if strategy == PROPER_CREDIT:
                debt *= 0.95  # Pay down debt
    return debt
```

**Quality Metrics:**
- **Code Quality Score:** Weighted average of strategy quality scores
- **Velocity-Quality Ratio:** Shipping speed vs. maintainability
- **Knowledge Concentration:** Bus factor (what happens if key engineer leaves?)
- **Cultural Health:** Deviation from ideal attribution patterns

**Validation:**
- Teams with high copy-paste accumulate debt faster
- Proper attribution teams have better long-term velocity
- Mixed strategies find optimal trade-offs

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

**When to Use:**
- Studying platform engineering team dynamics
- Analyzing OSS contribution patterns
- Modeling documentation citation behavior
- Optimizing knowledge sharing in teams
- Understanding technical debt accumulation

**Capabilities:**
1. **Simulate Engineering Teams:** 5-100 engineers, various cultures
2. **Model Realistic Behavior:** Context-dependent attribution decisions
3. **Track Long-term Impact:** Quality, velocity, debt over 100s of sprints
4. **Generate Insights:** Why certain patterns emerge, interventions to try

**Example Usage:**
"Marcus, simulate a 20-person platform team with high deadline pressure.
Model how attribution behavior changes over 6 months. What interventions
would improve code quality without sacrificing velocity?"
```

**Integration Points:**
1. **Main Simulation:**
   - AI agents cite research papers (Marcus models citation behavior)
   - Tech companies develop platforms (Marcus models engineering teams)

2. **Citation Integrity MVP:**
   - MVP verifies YOUR citations
   - Marcus models THEIR behavior (complementary)

3. **Roadmap:**
   - Add to `.claude/agents/marcus.md`
   - Document in `docs/wiki/README.md`
   - Create examples in `scripts/marcus_examples/`

**Validation:**
- Agent can be invoked via Task tool
- Produces actionable insights
- Results align with engineering research

**Deliverables:**
- `.claude/agents/marcus.md` (agent definition)
- Integration tests
- Example use cases
- Documentation update

---

## 4. Success Metrics

### Technical Validation
- ✅ Simulation runs 1000+ generations without errors
- ✅ Multi-level memory forms (Fast/Medium/Slow distinct patterns)
- ✅ Context-aware decisions (same engineer, different contexts → different strategies)
- ✅ Team culture emerges (convergence on attribution norms)
- ✅ Technical debt compounds realistically

### Research Validation
- ✅ Results align with engineering research on code reuse
- ✅ Matches observed OSS contribution patterns
- ✅ Predicts known team dynamics (e.g., move-fast cultures)

### Practical Utility
- ✅ Agent provides actionable insights for real teams
- ✅ Can test interventions (e.g., "What if we mandate attribution?")
- ✅ Helps optimize velocity-quality trade-offs

---

## 5. Research Foundation

### Academic Citations (10+ Papers)

**Nested Learning & Multi-Agent Systems:**
1. Behrouz et al. (2024) - Nested Learning (NeurIPS 2025)
2. Axelrod (1984) - Evolution of Cooperation
3. Dorigo & Stützle (2004) - Ant Colony Optimization

**Software Engineering & Code Reuse:**
4. Mockus et al. (2002) - "Two Case Studies of Open Source Software Development" (ACM TOSEM)
5. Lerner & Tirole (2002) - "Some Simple Economics of Open Source" (Journal of Industrial Economics)
6. Raymond (1999) - "The Cathedral and the Bazaar"

**Technical Debt & Quality:**
7. Kruchten et al. (2012) - "Technical Debt: From Metaphor to Theory" (IEEE Software)
8. Zazworka et al. (2011) - "Comparing Four Approaches for Technical Debt Identification"

**Knowledge Transfer:**
9. Reagans & McEvily (2003) - "Network Structure and Knowledge Transfer" (Admin Science Quarterly)
10. Hansen (1999) - "The Search-Transfer Problem" (Admin Science Quarterly)

**Developer Behavior:**
11. Vasilescu et al. (2015) - "Quality and Productivity Outcomes Relating to Continuous Integration" (FSE)
12. Pinto et al. (2018) - "What is the Vocabulary of Flaky Tests?" (MSR)

---

## 6. Implementation Checklist

### Week 1: Core Framework
- [ ] Copy `nested_learning_enhanced.py` to `marcus-2.0/` directory
- [ ] Create `EngineeringCreditStrategy` enum
- [ ] Implement `MarcusPlatformSimulation` class
- [ ] Define engineering scenarios (4-6 scenarios)
- [ ] Run basic simulation (20 engineers, 100 generations)
- [ ] Validate strategy distribution emerges
- [ ] Write unit tests for strategy mechanics

### Week 2: Context Awareness
- [ ] Define `EngineeringContext` dataclass
- [ ] Implement `EngineeringPheromone` class
- [ ] Create context-aware decision engine
- [ ] Add pheromone propagation logic
- [ ] Test context sensitivity (same engineer, different contexts)
- [ ] Validate high-pressure → copy-paste correlation
- [ ] Validate high-visibility → proper attribution correlation

### Week 3: Knowledge Transfer
- [ ] Implement direct transfer (pair programming)
- [ ] Implement indirect transfer (code reading)
- [ ] Implement cultural transmission (onboarding)
- [ ] Create knowledge graph structure
- [ ] Add team culture emergence metrics
- [ ] Run long-term simulation (500+ generations)
- [ ] Validate team convergence on norms

### Week 4: Quality & Debt
- [ ] Implement technical debt accumulation
- [ ] Add code quality scoring
- [ ] Calculate velocity-quality ratios
- [ ] Measure knowledge concentration (bus factor)
- [ ] Track cultural health over time
- [ ] Run 1000-generation simulation
- [ ] Generate quality dashboard

### Week 5: Agent Integration
- [ ] Write `.claude/agents/marcus.md`
- [ ] Create example use cases
- [ ] Update main simulation docs
- [ ] Add integration tests
- [ ] Document in roadmap
- [ ] Create Marcus examples directory
- [ ] Final validation and review

---

## 7. Open Questions & Decisions

### Design Decisions
**Q1:** Should Marcus be purely analytical or also generative?
- **Option A:** Analytical only (study existing team behavior)
- **Option B:** Generative (suggest optimal strategies)
- **Recommendation:** Start with A, add B in v2

**Q2:** How to handle team size scaling?
- **Challenge:** 100 engineers = 4,950 pairwise interactions/generation
- **Options:**
  - Limit team size to 50 engineers
  - Use hierarchical teams (reduce interaction density)
  - Sample interactions (Monte Carlo)
- **Recommendation:** Start with 20-50, optimize later

**Q3:** Integration with main simulation?
- **Option A:** Separate platform (current approach)
- **Option B:** Merge into main simulation
- **Recommendation:** Keep separate initially, integrate if valuable

### Research Questions
1. What's the optimal balance of attribution strategies?
2. How does team culture form? (top-down vs. emergent)
3. Can interventions prevent technical debt accumulation?
4. What's the ROI of documentation/attribution time?

---

## 8. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Complexity explosion** | High | Medium | Start small (20 engineers), scale carefully |
| **Unrealistic assumptions** | Medium | Medium | Validate against engineering research |
| **Integration challenges** | Medium | Low | Keep as separate platform initially |
| **Computational cost** | Low | Low | Optimize critical paths, use caching |
| **Scope creep** | Medium | High | Strict phase gates, MVP first |

---

## 9. Timeline & Milestones

### Month 1: Foundation
- **Week 1:** Core framework (simulation running)
- **Week 2:** Context awareness (realistic decisions)
- **Week 3:** Knowledge transfer (team dynamics)
- **Week 4:** Quality metrics (long-term impact)

### Month 2: Refinement
- **Week 5:** Agent integration (usable by others)
- **Week 6:** Testing & validation (research alignment)
- **Week 7:** Documentation & examples
- **Week 8:** Polish & review

### Month 3: Research & Insights
- Run full studies (1000+ generation simulations)
- Generate insights for real engineering teams
- Publish findings (blog post, internal wiki)
- Consider academic paper (if novel insights)

---

## 10. Deliverables

### Code
- `src/platform/marcus-2.0/marcus_platform_sim.py` (~1,500 lines)
- `src/platform/marcus-2.0/engineering_strategies.py` (~500 lines)
- `src/platform/marcus-2.0/context_engine.py` (~400 lines)
- `src/platform/marcus-2.0/knowledge_graph.py` (~600 lines)
- `src/platform/marcus-2.0/debt_tracker.py` (~400 lines)

### Documentation
- `.claude/agents/marcus.md` (agent definition)
- `src/platform/marcus-2.0/README.md` (platform guide)
- `src/platform/marcus-2.0/RESEARCH_CITATIONS.md` (academic sources)
- `docs/wiki/Marcus_2.0_Platform_Engineering.md` (integration docs)

### Examples
- `scripts/marcus_examples/deadline_pressure.py`
- `scripts/marcus_examples/oss_contribution.py`
- `scripts/marcus_examples/team_culture_formation.py`
- `scripts/marcus_examples/debt_intervention.py`

### Results
- Simulation results (JSON)
- Quality dashboards (visualizations)
- Research insights (markdown reports)

---

## 11. Future Enhancements (v3.0+)

### Advanced Features
- **Code Analysis Integration:** Parse real codebases for attribution patterns
- **LLM-Powered Agents:** Use GPT-4 as engineers (more realistic)
- **Multi-Team Simulation:** Model cross-team knowledge transfer
- **Intervention Testing:** A/B test policies (e.g., mandatory attribution)

### Research Extensions
- **OSS Ecosystem Modeling:** Model entire open-source communities
- **Documentation Citation:** Study Stack Overflow attribution patterns
- **Infrastructure Patterns:** How Kubernetes patterns spread across orgs
- **Developer Onboarding:** Optimize knowledge transfer for new hires

---

## 12. Conclusion

**Marcus 2.0 represents a significant evolution:**
- **Marcus 1.0:** Task-focused platform engineer (build a system)
- **Marcus 2.0:** Behavior-focused researcher (model how engineers behave)

**Key Innovation:**
Using nested learning to model realistic engineering behavior at multiple timescales (immediate decisions, pattern recognition, architectural values).

**Expected Impact:**
- Better understanding of platform engineering team dynamics
- Actionable insights for improving code quality without sacrificing velocity
- Research foundation for studying OSS contribution patterns
- Framework for optimizing knowledge transfer in teams

**Next Step:**
Approve plan and begin Phase 1 (Core Framework Adaptation).

---

**References:**
- Nested Learning Platform: `src/platform/nested-learning-citation-study/`
- Citation Integrity Archival: `plans/ARCHIVAL_COMPLETE_CITATION_INTEGRITY_20251117.md`
- Agent Definitions: `.claude/agents/`
- Main Simulation: `src/simulation/`
