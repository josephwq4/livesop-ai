from fastapi import APIRouter

router = APIRouter(tags=["integrations"])

@router.get("/test")
def test_int():
    return {"status": "ok", "message": "Integrations Router (Stubbed)"}
