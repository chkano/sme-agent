"""
Agent Controller - Manages agent lifecycle, task assignment, and execution order
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.agents.agentql import AgentQL
from app.agents.extraction_agent import ExtractionAgent
from app.agents.monitoring_agent import MonitoringAgent
from app.agents.forecasting_agent import ForecastingAgent
from app.database import AgentExecution


class AgentController:
    """Controls and orchestrates agent execution"""
    
    def __init__(self, db: Session):
        self.db = db
        self.agents = {
            "extraction": ExtractionAgent(db),
            "monitoring": MonitoringAgent(db),
            "forecasting": ForecastingAgent(db),
        }
    
    async def execute_query(self, agentql_query: str, sme_id: int, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute an AgentQL query
        Returns: Results from the agent execution pipeline
        """
        # Parse AgentQL query
        try:
            query = AgentQL(agentql_query)
        except ValueError as e:
            raise ValueError(f"AgentQL parsing error: {str(e)}")
        
        # Create execution record
        execution = AgentExecution(
            agent_type="orchestration",
            sme_id=sme_id,
            agentql_query=agentql_query,
            inputs=inputs or {},
            status="running",
            started_at=datetime.utcnow()
        )
        self.db.add(execution)
        self.db.commit()
        
        try:
            results = {}
            agent_outputs = {}
            
            # Execute agents in sequence
            for agent_name in query.agent_sequence:
                if agent_name not in self.agents:
                    raise ValueError(f"Unknown agent: {agent_name}")
                
                agent = self.agents[agent_name]
                
                # Prepare agent inputs (use previous agent outputs or original inputs)
                agent_inputs = inputs or {}
                if agent_outputs:
                    agent_inputs.update(agent_outputs)
                
                # Execute agent
                agent_result = await agent.execute(sme_id=sme_id, inputs=agent_inputs)
                agent_outputs[agent_name] = agent_result
                results[f"{agent_name}_result"] = agent_result
            
            # Filter results based on RETURN clause
            filtered_results = {}
            if query.return_fields:
                for field in query.return_fields:
                    # Map return fields to agent outputs
                    if field in results:
                        filtered_results[field] = results[field]
                    else:
                        # Try to find in nested results
                        for key, value in results.items():
                            if isinstance(value, dict) and field in value:
                                filtered_results[field] = value[field]
            else:
                filtered_results = results
            
            # Update execution record
            execution.status = "completed"
            execution.outputs = filtered_results
            execution.completed_at = datetime.utcnow()
            self.db.commit()
            
            return filtered_results
        
        except Exception as e:
            execution.status = "failed"
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            self.db.commit()
            raise
    
    async def execute_agent(self, agent_name: str, sme_id: int, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a single agent directly"""
        if agent_name not in self.agents:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        agent = self.agents[agent_name]
        return await agent.execute(sme_id=sme_id, inputs=inputs or {})
