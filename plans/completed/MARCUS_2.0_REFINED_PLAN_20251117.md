# Marcus 2.0 Plan Refinement
## Incorporating Learnings from Citation Integrity MVP

**Date:** November 17, 2025
**Status:** 🔧 Refined Planning Phase
**Previous Version:** `plans/MARCUS_2.0_NESTED_LEARNING_REMAKE.md`

---

## Changes from Original Plan

### 1. Integration with Citation Integrity MVP

**Branch Reference:** `feature/citation-platform`

**What Was Built:**
- Citation verification tools (`citationChecker.py`, `autoSearchCitations.py`)
- Citation verifier agent (autonomous verification specialist)
- PDF downloading and verification pipeline
- Verified citation database system
- Provenance tracking integration with GameState

**Key Learning:** The Citation Integrity MVP is a **quality assurance tool** (verify YOUR citations), while Marcus 2.0 is a **behavior modeling platform** (study THEIR behavior). They are complementary, not redundant.

**Integration Points:**
1. **Data Source:** Use citation verification results as training data for Marcus 2.0
   - Real citation patterns from the project → model calibration
   - Verified vs. unverified distribution → strategy initialization

2. **Validation:** Use citation checker to verify Marcus 2.0's realism
   - Does Marcus 2.0 predict actual project citation behavior?
   - Test interventions: "What if we had mandatory citation checking from day 1?"

3. **Shared Infrastructure:**
   - Both use `research/` directory for papers
   - Both track provenance (Citation MVP = current state, Marcus 2.0 = future predictions)
   - Both integrate with `.claude/agents/` system

---

### 2. Timeline Adjustment (More Realistic)

**Original Estimate:** 5 weeks
**Refined Estimate:** 8-10 weeks

**Justification:**
Looking at Citation Integrity MVP development (6 weeks for production system with 94.2% test coverage), Marcus 2.0 will need more time because:
- Behavioral modeling is harder than tooling
- Multi-agent simulations need extensive validation
- Integration with main simulation adds complexity

**New Timeline:**

#### Phase 0: Prep & Learning (Week 1)
- **NEW:** Study Citation Integrity MVP codebase
- Extract actual citation patterns from project history
- Set up shared infrastructure
- Define success criteria based on real data

#### Phase 1: Core Framework (Weeks 2-3)
- Adapt nested learning for platform engineering
- Implement basic strategy system
- **Changed:** Add integration hooks for Citation MVP from start

#### Phase 2: Context Awareness (Weeks 3-4)
- Engineering context dimensions
- Pheromone enhancement
- **New:** Validate against Citation MVP real data

#### Phase 3: Knowledge Transfer (Weeks 5-6)
- Team dynamics
- Cultural transmission
- **New:** Model actual team behavior from project

#### Phase 4: Quality & Debt (Weeks 7-8)
- Technical debt tracking
- Long-term simulation
- **New:** Compare predictions vs. actual Citation MVP outcomes

#### Phase 5: Integration & Polish (Weeks 9-10)
- Agent definition
- Documentation
- **New:** Comprehensive comparison with Citation MVP
- **New:** Case study write-up

---

### 3. Scope Refinement

#### Reduced Scope (MVP)

**Cut from Phase 1:**
- ❌ Multiple team cultures (start with "balanced" only)
- ❌ Advanced scenarios (just deadline pressure + OSS contribution)
- ✅ Keep: Basic strategy system, multi-level memory

**Cut from Phase 2:**
- ❌ Reputation stake dimension (too complex for MVP)
- ❌ Prior art availability (add in v2)
- ✅ Keep: Deadline pressure, visibility, team culture

**Cut from Phase 3:**
- ❌ Cross-team knowledge transfer (single team only)
- ❌ Documentation citation patterns (focus on code attribution)
- ✅ Keep: Pair programming, code reading, onboarding

**Cut from Phase 4:**
- ❌ Bus factor calculation (nice-to-have)
- ❌ Cultural health deviation metrics (v2 feature)
- ✅ Keep: Technical debt accumulation, quality scoring

#### Added Scope (Critical for Success)

**Added to Phase 0:**
- ✅ Extract real citation data from Citation MVP branch
- ✅ Baseline current project behavior
- ✅ Define validation criteria

**Added to All Phases:**
- ✅ Continuous comparison with Citation MVP reality
- ✅ Validation checkpoints (does model match reality?)

---

### 4. Success Criteria (More Specific)

#### Technical Validation

**Original (vague):**
- ✅ Simulation runs 1000+ generations
- ✅ Multi-level memory forms

**Refined (measurable):**
- ✅ Simulation runs 1000+ generations **with <5% crashes**
- ✅ Multi-level memory shows **distinct update frequencies (1x, 10x, 50x)**
- ✅ Context changes strategy distribution **by >20% (statistical test)**
- ✅ Team culture converges **within 50 generations (6 months simulated)**
- ✅ Technical debt compounds **predictably (R² > 0.9)**

#### Research Validation (NEW)

**Against Citation Integrity MVP:**
- ✅ Marcus 2.0 predicts actual project citation behavior **within 10% error**
- ✅ Strategy distribution matches observed patterns **in project history**
- ✅ Debt accumulation aligns **with actual refactoring needs**

**Against Academic Literature:**
- ✅ Results consistent **with Mockus et al. (2002) OSS findings**
- ✅ Behavior matches **Kruchten et al. (2012) debt patterns**
- ✅ Convergence aligns **with Axelrod (1984) cooperation evolution**

---

### 5. Risk Mitigation (More Concrete)

#### Risk 1: Model Doesn't Match Reality

**Original Mitigation:** "Validate against engineering research"

**Refined Mitigation:**
1. **Week 1:** Extract baseline from Citation MVP (actual citation rates, patterns)
2. **Week 3:** First validation checkpoint (does basic model predict real behavior?)
3. **Week 6:** Second validation (does context model explain observed variations?)
4. **Week 9:** Final validation (does full model predict project outcomes?)
5. **Acceptance Criteria:** <15% prediction error on Citation MVP historical data

#### Risk 2: Integration Complexity

**Original Mitigation:** "Keep as separate platform"

**Refined Mitigation:**
1. **Shared schema from day 1:** Both systems use same provenance types
2. **Adapters layer:** `marcus_to_citation_mvp.py` and vice versa
3. **Incremental integration:** Week 1 (read only), Week 5 (write), Week 9 (bidirectional)
4. **Fallback plan:** If integration too complex, keep separate with manual data transfer

#### Risk 3: Computational Cost

**Original Mitigation:** "Optimize critical paths"

**Refined Mitigation:**
1. **Profiling from Week 2:** Measure simulation speed continuously
2. **Performance budget:** <5 minutes for 1000 generations with 20 agents
3. **Optimization targets:** Identified in Week 3 profiling
4. **Fallback plan:** Reduce to 10 agents or 500 generations if needed

---

### 6. Deliverables (More Specific)

#### Code Deliverables

**Phase 0 (Week 1):**
- ✅ `scripts/extract_citation_mvp_data.py` (extract baseline from Citation MVP)
- ✅ `src/platform/marcus-2.0/citation_mvp_adapter.py` (integration layer)

**Phase 1 (Weeks 2-3):**
- ✅ `src/platform/marcus-2.0/marcus_platform_sim.py` (~800 lines, down from 1500)
- ✅ `src/platform/marcus-2.0/engineering_strategies.py` (~300 lines, down from 500)
- ✅ Unit tests for strategy mechanics (20+ tests)

**Phase 2 (Weeks 3-4):**
- ✅ `src/platform/marcus-2.0/context_engine.py` (~250 lines, down from 400)
- ✅ Context sensitivity tests (15+ tests)

**Phase 3 (Weeks 5-6):**
- ✅ `src/platform/marcus-2.0/knowledge_transfer.py` (~400 lines, down from 600)
- ✅ Team dynamics tests (10+ tests)

**Phase 4 (Weeks 7-8):**
- ✅ `src/platform/marcus-2.0/debt_tracker.py` (~300 lines, down from 400)
- ✅ Long-term simulation results (1000 gen, 3 scenarios)

**Phase 5 (Weeks 9-10):**
- ✅ `.claude/agents/marcus.md` (agent definition)
- ✅ Validation report comparing Marcus 2.0 vs. Citation MVP
- ✅ Case study write-up

**Total Code Estimate:** ~2,500 lines (down from ~3,900)

#### Documentation Deliverables

**New Documentation:**
- ✅ `src/platform/marcus-2.0/CITATION_MVP_INTEGRATION.md` (how systems connect)
- ✅ `src/platform/marcus-2.0/VALIDATION_REPORT.md` (model accuracy vs. reality)
- ✅ `src/platform/marcus-2.0/CASE_STUDY.md` (lessons from Citation MVP)

**Updated Documentation:**
- ✅ `README.md` (add Marcus 2.0 section)
- ✅ `docs/wiki/README.md` (document both Citation MVP and Marcus 2.0)
- ✅ `.claude/agents/citation-verifier.md` (add reference to Marcus 2.0)

---

### 7. Priority Adjustments

#### Original Priority: MEDIUM
#### Refined Priority: MEDIUM-HIGH

**Justification:**
- Citation Integrity MVP showed value of behavioral modeling
- Real data available from project makes validation possible
- Fills gap: we have QA tools (Citation MVP) but no behavior insights

**Roadmap Position:**
- After: Current CRITICAL/HIGH simulation work
- Before: Speculative far-future features
- Parallel with: Documentation and testing improvements

---

## New Implementation Plan

### Week 1: Preparation & Data Extraction

**Goal:** Understand Citation MVP and extract baseline data

**Tasks:**
1. ✅ Clone Citation MVP branch locally
2. ✅ Extract citation patterns from project history
   ```bash
   git checkout feature/citation-platform
   python scripts/extract_citation_mvp_data.py > baseline_data.json
   ```
3. ✅ Analyze actual behavior:
   - What % of citations were properly attributed?
   - How did this change over project timeline?
   - What contexts led to different behaviors?
4. ✅ Create integration adapter:
   ```python
   # citation_mvp_adapter.py
   def load_citation_mvp_history():
       """Load real citation data from Citation MVP branch."""
       pass

   def compare_model_vs_reality(marcus_results, mvp_data):
       """Validate Marcus 2.0 against actual project behavior."""
       pass
   ```
5. ✅ Set baseline metrics:
   - Citation MVP: 96% reduction in fabrication (baseline before intervention)
   - Target: Marcus 2.0 should predict this improvement

**Validation Checkpoint:**
- [ ] Can extract >100 citation instances from project
- [ ] Baseline behavior patterns identified
- [ ] Success criteria defined (prediction error <15%)

**Deliverables:**
- `baseline_data.json` (real citation patterns)
- `citation_mvp_adapter.py` (integration code)
- `VALIDATION_CRITERIA.md` (success metrics)

---

### Weeks 2-3: Core Framework (Validated Against Reality)

**Goal:** Build basic simulation that predicts Citation MVP behavior

**Tasks:**
1. ✅ Implement `EngineeringCreditStrategy` (5 strategies)
2. ✅ Adapt nested learning simulation
3. ✅ Add Citation MVP data loader
4. ✅ Run baseline simulation:
   - 20 engineers, 100 generations
   - No interventions (natural behavior)
   - Compare output vs. Citation MVP baseline
5. ✅ Tune parameters until model matches reality (±15%)

**Validation Checkpoint:**
- [ ] Model predicts Citation MVP baseline within 15% error
- [ ] Strategy distribution reasonable (not all defect or all cooperate)
- [ ] Multi-level memory forms (distinct update patterns)

**Deliverables:**
- `marcus_platform_sim.py` (core simulation)
- `engineering_strategies.py` (5 strategies)
- Baseline validation report

---

### Weeks 3-4: Context Awareness (Explain Variations)

**Goal:** Model why behavior varied across project timeline

**Tasks:**
1. ✅ Implement context dimensions (deadline, visibility, culture)
2. ✅ Add pheromone enhancements
3. ✅ Test context sensitivity:
   - High deadline pressure → more copy-paste?
   - High visibility (OSS) → more proper credit?
4. ✅ Validate against Citation MVP history:
   - Did behavior change during crunch periods?
   - Did OSS contributions have better attribution?

**Validation Checkpoint:**
- [ ] Context changes strategy distribution by >20%
- [ ] Model explains observed variations in Citation MVP
- [ ] Statistical tests confirm context effects (p < 0.05)

**Deliverables:**
- `context_engine.py` (context-aware decisions)
- Context sensitivity analysis
- Comparison report vs. Citation MVP timeline

---

### Weeks 5-6: Knowledge Transfer (Team Dynamics)

**Goal:** Model how citation norms formed in team

**Tasks:**
1. ✅ Implement knowledge transfer mechanisms
2. ✅ Model team culture emergence
3. ✅ Test onboarding effects:
   - New team members adopt existing norms?
   - How quickly does culture stabilize?
4. ✅ Validate against Citation MVP:
   - Did team behavior converge over time?
   - How did new contributors adapt?

**Validation Checkpoint:**
- [ ] Team culture converges within 50 generations (6 months)
- [ ] New members adopt norms within 10 generations (1 month)
- [ ] Matches observed Citation MVP team dynamics

**Deliverables:**
- `knowledge_transfer.py` (team dynamics)
- Culture emergence analysis
- Team behavior comparison report

---

### Weeks 7-8: Quality & Debt (Long-term Impact)

**Goal:** Model technical debt from attribution patterns

**Tasks:**
1. ✅ Implement debt accumulation model
2. ✅ Add quality scoring system
3. ✅ Run long-term simulations (1000 generations = 10 years)
4. ✅ Validate against Citation MVP outcomes:
   - Did poor attribution lead to refactoring needs?
   - Did quality improve after intervention (citation checking)?

**Validation Checkpoint:**
- [ ] Debt compounds predictably (R² > 0.9)
- [ ] Quality correlates with attribution strategy (r > 0.7)
- [ ] Model predicts Citation MVP improvement (96% reduction)

**Deliverables:**
- `debt_tracker.py` (debt modeling)
- Long-term simulation results (3 scenarios)
- Intervention analysis report

---

### Weeks 9-10: Integration & Case Study

**Goal:** Create usable agent and document findings

**Tasks:**
1. ✅ Write `.claude/agents/marcus.md`
2. ✅ Create integration tests
3. ✅ Write comprehensive case study:
   - What did Citation MVP teach us?
   - How well does Marcus 2.0 predict reality?
   - What interventions would have helped earlier?
4. ✅ Documentation updates
5. ✅ Polish and review

**Validation Checkpoint:**
- [ ] Agent can be invoked via Task tool
- [ ] Case study answers: "What if we had Marcus 2.0 from day 1?"
- [ ] All validation metrics passed (<15% error, >0.9 R², etc.)

**Deliverables:**
- `.claude/agents/marcus.md` (agent definition)
- `CASE_STUDY.md` (lessons learned)
- `VALIDATION_REPORT.md` (final accuracy metrics)
- Updated project documentation

---

## Comparison: Original vs. Refined Plan

| Aspect | Original Plan | Refined Plan | Reason |
|--------|--------------|--------------|--------|
| **Timeline** | 5 weeks | 8-10 weeks | Realistic based on Citation MVP |
| **Code Size** | ~3,900 lines | ~2,500 lines | Cut nice-to-haves, focus on MVP |
| **Validation** | Vague | Specific metrics | Need measurable success |
| **Integration** | Optional | Required | Learn from real data |
| **Priority** | MEDIUM | MEDIUM-HIGH | Real use case identified |
| **Scope** | Ambitious | Focused MVP | Ship useful tool, not research project |

---

## Key Decisions Made

### Decision 1: Required Integration with Citation MVP
**Rationale:** Real data makes validation possible. Without it, Marcus 2.0 is just speculation.

### Decision 2: 8-10 Week Timeline
**Rationale:** Citation MVP took 6 weeks for tooling. Behavior modeling is harder. Be realistic.

### Decision 3: Cut Advanced Features
**Rationale:** Multi-team, reputation, bus factor = nice-to-haves. Core behavior model = must-have.

### Decision 4: Validation Gates Every 2 Weeks
**Rationale:** Catch model drift early. If not matching reality by Week 3, pivot.

### Decision 5: Case Study as Deliverable
**Rationale:** "What if we had Marcus 2.0 from day 1 of Citation MVP?" = compelling story.

---

## Next Steps

1. **Review this refined plan**
2. **Approve or adjust further**
3. **Begin Week 1: Checkout Citation MVP branch and extract baseline data**

---

## Questions for Review

**Q1:** Is 8-10 weeks acceptable, or should we reduce scope further?
**Q2:** Should Marcus 2.0 integration be optional or required?
**Q3:** What validation error threshold is acceptable? (Currently 15%)
**Q4:** Priority MEDIUM-HIGH or keep at MEDIUM?
**Q5:** Should we write academic paper if results are novel?

---

**Status:** Ready for review and approval
**Next Action:** Approve plan → Begin Week 1 → Extract Citation MVP baseline data
