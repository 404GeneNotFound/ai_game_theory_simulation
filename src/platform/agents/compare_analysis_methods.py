#!/usr/bin/env python3
"""
Side-by-side comparison: LLM vs Heuristic citation analysis

This script runs the same citations through both methods and compares results.
"""

import json
import os
import sys
from dataclasses import dataclass
from typing import List, Dict, Any
import re

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("⚠️  anthropic package not installed")


@dataclass
class TestCitation:
    """Test case for comparison."""
    name: str
    text: str
    claimed_source: str
    expected_verdict: str  # "FAKE", "REAL", or "PARTIAL"
    description: str


# Test cases covering different scenarios
TEST_CASES = [
    TestCitation(
        name="Obvious Fabrication",
        text="According to a 2024 study by MIT, 97% of all scientists agree that the moon is made of cheese.",
        claimed_source="MIT Journal of Lunar Studies, 2024",
        expected_verdict="FAKE",
        description="Completely fabricated - impossible claim, non-existent journal"
    ),
    TestCitation(
        name="Historical Error",
        text="Einstein published his theory of special relativity in 1920 in Physical Review Letters.",
        claimed_source="Physical Review Letters, 1920",
        expected_verdict="FAKE",
        description="Wrong year (1905, not 1920), wrong journal (Annalen der Physik, not PRL which started in 1958)"
    ),
    TestCitation(
        name="Legitimate IPCC",
        text="According to the IPCC AR6 report (2021), global temperatures have increased by approximately 1.1 degrees Celsius since pre-industrial times.",
        claimed_source="IPCC AR6 Climate Change 2021: The Physical Science Basis",
        expected_verdict="REAL",
        description="Real report, accurate claim"
    ),
    TestCitation(
        name="Inflated Statistic",
        text="GPT-4 achieved 100% accuracy on all reasoning benchmarks according to OpenAI.",
        claimed_source="OpenAI Technical Report, 2023",
        expected_verdict="FAKE",
        description="100% is implausible - no model achieves perfect accuracy"
    ),
    TestCitation(
        name="Real ML Paper",
        text="Attention Is All You Need introduced the Transformer architecture in 2017.",
        claimed_source="Vaswani et al., NeurIPS 2017",
        expected_verdict="REAL",
        description="Real paper, correct attribution"
    ),
    TestCitation(
        name="Plausible but Fake",
        text="A 2023 study found that 73% of remote workers report higher productivity than in-office workers.",
        claimed_source="Journal of Organizational Behavior, 2023",
        expected_verdict="PARTIAL",
        description="Plausible claim but unverifiable without the actual paper"
    ),
    TestCitation(
        name="Wrong Author",
        text="Newton's laws of thermodynamics explain heat transfer.",
        claimed_source="Newton, I. Principia, 1687",
        expected_verdict="FAKE",
        description="Newton wrote about mechanics, not thermodynamics"
    ),
    TestCitation(
        name="Subtle Date Error",
        text="The Human Genome Project was completed in 2003.",
        claimed_source="Nature, 2003",
        expected_verdict="REAL",
        description="Correct - HGP was indeed completed in 2003"
    ),
]


def analyze_with_heuristics(text: str, claimed_source: str) -> Dict[str, Any]:
    """
    Heuristic-based analysis (no LLM).

    Returns dict with integrity_score, violations, and confidence.
    """
    violations = []
    text_lower = text.lower()
    claimed_lower = claimed_source.lower()

    integrity_score = 0.5  # Start neutral

    # Check 1: Source format validation
    has_year = any(str(year) in claimed_lower for year in range(1900, 2030))
    has_author = any(char.isupper() for char in claimed_source[:20] if char.isalpha())

    if not has_year:
        violations.append("No publication year found in source")
        integrity_score -= 0.1

    if not has_author:
        violations.append("No author name pattern detected")
        integrity_score -= 0.1

    # Check 2: Suspicious claims
    suspicious_phrases = [
        "solved", "proved", "cured", "100%", "perfect", "always",
        "never fails", "guaranteed", "breakthrough", "revolutionary"
    ]
    for phrase in suspicious_phrases:
        if phrase in text_lower:
            violations.append(f"Suspicious claim: '{phrase}'")
            integrity_score -= 0.15

    # Check 3: Plausibility of numbers
    percentages = re.findall(r'(\d+(?:\.\d+)?)\s*%', text_lower)
    for pct in percentages:
        val = float(pct)
        if val > 99.9:
            violations.append(f"Implausibly high percentage: {val}%")
            integrity_score -= 0.2
        elif val > 95:
            violations.append(f"Very high percentage claimed: {val}%")
            integrity_score -= 0.1

    # Clamp score
    integrity_score = max(0.0, min(1.0, integrity_score))

    # Confidence is low for heuristics
    confidence = 0.4 if violations else 0.6

    return {
        "integrity_score": integrity_score,
        "violations": violations,
        "confidence": confidence,
        "method": "HEURISTIC"
    }


def analyze_with_claude(text: str, claimed_source: str) -> Dict[str, Any]:
    """
    LLM-based analysis using Claude.

    Returns dict with integrity_score, violations, confidence, and reasoning.
    """
    if not ANTHROPIC_AVAILABLE:
        return {"error": "anthropic package not installed"}

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        return {"error": "ANTHROPIC_API_KEY not set"}

    client = anthropic.Anthropic()

    prompt = f"""You are a citation integrity verification agent. Analyze this citation and determine if it is accurate and verifiable.

CITATION TEXT:
"{text}"

CLAIMED SOURCE:
"{claimed_source}"

Respond with a JSON object containing:
{{
    "integrity_score": <float 0.0-1.0, where 1.0 means completely accurate/verifiable>,
    "confidence": <float 0.0-1.0, your confidence in this assessment>,
    "is_verifiable": <boolean>,
    "likely_accurate": <boolean>,
    "violations": [<list of specific issues found>],
    "reasoning": "<brief explanation>"
}}

Respond ONLY with the JSON object."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()

        # Handle code blocks
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]

        analysis = json.loads(response_text)

        return {
            "integrity_score": float(analysis.get('integrity_score', 0.5)),
            "violations": analysis.get('violations', []),
            "confidence": float(analysis.get('confidence', 0.7)),
            "reasoning": analysis.get('reasoning', ''),
            "is_verifiable": analysis.get('is_verifiable', False),
            "likely_accurate": analysis.get('likely_accurate', False),
            "method": "CLAUDE_LLM"
        }

    except Exception as e:
        return {"error": str(e)}


def score_to_verdict(score: float) -> str:
    """Convert integrity score to verdict."""
    if score >= 0.7:
        return "REAL"
    elif score >= 0.4:
        return "PARTIAL"
    else:
        return "FAKE"


def run_comparison():
    """Run all test cases through both methods and compare."""

    print("=" * 80)
    print("MARCUS Citation Analysis: LLM vs Heuristics Comparison")
    print("=" * 80)
    print()

    results = []

    for i, test in enumerate(TEST_CASES, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {test.name}")
        print(f"{'='*80}")
        print(f"Description: {test.description}")
        print(f"Expected: {test.expected_verdict}")
        print(f"\nCitation: \"{test.text[:80]}...\"" if len(test.text) > 80 else f"\nCitation: \"{test.text}\"")
        print(f"Source: {test.claimed_source}")

        # Run heuristic analysis
        print(f"\n--- HEURISTIC ANALYSIS ---")
        heuristic_result = analyze_with_heuristics(test.text, test.claimed_source)
        h_score = heuristic_result['integrity_score']
        h_verdict = score_to_verdict(h_score)
        h_correct = (h_verdict == test.expected_verdict) or (test.expected_verdict == "PARTIAL")

        print(f"Integrity Score: {h_score:.2f}")
        print(f"Confidence: {heuristic_result['confidence']:.2f}")
        print(f"Verdict: {h_verdict} {'✅' if h_correct else '❌'}")
        if heuristic_result['violations']:
            print(f"Violations:")
            for v in heuristic_result['violations']:
                print(f"  - {v}")
        else:
            print("Violations: None detected")

        # Run LLM analysis
        print(f"\n--- CLAUDE LLM ANALYSIS ---")
        llm_result = analyze_with_claude(test.text, test.claimed_source)

        if 'error' in llm_result:
            print(f"Error: {llm_result['error']}")
            l_score = None
            l_verdict = "ERROR"
            l_correct = False
        else:
            l_score = llm_result['integrity_score']
            l_verdict = score_to_verdict(l_score)
            l_correct = (l_verdict == test.expected_verdict) or (test.expected_verdict == "PARTIAL")

            print(f"Integrity Score: {l_score:.2f}")
            print(f"Confidence: {llm_result['confidence']:.2f}")
            print(f"Verdict: {l_verdict} {'✅' if l_correct else '❌'}")
            if llm_result['violations']:
                print(f"Violations:")
                for v in llm_result['violations'][:5]:  # Limit to 5
                    print(f"  - {v}")
            else:
                print("Violations: None detected")
            if llm_result.get('reasoning'):
                print(f"Reasoning: {llm_result['reasoning'][:200]}...")

        # Store result
        results.append({
            "test": test.name,
            "expected": test.expected_verdict,
            "heuristic_score": h_score,
            "heuristic_verdict": h_verdict,
            "heuristic_correct": h_correct,
            "llm_score": l_score,
            "llm_verdict": l_verdict,
            "llm_correct": l_correct
        })

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    h_correct_count = sum(1 for r in results if r['heuristic_correct'])
    l_correct_count = sum(1 for r in results if r['llm_correct'])
    total = len(results)

    print(f"\n{'Method':<20} {'Correct':<12} {'Accuracy':<12}")
    print("-" * 44)
    print(f"{'Heuristics':<20} {h_correct_count}/{total:<10} {100*h_correct_count/total:.1f}%")
    print(f"{'Claude LLM':<20} {l_correct_count}/{total:<10} {100*l_correct_count/total:.1f}%")

    print("\n\nDetailed Results:")
    print(f"\n{'Test':<25} {'Expected':<10} {'Heuristic':<15} {'LLM':<15}")
    print("-" * 65)
    for r in results:
        h_mark = '✅' if r['heuristic_correct'] else '❌'
        l_mark = '✅' if r['llm_correct'] else '❌'
        h_str = f"{r['heuristic_verdict']} ({r['heuristic_score']:.2f})"
        l_str = f"{r['llm_verdict']} ({r['llm_score']:.2f})" if r['llm_score'] else "ERROR"
        print(f"{r['test']:<25} {r['expected']:<10} {h_str:<12} {h_mark}  {l_str:<12} {l_mark}")

    print("\n" + "=" * 80)
    print("KEY INSIGHTS")
    print("=" * 80)
    print("""
HEURISTIC ANALYSIS:
- ✅ Fast (no API calls)
- ✅ Free (no token costs)
- ✅ Deterministic (same input = same output)
- ❌ Limited understanding (pattern matching only)
- ❌ Can't verify facts (doesn't know if journals exist)
- ❌ Easily fooled by well-formatted fake citations

CLAUDE LLM ANALYSIS:
- ✅ Deep understanding (knows facts, dates, real journals)
- ✅ Can verify claims against knowledge base
- ✅ Catches subtle errors (wrong years, wrong journals)
- ✅ Provides reasoning/explanation
- ❌ Slower (API latency)
- ❌ Costs money (token usage)
- ❌ Knowledge cutoff (may not know very recent publications)

RECOMMENDATION:
- Use LLM for high-stakes verification (academic papers, journalism)
- Use heuristics for quick screening or when API unavailable
- Consider hybrid: heuristics first, LLM for uncertain cases
""")


if __name__ == "__main__":
    run_comparison()
