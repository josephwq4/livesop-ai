from app.services.workflow_inference import generate_embeddings
from app.repositories.persistence import PersistenceRepository
from typing import List, Dict, Optional

from datetime import datetime, timezone

class RAGService:
    def __init__(self):
        self.repo = PersistenceRepository()

    def add_documents_batch(self, team_id: str, items: List[Dict]) -> int:
        """
        Batch ingest items.
        items: [{ "content": str, "metadata": dict }, ...]
        """
        if not items: return 0
        
        texts = [i["content"] for i in items]
        # In case texts is huge, generate_embeddings might need chunking too.
        # But our loop below handles 100 rows.
        # Let's hope generate_embeddings handles list of reasonable size or we should chunk here.
        
        vectors = generate_embeddings(texts)
        
        if not vectors or len(vectors) != len(items):
             # Fallback/Error?
             return 0

        rows = []
        for idx, item in enumerate(items):
            rows.append({
                "team_id": team_id,
                "content": item["content"],
                "embedding": vectors[idx],
                "metadata": item["metadata"],
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            
        return self.repo.bulk_insert_knowledge(rows)

    def add_document(self, team_id: str, content: str, metadata: Dict = {}) -> str:
        """
        Ingest a document into the Knowledge Base.
        Generates embedding and persists to Supabase.
        """
        # MVP: No sophisticated chunking. Support up to 8k tokens per doc.
        if not content:
            raise ValueError("Content cannot be empty")

        vectors = generate_embeddings([content])
        if not vectors:
            raise Exception("Failed to generate embedding")
            
        return self.repo.add_knowledge_item(team_id, content, vectors[0], metadata)

    def search_context(self, team_id: str, query: str, limit: int = 3) -> List[Dict]:
        """
        Retrieve relevant context for a query.
        """
        vectors = generate_embeddings([query])
        if not vectors:
            return []
            
        return self.repo.search_knowledge_base(team_id, vectors[0], limit=limit)

    def list_documents(self, team_id: str) -> List[Dict]:
        """List all KB items for a team"""
        return self.repo.get_knowledge_items(team_id)

    def delete_document(self, team_id: str, doc_id: str) -> bool:
        """Remove a document"""
        return self.repo.delete_knowledge_item(doc_id, team_id)
