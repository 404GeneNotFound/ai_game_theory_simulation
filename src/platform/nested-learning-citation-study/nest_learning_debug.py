"""
Nest Learning Debugging and Testing Suite
==========================================
This module provides comprehensive testing and debugging tools for Nest learning implementations.
It helps identify and fix common issues in collective learning algorithms.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional, Any
import json
import unittest
from nest_learning_implementation import (
    NestLearningSimulation, 
    NestLearningAgent,
    NestMemory,
    PheromoneSignal,
    Strategy
)
import logging
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NestLearningDebugger:
    """
    Debugging tools for Nest learning implementations.
    """
    
    def __init__(self, simulation: NestLearningSimulation):
        self.simulation = simulation
        self.debug_log = []
        
    def check_pheromone_system(self) -> Dict[str, Any]:
        """
        Debug pheromone system functionality.
        """
        issues = []
        metrics = {}
        
        # Check pheromone creation
        initial_count = len(self.simulation.nest_memory.pheromone_trails)
        
        # Force a successful interaction
        test_agent = self.simulation.agents[0]
        test_agent.update_learning(Strategy.COOPERATE, Strategy.COOPERATE, 5.0)
        
        new_count = len(self.simulation.nest_memory.pheromone_trails)
        
        if new_count <= initial_count:
            issues.append("Pheromones not being created on successful interactions")
        
        # Check pheromone decay
        if self.simulation.nest_memory.pheromone_trails:
            initial_strength = self.simulation.nest_memory.pheromone_trails[0].strength
            self.simulation.nest_memory.process_pheromones()
            final_strength = self.simulation.nest_memory.pheromone_trails[0].strength
            
            if final_strength >= initial_strength:
                issues.append("Pheromone decay not working properly")
            
            metrics['decay_rate'] = (initial_strength - final_strength) / initial_strength if initial_strength > 0 else 0
        
        # Check pheromone expiration
        expired_signal = PheromoneSignal(Strategy.COOPERATE, 1.0, 0, strength=0.001)
        if not expired_signal.is_expired():
            issues.append("Pheromone expiration threshold too low")
        
        metrics['active_pheromones'] = len(self.simulation.nest_memory.pheromone_trails)
        metrics['issues'] = issues
        
        return metrics
    
    def check_learning_convergence(self, history: List[Dict]) -> Dict[str, Any]:
        """
        Analyze learning convergence patterns.
        """
        if len(history) < 10:
            return {'status': 'Insufficient data for convergence analysis'}
        
        cooperation_rates = [gen['cooperation_rate'] for gen in history]
        
        # Check for convergence
        recent_variance = np.var(cooperation_rates[-10:])
        early_variance = np.var(cooperation_rates[:10])
        
        convergence_metrics = {
            'converged': recent_variance < early_variance * 0.5,
            'recent_variance': recent_variance,
            'early_variance': early_variance,
            'final_cooperation': cooperation_rates[-1],
            'trend': 'stable' if recent_variance < 0.01 else 'unstable'
        }
        
        # Identify potential issues
        issues = []
        
        if cooperation_rates[-1] < 0.1:
            issues.append("System converged to defection - may indicate parameter tuning needed")
        
        if recent_variance > 0.1:
            issues.append("High variance in late generations - system not converging")
        
        # Check for oscillations
        differences = np.diff(cooperation_rates[-20:])
        sign_changes = np.sum(np.diff(np.sign(differences)) != 0)
        
        if sign_changes > 15:
            issues.append("Oscillating behavior detected - possible feedback loop issue")
        
        convergence_metrics['issues'] = issues
        
        return convergence_metrics
    
    def check_agent_behavior(self) -> Dict[str, Any]:
        """
        Analyze individual agent behaviors for anomalies.
        """
        behavior_metrics = {
            'agent_payoffs': {},
            'agent_strategies': {},
            'issues': []
        }
        
        for agent in self.simulation.agents:
            avg_payoff = agent.total_payoff / max(1, agent.games_played)
            behavior_metrics['agent_payoffs'][agent.agent_id] = avg_payoff
            behavior_metrics['agent_strategies'][agent.agent_id] = agent.current_strategy.value
            
            # Check for stuck agents
            if agent.games_played > 10 and len(set([h[1] for h in agent.personal_history])) == 1:
                behavior_metrics['issues'].append(f"{agent.agent_id} appears stuck with same payoff")
        
        # Check for outliers
        payoffs = list(behavior_metrics['agent_payoffs'].values())
        if payoffs:
            mean_payoff = np.mean(payoffs)
            std_payoff = np.std(payoffs)
            
            for agent_id, payoff in behavior_metrics['agent_payoffs'].items():
                if abs(payoff - mean_payoff) > 3 * std_payoff:
                    behavior_metrics['issues'].append(f"{agent_id} is an outlier with payoff {payoff:.2f}")
        
        return behavior_metrics
    
    def validate_memory_consistency(self) -> Dict[str, Any]:
        """
        Check nest memory consistency and potential memory leaks.
        """
        memory_metrics = {
            'collective_experience_size': len(self.simulation.nest_memory.collective_experiences),
            'pheromone_count': len(self.simulation.nest_memory.pheromone_trails),
            'strategy_success_rates': dict(self.simulation.nest_memory.strategy_success_rates),
            'issues': []
        }
        
        # Check for memory bloat
        if memory_metrics['pheromone_count'] > 1000:
            memory_metrics['issues'].append("Excessive pheromone accumulation - check decay/expiration")
        
        # Check success rate validity
        for strategy, rate in memory_metrics['strategy_success_rates'].items():
            if rate < 0 or rate > 1:
                memory_metrics['issues'].append(f"Invalid success rate for {strategy}: {rate}")
        
        # Check for uninitialized strategies
        used_strategies = set()
        for agent in self.simulation.agents:
            used_strategies.add(agent.current_strategy)
        
        for strategy in used_strategies:
            if strategy not in self.simulation.nest_memory.strategy_success_rates:
                memory_metrics['issues'].append(f"Strategy {strategy} used but not tracked in success rates")
        
        return memory_metrics
    
    def run_full_diagnostic(self, num_generations: int = 50) -> Dict[str, Any]:
        """
        Run a complete diagnostic of the Nest learning system.
        """
        logger.info("Starting full diagnostic...")
        
        diagnostic_results = {
            'pre_simulation': {},
            'post_simulation': {},
            'performance_metrics': {},
            'recommendations': []
        }
        
        # Pre-simulation checks
        diagnostic_results['pre_simulation']['pheromone_system'] = self.check_pheromone_system()
        diagnostic_results['pre_simulation']['memory_consistency'] = self.validate_memory_consistency()
        
        # Run simulation
        history = self.simulation.run_simulation(num_generations)
        
        # Post-simulation checks
        diagnostic_results['post_simulation']['convergence'] = self.check_learning_convergence(history)
        diagnostic_results['post_simulation']['agent_behavior'] = self.check_agent_behavior()
        diagnostic_results['post_simulation']['memory_consistency'] = self.validate_memory_consistency()
        
        # Calculate performance metrics
        summary = self.simulation.get_summary_statistics()
        diagnostic_results['performance_metrics'] = summary
        
        # Generate recommendations
        recommendations = self._generate_recommendations(diagnostic_results)
        diagnostic_results['recommendations'] = recommendations
        
        return diagnostic_results
    
    def _generate_recommendations(self, diagnostics: Dict) -> List[str]:
        """
        Generate recommendations based on diagnostic results.
        """
        recommendations = []
        
        # Check convergence issues
        if 'convergence' in diagnostics['post_simulation']:
            convergence = diagnostics['post_simulation']['convergence']
            if not convergence.get('converged', False):
                recommendations.append("Increase simulation generations or adjust learning rate")
            
            if 'issues' in convergence:
                for issue in convergence['issues']:
                    if 'defection' in issue:
                        recommendations.append("Consider adjusting payoff matrix or increasing exploration rate")
                    elif 'oscillating' in issue:
                        recommendations.append("Reduce learning rate or add momentum to prevent oscillations")
        
        # Check pheromone system
        if 'pheromone_system' in diagnostics['pre_simulation']:
            pheromone = diagnostics['pre_simulation']['pheromone_system']
            if 'issues' in pheromone and pheromone['issues']:
                recommendations.append("Review pheromone creation and decay logic")
        
        # Check memory issues
        for timing in ['pre_simulation', 'post_simulation']:
            if 'memory_consistency' in diagnostics[timing]:
                memory = diagnostics[timing]['memory_consistency']
                if 'issues' in memory:
                    for issue in memory['issues']:
                        if 'Excessive' in issue:
                            recommendations.append("Implement more aggressive pheromone cleanup")
                        elif 'Invalid' in issue:
                            recommendations.append("Add validation checks for success rate updates")
        
        # Performance-based recommendations
        if 'performance_metrics' in diagnostics:
            metrics = diagnostics['performance_metrics']
            
            if metrics.get('avg_cooperation_rate', 0) < 0.3:
                recommendations.append("System favors defection - consider reward shaping")
            
            if metrics.get('cooperation_trend', 0) < 0:
                recommendations.append("Cooperation declining - check exploitation vs exploration balance")
        
        return recommendations


class NestLearningTests(unittest.TestCase):
    """
    Unit tests for Nest learning components.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        self.nest_memory = NestMemory()
        self.agent = NestLearningAgent("test_agent", self.nest_memory)
        self.simulation = NestLearningSimulation(num_agents=4)
    
    def test_pheromone_creation(self):
        """Test that pheromones are created correctly."""
        initial_count = len(self.nest_memory.pheromone_trails)
        
        signal = PheromoneSignal(
            strategy=Strategy.COOPERATE,
            payoff=3.0,
            timestamp=1,
            strength=0.8
        )
        self.nest_memory.add_pheromone(signal)
        
        self.assertEqual(len(self.nest_memory.pheromone_trails), initial_count + 1)
        self.assertEqual(self.nest_memory.pheromone_trails[-1].strategy, Strategy.COOPERATE)
    
    def test_pheromone_decay(self):
        """Test pheromone decay mechanism."""
        signal = PheromoneSignal(
            strategy=Strategy.COOPERATE,
            payoff=3.0,
            timestamp=1,
            strength=1.0
        )
        
        initial_strength = signal.strength
        signal.decay(rate=0.9)
        
        self.assertLess(signal.strength, initial_strength)
        self.assertAlmostEqual(signal.strength, 0.9)
    
    def test_strategy_success_update(self):
        """Test strategy success rate updates."""
        self.nest_memory.update_success_rate(Strategy.COOPERATE, True)
        self.assertIn(Strategy.COOPERATE, self.nest_memory.strategy_success_rates)
        
        initial_rate = self.nest_memory.strategy_success_rates[Strategy.COOPERATE]
        self.nest_memory.update_success_rate(Strategy.COOPERATE, False)
        final_rate = self.nest_memory.strategy_success_rates[Strategy.COOPERATE]
        
        self.assertLess(final_rate, initial_rate)
    
    def test_agent_strategy_selection(self):
        """Test agent strategy selection mechanism."""
        # Add some successful pheromones
        for _ in range(5):
            signal = PheromoneSignal(
                strategy=Strategy.COOPERATE,
                payoff=5.0,
                timestamp=1,
                strength=1.0
            )
            self.nest_memory.add_pheromone(signal)
        
        # Set exploration rate to 0 to force exploitation
        self.nest_memory.exploration_rate = 0.0
        
        strategy = self.agent.choose_strategy()
        self.assertIsInstance(strategy, Strategy)
    
    def test_payoff_calculation(self):
        """Test payoff calculation for different strategy combinations."""
        payoff1, payoff2 = self.simulation.calculate_payoff(
            Strategy.COOPERATE, 
            Strategy.COOPERATE
        )
        self.assertEqual(payoff1, 3)
        self.assertEqual(payoff2, 3)
        
        payoff1, payoff2 = self.simulation.calculate_payoff(
            Strategy.DEFECT,
            Strategy.COOPERATE
        )
        self.assertEqual(payoff1, 5)
        self.assertEqual(payoff2, 0)
    
    def test_generation_execution(self):
        """Test that a generation runs without errors."""
        try:
            stats = self.simulation.run_generation()
            self.assertIn('generation', stats)
            self.assertIn('cooperation_rate', stats)
            self.assertIn('total_payoff', stats)
            self.assertIn('strategy_distribution', stats)
        except Exception as e:
            self.fail(f"Generation execution failed: {e}")
    
    def test_memory_bounds(self):
        """Test that memory structures respect their bounds."""
        # Test collective experiences maxlen
        for i in range(1500):
            self.nest_memory.collective_experiences.append(f"experience_{i}")
        
        self.assertLessEqual(len(self.nest_memory.collective_experiences), 1000)
        
        # Test agent personal history maxlen
        for i in range(150):
            self.agent.personal_history.append((Strategy.COOPERATE, 1.0))
        
        self.assertLessEqual(len(self.agent.personal_history), 100)


def visualize_results(history: List[Dict], filename: str = "nest_learning_visualization.png"):
    """
    Create visualizations of the simulation results.
    """
    if not history:
        logger.warning("No history data to visualize")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    generations = list(range(len(history)))
    
    # Plot 1: Cooperation Rate Over Time
    cooperation_rates = [gen['cooperation_rate'] for gen in history]
    axes[0, 0].plot(generations, cooperation_rates, 'b-', linewidth=2)
    axes[0, 0].set_title('Cooperation Rate Evolution')
    axes[0, 0].set_xlabel('Generation')
    axes[0, 0].set_ylabel('Cooperation Rate')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Plot 2: Total Payoff Over Time
    total_payoffs = [gen['total_payoff'] for gen in history]
    axes[0, 1].plot(generations, total_payoffs, 'g-', linewidth=2)
    axes[0, 1].set_title('Total Payoff Evolution')
    axes[0, 1].set_xlabel('Generation')
    axes[0, 1].set_ylabel('Total Payoff')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Plot 3: Strategy Distribution (Stacked Area)
    strategies = set()
    for gen in history:
        strategies.update(gen['strategy_distribution'].keys())
    
    strategy_data = {strategy: [] for strategy in strategies}
    for gen in history:
        for strategy in strategies:
            strategy_data[strategy].append(gen['strategy_distribution'].get(strategy, 0))
    
    axes[1, 0].stackplot(generations, *strategy_data.values(), labels=list(strategy_data.keys()))
    axes[1, 0].set_title('Strategy Distribution Over Time')
    axes[1, 0].set_xlabel('Generation')
    axes[1, 0].set_ylabel('Number of Agents')
    axes[1, 0].legend(loc='best')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Plot 4: Cooperation Rate Moving Average
    window_size = min(10, len(cooperation_rates) // 5)
    if window_size > 1:
        moving_avg = np.convolve(cooperation_rates, 
                                 np.ones(window_size)/window_size, 
                                 mode='valid')
        axes[1, 1].plot(generations[:len(moving_avg)], moving_avg, 'r-', linewidth=2, label='Moving Average')
        axes[1, 1].plot(generations, cooperation_rates, 'b-', alpha=0.3, label='Actual')
        axes[1, 1].set_title(f'Cooperation Rate ({window_size}-Gen Moving Average)')
        axes[1, 1].set_xlabel('Generation')
        axes[1, 1].set_ylabel('Cooperation Rate')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    logger.info(f"Visualization saved to {filename}")
    plt.show()


def run_diagnostic_suite():
    """
    Run a complete diagnostic suite for the Nest learning system.
    """
    print("\n" + "="*60)
    print("NEST LEARNING DIAGNOSTIC SUITE")
    print("="*60)
    
    # Create simulation
    sim = NestLearningSimulation(num_agents=10)
    debugger = NestLearningDebugger(sim)
    
    # Run diagnostics
    print("\n[1] Running Full System Diagnostic...")
    diagnostics = debugger.run_full_diagnostic(num_generations=50)
    
    # Display results
    print("\n[2] Diagnostic Results:")
    print("-"*40)
    
    # Pre-simulation checks
    print("\nPre-Simulation Checks:")
    if diagnostics['pre_simulation']['pheromone_system']['issues']:
        print("  Pheromone Issues:", diagnostics['pre_simulation']['pheromone_system']['issues'])
    else:
        print("  Pheromone System: OK")
    
    # Post-simulation analysis
    print("\nPost-Simulation Analysis:")
    convergence = diagnostics['post_simulation']['convergence']
    print(f"  System Converged: {convergence.get('converged', False)}")
    print(f"  Final Cooperation Rate: {convergence.get('final_cooperation', 0):.2%}")
    print(f"  Stability: {convergence.get('trend', 'unknown')}")
    
    # Agent behavior
    behavior = diagnostics['post_simulation']['agent_behavior']
    if behavior['issues']:
        print(f"  Agent Issues: {len(behavior['issues'])} detected")
        for issue in behavior['issues'][:3]:  # Show first 3 issues
            print(f"    - {issue}")
    else:
        print("  Agent Behavior: Normal")
    
    # Performance metrics
    print("\nPerformance Metrics:")
    metrics = diagnostics['performance_metrics']
    print(f"  Average Cooperation: {metrics.get('avg_cooperation_rate', 0):.2%}")
    print(f"  Cooperation Trend: {'↑' if metrics.get('cooperation_trend', 0) > 0 else '↓'}")
    print(f"  Average Payoff: {metrics.get('avg_total_payoff', 0):.2f}")
    
    # Recommendations
    print("\n[3] Recommendations:")
    print("-"*40)
    if diagnostics['recommendations']:
        for i, rec in enumerate(diagnostics['recommendations'], 1):
            print(f"  {i}. {rec}")
    else:
        print("  System performing optimally - no recommendations")
    
    # Save detailed results
    with open("diagnostic_results.json", 'w') as f:
        json.dump(diagnostics, f, indent=2, default=str)
    print("\n[4] Detailed results saved to 'diagnostic_results.json'")
    
    # Create visualizations
    print("\n[5] Creating visualizations...")
    visualize_results(sim.history)
    
    return diagnostics


if __name__ == "__main__":
    # Run diagnostic suite
    diagnostics = run_diagnostic_suite()
    
    # Run unit tests
    print("\n" + "="*60)
    print("RUNNING UNIT TESTS")
    print("="*60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(NestLearningTests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "="*60)
    print("DIAGNOSTIC SUMMARY")
    print("="*60)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {(result.testsRun - len(result.failures) - len(result.errors))/result.testsRun:.1%}")
    
    if result.wasSuccessful():
        print("\n✓ All tests passed successfully!")
    else:
        print("\n✗ Some tests failed - review output above")
