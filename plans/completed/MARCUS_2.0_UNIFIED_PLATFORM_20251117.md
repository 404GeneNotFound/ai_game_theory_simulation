# Marcus 2.0: Unified Citation Platform
## Combining Citation Integrity MVP + Nested Learning Behavioral Modeling

**Created:** November 17, 2025
**Status:** 🎯 Unified Vision
**Priority:** MEDIUM-HIGH
**Complexity:** High (System integration + behavioral modeling)

---

## Executive Summary

**Vision:** Build ONE unified platform that both verifies citations AND models the behavioral dynamics of how citation cultures emerge in teams.

**Not:** Citation MVP validates Marcus 2.0 as separate systems
**Instead:** Merge both into unified Marcus 2.0 that does BOTH simultaneously

---

## The Unified System

```
┌─────────────────────────────────────────────────────────────┐
│              Marcus 2.0 Unified Platform                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────────────────────────────────────────────────┐ │
│  │         LAYER 1: Citation Integrity (MVP)             │ │
│  │                                                         │ │
│  │  • Verify citations (citationChecker.py)              │ │
│  │  • Download PDFs (autoSearchCitations.py)             │ │
│  │  • Extract claims (PDF reading)                       │ │
│  │  • Track provenance (database)                        │ │
│  │  • Real-time verification                             │ │
│  └───────────────────────────────────────────────────────┘ │
│                          │                                  │
│                          ↓ (feeds data to)                  │
│  ┌───────────────────────────────────────────────────────┐ │
│  │      LAYER 2: Nested Learning Behavior Model          │ │
│  │                                                         │ │
│  │  • Multi-level memory (Fast/Medium/Slow)              │ │
│  │  • Engineering strategies (Credit → Claim)            │ │
│  │  • Context-aware decisions                            │ │
│  │  • Team culture emergence                             │ │
│  │  • Future behavior prediction                         │ │
│  └───────────────────────────────────────────────────────┘ │
│                          │                                  │
│                          ↓ (suggests)                       │
│  ┌───────────────────────────────────────────────────────┐ │
│  │           LAYER 3: Intervention Engine                 │ │
│  │                                                         │ │
│  │  • Predict outcomes ("What if we require reviews?")   │ │
│  │  • Suggest interventions (optimal policies)           │ │
│  │  • Track effectiveness (did it work?)                 │ │
│  │  • Continuous learning (update model with results)    │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## How It Works: The Unified Flow

### Real-Time Operation

```python
# 1. Developer writes code with citation
code = """
# Based on Smith et al. (2023) approach
def optimize():
    ...
"""

# 2. LAYER 1: Citation Integrity verifies immediately
verification_result = marcus.verify_citation("Smith et al. (2023)")
# → Result: UNVERIFIED (not in database)

# 3. LAYER 2: Behavior model learns from this event
marcus.observe_citation_event(
    agent="developer_alice",
    strategy="copy_paste",  # No proper citation
    context={
        "deadline_pressure": 0.8,  # High pressure
        "code_visibility": 0.2,    # Internal code
        "team_culture": "move_fast"
    }
)

# 4. LAYER 3: Suggest intervention
if marcus.predict_debt_accumulation() > 0.5:
    marcus.suggest_intervention(
        "High copy-paste detected. Suggest: mandatory citation review before merge"
    )
```

### Continuous Learning Loop

```
Current Behavior → Verify & Observe → Model Updates → Predict Future → Suggest Intervention
       ↑                                                                        ↓
       └────────────────────── Track Effectiveness ←─────────────────────────┘
```

---

## Key Features of Unified Platform

### 1. Real-Time Verification + Behavioral Learning

**What Citation MVP Does:**
- Verify citation exists in database
- Download PDF if missing
- Check claim against paper content

**What Nested Learning Adds:**
- Track WHO made the citation (agent identity)
- Learn THEIR citation patterns over time
- Predict FUTURE behavior based on context

**Combined Power:**
```python
# Traditional (MVP only):
verify("Smith 2023")  # → VERIFIED or UNVERIFIED

# Unified (Marcus 2.0):
marcus.verify_and_learn(
    citation="Smith 2023",
    agent="developer_bob",
    context=current_context
)
# → VERIFIED + "Bob tends to copy-paste under deadline pressure"
# → Prediction: "Bob will likely skip citation in next 3 commits"
# → Suggestion: "Require citation review for Bob's next PR"
```

### 2. Multi-Level Memory for Citation Behavior

**Fast Memory (L1) - Immediate Verification**
- Real-time citation checking
- Instant feedback ("This citation is fabricated!")
- Updates every commit

**Medium Memory (L2) - Pattern Recognition**
- "This developer always cites properly for OSS"
- "Team cuts corners during sprint end"
- Updates every sprint

**Slow Memory (L3) - Cultural Values**
- "Our team values proper attribution"
- "Move-fast culture vs. quality-first"
- Updates quarterly or after major incidents

### 3. Context-Aware Citation Verification

**Traditional verification:**
```python
verify("Smith 2023")  # Same result regardless of who/when/why
```

**Context-aware (Marcus 2.0):**
```python
marcus.verify_with_context(
    citation="Smith 2023",
    developer="alice",
    deadline=2,  # 2 days until sprint end
    visibility="public",  # Open-source PR
    history=alice.past_citations
)
# → UNVERIFIED
# → Risk Assessment: HIGH (Alice usually cites properly, deadline pressure)
# → Recommendation: "Alice likely forgot due to pressure. Auto-suggest citation."
```

### 4. Team Culture Modeling

**Track team-wide patterns:**
```python
team_culture = marcus.analyze_team_culture()
# Output:
{
    "attribution_rate": 0.65,  # 65% of code properly attributed
    "strategy_distribution": {
        "proper_credit": 0.40,
        "adapt_pattern": 0.25,
        "copy_paste": 0.30,
        "claim_original": 0.05
    },
    "culture_type": "balanced",  # Not move-fast, not quality-first
    "trend": "improving",  # Attribution rate increasing
    "convergence": 0.7  # Team norms stabilizing
}
```

### 5. Predictive Interventions

**Predict future issues:**
```python
prediction = marcus.predict_next_sprint()
# Output:
{
    "predicted_fabrication_rate": 0.12,  # 12% will be fabricated
    "high_risk_developers": ["bob", "charlie"],
    "recommended_interventions": [
        "Require citation review before merge",
        "Pair bob with alice (high attribution rate)",
        "Add 20% buffer to sprint (reduce pressure)"
    ],
    "expected_improvement": {
        "with_intervention": 0.03,  # 3% fabrication
        "without_intervention": 0.12  # 12% fabrication
    }
}
```

---

## Implementation Architecture

### Core Components

#### 1. Citation Integrity Core (from MVP)

```python
class CitationIntegrityCore:
    """Layer 1: Real-time verification (from MVP)"""

    def __init__(self):
        self.checker = CitationChecker()  # From MVP
        self.searcher = AutoSearchCitations()  # From MVP
        self.database = VerifiedCitationDB()  # From MVP

    def verify_citation(self, citation: str) -> VerificationResult:
        """Verify citation against database"""
        return self.checker.check(citation)

    def download_paper(self, citation: str) -> Path:
        """Download PDF if missing"""
        return self.searcher.download(citation)

    def verify_claim(self, citation: str, claim: str) -> bool:
        """Check claim against paper content"""
        pdf = self.download_paper(citation)
        return self.check_claim_in_pdf(pdf, claim)
```

#### 2. Nested Learning Engine (from Platform)

```python
class NestedLearningEngine:
    """Layer 2: Behavioral modeling (from Nested Learning)"""

    def __init__(self):
        self.agents = {}  # Developer agents
        self.memory_system = MultiLevelMemory()  # Fast/Medium/Slow
        self.pheromones = AssociativeMemoryPheromones()
        self.strategy_system = EngineeringCreditStrategy

    def observe_citation_event(self, agent_id: str, citation: str,
                              strategy: Strategy, context: Context):
        """Learn from citation event"""
        agent = self.agents[agent_id]
        agent.update_memory(strategy, context)
        self.pheromones.deposit(context, strategy)

    def predict_behavior(self, agent_id: str, context: Context) -> Strategy:
        """Predict what agent will do in context"""
        agent = self.agents[agent_id]
        return agent.choose_strategy(context, self.pheromones)

    def analyze_team_culture(self) -> CultureAnalysis:
        """Analyze team-wide patterns"""
        return self.compute_culture_metrics()
```

#### 3. Unified Marcus Platform

```python
class MarcusUnifiedPlatform:
    """Layer 3: Combined system"""

    def __init__(self):
        self.citation_core = CitationIntegrityCore()
        self.behavior_engine = NestedLearningEngine()
        self.intervention_engine = InterventionEngine()

    def verify_and_learn(self, citation: str, agent_id: str,
                         context: Context) -> UnifiedResult:
        """UNIFIED: Verify + Learn + Predict"""

        # Step 1: Verify citation (MVP functionality)
        verification = self.citation_core.verify_citation(citation)

        # Step 2: Infer strategy from verification result
        if verification.status == "VERIFIED":
            strategy = Strategy.PROPER_CREDIT
        elif verification.status == "UNVERIFIED":
            # Check if developer tried to cite or just copied
            strategy = self.infer_strategy(citation, agent_id)
        else:  # FABRICATED
            strategy = Strategy.CLAIM_ORIGINAL

        # Step 3: Update behavioral model (Nested Learning)
        self.behavior_engine.observe_citation_event(
            agent_id, citation, strategy, context
        )

        # Step 4: Predict future behavior
        future_prediction = self.behavior_engine.predict_behavior(
            agent_id, context
        )

        # Step 5: Suggest interventions if needed
        interventions = self.intervention_engine.suggest(
            current_strategy=strategy,
            predicted_strategy=future_prediction,
            team_culture=self.behavior_engine.analyze_team_culture()
        )

        return UnifiedResult(
            verification=verification,
            observed_strategy=strategy,
            predicted_future=future_prediction,
            suggested_interventions=interventions
        )
```

---

## Implementation Phases

### Phase 1: Foundation Integration (Weeks 1-2)

**Goal:** Merge MVP codebase with Nested Learning platform

**Tasks:**
1. ✅ Copy Citation MVP code to `src/platform/marcus-2.0/`
   - `citation_integrity/` (MVP tools)
   - `nested_learning/` (behavior model)
   - `unified/` (integration layer)

2. ✅ Create unified data model:
   ```python
   @dataclass
   class CitationEvent:
       citation: str
       agent_id: str
       timestamp: datetime
       context: Context
       verification: VerificationResult  # From MVP
       strategy: Strategy  # From Nested Learning
   ```

3. ✅ Build integration layer:
   - Map verification results → strategies
   - Feed citation events → behavior model
   - Connect both systems with shared state

4. ✅ Basic unified workflow:
   - Developer makes citation
   - System verifies AND learns simultaneously
   - Returns combined result

**Validation:**
- [ ] Can verify citation AND update behavior model in one call
- [ ] Both systems share same citation database
- [ ] Integration tests pass (20+ tests)

**Deliverables:**
- `src/platform/marcus-2.0/citation_integrity/` (MVP tools)
- `src/platform/marcus-2.0/nested_learning/` (behavior model)
- `src/platform/marcus-2.0/unified/marcus_platform.py` (integration)
- Integration tests

---

### Phase 2: Multi-Level Memory for Citations (Weeks 3-4)

**Goal:** Add multi-level memory to citation verification

**Tasks:**
1. ✅ Extend CitationIntegrityCore with memory:
   ```python
   class MemoryAwareCitationCore(CitationIntegrityCore):
       def __init__(self):
           super().__init__()
           self.fast_memory = {}   # Recent citations (last 10 commits)
           self.medium_memory = {} # Sprint patterns (last 2 weeks)
           self.slow_memory = {}   # Cultural norms (last quarter)
   ```

2. ✅ Context-aware verification:
   - Fast: "Did developer just cite this 5 minutes ago?" (duplicate)
   - Medium: "Does developer usually cite this type of source?"
   - Slow: "Does team culture value attribution?"

3. ✅ Pheromone-based suggestions:
   - Suggest citations based on what similar developers used
   - "Alice cited Smith 2023 for similar function"
   - Context-aware recommendations

**Validation:**
- [ ] Memory levels update at different frequencies (1x, 10x, 50x)
- [ ] Suggestions improve over time (>20% better citation rates)
- [ ] Context changes verification priorities

**Deliverables:**
- `memory_aware_verification.py` (multi-level memory for citations)
- Pheromone-based suggestion system
- Context sensitivity tests

---

### Phase 3: Team Culture & Predictive Modeling (Weeks 5-6)

**Goal:** Model how citation cultures emerge and predict future behavior

**Tasks:**
1. ✅ Team culture analysis:
   - Track team-wide attribution rates
   - Identify cultural patterns (move-fast vs. quality-first)
   - Detect culture shifts (improving/degrading)

2. ✅ Future behavior prediction:
   ```python
   def predict_next_sprint(team_state, deadline_pressure):
       """Predict citation behavior for upcoming sprint"""
       model = self.behavior_engine.get_team_model()
       predicted_events = model.simulate(
           num_commits=100,
           context=Context(deadline_pressure=deadline_pressure)
       )
       return predicted_events.citation_stats()
   ```

3. ✅ Individual developer modeling:
   - Track each developer's citation patterns
   - Predict behavior based on context + history
   - Identify high-risk developers (likely to skip citations)

**Validation:**
- [ ] Team culture converges over time
- [ ] Predictions accurate within 15% error
- [ ] Can identify high-risk situations in advance

**Deliverables:**
- `team_culture_analyzer.py` (culture metrics)
- `behavior_predictor.py` (future predictions)
- Developer risk scoring system

---

### Phase 4: Intervention Engine (Weeks 7-8)

**Goal:** Suggest optimal interventions to improve citation culture

**Tasks:**
1. ✅ Intervention testing:
   ```python
   def test_intervention(intervention: Intervention) -> Prediction:
       """Simulate impact of intervention"""
       baseline = self.predict_next_sprint(current_state)
       with_intervention = self.predict_next_sprint(
           current_state.apply(intervention)
       )
       return compare(baseline, with_intervention)
   ```

2. ✅ Intervention library:
   - Require citation review before merge
   - Pair high-risk with high-attribution developers
   - Add time buffer to reduce deadline pressure
   - Mandatory citation templates
   - Automated citation suggestions

3. ✅ Continuous learning:
   - Track which interventions actually worked
   - Update model based on effectiveness
   - Improve future recommendations

**Validation:**
- [ ] Can test 5+ different interventions
- [ ] Predicts intervention impact accurately
- [ ] Learns from actual intervention results

**Deliverables:**
- `intervention_engine.py` (suggestion system)
- Intervention library (5+ interventions)
- Effectiveness tracking system

---

### Phase 5: Production Integration & Polish (Weeks 9-10)

**Goal:** Make Marcus 2.0 production-ready and usable

**Tasks:**
1. ✅ Agent definition:
   ```markdown
   # Marcus 2.0 - Platform Engineer (Unified)

   **Capabilities:**
   - Real-time citation verification (MVP)
   - Behavioral pattern recognition (Nested Learning)
   - Team culture analysis
   - Future behavior prediction
   - Intervention recommendations

   **Usage:**
   "Marcus, analyze our team's citation behavior over the last sprint
   and suggest interventions to improve attribution rates."
   ```

2. ✅ CLI interface:
   ```bash
   # Verify and learn from single citation
   marcus verify "Smith et al. (2023)" --developer alice --context high_pressure

   # Analyze team culture
   marcus analyze-team --sprint current

   # Predict next sprint
   marcus predict --weeks 2 --scenario "high_deadline"

   # Test intervention
   marcus test-intervention "require_review" --duration 4weeks
   ```

3. ✅ Integration with main simulation:
   - AI agents in simulation use Marcus for research citations
   - Track citation behavior as part of research ecosystem
   - Model research integrity dynamics

4. ✅ Documentation and examples

**Validation:**
- [ ] Agent works via Task tool
- [ ] CLI commands functional
- [ ] Integration tests pass
- [ ] Documentation complete

**Deliverables:**
- `.claude/agents/marcus.md` (agent definition)
- CLI interface (`marcus` command)
- Integration with main simulation (optional)
- Complete documentation

---

## Success Metrics

### Technical Success

✅ **Integration:**
- MVP tools + Nested Learning work together seamlessly
- Single API call does both verification AND learning
- Shared data model for citation events

✅ **Accuracy:**
- Verification: 98.7% accuracy (from MVP)
- Prediction: <15% error on future behavior
- Culture analysis: Team patterns identified within 6 months

✅ **Performance:**
- Real-time verification (<1 second per citation)
- Behavior prediction (<5 seconds per developer)
- Team analysis (<30 seconds for 20 developers)

### Practical Success

✅ **Immediate Value:**
- Developers get instant citation verification (MVP)
- Team leads see culture analysis dashboard
- Managers get predictive insights for planning

✅ **Long-term Impact:**
- Citation fabrication <1% (MVP target)
- Attribution culture improves over time (predictable)
- Interventions show measurable effectiveness

---

## Why This Is Better Than Separate Systems

### Problem with Separate Systems

**Citation MVP (Alone):**
- ✅ Tells you IF citation is verified
- ❌ Doesn't tell you WHY developer skipped citation
- ❌ Can't predict FUTURE behavior
- ❌ No intervention recommendations

**Nested Learning (Alone):**
- ✅ Models behavior patterns
- ❌ No real citation verification
- ❌ Just simulation, not production tool
- ❌ Can't learn from actual citation events

### Unified System Advantages

**Marcus 2.0 (Combined):**
- ✅ Verifies citations in real-time (MVP strength)
- ✅ Learns from verification events (Nested Learning strength)
- ✅ Predicts future behavior (unique to combination)
- ✅ Suggests effective interventions (unique to combination)
- ✅ Continuous learning loop (unique to combination)

**Example Scenario:**

```
Developer Bob submits PR with unverified citation "Smith 2023"

Citation MVP (alone):
→ "❌ UNVERIFIED. Citation not in database."
→ End of interaction.

Nested Learning (alone):
→ Models Bob's behavior in simulation
→ No real-time feedback

Marcus 2.0 (unified):
→ "❌ UNVERIFIED. Citation not in database."
→ "⚠️ Bob usually cites properly (85% rate)."
→ "📊 Context: High deadline pressure (2 days to sprint end)."
→ "🔮 Prediction: Bob likely forgot due to time pressure."
→ "💡 Suggestion: Auto-add citation template to PR."
→ "🎯 Expected improvement: 95% → 98% citation rate."
→ Updates Bob's behavior model for future predictions.
```

---

## Timeline Summary

**Total Time:** 10 weeks
**Deliverable:** Unified Marcus 2.0 platform

```
Weeks 1-2:  Merge MVP + Nested Learning
Weeks 3-4:  Multi-level memory for citations
Weeks 5-6:  Team culture + prediction
Weeks 7-8:  Intervention engine
Weeks 9-10: Production polish + agent definition
```

---

## Deliverables Summary

### Code (~3,500 lines)
- `citation_integrity/` (1,200 lines, from MVP)
- `nested_learning/` (1,500 lines, from platform)
- `unified/` (800 lines, integration layer)

### Documentation
- Marcus 2.0 agent definition
- Unified platform guide
- Integration examples
- API documentation

### Tools
- CLI interface (`marcus` command)
- Dashboard (team culture visualization)
- Integration hooks (for main simulation)

---

## Next Steps

**Approve this unified vision?**

If yes, begin Phase 1:
1. Copy Citation MVP code to `src/platform/marcus-2.0/citation_integrity/`
2. Copy Nested Learning code to `src/platform/marcus-2.0/nested_learning/`
3. Create unified data model
4. Build integration layer

**This is the ambitious plan you wanted** - combining both systems into one powerful platform, not validating one against the other.

---

**Status:** 🎯 Ready for approval
**Recommendation:** Proceed with unified 10-week plan
**Impact:** Much more powerful than either system alone
