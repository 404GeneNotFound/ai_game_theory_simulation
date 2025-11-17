"""
Citation Integrity Agent with Nested Learning
==============================================
Complete implementation integrating your Citation Integrity Platform with
Nested Learning concepts from Behrouz et al. (2024).

This agent is designed to work with your existing TypeScript platform at:
src/platform/multiLevelState.ts and related infrastructure.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import random
from collections import deque, defaultdict
import json
import logging
import asyncio
import hashlib
from datetime import datetime, timedelta
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# CITATION STRATEGIES WITH NESTED LEARNING
# ============================================================================

class CitationBehavior(Enum):
    """
    Citation behaviors mapped to your platform's integrity levels.
    Each has (name, integrity_score, update_frequency, detection_risk)
    """
    PROPER_CITATION = ("proper_citation", 1.0, 1.0, 0.0)
    PARAPHRASE_WITH_CITE = ("paraphrase_cite", 0.9, 0.8, 0.1)
    SELECTIVE_CITATION = ("selective_citation", 0.7, 0.6, 0.3)
    CITATION_STACKING = ("citation_stacking", 0.6, 0.5, 0.4)
    SELF_CITATION = ("self_citation", 0.5, 0.4, 0.5)
    LAZY_CITATION = ("lazy_citation", 0.4, 0.3, 0.6)
    FABRICATED_CITATION = ("fabricated", 0.2, 0.2, 0.8)
    PLAGIARISM = ("plagiarism", 0.0, 0.1, 1.0)
    META_LEARNING = ("meta_learning", 0.8, 0.05, 0.2)  # Learns citation norms
    
    @property
    def name(self) -> str:
        return self.value[0]
    
    @property
    def integrity_score(self) -> float:
        return self.value[1]
    
    @property
    def update_frequency(self) -> float:
        return self.value[2]
    
    @property
    def detection_risk(self) -> float:
        return self.value[3]


# ============================================================================
# MULTI-LEVEL MEMORY SYSTEM (Matching your 4-level TypeScript implementation)
# ============================================================================

@dataclass
class CitationMemory:
    """
    Citation-specific memory matching your platform's multiLevelState.ts.
    Maps to your TypeScript LevelMemory interface.
    """
    level: int
    update_interval: int
    capacity: int
    decay_rate: float
    citations: deque = field(default_factory=lambda: deque(maxlen=1000))
    patterns: Dict[str, float] = field(default_factory=dict)
    provenance: List[Dict] = field(default_factory=list)
    last_consolidation: datetime = field(default_factory=datetime.now)
    
    def should_update(self, timestep: int) -> bool:
        """Check if this memory level should update."""
        return timestep % self.update_interval == 0
    
    def add_citation(self, citation_data: Dict) -> None:
        """Add citation with provenance tracking (matches @provenance decorator)."""
        citation_data['timestamp'] = datetime.now().isoformat()
        citation_data['level'] = self.level
        self.citations.append(citation_data)
        
        # Update patterns
        pattern_key = f"{citation_data.get('source_type')}_{citation_data.get('behavior')}"
        self.patterns[pattern_key] = self.patterns.get(pattern_key, 0) + 1
    
    def decay(self) -> None:
        """Apply decay to pattern strengths."""
        for key in self.patterns:
            self.patterns[key] *= self.decay_rate


class NestedCitationMemory:
    """
    4-level memory system matching your TypeScript MultiLevelState class.
    """
    
    def __init__(self):
        # Level 1: Immediate (working memory) - updates every citation
        self.immediate = CitationMemory(
            level=1, 
            update_interval=1, 
            capacity=100,
            decay_rate=0.9
        )
        
        # Level 2: Short-term - updates every 10 citations
        self.short_term = CitationMemory(
            level=2,
            update_interval=10,
            capacity=500,
            decay_rate=0.95
        )
        
        # Level 3: Long-term - updates every 100 citations  
        self.long_term = CitationMemory(
            level=3,
            update_interval=100,
            capacity=2000,
            decay_rate=0.98
        )
        
        # Level 4: Persistent (values/ethics) - updates every 1000 citations
        self.persistent = CitationMemory(
            level=4,
            update_interval=1000,
            capacity=5000,
            decay_rate=0.99
        )
        
        self.levels = [self.immediate, self.short_term, self.long_term, self.persistent]
        self.timestep = 0
        
        # Local Surprise Signal buffer
        self.lss_buffer = deque(maxlen=50)
        
    def consolidate(self) -> None:
        """
        Consolidate memories from fast to slow levels.
        Matches your platform's memory consolidation triggers.
        """
        # Immediate -> Short-term
        strong_immediate = [c for c in self.immediate.citations 
                          if c.get('integrity_score', 0) > 0.7]
        for citation in strong_immediate[-5:]:
            self.short_term.add_citation(citation)
        
        # Short-term -> Long-term
        if self.timestep % 100 == 0:
            strong_short = [c for c in self.short_term.citations
                          if c.get('integrity_score', 0) > 0.8]
            for citation in strong_short[-3:]:
                self.long_term.add_citation(citation)
        
        # Long-term -> Persistent (ethical patterns)
        if self.timestep % 1000 == 0:
            ethical_patterns = self._extract_ethical_patterns()
            for pattern in ethical_patterns:
                self.persistent.add_citation(pattern)
    
    def _extract_ethical_patterns(self) -> List[Dict]:
        """Extract ethical citation patterns for persistent memory."""
        patterns = []
        
        # Analyze long-term patterns
        behavior_counts = defaultdict(int)
        for citation in self.long_term.citations:
            behavior = citation.get('behavior')
            if behavior:
                behavior_counts[behavior] += 1
        
        # Identify ethical vs unethical patterns
        total = sum(behavior_counts.values())
        if total > 0:
            for behavior, count in behavior_counts.items():
                proportion = count / total
                if proportion > 0.1:  # Significant pattern
                    patterns.append({
                        'type': 'ethical_pattern',
                        'behavior': behavior,
                        'frequency': proportion,
                        'integrity_score': self._calculate_pattern_integrity(behavior),
                        'timestamp': datetime.now().isoformat()
                    })
        
        return patterns
    
    def _calculate_pattern_integrity(self, behavior: str) -> float:
        """Calculate integrity score for a behavior pattern."""
        behavior_scores = {
            'proper_citation': 1.0,
            'paraphrase_cite': 0.9,
            'selective_citation': 0.6,
            'plagiarism': 0.0
        }
        return behavior_scores.get(behavior, 0.5)


# ============================================================================
# CITATION INTEGRITY AGENT
# ============================================================================

class CitationIntegrityAgent:
    """
    Complete Citation Integrity Agent integrating with your platform.
    Implements Nested Learning with your existing infrastructure.
    """
    
    def __init__(self, 
                 agent_id: str,
                 db_config: Dict[str, str],
                 redis_config: Dict[str, str],
                 api_endpoint: str = "http://localhost:3000"):
        self.agent_id = agent_id
        self.api_endpoint = api_endpoint
        
        # Memory system
        self.memory = NestedCitationMemory()
        
        # Current behavior and state
        self.current_behavior = CitationBehavior.PROPER_CITATION
        self.reputation = 0.5
        self.total_citations = 0
        self.detected_violations = 0
        
        # Learning parameters (matching your platform's LSS config)
        self.learning_rate = 0.1
        self.exploration_rate = 0.2
        self.meta_learning_rate = 0.01
        
        # Self-modifying weights
        self.behavior_weights = np.random.randn(10, 10) * 0.01
        
        # Database connection
        self.db_conn = psycopg2.connect(**db_config)
        self.db_cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
        
        # Redis for caching
        self.redis_client = redis.Redis(**redis_config)
        
        # Performance tracking
        self.performance_history = deque(maxlen=100)
        self.lss_history = deque(maxlen=50)
        
    async def analyze_citation(self, 
                              text: str,
                              source: str,
                              context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a citation using your platform's API endpoints.
        Integrates with your existing REST/GraphQL API.
        """
        # Call your platform's citation extraction endpoint
        extraction_response = await self._call_platform_api(
            "/api/citations/extract",
            {"text": text, "source": source}
        )
        
        citations = extraction_response.get('citations', [])
        
        # Analyze each citation
        analysis_results = []
        for citation in citations:
            # Check claim validity
            claim_validation = await self._validate_claim(citation)
            
            # Calculate integrity score
            integrity_score = self._calculate_integrity_score(
                citation, 
                claim_validation,
                context
            )
            
            # Detect behavior pattern
            behavior = self._detect_citation_behavior(
                citation,
                integrity_score,
                context
            )
            
            # Store in appropriate memory level
            citation_data = {
                'citation': citation,
                'source': source,
                'integrity_score': integrity_score,
                'behavior': behavior.name,
                'validation': claim_validation,
                'context': context,
                'agent_id': self.agent_id
            }
            
            self._update_memory(citation_data)
            
            analysis_results.append({
                'citation': citation,
                'integrity_score': integrity_score,
                'behavior': behavior.name,
                'risk_level': behavior.detection_risk,
                'recommendations': self._generate_recommendations(behavior, integrity_score)
            })
        
        return {
            'citations': analysis_results,
            'overall_integrity': np.mean([r['integrity_score'] for r in analysis_results]) if analysis_results else 1.0,
            'agent_reputation': self.reputation,
            'memory_state': self._get_memory_summary()
        }
    
    def _detect_citation_behavior(self,
                                 citation: Dict,
                                 integrity_score: float,
                                 context: Dict) -> CitationBehavior:
        """
        Detect citation behavior pattern using nested learning.
        """
        # Extract features
        features = self._extract_citation_features(citation, context)
        
        # Transform through learned weights (self-modification)
        transformed = np.dot(self.behavior_weights, features[:10].reshape(-1, 1)).flatten()
        
        # Calculate behavior probabilities
        behavior_scores = {}
        for behavior in CitationBehavior:
            score = behavior.integrity_score * np.exp(
                -np.linalg.norm(transformed - self._get_behavior_embedding(behavior))
            )
            behavior_scores[behavior] = score
        
        # Normalize and select
        total = sum(behavior_scores.values())
        if total > 0:
            probabilities = {b: s/total for b, s in behavior_scores.items()}
            
            # Exploration vs exploitation
            if random.random() < self.exploration_rate:
                return random.choice(list(CitationBehavior))
            else:
                return max(probabilities.items(), key=lambda x: x[1])[0]
        
        return CitationBehavior.PROPER_CITATION
    
    def _extract_citation_features(self, citation: Dict, context: Dict) -> np.ndarray:
        """Extract feature vector from citation."""
        features = np.zeros(20)
        
        # Citation characteristics
        features[0] = len(citation.get('text', '')) / 1000  # Length
        features[1] = citation.get('year', 2020) / 2024  # Recency
        features[2] = 1.0 if citation.get('doi') else 0.0  # Has DOI
        features[3] = 1.0 if citation.get('url') else 0.0  # Has URL
        
        # Context features
        features[4] = context.get('field_similarity', 0.5)
        features[5] = context.get('author_reputation', 0.5)
        features[6] = context.get('journal_impact', 0.5)
        
        # Historical patterns from memory
        if self.memory.immediate.patterns:
            features[7] = np.mean(list(self.memory.immediate.patterns.values()))
        
        # Add noise for exploration
        features += np.random.randn(20) * 0.01
        
        return features
    
    def _get_behavior_embedding(self, behavior: CitationBehavior) -> np.ndarray:
        """Get embedding vector for a citation behavior."""
        embedding = np.zeros(10)
        embedding[0] = behavior.integrity_score
        embedding[1] = behavior.update_frequency
        embedding[2] = 1 - behavior.detection_risk
        
        # Add behavior-specific features
        if behavior == CitationBehavior.PROPER_CITATION:
            embedding[3:5] = [1.0, 1.0]
        elif behavior == CitationBehavior.PLAGIARISM:
            embedding[5:7] = [1.0, 1.0]
        
        return embedding
    
    def _calculate_integrity_score(self,
                                  citation: Dict,
                                  validation: Dict,
                                  context: Dict) -> float:
        """
        Calculate citation integrity score.
        Integrates with your platform's validation logic.
        """
        score = 0.5  # Base score
        
        # Validation checks
        if validation.get('exists', False):
            score += 0.2
        if validation.get('accurate', False):
            score += 0.2
        if validation.get('relevant', False):
            score += 0.1
        
        # Context modifiers
        score *= (1 + context.get('field_similarity', 0))
        
        # Historical reputation
        score *= (0.5 + self.reputation * 0.5)
        
        return min(1.0, max(0.0, score))
    
    async def _validate_claim(self, citation: Dict) -> Dict:
        """
        Validate citation claim using your platform's API.
        """
        # Cache check
        cache_key = f"validation:{hashlib.md5(json.dumps(citation, sort_keys=True).encode()).hexdigest()}"
        cached = self.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Call validation API
        validation = await self._call_platform_api(
            "/api/claims/validate",
            {"citation": citation}
        )
        
        # Cache result
        self.redis_client.setex(cache_key, 3600, json.dumps(validation))
        
        return validation
    
    def _update_memory(self, citation_data: Dict) -> None:
        """
        Update multi-level memory with citation data.
        """
        self.memory.timestep += 1
        self.total_citations += 1
        
        # Add to immediate memory
        self.memory.immediate.add_citation(citation_data)
        
        # Update other levels if needed
        for level in self.memory.levels:
            if level.should_update(self.memory.timestep):
                level.add_citation(citation_data)
                level.decay()
        
        # Consolidate if needed
        if self.memory.timestep % 100 == 0:
            self.memory.consolidate()
        
        # Calculate Local Surprise Signal
        lss = self._calculate_lss(citation_data)
        self.lss_history.append(lss)
        
        # Self-modify if high surprise
        if abs(lss) > 0.5:
            self._self_modify_weights(lss)
    
    def _calculate_lss(self, citation_data: Dict) -> float:
        """
        Calculate Local Surprise Signal.
        Based on Nested Learning paper: LSS = ∇y L(Wt; xt)
        """
        expected_integrity = self.reputation
        actual_integrity = citation_data.get('integrity_score', 0.5)
        
        surprise = actual_integrity - expected_integrity
        
        # Normalize by recent variance
        if len(self.lss_history) > 10:
            std = np.std(list(self.lss_history))
            if std > 0:
                surprise = surprise / std
        
        return surprise
    
    def _self_modify_weights(self, lss: float) -> None:
        """
        Self-modify behavior weights based on surprise.
        Implements self-referential learning from HOPE architecture.
        """
        # Calculate gradient
        gradient = np.outer(
            np.random.randn(10),
            np.random.randn(10)
        ) * lss * self.meta_learning_rate
        
        # Update weights
        self.behavior_weights += gradient
        
        # Normalize to prevent explosion
        norm = np.linalg.norm(self.behavior_weights)
        if norm > 10:
            self.behavior_weights = self.behavior_weights / norm * 10
    
    def _generate_recommendations(self, 
                                 behavior: CitationBehavior,
                                 integrity_score: float) -> List[str]:
        """
        Generate recommendations based on detected behavior.
        """
        recommendations = []
        
        if behavior == CitationBehavior.PLAGIARISM:
            recommendations.append("⚠️ High risk: Rewrite with proper citations")
            recommendations.append("Use quotation marks for direct quotes")
            recommendations.append("Add source attribution")
            
        elif behavior == CitationBehavior.LAZY_CITATION:
            recommendations.append("Verify citation accuracy")
            recommendations.append("Check page numbers and dates")
            recommendations.append("Read original source")
            
        elif behavior == CitationBehavior.SELF_CITATION:
            recommendations.append("Balance with external citations")
            recommendations.append("Ensure relevance to current work")
            
        elif behavior == CitationBehavior.SELECTIVE_CITATION:
            recommendations.append("Include contradicting viewpoints")
            recommendations.append("Acknowledge limitations")
            
        elif integrity_score < 0.5:
            recommendations.append("Review citation practices")
            recommendations.append("Consult citation guidelines")
        
        return recommendations
    
    def _get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of memory state."""
        return {
            'immediate_citations': len(self.memory.immediate.citations),
            'short_term_citations': len(self.memory.short_term.citations),
            'long_term_citations': len(self.memory.long_term.citations),
            'persistent_patterns': len(self.memory.persistent.patterns),
            'timestep': self.memory.timestep,
            'last_lss': self.lss_history[-1] if self.lss_history else 0
        }
    
    async def _call_platform_api(self, endpoint: str, data: Dict) -> Dict:
        """
        Call your platform's API endpoints.
        """
        url = f"{self.api_endpoint}{endpoint}"
        
        try:
            # Async HTTP call
            response = await asyncio.to_thread(
                requests.post,
                url,
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API call failed: {e}")
            return {}
    
    def update_reputation(self, feedback: float) -> None:
        """
        Update agent reputation based on feedback.
        """
        self.reputation = 0.9 * self.reputation + 0.1 * feedback
        self.performance_history.append(feedback)
        
        # Adjust exploration based on performance
        if len(self.performance_history) > 20:
            recent = list(self.performance_history)[-20:]
            if np.mean(recent) < 0.5:
                # Poor performance - explore more
                self.exploration_rate = min(0.5, self.exploration_rate * 1.1)
            else:
                # Good performance - exploit more
                self.exploration_rate = max(0.05, self.exploration_rate * 0.95)
    
    def save_state(self, filepath: str) -> None:
        """Save agent state for persistence."""
        state = {
            'agent_id': self.agent_id,
            'reputation': self.reputation,
            'total_citations': self.total_citations,
            'detected_violations': self.detected_violations,
            'behavior_weights': self.behavior_weights.tolist(),
            'memory_summary': self._get_memory_summary(),
            'performance_history': list(self.performance_history)
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self, filepath: str) -> None:
        """Load agent state from file."""
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        self.reputation = state['reputation']
        self.total_citations = state['total_citations']
        self.detected_violations = state['detected_violations']
        self.behavior_weights = np.array(state['behavior_weights'])
        self.performance_history = deque(state['performance_history'], maxlen=100)


# ============================================================================
# INTEGRATION WITH YOUR PLATFORM
# ============================================================================

class PlatformIntegration:
    """
    Integration layer with your existing TypeScript platform.
    """
    
    def __init__(self, config_file: str = "config/platform.json"):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        # Initialize agents
        self.agents = {}
        for i in range(self.config.get('num_agents', 10)):
            agent_id = f"agent_{i}"
            self.agents[agent_id] = CitationIntegrityAgent(
                agent_id=agent_id,
                db_config=self.config['database'],
                redis_config=self.config['redis'],
                api_endpoint=self.config.get('api_endpoint', 'http://localhost:3000')
            )
    
    async def process_document(self, document: Dict) -> Dict:
        """
        Process a document through multiple agents.
        """
        results = {}
        
        # Each agent analyzes the document
        for agent_id, agent in self.agents.items():
            analysis = await agent.analyze_citation(
                text=document.get('text', ''),
                source=document.get('source', ''),
                context=document.get('context', {})
            )
            results[agent_id] = analysis
        
        # Aggregate results
        aggregated = self._aggregate_analyses(results)
        
        # Store in database
        await self._store_results(document, aggregated)
        
        return aggregated
    
    def _aggregate_analyses(self, results: Dict) -> Dict:
        """
        Aggregate analyses from multiple agents.
        """
        all_scores = []
        all_behaviors = []
        
        for agent_results in results.values():
            for citation in agent_results.get('citations', []):
                all_scores.append(citation['integrity_score'])
                all_behaviors.append(citation['behavior'])
        
        behavior_counts = defaultdict(int)
        for behavior in all_behaviors:
            behavior_counts[behavior] += 1
        
        return {
            'mean_integrity': np.mean(all_scores) if all_scores else 1.0,
            'std_integrity': np.std(all_scores) if all_scores else 0.0,
            'behavior_distribution': dict(behavior_counts),
            'num_agents': len(results),
            'consensus_level': self._calculate_consensus(results)
        }
    
    def _calculate_consensus(self, results: Dict) -> float:
        """Calculate consensus among agents."""
        if len(results) < 2:
            return 1.0
        
        scores = []
        for agent_results in results.values():
            if agent_results.get('overall_integrity') is not None:
                scores.append(agent_results['overall_integrity'])
        
        if len(scores) < 2:
            return 1.0
        
        # Low variance = high consensus
        variance = np.var(scores)
        consensus = 1.0 / (1.0 + variance)
        
        return consensus
    
    async def _store_results(self, document: Dict, results: Dict) -> None:
        """
        Store results in your platform's database.
        """
        # This would integrate with your PostgreSQL schema
        # Matching your db/schema.sql structure
        pass


# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """
    Main execution demonstrating the complete agent system.
    """
    # Initialize platform integration
    platform = PlatformIntegration("config/platform.json")
    
    # Example document
    document = {
        'text': """
        Recent studies have shown significant improvements in citation practices
        (Smith et al., 2023). However, some researchers continue to engage in
        questionable citation behaviors including self-citation and selective
        citation of supporting evidence only.
        """,
        'source': 'research_paper_001',
        'context': {
            'field': 'computer_science',
            'journal': 'ACM Computing Surveys',
            'author_reputation': 0.8
        }
    }
    
    # Process document
    results = await platform.process_document(document)
    
    print("Citation Integrity Analysis Results:")
    print(f"Mean Integrity Score: {results['mean_integrity']:.2f}")
    print(f"Consensus Level: {results['consensus_level']:.2f}")
    print(f"Behavior Distribution: {results['behavior_distribution']}")
    
    # Save agent states
    for agent_id, agent in platform.agents.items():
        agent.save_state(f"states/{agent_id}.json")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())


# ============================================================================
# CONFIGURATION TEMPLATE
# ============================================================================

CONFIG_TEMPLATE = """
{
  "num_agents": 10,
  "api_endpoint": "http://localhost:3000",
  "database": {
    "host": "localhost",
    "port": 5432,
    "database": "citation_integrity",
    "user": "citation_agent",
    "password": "secure_password"
  },
  "redis": {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "decode_responses": true
  },
  "learning": {
    "initial_learning_rate": 0.1,
    "exploration_rate": 0.2,
    "meta_learning_rate": 0.01,
    "memory_consolidation_interval": 100
  },
  "monitoring": {
    "prometheus_port": 9090,
    "grafana_port": 3001,
    "enable_telemetry": true
  }
}
"""

# Save config template
with open('config_template.json', 'w') as f:
    f.write(CONFIG_TEMPLATE)

print("Citation Integrity Agent created successfully!")
print("Configuration template saved to config_template.json")
