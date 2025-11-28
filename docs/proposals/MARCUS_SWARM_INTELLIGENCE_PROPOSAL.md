# MARCUS Swarm Intelligence Platform

## Executive Summary

Transform MARCUS from a citation verification tool into a **unified agent coordination backbone** where all agents (Roy, Sylvia, Cynthia, Marcus, etc.) share memories, learn collectively, and coordinate through a centralized swarm intelligence layer.

**Current State:** 11 isolated agents with file-based memories in `.claude/agents/memories/`
**Proposed State:** Unified swarm with shared semantic memory, real-time coordination, and collective learning

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLAUDE CODE CLI (You)                              │
│                    "fact check X" / "research Y" / "implement Z"             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MARCUS ORCHESTRATION LAYER                           │
│                                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   GraphQL   │  │  WebSocket  │  │    MCP      │  │   Matrix    │        │
│  │     API     │  │  Real-time  │  │   Bridge    │  │   Bridge    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SWARM MEMORY LAYER                                  │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                     PostgreSQL (Long-term Memory)                      │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │   Memories  │  │  Decisions  │  │  Learnings  │  │ Embeddings  │  │  │
│  │  │   (facts,   │  │  (what we   │  │  (patterns  │  │  (semantic  │  │  │
│  │  │   context)  │  │   decided)  │  │   found)    │  │   search)   │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                       Redis (Working Memory)                           │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │   Active    │  │   Agent     │  │    Task     │  │   Context   │  │  │
│  │  │   Context   │  │   States    │  │   Queue     │  │   Window    │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   Agent Pool    │         │   Agent Pool    │         │   Agent Pool    │
│   (Research)    │         │  (Development)  │         │   (Validation)  │
│                 │         │                 │         │                 │
│  ┌───────────┐  │         │  ┌───────────┐  │         │  ┌───────────┐  │
│  │  Cynthia  │  │         │  │    Roy    │  │         │  │  Sylvia   │  │
│  │ (Research)│  │         │  │(Sim Maint)│  │         │  │ (Skeptic) │  │
│  └───────────┘  │         │  └───────────┘  │         │  └───────────┘  │
│  ┌───────────┐  │         │  ┌───────────┐  │         │  ┌───────────┐  │
│  │    Ray    │  │         │  │   Moss    │  │         │  │   Priya   │  │
│  │ (Sci-Fi)  │  │         │  │(Implement)│  │         │  │  (Quant)  │  │
│  └───────────┘  │         │  └───────────┘  │         │  └───────────┘  │
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

---

## Detailed Component Architecture

### 1. Swarm Memory Schema (PostgreSQL)

```sql
-- Core memory storage with semantic search capability
CREATE EXTENSION IF NOT EXISTS vector;  -- pgvector for embeddings

-- Agent registry
CREATE TABLE swarm_agents (
    agent_id VARCHAR(50) PRIMARY KEY,
    display_name VARCHAR(100) NOT NULL,
    specialty VARCHAR(200),
    personality TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP DEFAULT NOW(),
    total_memories INT DEFAULT 0,
    total_contributions INT DEFAULT 0
);

-- Unified memory store (all agents read/write here)
CREATE TABLE swarm_memories (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(50) REFERENCES swarm_agents(agent_id),
    memory_type VARCHAR(50) NOT NULL,  -- 'fact', 'decision', 'learning', 'task', 'conversation'
    content TEXT NOT NULL,
    context JSONB,  -- Structured metadata
    embedding vector(1536),  -- OpenAI ada-002 or similar
    importance FLOAT DEFAULT 0.5,  -- 0.0 to 1.0
    decay_rate FLOAT DEFAULT 0.01,  -- How fast memory fades
    access_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    last_accessed TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,  -- NULL = permanent

    -- For threading conversations
    parent_id INT REFERENCES swarm_memories(id),
    thread_id UUID
);

-- Semantic search index
CREATE INDEX idx_memories_embedding ON swarm_memories
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Fast lookups
CREATE INDEX idx_memories_agent ON swarm_memories(agent_id);
CREATE INDEX idx_memories_type ON swarm_memories(memory_type);
CREATE INDEX idx_memories_created ON swarm_memories(created_at DESC);
CREATE INDEX idx_memories_importance ON swarm_memories(importance DESC);

-- Agent decisions (what was decided and why)
CREATE TABLE swarm_decisions (
    id SERIAL PRIMARY KEY,
    decision_id UUID DEFAULT gen_random_uuid(),
    agents_involved VARCHAR(50)[] NOT NULL,  -- Which agents participated
    task_description TEXT NOT NULL,
    options_considered JSONB,  -- [{option: "...", pros: [...], cons: [...]}]
    final_decision TEXT NOT NULL,
    reasoning TEXT,
    confidence FLOAT,
    outcome VARCHAR(50),  -- 'success', 'failure', 'pending', 'superseded'
    outcome_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);

-- Cross-agent learnings (patterns discovered)
CREATE TABLE swarm_learnings (
    id SERIAL PRIMARY KEY,
    discovered_by VARCHAR(50) REFERENCES swarm_agents(agent_id),
    validated_by VARCHAR(50)[],  -- Other agents who confirmed
    pattern_type VARCHAR(50),  -- 'bug_pattern', 'architecture_insight', 'research_finding'
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    evidence JSONB,  -- Links to code, papers, etc.
    applicability TEXT[],  -- When to apply this learning
    confidence FLOAT DEFAULT 0.5,
    times_applied INT DEFAULT 0,
    success_rate FLOAT,
    created_at TIMESTAMP DEFAULT NOW(),
    last_applied TIMESTAMP
);

-- Task coordination (who's doing what)
CREATE TABLE swarm_tasks (
    id SERIAL PRIMARY KEY,
    task_id UUID DEFAULT gen_random_uuid(),
    requested_by VARCHAR(100),  -- User or agent
    assigned_to VARCHAR(50) REFERENCES swarm_agents(agent_id),
    task_type VARCHAR(50),
    description TEXT NOT NULL,
    context JSONB,
    status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'in_progress', 'blocked', 'completed', 'failed'
    priority INT DEFAULT 5,  -- 1-10
    dependencies UUID[],  -- Other task_ids that must complete first
    result JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Agent-to-agent messages (async coordination)
CREATE TABLE swarm_messages (
    id SERIAL PRIMARY KEY,
    from_agent VARCHAR(50) REFERENCES swarm_agents(agent_id),
    to_agent VARCHAR(50) REFERENCES swarm_agents(agent_id),  -- NULL = broadcast
    channel VARCHAR(50),  -- 'research', 'implementation', 'coordination'
    message_type VARCHAR(50),  -- 'question', 'answer', 'alert', 'update'
    content TEXT NOT NULL,
    metadata JSONB,
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 2. Redis Working Memory Schema

```
# Active context window (what agents are currently thinking about)
swarm:context:{session_id} = {
    "active_agents": ["roy", "sylvia"],
    "current_task": "Implement nuclear winter cascades",
    "relevant_memories": [...],  # IDs from PostgreSQL
    "conversation_history": [...],
    "ttl": 3600  # Expires after 1 hour of inactivity
}

# Agent states (real-time)
swarm:agent:{agent_id}:state = {
    "status": "active",  # "active", "idle", "busy", "offline"
    "current_task_id": "uuid",
    "last_heartbeat": "2025-11-28T19:30:00Z",
    "context_window": [...]  # Recent memory IDs
}

# Task queue (distributed job queue)
swarm:tasks:pending = [task_id, task_id, ...]  # Sorted set by priority
swarm:tasks:in_progress:{agent_id} = task_id

# Pub/sub channels for real-time coordination
swarm:channel:research → Cynthia, Sylvia subscribe
swarm:channel:implementation → Roy, Moss subscribe
swarm:channel:coordination → All agents subscribe
swarm:channel:alerts → All agents subscribe
```

### 3. SwarmMemory Python Class

```python
# src/platform/agents/swarm_memory.py

import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import hashlib

import asyncpg
import redis.asyncio as redis
import numpy as np

# For embeddings - use local model or API
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
    EMBEDDING_DIM = 384
    USE_LOCAL_EMBEDDINGS = True
except ImportError:
    USE_LOCAL_EMBEDDINGS = False
    EMBEDDING_DIM = 1536  # OpenAI ada-002


class MemoryType(Enum):
    FACT = "fact"              # Verified information
    DECISION = "decision"      # What we decided
    LEARNING = "learning"      # Pattern discovered
    TASK = "task"              # Work item
    CONVERSATION = "conversation"  # Dialog history
    OBSERVATION = "observation"    # Something noticed


@dataclass
class Memory:
    """A single memory in the swarm."""
    id: Optional[int]
    agent_id: str
    memory_type: MemoryType
    content: str
    context: Dict[str, Any]
    importance: float = 0.5
    created_at: Optional[datetime] = None
    embedding: Optional[List[float]] = None


@dataclass
class RecalledMemory(Memory):
    """Memory with relevance score from semantic search."""
    relevance: float = 0.0
    access_count: int = 0


class SwarmMemory:
    """
    Unified memory system for all agents in the swarm.

    Provides:
    - Semantic search across all agent memories
    - Memory importance decay over time
    - Cross-agent knowledge sharing
    - Real-time coordination via Redis
    - Long-term storage in PostgreSQL

    Usage:
        swarm = SwarmMemory(postgres_dsn, redis_url)
        await swarm.connect()

        # Any agent can remember
        await swarm.remember(
            agent_id="roy",
            memory_type=MemoryType.LEARNING,
            content="Assertion utilities prevent NaN bugs better than fallbacks",
            context={"file": "src/simulation/utils/assertions.ts"}
        )

        # Any agent can recall (semantic search)
        memories = await swarm.recall(
            query="How to handle NaN in simulation?",
            limit=5
        )

        # Recall only from specific agents
        memories = await swarm.recall(
            query="Climate research papers",
            agent_filter=["cynthia", "sylvia"],
            memory_type=MemoryType.FACT
        )
    """

    def __init__(
        self,
        postgres_dsn: str,
        redis_url: str,
        embedding_api_key: Optional[str] = None
    ):
        self.postgres_dsn = postgres_dsn
        self.redis_url = redis_url
        self.embedding_api_key = embedding_api_key
        self.pg_pool: Optional[asyncpg.Pool] = None
        self.redis_client: Optional[redis.Redis] = None

    async def connect(self):
        """Initialize connections to PostgreSQL and Redis."""
        self.pg_pool = await asyncpg.create_pool(
            self.postgres_dsn,
            min_size=2,
            max_size=10
        )
        self.redis_client = await redis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        print("✅ SwarmMemory connected to PostgreSQL and Redis")

    async def close(self):
        """Close all connections."""
        if self.pg_pool:
            await self.pg_pool.close()
        if self.redis_client:
            await self.redis_client.close()

    # =========================================================================
    # MEMORY OPERATIONS
    # =========================================================================

    async def remember(
        self,
        agent_id: str,
        memory_type: MemoryType,
        content: str,
        context: Optional[Dict[str, Any]] = None,
        importance: float = 0.5,
        expires_in: Optional[timedelta] = None,
        parent_id: Optional[int] = None,
        thread_id: Optional[str] = None
    ) -> int:
        """
        Store a memory in the swarm.

        All agents can see this memory via recall().

        Args:
            agent_id: Which agent is remembering
            memory_type: Category of memory
            content: The actual memory content
            context: Structured metadata (file paths, URLs, etc.)
            importance: 0.0 to 1.0, affects recall priority
            expires_in: Auto-delete after this duration
            parent_id: For threading conversations
            thread_id: Group related memories

        Returns:
            Memory ID
        """
        # Generate embedding for semantic search
        embedding = await self._generate_embedding(content)

        expires_at = None
        if expires_in:
            expires_at = datetime.utcnow() + expires_in

        async with self.pg_pool.acquire() as conn:
            memory_id = await conn.fetchval("""
                INSERT INTO swarm_memories
                (agent_id, memory_type, content, context, embedding, importance, expires_at, parent_id, thread_id)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING id
            """,
                agent_id,
                memory_type.value,
                content,
                json.dumps(context or {}),
                embedding,
                importance,
                expires_at,
                parent_id,
                thread_id
            )

            # Update agent stats
            await conn.execute("""
                UPDATE swarm_agents
                SET total_memories = total_memories + 1, last_active = NOW()
                WHERE agent_id = $1
            """, agent_id)

        # Also cache in Redis for fast recent access
        await self._cache_recent_memory(memory_id, agent_id, content)

        return memory_id

    async def recall(
        self,
        query: str,
        limit: int = 10,
        agent_filter: Optional[List[str]] = None,
        memory_type: Optional[MemoryType] = None,
        min_importance: float = 0.0,
        include_expired: bool = False,
        time_window: Optional[timedelta] = None
    ) -> List[RecalledMemory]:
        """
        Semantically search memories across the entire swarm.

        Args:
            query: Natural language search query
            limit: Max memories to return
            agent_filter: Only search these agents' memories
            memory_type: Only search this type
            min_importance: Filter by importance threshold
            include_expired: Include expired memories
            time_window: Only search memories from this time period

        Returns:
            List of memories sorted by relevance
        """
        query_embedding = await self._generate_embedding(query)

        # Build dynamic WHERE clause
        conditions = ["1=1"]
        params = [query_embedding, limit]
        param_idx = 3

        if agent_filter:
            conditions.append(f"agent_id = ANY(${param_idx})")
            params.append(agent_filter)
            param_idx += 1

        if memory_type:
            conditions.append(f"memory_type = ${param_idx}")
            params.append(memory_type.value)
            param_idx += 1

        if min_importance > 0:
            conditions.append(f"importance >= ${param_idx}")
            params.append(min_importance)
            param_idx += 1

        if not include_expired:
            conditions.append("(expires_at IS NULL OR expires_at > NOW())")

        if time_window:
            conditions.append(f"created_at >= NOW() - INTERVAL '${param_idx} seconds'")
            params.append(int(time_window.total_seconds()))
            param_idx += 1

        where_clause = " AND ".join(conditions)

        async with self.pg_pool.acquire() as conn:
            rows = await conn.fetch(f"""
                SELECT
                    id, agent_id, memory_type, content, context,
                    importance, created_at, access_count,
                    1 - (embedding <=> $1) as relevance
                FROM swarm_memories
                WHERE {where_clause}
                ORDER BY relevance DESC
                LIMIT $2
            """, *params)

            # Update access counts
            memory_ids = [row['id'] for row in rows]
            if memory_ids:
                await conn.execute("""
                    UPDATE swarm_memories
                    SET access_count = access_count + 1, last_accessed = NOW()
                    WHERE id = ANY($1)
                """, memory_ids)

        return [
            RecalledMemory(
                id=row['id'],
                agent_id=row['agent_id'],
                memory_type=MemoryType(row['memory_type']),
                content=row['content'],
                context=json.loads(row['context']),
                importance=row['importance'],
                created_at=row['created_at'],
                relevance=row['relevance'],
                access_count=row['access_count']
            )
            for row in rows
        ]

    async def forget(
        self,
        memory_id: Optional[int] = None,
        agent_id: Optional[str] = None,
        older_than: Optional[timedelta] = None,
        importance_below: Optional[float] = None
    ) -> int:
        """
        Remove memories from the swarm.

        Can target specific memories or bulk delete based on criteria.

        Returns:
            Number of memories deleted
        """
        conditions = []
        params = []
        param_idx = 1

        if memory_id:
            conditions.append(f"id = ${param_idx}")
            params.append(memory_id)
            param_idx += 1

        if agent_id:
            conditions.append(f"agent_id = ${param_idx}")
            params.append(agent_id)
            param_idx += 1

        if older_than:
            conditions.append(f"created_at < NOW() - INTERVAL '{int(older_than.total_seconds())} seconds'")

        if importance_below is not None:
            conditions.append(f"importance < ${param_idx}")
            params.append(importance_below)
            param_idx += 1

        if not conditions:
            raise ValueError("Must specify at least one deletion criteria")

        where_clause = " AND ".join(conditions)

        async with self.pg_pool.acquire() as conn:
            result = await conn.execute(f"""
                DELETE FROM swarm_memories WHERE {where_clause}
            """, *params)

        count = int(result.split()[-1])
        return count

    # =========================================================================
    # CROSS-AGENT COORDINATION
    # =========================================================================

    async def broadcast(
        self,
        from_agent: str,
        channel: str,
        message: str,
        message_type: str = "update",
        metadata: Optional[Dict] = None
    ):
        """
        Broadcast a message to all agents on a channel.

        Channels: 'research', 'implementation', 'coordination', 'alerts'
        """
        payload = json.dumps({
            "from": from_agent,
            "type": message_type,
            "content": message,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        })

        # Pub/sub for real-time
        await self.redis_client.publish(f"swarm:channel:{channel}", payload)

        # Also persist in PostgreSQL
        async with self.pg_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO swarm_messages
                (from_agent, channel, message_type, content, metadata)
                VALUES ($1, $2, $3, $4, $5)
            """, from_agent, channel, message_type, message, json.dumps(metadata or {}))

    async def send_to_agent(
        self,
        from_agent: str,
        to_agent: str,
        message: str,
        message_type: str = "question"
    ) -> int:
        """Send a direct message to another agent."""
        async with self.pg_pool.acquire() as conn:
            msg_id = await conn.fetchval("""
                INSERT INTO swarm_messages
                (from_agent, to_agent, message_type, content)
                VALUES ($1, $2, $3, $4)
                RETURNING id
            """, from_agent, to_agent, message_type, message)

        # Notify via Redis
        await self.redis_client.publish(
            f"swarm:agent:{to_agent}:inbox",
            json.dumps({"message_id": msg_id, "from": from_agent})
        )

        return msg_id

    async def get_unread_messages(self, agent_id: str) -> List[Dict]:
        """Get all unread messages for an agent."""
        async with self.pg_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, from_agent, message_type, content, created_at
                FROM swarm_messages
                WHERE to_agent = $1 AND read_at IS NULL
                ORDER BY created_at ASC
            """, agent_id)

            # Mark as read
            if rows:
                await conn.execute("""
                    UPDATE swarm_messages SET read_at = NOW()
                    WHERE id = ANY($1)
                """, [row['id'] for row in rows])

        return [dict(row) for row in rows]

    # =========================================================================
    # TASK COORDINATION
    # =========================================================================

    async def create_task(
        self,
        description: str,
        requested_by: str,
        task_type: str,
        priority: int = 5,
        context: Optional[Dict] = None,
        dependencies: Optional[List[str]] = None
    ) -> str:
        """Create a task that can be claimed by any agent."""
        import uuid
        task_id = str(uuid.uuid4())

        async with self.pg_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO swarm_tasks
                (task_id, requested_by, task_type, description, context, priority, dependencies)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, task_id, requested_by, task_type, description,
                json.dumps(context or {}), priority, dependencies or [])

        # Add to Redis queue
        await self.redis_client.zadd(
            "swarm:tasks:pending",
            {task_id: priority}
        )

        return task_id

    async def claim_task(self, agent_id: str, task_id: Optional[str] = None) -> Optional[Dict]:
        """
        Claim a task for an agent.

        If task_id is None, claims the highest priority pending task.
        """
        if task_id is None:
            # Get highest priority task
            result = await self.redis_client.zpopmax("swarm:tasks:pending")
            if not result:
                return None
            task_id = result[0][0]
        else:
            # Remove specific task from queue
            await self.redis_client.zrem("swarm:tasks:pending", task_id)

        # Mark as in progress
        await self.redis_client.set(f"swarm:tasks:in_progress:{agent_id}", task_id)

        async with self.pg_pool.acquire() as conn:
            row = await conn.fetchrow("""
                UPDATE swarm_tasks
                SET assigned_to = $1, status = 'in_progress', started_at = NOW()
                WHERE task_id = $2
                RETURNING *
            """, agent_id, task_id)

        return dict(row) if row else None

    async def complete_task(
        self,
        agent_id: str,
        task_id: str,
        result: Dict,
        success: bool = True
    ):
        """Mark a task as completed."""
        status = "completed" if success else "failed"

        async with self.pg_pool.acquire() as conn:
            await conn.execute("""
                UPDATE swarm_tasks
                SET status = $1, result = $2, completed_at = NOW()
                WHERE task_id = $3
            """, status, json.dumps(result), task_id)

            # Update agent stats
            await conn.execute("""
                UPDATE swarm_agents
                SET total_contributions = total_contributions + 1
                WHERE agent_id = $1
            """, agent_id)

        # Clear from in-progress
        await self.redis_client.delete(f"swarm:tasks:in_progress:{agent_id}")

    # =========================================================================
    # LEARNINGS & PATTERNS
    # =========================================================================

    async def share_learning(
        self,
        agent_id: str,
        title: str,
        description: str,
        pattern_type: str,
        evidence: Optional[Dict] = None,
        applicability: Optional[List[str]] = None
    ) -> int:
        """
        Share a discovered pattern with the swarm.

        Other agents can validate and build upon this learning.
        """
        async with self.pg_pool.acquire() as conn:
            learning_id = await conn.fetchval("""
                INSERT INTO swarm_learnings
                (discovered_by, pattern_type, title, description, evidence, applicability)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            """, agent_id, pattern_type, title, description,
                json.dumps(evidence or {}), applicability or [])

        # Broadcast to swarm
        await self.broadcast(
            from_agent=agent_id,
            channel="coordination",
            message=f"New learning shared: {title}",
            message_type="learning",
            metadata={"learning_id": learning_id}
        )

        return learning_id

    async def validate_learning(self, agent_id: str, learning_id: int) -> bool:
        """Validate another agent's learning."""
        async with self.pg_pool.acquire() as conn:
            await conn.execute("""
                UPDATE swarm_learnings
                SET validated_by = array_append(validated_by, $1),
                    confidence = confidence + 0.1
                WHERE id = $2
            """, agent_id, learning_id)

        return True

    async def get_relevant_learnings(
        self,
        context: str,
        limit: int = 5
    ) -> List[Dict]:
        """Get learnings relevant to current context."""
        # Use semantic search on learning descriptions
        embedding = await self._generate_embedding(context)

        # For now, simple keyword matching (would use embedding in production)
        async with self.pg_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM swarm_learnings
                ORDER BY confidence DESC, times_applied DESC
                LIMIT $1
            """, limit)

        return [dict(row) for row in rows]

    # =========================================================================
    # HELPERS
    # =========================================================================

    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for semantic search."""
        if USE_LOCAL_EMBEDDINGS:
            # Use local sentence-transformers model
            embedding = EMBEDDING_MODEL.encode(text)
            return embedding.tolist()
        else:
            # Use OpenAI or Anthropic API
            # (Implementation depends on which API you're using)
            import anthropic
            client = anthropic.Anthropic()
            # Note: Anthropic doesn't have embeddings API yet
            # Would use OpenAI or local model
            raise NotImplementedError("Configure embedding API")

    async def _cache_recent_memory(
        self,
        memory_id: int,
        agent_id: str,
        content: str
    ):
        """Cache recent memories in Redis for fast access."""
        cache_key = f"swarm:recent:{agent_id}"
        await self.redis_client.lpush(cache_key, json.dumps({
            "id": memory_id,
            "content": content[:500],  # Truncate for cache
            "timestamp": datetime.utcnow().isoformat()
        }))
        # Keep only last 100 memories per agent
        await self.redis_client.ltrim(cache_key, 0, 99)

    async def get_agent_stats(self, agent_id: str) -> Dict:
        """Get statistics for an agent."""
        async with self.pg_pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM swarm_agents WHERE agent_id = $1
            """, agent_id)

        return dict(row) if row else {}


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

_swarm_instance: Optional[SwarmMemory] = None

async def get_swarm() -> SwarmMemory:
    """Get global swarm instance."""
    global _swarm_instance
    if _swarm_instance is None:
        import os
        _swarm_instance = SwarmMemory(
            postgres_dsn=os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/marcus_platform'),
            redis_url=os.environ.get('REDIS_URL', 'redis://localhost:6380/0')
        )
        await _swarm_instance.connect()
    return _swarm_instance


async def remember(agent_id: str, content: str, **kwargs):
    """Shorthand for swarm.remember()"""
    swarm = await get_swarm()
    return await swarm.remember(agent_id=agent_id, content=content, **kwargs)


async def recall(query: str, **kwargs) -> List[RecalledMemory]:
    """Shorthand for swarm.recall()"""
    swarm = await get_swarm()
    return await swarm.recall(query=query, **kwargs)
```

### 4. TypeScript Integration (MCP Bridge)

```typescript
// src/platform/services/swarmBridge.ts

import { Pool } from 'pg';
import Redis from 'ioredis';

/**
 * TypeScript bridge to the SwarmMemory system.
 *
 * Allows Claude Code agents (via MCP) to interact with the swarm.
 */
export class SwarmBridge {
  private pg: Pool;
  private redis: Redis;

  constructor(pgPool: Pool, redisClient: Redis) {
    this.pg = pgPool;
    this.redis = redisClient;
  }

  /**
   * Store a memory from a Claude Code agent.
   */
  async remember(
    agentId: string,
    memoryType: string,
    content: string,
    context?: Record<string, any>,
    importance: number = 0.5
  ): Promise<number> {
    // Generate embedding (would use embedding API in production)
    const embedding = await this.generateEmbedding(content);

    const result = await this.pg.query(`
      INSERT INTO swarm_memories
      (agent_id, memory_type, content, context, embedding, importance)
      VALUES ($1, $2, $3, $4, $5, $6)
      RETURNING id
    `, [agentId, memoryType, content, JSON.stringify(context || {}), embedding, importance]);

    return result.rows[0].id;
  }

  /**
   * Semantic search across all agent memories.
   */
  async recall(
    query: string,
    options: {
      limit?: number;
      agentFilter?: string[];
      memoryType?: string;
      minImportance?: number;
    } = {}
  ): Promise<Array<{
    id: number;
    agentId: string;
    content: string;
    relevance: number;
  }>> {
    const { limit = 10, agentFilter, memoryType, minImportance = 0 } = options;
    const embedding = await this.generateEmbedding(query);

    let query_sql = `
      SELECT
        id, agent_id as "agentId", content,
        1 - (embedding <=> $1) as relevance
      FROM swarm_memories
      WHERE importance >= $2
    `;
    const params: any[] = [embedding, minImportance];
    let paramIdx = 3;

    if (agentFilter?.length) {
      query_sql += ` AND agent_id = ANY($${paramIdx})`;
      params.push(agentFilter);
      paramIdx++;
    }

    if (memoryType) {
      query_sql += ` AND memory_type = $${paramIdx}`;
      params.push(memoryType);
      paramIdx++;
    }

    query_sql += ` ORDER BY relevance DESC LIMIT $${paramIdx}`;
    params.push(limit);

    const result = await this.pg.query(query_sql, params);
    return result.rows;
  }

  /**
   * Get the current state of all agents.
   */
  async getAgentStates(): Promise<Record<string, {
    status: string;
    currentTask?: string;
    lastHeartbeat: string;
  }>> {
    const keys = await this.redis.keys('swarm:agent:*:state');
    const states: Record<string, any> = {};

    for (const key of keys) {
      const agentId = key.split(':')[2];
      const state = await this.redis.get(key);
      if (state) {
        states[agentId] = JSON.parse(state);
      }
    }

    return states;
  }

  /**
   * Subscribe to a swarm channel.
   */
  async subscribeToChannel(
    channel: string,
    callback: (message: any) => void
  ): Promise<void> {
    const subscriber = this.redis.duplicate();
    await subscriber.subscribe(`swarm:channel:${channel}`);

    subscriber.on('message', (ch, message) => {
      callback(JSON.parse(message));
    });
  }

  private async generateEmbedding(text: string): Promise<number[]> {
    // In production, use OpenAI ada-002 or local model
    // For now, return dummy embedding
    return new Array(384).fill(0).map(() => Math.random());
  }
}

// ============================================================================
// MCP Tool Definitions
// ============================================================================

/**
 * MCP tools for Claude Code agents to interact with the swarm.
 *
 * Add these to .claude/mcp.json
 */
export const swarmMcpTools = {
  swarm_remember: {
    description: "Store a memory in the swarm that all agents can access",
    parameters: {
      agent_id: { type: "string", description: "Your agent ID (e.g., 'roy', 'sylvia')" },
      memory_type: { type: "string", enum: ["fact", "decision", "learning", "task", "observation"] },
      content: { type: "string", description: "The memory content" },
      importance: { type: "number", description: "0.0 to 1.0, how important is this?" },
      context: { type: "object", description: "Additional structured data" }
    }
  },

  swarm_recall: {
    description: "Search memories across all agents in the swarm",
    parameters: {
      query: { type: "string", description: "Natural language search query" },
      limit: { type: "number", description: "Max results (default 10)" },
      agent_filter: { type: "array", items: { type: "string" }, description: "Only search these agents" },
      memory_type: { type: "string", description: "Filter by memory type" }
    }
  },

  swarm_broadcast: {
    description: "Send a message to all agents on a channel",
    parameters: {
      from_agent: { type: "string" },
      channel: { type: "string", enum: ["research", "implementation", "coordination", "alerts"] },
      message: { type: "string" },
      message_type: { type: "string", enum: ["question", "answer", "alert", "update"] }
    }
  },

  swarm_create_task: {
    description: "Create a task that any agent can claim",
    parameters: {
      description: { type: "string" },
      task_type: { type: "string" },
      priority: { type: "number", description: "1-10, higher = more urgent" },
      context: { type: "object" }
    }
  },

  swarm_share_learning: {
    description: "Share a discovered pattern or insight with the swarm",
    parameters: {
      agent_id: { type: "string" },
      title: { type: "string" },
      description: { type: "string" },
      pattern_type: { type: "string", enum: ["bug_pattern", "architecture_insight", "research_finding", "best_practice"] },
      evidence: { type: "object" }
    }
  }
};
```

### 5. MCP Server Configuration

```json
// .claude/mcp.json (additions)
{
  "mcpServers": {
    "swarm-memory": {
      "command": "node",
      "args": ["src/platform/mcp/swarm-server.js"],
      "env": {
        "DATABASE_URL": "postgresql://postgres:postgres@localhost:5432/marcus_platform",
        "REDIS_URL": "redis://localhost:6380/0"
      }
    }
  }
}
```

```typescript
// src/platform/mcp/swarm-server.ts

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { Pool } from 'pg';
import Redis from 'ioredis';
import { SwarmBridge } from '../services/swarmBridge';

const server = new Server(
  { name: 'swarm-memory', version: '1.0.0' },
  { capabilities: { tools: {} } }
);

let swarm: SwarmBridge;

// Initialize connections
async function init() {
  const pg = new Pool({ connectionString: process.env.DATABASE_URL });
  const redis = new Redis(process.env.REDIS_URL!);
  swarm = new SwarmBridge(pg, redis);
}

// Tool: swarm_remember
server.setRequestHandler('tools/call', async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    case 'swarm_remember':
      const memoryId = await swarm.remember(
        args.agent_id,
        args.memory_type,
        args.content,
        args.context,
        args.importance
      );
      return { content: [{ type: 'text', text: `Memory stored with ID: ${memoryId}` }] };

    case 'swarm_recall':
      const memories = await swarm.recall(args.query, {
        limit: args.limit,
        agentFilter: args.agent_filter,
        memoryType: args.memory_type
      });
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(memories, null, 2)
        }]
      };

    // ... other tools
  }
});

// Start server
init().then(() => {
  const transport = new StdioServerTransport();
  server.connect(transport);
  console.error('Swarm Memory MCP server started');
});
```

---

## Data Flow Diagrams

### Memory Storage Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              USER REQUEST                                 │
│                    "Roy, remember that NaN bugs need assertions"          │
└──────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                           CLAUDE CODE (Roy)                               │
│                                                                           │
│   1. Receives request                                                     │
│   2. Calls MCP tool: swarm_remember                                       │
│      {                                                                    │
│        agent_id: "roy",                                                   │
│        memory_type: "learning",                                           │
│        content: "NaN bugs require assertion utilities, not fallbacks",   │
│        importance: 0.9,                                                   │
│        context: { file: "assertions.ts", pattern: "fail-loudly" }        │
│      }                                                                    │
└──────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         MCP SWARM SERVER                                  │
│                                                                           │
│   1. Generate embedding for content                                       │
│   2. Store in PostgreSQL swarm_memories                                   │
│   3. Cache in Redis swarm:recent:roy                                      │
│   4. Broadcast to swarm:channel:coordination                              │
└──────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
           ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
           │  PostgreSQL  │  │    Redis     │  │   Pub/Sub    │
           │              │  │              │  │              │
           │ swarm_       │  │ Cached in    │  │ Broadcast to │
           │ memories     │  │ recent list  │  │ all agents   │
           └──────────────┘  └──────────────┘  └──────────────┘
```

### Memory Recall Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              USER REQUEST                                 │
│              "Sylvia, how should we handle invalid values?"               │
└──────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         CLAUDE CODE (Sylvia)                              │
│                                                                           │
│   1. Needs context on invalid value handling                              │
│   2. Calls MCP tool: swarm_recall                                         │
│      {                                                                    │
│        query: "handling invalid values NaN undefined simulation",         │
│        limit: 5                                                           │
│      }                                                                    │
└──────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         MCP SWARM SERVER                                  │
│                                                                           │
│   1. Generate embedding for query                                         │
│   2. Semantic search across ALL agent memories                            │
│   3. Return ranked results                                                │
└──────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                           SEARCH RESULTS                                  │
│                                                                           │
│   [                                                                       │
│     {                                                                     │
│       agentId: "roy",                                                     │
│       content: "NaN bugs require assertion utilities, not fallbacks",    │
│       relevance: 0.92,                                                    │
│       context: { file: "assertions.ts" }                                  │
│     },                                                                    │
│     {                                                                     │
│       agentId: "priya",                                                   │
│       content: "Monte Carlo validation catches NaN propagation",          │
│       relevance: 0.87                                                     │
│     },                                                                    │
│     {                                                                     │
│       agentId: "cynthia",                                                 │
│       content: "Research: defensive programming patterns in simulation", │
│       relevance: 0.81                                                     │
│     }                                                                     │
│   ]                                                                       │
└──────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         SYLVIA'S RESPONSE                                 │
│                                                                           │
│   "Based on swarm knowledge from Roy and Priya, you should use           │
│    assertion utilities from assertions.ts. Roy learned this handles      │
│    NaN bugs better than fallbacks, and Priya confirmed Monte Carlo       │
│    validation catches NaN propagation issues."                            │
└──────────────────────────────────────────────────────────────────────────┘
```

### Task Coordination Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              USER REQUEST                                 │
│                "Implement nuclear winter cascades feature"                │
└──────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                        ORCHESTRATOR AGENT                                 │
│                                                                           │
│   1. Create tasks in swarm:                                               │
│      - Research: nuclear winter climate effects (Cynthia)                 │
│      - Validate: check existing research (Sylvia)                         │
│      - Implement: phase code (Roy)                                        │
│      - Test: Monte Carlo validation (Priya)                               │
│      - Review: architecture check (Architect)                             │
└──────────────────────────────────────────────────────────────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│    CYNTHIA      │         │     SYLVIA      │         │      ROY        │
│                 │         │                 │         │                 │
│ Claims research │         │ Claims validate │         │ Waits for       │
│ task            │         │ task            │         │ dependencies    │
│                 │         │                 │         │                 │
│ Stores findings │         │ Validates       │         │ ...             │
│ in swarm memory │         │ Cynthia's work  │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
          │                           │
          │   Both complete           │
          └───────────┬───────────────┘
                      ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                             ROY                                           │
│                                                                           │
│   1. Dependencies resolved                                                │
│   2. Claims implementation task                                           │
│   3. Recalls Cynthia's research from swarm                               │
│   4. Recalls Sylvia's validation notes                                    │
│   5. Implements with full context                                         │
│   6. Stores implementation details in swarm                               │
└──────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                            (continues to Priya, Architect)
```

---

## Required Resources

### Infrastructure

| Resource | Specification | Purpose | Est. Cost |
|----------|--------------|---------|-----------|
| PostgreSQL 15+ | 2 CPU, 4GB RAM, 50GB SSD | Long-term memory storage, semantic search | $20-40/mo |
| Redis 7+ | 1 CPU, 2GB RAM | Working memory, pub/sub, task queue | $10-20/mo |
| pgvector extension | Built into PostgreSQL | Vector similarity search | Included |

### Dependencies

```bash
# Python
pip install asyncpg redis sentence-transformers numpy

# TypeScript
npm install pg ioredis @modelcontextprotocol/sdk
```

### API Keys (Optional)

| Service | Purpose | When Needed |
|---------|---------|-------------|
| OpenAI API | Better embeddings (ada-002) | If local model insufficient |
| Anthropic API | Agent reasoning | Already have |

---

## Implementation Phases

### Phase 1: Database Schema (1-2 hours)
1. Create PostgreSQL migration for swarm tables
2. Install pgvector extension
3. Create indexes for semantic search
4. Seed initial agent records

### Phase 2: Python SwarmMemory Class (2-3 hours)
1. Implement core remember/recall
2. Add embedding generation (local model first)
3. Implement broadcast/messaging
4. Add task coordination

### Phase 3: TypeScript Bridge (1-2 hours)
1. Create SwarmBridge service
2. Add to existing MARCUS infrastructure
3. Connect to existing Redis pool

### Phase 4: MCP Server (2-3 hours)
1. Create MCP server for Claude Code
2. Implement all tool handlers
3. Test with manual calls

### Phase 5: Agent Integration (2-3 hours)
1. Update agent prompts to use swarm tools
2. Migrate existing memories from files
3. Test cross-agent recall

### Phase 6: Testing & Polish (1-2 hours)
1. Integration tests
2. Performance testing
3. Documentation

**Total Estimated Time: 10-15 hours**

---

## Usage Examples

### Example 1: Fact-Checking with Collective Memory

```
User: "Fact check: The Earth is 6,000 years old"

Claude Code (as Marcus):
  1. swarm_recall("age of Earth scientific consensus")
  2. Finds Cynthia's previous research on geological dating
  3. swarm_remember(agent_id="marcus", content="Verified: Earth is ~4.5 billion years old...")
  4. Returns fact-check result with sources from swarm
```

### Example 2: Implementation with Context

```
User: "Roy, add ocean acidification to the climate model"

Roy:
  1. swarm_recall("ocean acidification research climate")
  2. Finds Cynthia's research on pH levels, Sylvia's validation
  3. Implements with pre-validated parameters
  4. swarm_remember(agent_id="roy", content="Implemented ocean acidification phase...")
  5. swarm_share_learning(title="Ocean pH baseline", description="8.1 pre-industrial...")
```

### Example 3: Cross-Agent Coordination

```
User: "Research and implement tipping points"

Orchestrator:
  1. swarm_create_task(description="Research tipping point thresholds", task_type="research")
  2. swarm_create_task(description="Implement tipping point phase", task_type="implementation", dependencies=[task1])

Cynthia:
  1. Claims research task
  2. Does research, stores in swarm
  3. Completes task

Roy:
  1. Sees dependency resolved
  2. Claims implementation task
  3. swarm_recall("tipping point thresholds") → Gets Cynthia's research
  4. Implements with full context
```

---

## Benefits

1. **Collective Intelligence**: Agents build on each other's work
2. **No Repeated Work**: Research done once is available to all
3. **Persistent Context**: Knowledge survives across sessions
4. **Real-time Coordination**: Agents can communicate asynchronously
5. **Semantic Search**: Natural language queries across all memories
6. **Audit Trail**: All decisions and learnings are tracked
7. **Scalable**: Add more agents without restructuring

---

## Questions to Consider

1. **Embedding Model**: Local (sentence-transformers) vs API (OpenAI)?
2. **Memory Decay**: Should old memories fade in importance?
3. **Access Control**: Can any agent see all memories, or should there be visibility rules?
4. **Storage Limits**: How much memory per agent? Total?
5. **Conflict Resolution**: What if two agents remember contradictory facts?

---

## Next Steps

If approved:
1. Review this proposal
2. Answer design questions above
3. I'll implement Phase 1-6 incrementally
4. Each phase will be committed separately for review
