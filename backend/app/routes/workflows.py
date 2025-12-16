from fastapi import APIRouter

router = APIRouter(tags=["workflows"])

@router.get("/test")
def test_workflow_route():
    return {"status": "minimal_workflow_active"}
