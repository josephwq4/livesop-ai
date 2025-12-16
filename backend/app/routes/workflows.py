from fastapi import APIRouter, HTTPException, Depends, Response
from app.models.workflow import WorkflowGraph
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.dependencies.auth import get_current_user

router = APIRouter(tags=["workflows"])

class WorkflowNodeBatchUpdate(BaseModel):
    id: str
    label: Optional[str] = None
    description: Optional[str] = None
    auto_run_enabled: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

@router.get("/test_models")
def test_models():
    # Instantiate to test runtime
    node = WorkflowNodeBatchUpdate(id="1")
    return {"status": "ok", "node": node.dict()}
