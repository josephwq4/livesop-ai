from fastapi import APIRouter

router = APIRouter(tags=["automations"])

@router.get("/test")
def test_auto():
    return {"status": "ok", "message": "Automations Router (Stubbed)"}
