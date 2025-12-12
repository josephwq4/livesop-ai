from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class WorkflowNode(BaseModel):
    id: str
    step: str
    owner: str
    description: Optional[str] = None
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class WorkflowEdge(BaseModel):
    source: str
    target: str
    label: Optional[str] = None


class WorkflowGraph(BaseModel):
    team_id: str
    workflow_id: str
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    created_at: datetime
    updated_at: datetime


class Event(BaseModel):
    id: str
    text: str
    timestamp: str
    actor: str
    source: str  # slack, jira, gmail, csv
    team_id: str
    embedding: Optional[List[float]] = None
    metadata: Optional[Dict[str, Any]] = None


class AutomationRequest(BaseModel):
    team_id: str
    workflow_id: str
    parameters: Optional[Dict[str, Any]] = None


class IntegrationConfig(BaseModel):
    team_id: str
    integration_type: str  # slack, jira, gmail
    credentials: Dict[str, str]
    enabled: bool = True
