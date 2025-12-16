from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from app.services.rag_service import RAGService
from app.dependencies.auth import get_current_user
from typing import Optional
import io

router = APIRouter(tags=["knowledge"])

@router.post("/{team_id}/knowledge")
async def upload_knowledge(
    team_id: str,
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    source_type: str = Form("manual"),
    current_user: dict = Depends(get_current_user)
):
    try:
        service = RAGService()
        # Resolve Team ID (Security)
        user_id = current_user.get("sub")
        # Ensure team matches user (using get_or_create_team logic from repo)
        real_team_id = service.repo.get_or_create_team(f"Team {user_id[:4]}", user_id)
        
        content = ""
        metadata = {"source": source_type, "uploaded_by": user_id}

        if text:
            content = text
            metadata["filename"] = "Manual Text"
        elif file:
            metadata["filename"] = file.filename
            content_type = file.content_type
            file_bytes = await file.read()
            
            # Basic text decoding support
            try:
                content = file_bytes.decode('utf-8')
            except UnicodeDecodeError:
                raise HTTPException(status_code=400, detail="Only text-based files supported currently")
        
        if not content.strip():
            raise HTTPException(status_code=400, detail="No content found")

        doc_id = service.add_document(real_team_id, content, metadata)
        return {"success": True, "id": doc_id}

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{team_id}/knowledge")
def list_knowledge(team_id: str, current_user: dict = Depends(get_current_user)):
    service = RAGService()
    user_id = current_user.get("sub")
    real_team_id = service.repo.get_or_create_team(f"Team {user_id[:4]}", user_id)
    return {"success": True, "documents": service.list_documents(real_team_id)}

@router.delete("/{team_id}/knowledge/{doc_id}")
def delete_knowledge(team_id: str, doc_id: str, current_user: dict = Depends(get_current_user)):
    service = RAGService()
    user_id = current_user.get("sub")
    real_team_id = service.repo.get_or_create_team(f"Team {user_id[:4]}", user_id)
    
    deleted = service.delete_document(real_team_id, doc_id)
    return {"success": deleted}
