"""
Enhanced Nest Learning Implementation with Common Fixes
========================================================
This module provides an improved Nest learning implementation that addresses
common issues and integrates smoothly with game theory simulations.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import random
from collections import deque, defaultdict
import json
import logging
import time
import hashlib
import pickle

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Strategy(Enum):
    """Enhanced strategy enum with metadata."""
    COOPERATE = ("cooperate", 1.0)  # (name, base_weight)
    DEFECT = ("defect", 0.8)
    TIT_FOR_TAT = ("tit_for_tat", 0.9)
    RANDOM = ("random", 0.5)
    ADAPTIVE = ("adaptive", 1.1)
    GENEROUS_TIT_FOR_TAT = ("generous_tit_for_tat", 0.95)
    PAVLOV = ("pavlov", 0.85)
    
    @property
    def name(self) -> str:
        return self.value[0]
    
    @property
    def base_weight(self) -> float:
        return self.value[1]


@dataclass
class EnhancedPheromone:
    """
    Enhanced pheromone with additional metadata for better learning.
    """
    strategy: Strategy
    payoff: float
    timestamp: int
    strength: float = 1.0
    agent_id: str = ""
    opponent_strategy: Optional[Strategy] = None
    context_hash: str = ""
    decay_rate: float = 0.95
    reinforcement_count: int = 1
    
    def __post_init__(self):
        """Generate context hash if not provided."""
        if not self.context_hash:
            context = f"{self.strategy}_{self.opponent_strategy}_{self.payoff}"
            self.context_hash = hashlib.md5(context.encode()).hexdigest()[:8]
    
    def decay(self, custom_rate: Optional[float] = None) -> None:
        """Enhanced decay with adaptive rate."""
        rate = custom_rate or self.decay_rate
        # Slower decay for frequently reinforced pheromones
        if self.reinforcement_count > 5:
            rate = rate + (1 - rate) * 0.3
        self.strength *= rate
    
    def reinforce(self, additional_strength: float = 0.2) -> None:
        """Reinforce pheromone when strategy succeeds again."""
        self.strength = min(1.0, self.strength + additional_strength)
        self.reinforcement_count += 1
        # Adapt decay rate for successful strategies
        self.decay_rate = min(0.98, self.decay_rate + 0.01)
    
    def is_expired(self, threshold: float = 0.01) -> bool:
        """Check if pheromone has decayed below threshold."""
        return self.strength < threshold


@dataclass
class NestMemoryV2:
    """
    Enhanced collective memory with improved learning mechanisms.
    """
    # Core memory structures
    strategy_success_rates: Dict[Strategy, float] = field(default_factory=dict)
    pheromone_trails: List[EnhancedPheromone] = field(default_factory=list)
    pheromone_index: Dict[str, List[EnhancedPheromone]] = field(default_factory=lambda: defaultdict(list))
    
    # Experience storage
    collective_experiences: deque = field(default_factory=lambda: deque(maxlen=2000))
    strategy_pair_outcomes: Dict[Tuple[Strategy, Strategy], List[float]] = field(default_factory=lambda: defaultdict(list))
    
    # Learning parameters
    learning_rate: float = 0.15
    exploration_rate: float = 0.3
    exploration_decay: float = 0.995
    min_exploration: float = 0.05
    
    # Advanced features
    meta_strategies: Dict[str, float] = field(default_factory=dict)
    adaptation_threshold: float = 0.7
    memory_consolidation_interval: int = 50
    
    def update_success_rate(self, strategy: Strategy, success: bool, weight: float = 1.0) -> None:
        """
        Update success rate with weighted learning.
        """
        if strategy not in self.strategy_success_rates:
            self.strategy_success_rates[strategy] = 0.5
        
        # Weighted update based on confidence
        effective_learning_rate = self.learning_rate * weight
        current_rate = self.strategy_success_rates[strategy]
        new_rate = current_rate * (1 - effective_learning_rate) + success * effective_learning_rate
        self.strategy_success_rates[strategy] = np.clip(new_rate, 0.01, 0.99)
    
    def add_pheromone(self, pheromone: EnhancedPheromone) -> None:
        """
        Add pheromone with intelligent reinforcement.
        """
        # Check if similar pheromone exists
        similar_found = False
        for existing in self.pheromone_trails:
            if (existing.strategy == pheromone.strategy and 
                existing.opponent_strategy == pheromone.opponent_strategy and
                abs(existing.payoff - pheromone.payoff) < 0.5):
                existing.reinforce()
                similar_found = True
                break
        
        if not similar_found:
            self.pheromone_trails.append(pheromone)
            self.pheromone_index[pheromone.context_hash].append(pheromone)
    
    def process_pheromones(self) -> None:
        """
        Process pheromones with adaptive decay.
        """
        # Decay all pheromones
        for pheromone in self.pheromone_trails:
            # Adaptive decay based on global performance
            avg_strength = np.mean([p.strength for p in self.pheromone_trails]) if self.pheromone_trails else 0.5
            if pheromone.strength > avg_strength:
                pheromone.decay(custom_rate=0.98)  # Slower decay for strong pheromones
            else:
                pheromone.decay()
        
        # Remove expired pheromones
        self.pheromone_trails = [p for p in self.pheromone_trails if not p.is_expired()]
        
        # Update index
        self.pheromone_index.clear()
        for pheromone in self.pheromone_trails:
            self.pheromone_index[pheromone.context_hash].append(pheromone)
    
    def get_contextual_strategy(self, opponent_last: Optional[Strategy] = None) -> Optional[Strategy]:
        """
        Select strategy based on context-aware pheromone signals.
        """
        if not self.pheromone_trails:
            return None
        
        # Filter relevant pheromones
        relevant_pheromones = self.pheromone_trails
        if opponent_last:
            relevant_pheromones = [
                p for p in self.pheromone_trails 
                if p.opponent_strategy == opponent_last or p.opponent_strategy is None
            ]
        
        if not relevant_pheromones:
            relevant_pheromones = self.pheromone_trails
        
        # Calculate weighted probabilities
        strategies = []
        weights = []
        
        for pheromone in relevant_pheromones:
            # Complex weight calculation
            base_weight = pheromone.strength
            payoff_weight = 1 + (pheromone.payoff / 5.0)  # Normalize payoff
            reinforcement_weight = 1 + (pheromone.reinforcement_count * 0.1)
            strategy_weight = pheromone.strategy.base_weight
            
            total_weight = base_weight * payoff_weight * reinforcement_weight * strategy_weight
            
            strategies.append(pheromone.strategy)
            weights.append(total_weight)
        
        # Normalize and select
        total = sum(weights)
        if total == 0:
            return None
        
        probabilities = [w / total for w in weights]
        return np.random.choice(strategies, p=probabilities)
    
    def consolidate_memory(self) -> None:
        """
        Consolidate memory by analyzing patterns and updating meta-strategies.
        """
        if len(self.collective_experiences) < 100:
            return
        
        # Analyze recent experiences
        recent = list(self.collective_experiences)[-100:]
        
        # Calculate meta-strategy effectiveness
        strategy_combos = defaultdict(list)
        for exp in recent:
            if isinstance(exp, dict) and 'my_move' in exp and 'payoff' in exp:
                key = f"{exp['my_move']}_{exp.get('opponent_move', 'unknown')}"
                strategy_combos[key].append(exp['payoff'])
        
        # Update meta-strategies
        for combo, payoffs in strategy_combos.items():
            avg_payoff = np.mean(payoffs)
            self.meta_strategies[combo] = avg_payoff
        
        # Prune weak strategies
        if len(self.strategy_success_rates) > 5:
            min_rate = min(self.strategy_success_rates.values())
            weak_strategies = [s for s, r in self.strategy_success_rates.items() if r < min_rate + 0.1]
            for strategy in weak_strategies[:1]:  # Remove one weak strategy
                if len(self.strategy_success_rates) > 3:  # Keep minimum diversity
                    del self.strategy_success_rates[strategy]
    
    def update_exploration_rate(self) -> None:
        """
        Adaptively update exploration rate.
        """
        self.exploration_rate *= self.exploration_decay
        self.exploration_rate = max(self.min_exploration, self.exploration_rate)


class ImprovedNestAgent:
    """
    Enhanced agent with better learning capabilities.
    """
    
    def __init__(self, agent_id: str, nest_memory: NestMemoryV2):
        self.agent_id = agent_id
        self.nest_memory = nest_memory
        self.current_strategy = Strategy.COOPERATE
        self.personal_history = deque(maxlen=200)
        self.opponent_model = defaultdict(lambda: defaultdict(int))
        self.total_payoff = 0.0
        self.games_played = 0
        self.recent_payoffs = deque(maxlen=20)
        self.strategy_history = deque(maxlen=50)
        self.adaptation_mode = False
        
    def choose_strategy(self, opponent_last_move: Optional[Strategy] = None) -> Strategy:
        """
        Enhanced strategy selection with opponent modeling.
        """
        # Check if we should adapt
        if self.recent_payoffs and len(self.recent_payoffs) >= 10:
            avg_recent = np.mean(list(self.recent_payoffs)[-10:])
            if avg_recent < 1.5:  # Poor performance threshold
                self.adaptation_mode = True
        
        # Exploration vs Exploitation
        if random.random() < self.nest_memory.exploration_rate:
            # Intelligent exploration
            if self.adaptation_mode:
                # Explore strategies we haven't tried recently
                recent_strategies = set(self.strategy_history)
                unexplored = [s for s in Strategy if s not in recent_strategies]
                if unexplored:
                    self.current_strategy = random.choice(unexplored)
                else:
                    self.current_strategy = random.choice(list(Strategy))
            else:
                self.current_strategy = random.choice(list(Strategy))
            
            logger.debug(f"Agent {self.agent_id} exploring: {self.current_strategy.name}")
        else:
            # Exploitation with context
            contextual_strategy = self.nest_memory.get_contextual_strategy(opponent_last_move)
            
            if contextual_strategy:
                self.current_strategy = contextual_strategy
            else:
                # Use opponent modeling
                if opponent_last_move and self.opponent_model[opponent_last_move]:
                    # Predict opponent's next move
                    opponent_patterns = self.opponent_model[opponent_last_move]
                    likely_next = max(opponent_patterns.items(), key=lambda x: x[1])[0]
                    self.current_strategy = self._counter_strategy(likely_next)
                else:
                    # Default to best known strategy
                    if self.nest_memory.strategy_success_rates:
                        best_strategy = max(
                            self.nest_memory.strategy_success_rates.items(),
                            key=lambda x: x[1]
                        )[0]
                        self.current_strategy = best_strategy
                    else:
                        self.current_strategy = Strategy.COOPERATE
        
        # Execute specific strategy logic
        final_strategy = self._execute_strategy_logic(self.current_strategy, opponent_last_move)
        
        # Record strategy
        self.strategy_history.append(final_strategy)
        
        return final_strategy
    
    def _execute_strategy_logic(self, strategy: Strategy, opponent_last: Optional[Strategy]) -> Strategy:
        """
        Execute specific strategy logic.
        """
        if strategy == Strategy.TIT_FOR_TAT:
            return opponent_last if opponent_last else Strategy.COOPERATE
        
        elif strategy == Strategy.GENEROUS_TIT_FOR_TAT:
            if opponent_last == Strategy.DEFECT:
                return Strategy.COOPERATE if random.random() < 0.1 else Strategy.DEFECT
            return opponent_last if opponent_last else Strategy.COOPERATE
        
        elif strategy == Strategy.PAVLOV:
            if self.personal_history:
                last_outcome = self.personal_history[-1]
                if last_outcome[1] >= 3:  # Good outcome
                    return self.strategy_history[-1] if self.strategy_history else Strategy.COOPERATE
                else:  # Bad outcome
                    return Strategy.DEFECT if self.strategy_history and self.strategy_history[-1] == Strategy.COOPERATE else Strategy.COOPERATE
            return Strategy.COOPERATE
        
        elif strategy == Strategy.RANDOM:
            return random.choice([Strategy.COOPERATE, Strategy.DEFECT])
        
        elif strategy == Strategy.ADAPTIVE:
            return self._adaptive_strategy(opponent_last)
        
        else:
            return strategy
    
    def _counter_strategy(self, predicted_move: Strategy) -> Strategy:
        """
        Return counter-strategy for predicted opponent move.
        """
        if predicted_move == Strategy.COOPERATE:
            return Strategy.COOPERATE  # Reciprocate cooperation
        else:
            return Strategy.DEFECT  # Defend against defection
    
    def _adaptive_strategy(self, opponent_last: Optional[Strategy]) -> Strategy:
        """
        Advanced adaptive strategy.
        """
        if len(self.personal_history) < 5:
            return Strategy.COOPERATE
        
        # Analyze patterns
        recent_history = list(self.personal_history)[-10:]
        opponent_cooperations = sum(1 for move, _ in recent_history if move == Strategy.COOPERATE)
        cooperation_rate = opponent_cooperations / len(recent_history)
        
        # Check for patterns
        if len(recent_history) >= 3:
            last_three = [move for move, _ in recent_history[-3:]]
            if len(set(last_three)) == 1:  # Opponent is consistent
                if last_three[0] == Strategy.COOPERATE:
                    return Strategy.COOPERATE
                else:
                    return Strategy.DEFECT
        
        # Adaptive thresholds
        if cooperation_rate > 0.7:
            return Strategy.COOPERATE
        elif cooperation_rate < 0.3:
            return Strategy.DEFECT
        else:
            # Mixed strategy
            return Strategy.COOPERATE if random.random() < cooperation_rate else Strategy.DEFECT
    
    def update_learning(self, my_move: Strategy, opponent_move: Strategy, payoff: float) -> None:
        """
        Enhanced learning update with opponent modeling.
        """
        # Update history
        self.personal_history.append((opponent_move, payoff))
        self.recent_payoffs.append(payoff)
        self.total_payoff += payoff
        self.games_played += 1
        
        # Update opponent model
        if len(self.personal_history) >= 2:
            prev_opponent_move = self.personal_history[-2][0]
            self.opponent_model[prev_opponent_move][opponent_move] += 1
        
        # Calculate success
        avg_payoff = self.total_payoff / self.games_played
        recent_avg = np.mean(list(self.recent_payoffs)) if self.recent_payoffs else 0
        success = payoff > max(avg_payoff, recent_avg)
        
        # Weight based on payoff magnitude
        weight = min(2.0, 1.0 + (payoff - avg_payoff) / 3.0)
        
        # Update nest memory
        self.nest_memory.update_success_rate(my_move, success, weight)
        
        # Create enhanced pheromone
        if success or payoff > 3:  # Leave pheromone for good outcomes
            pheromone = EnhancedPheromone(
                strategy=my_move,
                payoff=payoff,
                timestamp=self.games_played,
                strength=min(1.0, payoff / 5.0),
                agent_id=self.agent_id,
                opponent_strategy=opponent_move
            )
            self.nest_memory.add_pheromone(pheromone)
        
        # Update collective experiences
        experience = {
            'agent': self.agent_id,
            'my_move': my_move.name,
            'opponent_move': opponent_move.name,
            'payoff': payoff,
            'success': success,
            'timestamp': time.time()
        }
        self.nest_memory.collective_experiences.append(experience)
        self.nest_memory.strategy_pair_outcomes[(my_move, opponent_move)].append(payoff)
        
        # Reset adaptation mode if performance improves
        if self.adaptation_mode and recent_avg > 2.5:
            self.adaptation_mode = False


class EnhancedNestSimulation:
    """
    Enhanced simulation with better performance and stability.
    """
    
    def __init__(self, 
                 num_agents: int = 10,
                 payoff_matrix: Optional[Dict] = None,
                 enable_advanced_features: bool = True):
        self.nest_memory = NestMemoryV2()
        self.agents = [
            ImprovedNestAgent(f"agent_{i}", self.nest_memory) 
            for i in range(num_agents)
        ]
        self.payoff_matrix = payoff_matrix or self._default_payoff_matrix()
        self.generation = 0
        self.history = []
        self.enable_advanced = enable_advanced_features
        self.convergence_detector = ConvergenceDetector()
        
    def _default_payoff_matrix(self) -> Dict[Tuple[Strategy, Strategy], Tuple[float, float]]:
        """
        Default prisoner's dilemma payoff matrix.
        """
        return {
            (Strategy.COOPERATE, Strategy.COOPERATE): (3, 3),
            (Strategy.COOPERATE, Strategy.DEFECT): (0, 5),
            (Strategy.DEFECT, Strategy.COOPERATE): (5, 0),
            (Strategy.DEFECT, Strategy.DEFECT): (1, 1),
        }
    
    def calculate_payoff(self, strategy1: Strategy, strategy2: Strategy) -> Tuple[float, float]:
        """
        Calculate payoffs with noise for realism.
        """
        # Simplify to basic strategies for payoff
        s1 = strategy1 if strategy1 in [Strategy.COOPERATE, Strategy.DEFECT] else Strategy.COOPERATE
        s2 = strategy2 if strategy2 in [Strategy.COOPERATE, Strategy.DEFECT] else Strategy.COOPERATE
        
        base_payoffs = self.payoff_matrix.get((s1, s2), (0, 0))
        
        # Add small noise for realism
        if self.enable_advanced:
            noise = np.random.normal(0, 0.1, 2)
            return (base_payoffs[0] + noise[0], base_payoffs[1] + noise[1])
        
        return base_payoffs
    
    def run_generation(self) -> Dict[str, Any]:
        """
        Run one generation with improved mechanics.
        """
        self.generation += 1
        
        # Process pheromones
        self.nest_memory.process_pheromones()
        
        # Memory consolidation
        if self.generation % self.nest_memory.memory_consolidation_interval == 0:
            self.nest_memory.consolidate_memory()
        
        # Pair agents
        agents_copy = self.agents.copy()
        random.shuffle(agents_copy)
        
        if len(agents_copy) % 2 == 1:
            # Handle odd number - last agent plays against random previous agent
            agents_copy.append(random.choice(agents_copy[:-1]))
        
        pairs = [(agents_copy[i], agents_copy[i+1]) 
                for i in range(0, len(agents_copy), 2)]
        
        # Run games
        generation_data = {
            'generation': self.generation,
            'games': [],
            'total_payoff': 0,
            'cooperation_count': 0,
            'defection_count': 0,
            'other_strategy_count': 0
        }
        
        for agent1, agent2 in pairs:
            # Get last moves from history
            last1 = agent1.strategy_history[-1] if agent1.strategy_history else None
            last2 = agent2.strategy_history[-1] if agent2.strategy_history else None
            
            # Choose strategies
            strategy1 = agent1.choose_strategy(last2)
            strategy2 = agent2.choose_strategy(last1)
            
            # Calculate payoffs
            payoff1, payoff2 = self.calculate_payoff(strategy1, strategy2)
            
            # Update learning
            agent1.update_learning(strategy1, strategy2, payoff1)
            agent2.update_learning(strategy2, strategy1, payoff2)
            
            # Record game
            game_record = {
                'agent1': agent1.agent_id,
                'agent2': agent2.agent_id,
                'strategy1': strategy1.name,
                'strategy2': strategy2.name,
                'payoff1': payoff1,
                'payoff2': payoff2
            }
            generation_data['games'].append(game_record)
            
            # Update statistics
            generation_data['total_payoff'] += payoff1 + payoff2
            
            for strategy in [strategy1, strategy2]:
                if strategy == Strategy.COOPERATE:
                    generation_data['cooperation_count'] += 1
                elif strategy == Strategy.DEFECT:
                    generation_data['defection_count'] += 1
                else:
                    generation_data['other_strategy_count'] += 1
        
        # Calculate rates
        total_moves = generation_data['cooperation_count'] + generation_data['defection_count'] + generation_data['other_strategy_count']
        generation_data['cooperation_rate'] = generation_data['cooperation_count'] / max(1, total_moves)
        generation_data['defection_rate'] = generation_data['defection_count'] / max(1, total_moves)
        
        # Strategy distribution
        generation_data['strategy_distribution'] = {}
        for agent in self.agents:
            if agent.strategy_history:
                strategy = agent.strategy_history[-1].name
                generation_data['strategy_distribution'][strategy] = \
                    generation_data['strategy_distribution'].get(strategy, 0) + 1
        
        # Update exploration rate
        self.nest_memory.update_exploration_rate()
        
        # Check convergence
        if self.enable_advanced:
            generation_data['convergence_status'] = self.convergence_detector.check(generation_data)
        
        self.history.append(generation_data)
        return generation_data
    
    def run_simulation(self, 
                       num_generations: int = 100,
                       early_stop: bool = True) -> List[Dict[str, Any]]:
        """
        Run simulation with optional early stopping.
        """
        logger.info(f"Starting enhanced simulation with {len(self.agents)} agents")
        
        for i in range(num_generations):
            stats = self.run_generation()
            
            # Logging
            if i % 10 == 0 or i == num_generations - 1:
                logger.info(f"Generation {i}: Cooperation={stats['cooperation_rate']:.2%}, "
                          f"Payoff={stats['total_payoff']:.2f}, "
                          f"Pheromones={len(self.nest_memory.pheromone_trails)}, "
                          f"Exploration={self.nest_memory.exploration_rate:.3f}")
            
            # Early stopping
            if early_stop and i > 30:
                if stats.get('convergence_status', {}).get('converged', False):
                    logger.info(f"Early stopping at generation {i} - system converged")
                    break
        
        return self.history
    
    def get_detailed_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary statistics.
        """
        if not self.history:
            return {}
        
        cooperation_rates = [gen['cooperation_rate'] for gen in self.history]
        total_payoffs = [gen['total_payoff'] for gen in self.history]
        
        # Agent performance
        agent_stats = {}
        for agent in self.agents:
            agent_stats[agent.agent_id] = {
                'total_payoff': agent.total_payoff,
                'games_played': agent.games_played,
                'avg_payoff': agent.total_payoff / max(1, agent.games_played),
                'final_strategy': agent.current_strategy.name,
                'adaptation_mode': agent.adaptation_mode
            }
        
        # Best performing agent
        best_agent = max(agent_stats.items(), key=lambda x: x[1]['avg_payoff'])
        
        return {
            'simulation_stats': {
                'generations_run': len(self.history),
                'total_games': sum(len(gen['games']) for gen in self.history),
                'convergence_achieved': self.history[-1].get('convergence_status', {}).get('converged', False)
            },
            'cooperation_metrics': {
                'avg_cooperation_rate': np.mean(cooperation_rates),
                'final_cooperation_rate': cooperation_rates[-1],
                'cooperation_trend': np.polyfit(range(len(cooperation_rates)), cooperation_rates, 1)[0],
                'cooperation_stability': np.std(cooperation_rates[-10:]) if len(cooperation_rates) >= 10 else None
            },
            'payoff_metrics': {
                'avg_total_payoff': np.mean(total_payoffs),
                'final_total_payoff': total_payoffs[-1],
                'payoff_trend': np.polyfit(range(len(total_payoffs)), total_payoffs, 1)[0]
            },
            'learning_metrics': {
                'final_exploration_rate': self.nest_memory.exploration_rate,
                'active_pheromones': len(self.nest_memory.pheromone_trails),
                'strategy_success_rates': dict(self.nest_memory.strategy_success_rates),
                'meta_strategies': dict(self.nest_memory.meta_strategies)
            },
            'agent_performance': {
                'best_agent': best_agent[0],
                'best_agent_payoff': best_agent[1]['avg_payoff'],
                'agent_stats': agent_stats
            },
            'final_state': {
                'strategy_distribution': self.history[-1]['strategy_distribution'],
                'dominant_strategy': max(self.history[-1]['strategy_distribution'].items(), 
                                        key=lambda x: x[1])[0] if self.history[-1]['strategy_distribution'] else None
            }
        }
    
    def save_state(self, filename: str = "simulation_state.pkl") -> None:
        """
        Save complete simulation state for later analysis.
        """
        state = {
            'history': self.history,
            'summary': self.get_detailed_summary(),
            'nest_memory': {
                'strategy_success_rates': dict(self.nest_memory.strategy_success_rates),
                'meta_strategies': dict(self.nest_memory.meta_strategies),
                'exploration_rate': self.nest_memory.exploration_rate
            },
            'timestamp': time.time()
        }
        
        with open(filename, 'wb') as f:
            pickle.dump(state, f)
        
        logger.info(f"Simulation state saved to {filename}")


class ConvergenceDetector:
    """
    Detect convergence in the simulation.
    """
    
    def __init__(self, window_size: int = 20, variance_threshold: float = 0.01):
        self.window_size = window_size
        self.variance_threshold = variance_threshold
        self.history = deque(maxlen=window_size)
        
    def check(self, generation_data: Dict) -> Dict[str, Any]:
        """
        Check if the system has converged.
        """
        self.history.append(generation_data['cooperation_rate'])
        
        if len(self.history) < self.window_size:
            return {'converged': False, 'reason': 'Insufficient data'}
        
        # Calculate variance
        variance = np.var(list(self.history))
        
        # Check trend
        trend = np.polyfit(range(len(self.history)), list(self.history), 1)[0]
        
        # Convergence criteria
        converged = variance < self.variance_threshold and abs(trend) < 0.001
        
        return {
            'converged': converged,
            'variance': variance,
            'trend': trend,
            'stable_value': np.mean(list(self.history)) if converged else None
        }


# Example usage
if __name__ == "__main__":
    # Create enhanced simulation
    sim = EnhancedNestSimulation(num_agents=20, enable_advanced_features=True)
    
    # Run simulation
    history = sim.run_simulation(num_generations=100, early_stop=True)
    
    # Get detailed summary
    summary = sim.get_detailed_summary()
    
    # Display results
    print("\n" + "="*60)
    print("ENHANCED NEST LEARNING SIMULATION RESULTS")
    print("="*60)
    
    print("\n📊 Simulation Statistics:")
    print(f"  Generations Run: {summary['simulation_stats']['generations_run']}")
    print(f"  Total Games: {summary['simulation_stats']['total_games']}")
    print(f"  Convergence: {summary['simulation_stats']['convergence_achieved']}")
    
    print("\n🤝 Cooperation Metrics:")
    print(f"  Average Rate: {summary['cooperation_metrics']['avg_cooperation_rate']:.2%}")
    print(f"  Final Rate: {summary['cooperation_metrics']['final_cooperation_rate']:.2%}")
    print(f"  Trend: {'↑' if summary['cooperation_metrics']['cooperation_trend'] > 0 else '↓'}")
    
    print("\n💰 Payoff Metrics:")
    print(f"  Average Total: {summary['payoff_metrics']['avg_total_payoff']:.2f}")
    print(f"  Final Total: {summary['payoff_metrics']['final_total_payoff']:.2f}")
    
    print("\n🧠 Learning Metrics:")
    print(f"  Active Pheromones: {summary['learning_metrics']['active_pheromones']}")
    print(f"  Exploration Rate: {summary['learning_metrics']['final_exploration_rate']:.3f}")
    
    print("\n🏆 Best Agent:")
    print(f"  ID: {summary['agent_performance']['best_agent']}")
    print(f"  Average Payoff: {summary['agent_performance']['best_agent_payoff']:.2f}")
    
    print("\n🎯 Final Strategy Distribution:")
    for strategy, count in summary['final_state']['strategy_distribution'].items():
        print(f"  {strategy}: {count} agents")
    
    # Save results
    sim.save_state("enhanced_simulation_state.pkl")
    
    with open("enhanced_simulation_results.json", 'w') as f:
        # Convert summary to JSON-serializable format
        def convert_to_json_serializable(obj):
            if isinstance(obj, dict):
                return {str(k): convert_to_json_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_json_serializable(item) for item in obj]
            elif isinstance(obj, (Strategy, np.float64, np.float32, np.int64, np.int32)):
                return str(obj)
            else:
                return obj
        
        json_summary = convert_to_json_serializable(summary)
        json.dump(json_summary, f, indent=2)
    
    print("\n✅ Results saved to enhanced_simulation_results.json")
