/**
 * Citation Integrity Agent Integration
 * =====================================
 * TypeScript integration layer for the Nested Learning Citation Agent
 * Designed to work with your existing platform at src/platform/
 */

import { EventEmitter } from 'events';
import { spawn, ChildProcess } from 'child_process';
import axios from 'axios';
import { Redis } from 'ioredis';
import { Pool } from 'pg';
import pino from 'pino';

// Import your existing platform modules
import { MultiLevelState } from './multiLevelState';
import { ProvenanceDecorator } from './decorators/provenance';
import { CitationExtractor } from './parsers/citationExtractor';
import { ClaimValidator } from './validators/claimValidator';
import { LSSMonitor } from './utils/lssMonitor';
import { CitationCache } from './cache/citationCache';

// ============================================================================
// TYPES AND INTERFACES
// ============================================================================

/**
 * Citation behavior types matching Python CitationBehavior enum
 */
export enum CitationBehavior {
  PROPER_CITATION = 'proper_citation',
  PARAPHRASE_WITH_CITE = 'paraphrase_cite',
  SELECTIVE_CITATION = 'selective_citation',
  CITATION_STACKING = 'citation_stacking',
  SELF_CITATION = 'self_citation',
  LAZY_CITATION = 'lazy_citation',
  FABRICATED_CITATION = 'fabricated',
  PLAGIARISM = 'plagiarism',
  META_LEARNING = 'meta_learning'
}

/**
 * Agent state interface
 */
export interface AgentState {
  agentId: string;
  reputation: number;
  totalCitations: number;
  detectedViolations: number;
  currentBehavior: CitationBehavior;
  memoryLevels: {
    immediate: number;
    shortTerm: number;
    longTerm: number;
    persistent: number;
  };
  lastLSS: number;
  explorationRate: number;
}

/**
 * Citation analysis result
 */
export interface CitationAnalysis {
  citations: Array<{
    citation: any;
    integrityScore: number;
    behavior: CitationBehavior;
    riskLevel: number;
    recommendations: string[];
  }>;
  overallIntegrity: number;
  agentReputation: number;
  memoryState: any;
}

/**
 * Document processing request
 */
export interface DocumentRequest {
  text: string;
  source: string;
  context: {
    field?: string;
    journal?: string;
    authorReputation?: number;
    fieldSimilarity?: number;
    journalImpact?: number;
  };
}

// ============================================================================
// CITATION INTEGRITY AGENT WRAPPER
// ============================================================================

export class CitationIntegrityAgent extends EventEmitter {
  private agentId: string;
  private pythonProcess: ChildProcess | null = null;
  private state: AgentState;
  private logger: pino.Logger;
  private db: Pool;
  private redis: Redis;
  private cache: CitationCache;
  private multiLevelState: MultiLevelState;
  private lssMonitor: LSSMonitor;
  
  constructor(
    agentId: string,
    dbConfig: any,
    redisConfig: any,
    logger?: pino.Logger
  ) {
    super();
    this.agentId = agentId;
    this.logger = logger || pino();
    
    // Initialize database connection
    this.db = new Pool(dbConfig);
    
    // Initialize Redis
    this.redis = new Redis(redisConfig);
    
    // Initialize cache
    this.cache = new CitationCache(this.redis);
    
    // Initialize multi-level state
    this.multiLevelState = new MultiLevelState({
      levels: 4,
      updateIntervals: [1, 10, 100, 1000],
      capacities: [100, 500, 2000, 5000],
      decayRates: [0.9, 0.95, 0.98, 0.99]
    });
    
    // Initialize LSS monitor
    this.lssMonitor = new LSSMonitor();
    
    // Initialize agent state
    this.state = {
      agentId,
      reputation: 0.5,
      totalCitations: 0,
      detectedViolations: 0,
      currentBehavior: CitationBehavior.PROPER_CITATION,
      memoryLevels: {
        immediate: 0,
        shortTerm: 0,
        longTerm: 0,
        persistent: 0
      },
      lastLSS: 0,
      explorationRate: 0.2
    };
    
    this.logger.info({ agentId }, 'Citation Integrity Agent initialized');
  }
  
  /**
   * Start the Python agent process
   */
  async start(): Promise<void> {
    return new Promise((resolve, reject) => {
      const pythonScript = `${__dirname}/../../python/citation_integrity_agent.py`;
      
      this.pythonProcess = spawn('python3', [
        pythonScript,
        '--agent-id', this.agentId,
        '--mode', 'service'
      ]);
      
      this.pythonProcess.stdout?.on('data', (data) => {
        const message = data.toString();
        this.handlePythonMessage(message);
      });
      
      this.pythonProcess.stderr?.on('data', (data) => {
        this.logger.error({ data: data.toString() }, 'Python agent error');
      });
      
      this.pythonProcess.on('close', (code) => {
        this.logger.info({ code }, 'Python agent process closed');
        this.pythonProcess = null;
      });
      
      // Wait for ready signal
      setTimeout(() => resolve(), 1000);
    });
  }
  
  /**
   * Stop the Python agent process
   */
  async stop(): Promise<void> {
    if (this.pythonProcess) {
      this.pythonProcess.kill();
      this.pythonProcess = null;
    }
    await this.db.end();
    this.redis.disconnect();
  }
  
  /**
   * Analyze citations in a document
   */
  @ProvenanceDecorator()
  async analyzeCitation(request: DocumentRequest): Promise<CitationAnalysis> {
    const startTime = Date.now();
    
    try {
      // Extract citations using existing platform module
      const extractor = new CitationExtractor();
      const citations = await extractor.extract(request.text);
      
      // Validate claims
      const validator = new ClaimValidator(this.db);
      const validations = await Promise.all(
        citations.map(c => validator.validate(c))
      );
      
      // Check cache
      const cacheKey = `analysis:${this.agentId}:${Buffer.from(request.text).toString('base64').slice(0, 32)}`;
      const cached = await this.cache.get(cacheKey);
      if (cached) {
        this.logger.debug({ cacheKey }, 'Cache hit for citation analysis');
        return cached;
      }
      
      // Prepare analysis request
      const analysisRequest = {
        agentId: this.agentId,
        text: request.text,
        source: request.source,
        citations,
        validations,
        context: request.context,
        state: this.state
      };
      
      // Call Python agent for deep analysis
      const analysis = await this.callPythonAgent('analyze', analysisRequest);
      
      // Update multi-level state
      await this.updateMultiLevelState(analysis);
      
      // Calculate Local Surprise Signal
      const lss = this.calculateLSS(analysis);
      this.state.lastLSS = lss;
      
      // Self-modify if high surprise
      if (Math.abs(lss) > 0.5) {
        await this.selfModify(lss);
      }
      
      // Update agent state
      this.updateState(analysis);
      
      // Cache result
      await this.cache.set(cacheKey, analysis, 3600);
      
      // Record metrics
      this.recordMetrics(analysis, Date.now() - startTime);
      
      return analysis;
      
    } catch (error) {
      this.logger.error({ error, request }, 'Citation analysis failed');
      throw error;
    }
  }
  
  /**
   * Update multi-level memory state
   */
  private async updateMultiLevelState(analysis: CitationAnalysis): Promise<void> {
    // Update each memory level based on analysis
    const memoryUpdate = {
      level: 1, // Immediate
      data: {
        citations: analysis.citations,
        integrity: analysis.overallIntegrity,
        timestamp: new Date().toISOString()
      }
    };
    
    await this.multiLevelState.update(memoryUpdate);
    
    // Consolidate if needed
    if (this.state.totalCitations % 100 === 0) {
      await this.multiLevelState.consolidate();
    }
  }
  
  /**
   * Calculate Local Surprise Signal
   */
  private calculateLSS(analysis: CitationAnalysis): number {
    const expected = this.state.reputation;
    const actual = analysis.overallIntegrity;
    
    const surprise = actual - expected;
    
    // Get historical LSS values
    const history = this.lssMonitor.getHistory();
    if (history.length > 10) {
      const std = this.standardDeviation(history);
      if (std > 0) {
        return surprise / std;
      }
    }
    
    return surprise;
  }
  
  /**
   * Self-modify agent behavior based on surprise
   */
  private async selfModify(lss: number): Promise<void> {
    this.logger.info({ lss }, 'Self-modifying agent behavior');
    
    // Adjust exploration rate
    if (lss > 0) {
      // Positive surprise - reduce exploration
      this.state.explorationRate = Math.max(0.05, this.state.explorationRate * 0.9);
    } else {
      // Negative surprise - increase exploration
      this.state.explorationRate = Math.min(0.5, this.state.explorationRate * 1.1);
    }
    
    // Update behavior weights in Python agent
    await this.callPythonAgent('self_modify', { lss, explorationRate: this.state.explorationRate });
  }
  
  /**
   * Update agent state based on analysis
   */
  private updateState(analysis: CitationAnalysis): void {
    this.state.totalCitations++;
    this.state.reputation = 0.9 * this.state.reputation + 0.1 * analysis.overallIntegrity;
    
    // Count violations
    const violations = analysis.citations.filter(c => c.integrityScore < 0.5);
    this.state.detectedViolations += violations.length;
    
    // Update memory levels
    if (analysis.memoryState) {
      this.state.memoryLevels = {
        immediate: analysis.memoryState.immediate_citations || 0,
        shortTerm: analysis.memoryState.short_term_citations || 0,
        longTerm: analysis.memoryState.long_term_citations || 0,
        persistent: analysis.memoryState.persistent_patterns || 0
      };
    }
    
    // Determine current behavior
    const behaviorCounts = new Map<CitationBehavior, number>();
    for (const citation of analysis.citations) {
      const behavior = citation.behavior as CitationBehavior;
      behaviorCounts.set(behavior, (behaviorCounts.get(behavior) || 0) + 1);
    }
    
    if (behaviorCounts.size > 0) {
      const [dominantBehavior] = [...behaviorCounts.entries()]
        .sort((a, b) => b[1] - a[1])[0];
      this.state.currentBehavior = dominantBehavior;
    }
  }
  
  /**
   * Call Python agent via HTTP or IPC
   */
  private async callPythonAgent(method: string, data: any): Promise<any> {
    // Option 1: HTTP API call
    try {
      const response = await axios.post(`http://localhost:8001/agent/${this.agentId}/${method}`, data);
      return response.data;
    } catch (error) {
      this.logger.error({ error, method, data }, 'Python agent call failed');
      
      // Fallback to default behavior
      return this.getDefaultResponse(method);
    }
  }
  
  /**
   * Handle messages from Python process
   */
  private handlePythonMessage(message: string): void {
    try {
      const data = JSON.parse(message);
      this.emit('message', data);
      
      if (data.type === 'state_update') {
        Object.assign(this.state, data.state);
      } else if (data.type === 'alert') {
        this.logger.warn({ alert: data }, 'Agent alert');
        this.emit('alert', data);
      }
    } catch (error) {
      // Non-JSON message, log it
      this.logger.debug({ message }, 'Python agent message');
    }
  }
  
  /**
   * Get default response when Python agent is unavailable
   */
  private getDefaultResponse(method: string): any {
    if (method === 'analyze') {
      return {
        citations: [],
        overallIntegrity: 0.5,
        agentReputation: this.state.reputation,
        memoryState: this.state.memoryLevels
      };
    }
    return {};
  }
  
  /**
   * Record metrics for monitoring
   */
  private recordMetrics(analysis: CitationAnalysis, duration: number): void {
    // Record to Prometheus metrics
    const metrics = {
      citations_analyzed: analysis.citations.length,
      integrity_score: analysis.overallIntegrity,
      agent_reputation: this.state.reputation,
      analysis_duration_ms: duration,
      memory_immediate: this.state.memoryLevels.immediate,
      memory_long_term: this.state.memoryLevels.longTerm,
      lss_value: this.state.lastLSS,
      exploration_rate: this.state.explorationRate
    };
    
    this.emit('metrics', metrics);
  }
  
  /**
   * Get current agent state
   */
  getState(): AgentState {
    return { ...this.state };
  }
  
  /**
   * Save agent state to database
   */
  async saveState(): Promise<void> {
    const query = `
      INSERT INTO agent_states (
        agent_id, reputation, total_citations, detected_violations,
        current_behavior, memory_state, exploration_rate, timestamp
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
      ON CONFLICT (agent_id) DO UPDATE SET
        reputation = $2,
        total_citations = $3,
        detected_violations = $4,
        current_behavior = $5,
        memory_state = $6,
        exploration_rate = $7,
        timestamp = NOW()
    `;
    
    await this.db.query(query, [
      this.agentId,
      this.state.reputation,
      this.state.totalCitations,
      this.state.detectedViolations,
      this.state.currentBehavior,
      JSON.stringify(this.state.memoryLevels),
      this.state.explorationRate
    ]);
  }
  
  /**
   * Load agent state from database
   */
  async loadState(): Promise<void> {
    const query = 'SELECT * FROM agent_states WHERE agent_id = $1';
    const result = await this.db.query(query, [this.agentId]);
    
    if (result.rows.length > 0) {
      const row = result.rows[0];
      this.state = {
        agentId: row.agent_id,
        reputation: row.reputation,
        totalCitations: row.total_citations,
        detectedViolations: row.detected_violations,
        currentBehavior: row.current_behavior,
        memoryLevels: row.memory_state,
        lastLSS: 0,
        explorationRate: row.exploration_rate
      };
    }
  }
  
  /**
   * Calculate standard deviation
   */
  private standardDeviation(values: number[]): number {
    const mean = values.reduce((a, b) => a + b, 0) / values.length;
    const squaredDiffs = values.map(v => Math.pow(v - mean, 2));
    const variance = squaredDiffs.reduce((a, b) => a + b, 0) / values.length;
    return Math.sqrt(variance);
  }
}

// ============================================================================
// AGENT ORCHESTRATOR
// ============================================================================

export class CitationAgentOrchestrator {
  private agents: Map<string, CitationIntegrityAgent> = new Map();
  private logger: pino.Logger;
  private db: Pool;
  private redis: Redis;
  
  constructor(config: any) {
    this.logger = pino(config.logging);
    this.db = new Pool(config.database);
    this.redis = new Redis(config.redis);
    
    // Initialize agents
    for (let i = 0; i < config.numAgents; i++) {
      const agentId = `agent_${i}`;
      const agent = new CitationIntegrityAgent(
        agentId,
        config.database,
        config.redis,
        this.logger.child({ agentId })
      );
      
      this.agents.set(agentId, agent);
    }
  }
  
  /**
   * Start all agents
   */
  async start(): Promise<void> {
    const startPromises = Array.from(this.agents.values()).map(agent => agent.start());
    await Promise.all(startPromises);
    this.logger.info(`Started ${this.agents.size} agents`);
  }
  
  /**
   * Stop all agents
   */
  async stop(): Promise<void> {
    const stopPromises = Array.from(this.agents.values()).map(agent => agent.stop());
    await Promise.all(stopPromises);
    await this.db.end();
    this.redis.disconnect();
    this.logger.info('All agents stopped');
  }
  
  /**
   * Process document through multiple agents
   */
  async processDocument(request: DocumentRequest): Promise<any> {
    const analyses = new Map<string, CitationAnalysis>();
    
    // Each agent analyzes independently
    const analysisPromises = Array.from(this.agents.entries()).map(async ([agentId, agent]) => {
      const analysis = await agent.analyzeCitation(request);
      analyses.set(agentId, analysis);
    });
    
    await Promise.all(analysisPromises);
    
    // Aggregate results
    const aggregated = this.aggregateAnalyses(analyses);
    
    // Store results
    await this.storeResults(request, aggregated);
    
    return aggregated;
  }
  
  /**
   * Aggregate analyses from multiple agents
   */
  private aggregateAnalyses(analyses: Map<string, CitationAnalysis>): any {
    const scores: number[] = [];
    const behaviors = new Map<CitationBehavior, number>();
    const recommendations = new Set<string>();
    
    for (const analysis of analyses.values()) {
      scores.push(analysis.overallIntegrity);
      
      for (const citation of analysis.citations) {
        behaviors.set(
          citation.behavior as CitationBehavior,
          (behaviors.get(citation.behavior as CitationBehavior) || 0) + 1
        );
        
        citation.recommendations.forEach(r => recommendations.add(r));
      }
    }
    
    const meanIntegrity = scores.reduce((a, b) => a + b, 0) / scores.length;
    const consensus = this.calculateConsensus(scores);
    
    return {
      meanIntegrity,
      consensus,
      behaviorDistribution: Object.fromEntries(behaviors),
      recommendations: Array.from(recommendations),
      numAgents: analyses.size,
      timestamp: new Date().toISOString()
    };
  }
  
  /**
   * Calculate consensus among agents
   */
  private calculateConsensus(scores: number[]): number {
    if (scores.length < 2) return 1.0;
    
    const mean = scores.reduce((a, b) => a + b, 0) / scores.length;
    const variance = scores.reduce((sum, s) => sum + Math.pow(s - mean, 2), 0) / scores.length;
    
    // Low variance = high consensus
    return 1.0 / (1.0 + variance);
  }
  
  /**
   * Store analysis results in database
   */
  private async storeResults(request: DocumentRequest, results: any): Promise<void> {
    const query = `
      INSERT INTO citation_analyses (
        source, text_hash, mean_integrity, consensus,
        behavior_distribution, recommendations, num_agents, timestamp
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
    `;
    
    const textHash = require('crypto')
      .createHash('sha256')
      .update(request.text)
      .digest('hex');
    
    await this.db.query(query, [
      request.source,
      textHash,
      results.meanIntegrity,
      results.consensus,
      JSON.stringify(results.behaviorDistribution),
      JSON.stringify(results.recommendations),
      results.numAgents,
      results.timestamp
    ]);
  }
  
  /**
   * Get agent by ID
   */
  getAgent(agentId: string): CitationIntegrityAgent | undefined {
    return this.agents.get(agentId);
  }
  
  /**
   * Get all agent states
   */
  getAllStates(): AgentState[] {
    return Array.from(this.agents.values()).map(agent => agent.getState());
  }
}

// Export for use in your platform
export default CitationAgentOrchestrator;
