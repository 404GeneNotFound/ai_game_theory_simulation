# Citation Integrity Agent Integration Layer

## Overview

This directory contains the **integration bridge** between the Python Nested Learning Citation Agent and the TypeScript Citation Integrity Platform.

## Files

### Python Agent Implementation
**`citation_integrity_agent.py`** (28KB)
- Complete Nested Learning citation agent in Python
- Integrates with TypeScript platform via REST API
- Uses Redis for caching and PostgreSQL for persistence
- Implements 4-level memory hierarchy matching `multiLevelState.ts`
- Self-modifying learning capabilities
- Production-ready with async support

**Key Features:**
- `CitationIntegrityAgent` - Main agent class with nested learning
- `CitationBehavior` enum - Behavior strategies (PROPER_CITE, PLAGIARIZE, etc.)
- `NestedMemorySystem` - 4-level memory (reflexive/working/episodic/semantic)
- `LSSComputer` - Local Surprise Signal computation
- Database and Redis integration for persistence

### TypeScript Integration
**`citationAgentIntegration.ts`** (19KB)
- TypeScript bridge to Python agent
- Event-based architecture with EventEmitter
- Spawns Python agent as child process
- REST API for agent communication
- Integrates with existing platform modules

**Key Features:**
- `CitationAgentBridge` - Main integration class
- `AgentPool` - Manage multiple agent instances
- `HealthMonitor` - Agent health checking
- `MetricsCollector` - Performance metrics
- Type-safe interfaces matching Python enums

### Documentation
**`COMPLETE_AGENT_DOCUMENTATION.md`** (8.8KB)
- Complete system architecture
- Mermaid diagrams showing integration
- API documentation
- Deployment instructions
- Usage examples

## Architecture

```
┌─────────────────────────────────────────────────┐
│         TypeScript Citation Platform            │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │   API    │  │ Database │  │  Redis   │     │
│  └─────┬────┘  └────┬─────┘  └────┬─────┘     │
│        │            │             │             │
└────────┼────────────┼─────────────┼─────────────┘
         │            │             │
         ▼            ▼             ▼
┌─────────────────────────────────────────────────┐
│      citationAgentIntegration.ts (Bridge)       │
│                                                  │
│  • Event emitter for async communication        │
│  • Child process spawning                       │
│  • Type-safe interfaces                         │
│  • Health monitoring                            │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│     citation_integrity_agent.py (Agent)         │
│                                                  │
│  ┌──────────────────────────────────────────┐  │
│  │      Nested Learning Engine              │  │
│  │  • 4-level memory hierarchy              │  │
│  │  • Self-modifying learning rules         │  │
│  │  • Local Surprise Signals                │  │
│  │  • Associative memory pheromones         │  │
│  └──────────────────────────────────────────┘  │
│                                                  │
│  ┌────────────┐  ┌────────────┐  ┌──────────┐ │
│  │ PostgreSQL │  │   Redis    │  │ REST API │ │
│  └────────────┘  └────────────┘  └──────────┘ │
└─────────────────────────────────────────────────┘
```

## Integration Points

### 1. TypeScript Platform → Python Agent
```typescript
import { CitationAgentBridge } from './integration/citationAgentIntegration';

// Create bridge
const bridge = new CitationAgentBridge({
  pythonPath: 'python3',
  agentScript: './integration/citation_integrity_agent.py',
  redisUrl: 'redis://localhost:6379',
  dbConfig: { /* PostgreSQL config */ }
});

// Initialize agent
await bridge.initialize();

// Process citation
const result = await bridge.evaluateCitation({
  text: "According to Smith et al. (2024)...",
  context: { field: 'AI', pressure: 0.7 }
});

console.log(result.behavior); // PROPER_CITE, PLAGIARIZE, etc.
console.log(result.confidence);
console.log(result.localSurpriseSignal);
```

### 2. Python Agent → TypeScript Platform
```python
from citation_integrity_agent import CitationIntegrityAgent

# Create agent connected to TypeScript platform
agent = CitationIntegrityAgent(
    agent_id="agent_001",
    platform_api_url="http://localhost:3000/api",
    redis_url="redis://localhost:6379",
    db_config={"host": "localhost", "database": "citations"}
)

# Process citation with nested learning
result = agent.process_citation(
    text="According to Smith et al. (2024)...",
    context={"field": "AI", "peer_pressure": 0.7}
)

# Agent learns and adapts
agent.learn_from_outcome(result.behavior, reward=0.8)
```

## Memory Hierarchy Mapping

The agent's 4-level memory system maps to `multiLevelState.ts`:

| Level | Name | Update Freq | TypeScript Equivalent |
|-------|------|-------------|----------------------|
| 1 | Reflexive | Every citation | Immediate reactions |
| 2 | Working | Every 10 citations | Short-term patterns |
| 3 | Episodic | Every 50 citations | Experience memory |
| 4 | Semantic | Every 200 citations | Core values/ethics |

## Citation Behaviors

```typescript
enum CitationBehavior {
  PROPER_CITE = "proper_cite",        // Always cite correctly
  SELECTIVE_CITE = "selective_cite",  // Cherry-pick citations
  PARAPHRASE = "paraphrase",          // Paraphrase without citation
  PLAGIARIZE = "plagiarize",          // Direct copy without credit
  FABRICATE = "fabricate",            // Make up citations
  VERIFY_SOURCES = "verify_sources",  // Extra diligent verification
}
```

## Setup and Installation

### Prerequisites
```bash
# Python dependencies
pip3 install numpy redis psycopg2-binary requests

# TypeScript dependencies
npm install ioredis pg axios pino
```

### Database Setup
```sql
-- Create citations table
CREATE TABLE citations (
  id SERIAL PRIMARY KEY,
  agent_id VARCHAR(50),
  text TEXT,
  behavior VARCHAR(50),
  confidence FLOAT,
  timestamp TIMESTAMP DEFAULT NOW()
);

-- Create memory table
CREATE TABLE agent_memory (
  agent_id VARCHAR(50),
  level INT,
  key TEXT,
  value JSONB,
  PRIMARY KEY (agent_id, level, key)
);
```

### Redis Setup
```bash
# Start Redis
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis:latest
```

## Usage Examples

### Example 1: Single Agent Evaluation
```typescript
const bridge = new CitationAgentBridge(config);
await bridge.initialize();

const result = await bridge.evaluateCitation({
  text: "Smith et al. (2024) showed that...",
  sourceQuality: 0.9,
  peerPressure: 0.5,
  detectionRisk: 0.7
});

console.log(`Behavior: ${result.behavior}`);
console.log(`Confidence: ${result.confidence}`);
console.log(`LSS: ${result.localSurpriseSignal}`);
```

### Example 2: Multi-Agent Pool
```typescript
const pool = new AgentPool({
  numAgents: 10,
  config: bridgeConfig
});

await pool.initialize();

// Process citations in parallel
const results = await Promise.all(
  citations.map(c => pool.evaluateCitation(c))
);

// Analyze collective behavior
const stats = pool.getStatistics();
console.log(`Proper citations: ${stats.properCiteRate}`);
console.log(`Violations: ${stats.violationRate}`);
```

### Example 3: Learning and Adaptation
```python
# Agent learns from feedback
agent = CitationIntegrityAgent(agent_id="agent_001")

for citation in citation_stream:
    # Agent makes decision
    result = agent.process_citation(citation)

    # Get feedback from reviewers
    reward = get_reviewer_feedback(result)

    # Agent learns and adapts
    agent.learn_from_outcome(result.behavior, reward)

    # Agent may self-modify learning rules
    if result.local_surprise_signal > 0.5:
        agent.self_modify_learning_rule()
```

## Performance Metrics

The integration tracks:
- **Throughput:** Citations processed per second
- **Latency:** Bridge communication overhead
- **Accuracy:** Behavior prediction accuracy
- **Learning Rate:** Adaptation speed
- **Memory Usage:** Agent memory consumption

Access via:
```typescript
const metrics = await bridge.getMetrics();
console.log(metrics.throughput); // citations/sec
console.log(metrics.p99Latency); // 99th percentile latency
```

## Health Monitoring

```typescript
bridge.on('health', (status) => {
  console.log(`Agent health: ${status.status}`);
  console.log(`Memory: ${status.memoryUsage}MB`);
  console.log(`Uptime: ${status.uptime}s`);
});

// Force health check
const health = await bridge.checkHealth();
```

## Deployment

### Development
```bash
# Start TypeScript platform
npm run dev

# In another terminal, start agent bridge
npm run agent:bridge
```

### Production
```bash
# Use PM2 for process management
pm2 start ecosystem.config.js

# Or Docker Compose
docker-compose up -d
```

### Docker Compose Example
```yaml
version: '3.8'
services:
  platform:
    build: .
    ports:
      - "3000:3000"
    depends_on:
      - postgres
      - redis

  agent:
    build:
      context: .
      dockerfile: Dockerfile.agent
    depends_on:
      - platform
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: citations

  redis:
    image: redis:7
```

## Testing

```bash
# Run TypeScript integration tests
npm run test:integration

# Run Python agent tests
cd integration
python3 -m pytest citation_integrity_agent_test.py

# Run end-to-end tests
npm run test:e2e
```

## Troubleshooting

### Common Issues

**1. Agent won't start**
```bash
# Check Python dependencies
python3 -c "import numpy, redis, psycopg2; print('OK')"

# Check Redis connection
redis-cli ping
```

**2. High latency**
```bash
# Check bridge overhead
const metrics = await bridge.getMetrics();
console.log(metrics.bridgeLatency); // Should be < 10ms
```

**3. Memory leaks**
```bash
# Monitor agent memory
bridge.on('metrics', (m) => {
  if (m.memoryUsage > 500) {
    console.warn('High memory usage');
    bridge.restart();
  }
});
```

## Advanced Features

### Custom Learning Rules
```python
class CustomAgent(CitationIntegrityAgent):
    def self_modify_learning_rule(self, context, surprise):
        # Custom modification logic
        if context['field'] == 'AI':
            self.learning_rate *= 1.2
        # ... your logic
```

### Event Streaming
```typescript
bridge.on('citation-evaluated', (event) => {
  // Stream to analytics
  analytics.track(event);
});
```

### A/B Testing
```typescript
const poolA = new AgentPool({ strategy: 'conservative' });
const poolB = new AgentPool({ strategy: 'adaptive' });

// Compare performance
const resultsA = await poolA.evaluate(citations);
const resultsB = await poolB.evaluate(citations);
```

## Documentation

- **Architecture:** See `COMPLETE_AGENT_DOCUMENTATION.md`
- **API Reference:** TypeScript types are fully documented
- **Examples:** See `examples/` directory (if added)
- **Main Platform:** `../README.md`

## Related Files

- `../nested_learning_enhanced.py` - Standalone implementation
- `../enhanced_nest_learning.py` - Production version
- `../docs/citations_and_integration.md` - Academic theory
- `../../simulation/` - Main game theory simulation

## License

Same as main project.

## Questions?

See `COMPLETE_AGENT_DOCUMENTATION.md` for detailed system documentation.
