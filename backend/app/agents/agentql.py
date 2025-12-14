"""
AgentQL - Domain-specific language for agent control and instruction
Provides structured, auditable agent execution commands
"""
from typing import Dict, List, Optional
import re
from enum import Enum


class AgentQLKeyword(Enum):
    QUERY = "QUERY"
    USING = "USING"
    EXECUTE = "EXECUTE"
    RETURN = "RETURN"


class AgentQL:
    """Parses and validates AgentQL queries"""
    
    def __init__(self, query: str):
        self.raw_query = query
        self.query_type: Optional[str] = None
        self.data_sources: List[str] = []
        self.agent_sequence: List[str] = []
        self.return_fields: List[str] = []
        self._parse()
    
    def _parse(self):
        """Parse AgentQL query string"""
        lines = [line.strip() for line in self.raw_query.split('\n') if line.strip()]
        
        for line in lines:
            if line.startswith("QUERY"):
                match = re.match(r"QUERY\s+(\w+)", line, re.IGNORECASE)
                if match:
                    self.query_type = match.group(1).lower()
            
            elif line.startswith("USING"):
                match = re.match(r"USING\s+(.+)", line, re.IGNORECASE)
                if match:
                    # Parse comma-separated data sources
                    sources = [s.strip() for s in match.group(1).split(',')]
                    self.data_sources = sources
            
            elif line.startswith("EXECUTE"):
                match = re.match(r"EXECUTE\s+(.+)", line, re.IGNORECASE)
                if match:
                    # Parse agent sequence (e.g., "Extraction -> Monitoring -> Forecasting")
                    sequence = match.group(1)
                    agents = [a.strip() for a in sequence.split('->')]
                    self.agent_sequence = [a.lower() for a in agents]
            
            elif line.startswith("RETURN"):
                match = re.match(r"RETURN\s+(.+)", line, re.IGNORECASE)
                if match:
                    # Parse return fields
                    fields = [f.strip() for f in match.group(1).split(',')]
                    self.return_fields = fields
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate the parsed query"""
        if not self.query_type:
            return False, "Missing QUERY clause"
        
        if not self.agent_sequence:
            return False, "Missing EXECUTE clause"
        
        valid_agents = {"extraction", "monitoring", "forecasting"}
        for agent in self.agent_sequence:
            if agent not in valid_agents:
                return False, f"Invalid agent: {agent}"
        
        return True, None
    
    def to_dict(self) -> Dict:
        """Convert parsed query to dictionary"""
        return {
            "query_type": self.query_type,
            "data_sources": self.data_sources,
            "agent_sequence": self.agent_sequence,
            "return_fields": self.return_fields
        }


def parse_agentql_query(query: str) -> AgentQL:
    """Parse an AgentQL query string"""
    agentql = AgentQL(query)
    is_valid, error = agentql.validate()
    if not is_valid:
        raise ValueError(f"Invalid AgentQL query: {error}")
    return agentql
