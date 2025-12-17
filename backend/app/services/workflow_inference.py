import os
import json
from typing import List, Dict, Any
from datetime import datetime
from app.services.integration_clients import fetch_all_events
from app.repositories.persistence import PersistenceRepository

# Force Disable ChromaDB to rule out C-extension crash on boot
# If we need it, we must mock it or implement pure python fallback
CHROMADB_AVAILABLE = False

# MOCK CLASSES (Fallback if OpenAI missing)
class MockOpenAI:
    def __init__(self, **kwargs): pass
    @property
    def chat(self): return MockChat()
    @property
    def embeddings(self): return MockEmbeddings()

class MockChat:
    @property
    def completions(self): return MockCompletions()

class MockCompletions:
    def create(self, **kwargs): raise Exception("OpenAI Disabled or Key Missing")

class MockEmbeddings:
    def create(self, **kwargs): raise Exception("OpenAI Disabled or Key Missing")

# LAZY OPENAI CLIENT
def get_openai_client():
    """Lazily import and initialize OpenAI client"""
    try:
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("[Warn] No OPENAI_API_KEY found in env.")
            return MockOpenAI()
        return OpenAI(api_key=api_key)
    except ImportError:
        print("[Error] OpenAI library not installed.")
        return MockOpenAI()
    except Exception as e:
        print(f"[Error] OpenAI Init: {e}")
        return MockOpenAI()

# --- HELPER FUNCTIONS ---

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings using OpenAI"""
    try:
        client = get_openai_client()
        if isinstance(client, MockOpenAI):
             # Return mock random embeddings
            import random
            return [[random.random() for _ in range(1536)] for _ in texts]
            
        response = client.embeddings.create(
            input=texts,
            model="text-embedding-3-small"
        )
        return [item.embedding for item in response.data]
    except Exception as e:
        print(f"OpenAI Embedding Error: {e}")
        import random
        return [[random.random() for _ in range(1536)] for _ in texts]


def generate_workflow_graph_with_llm(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Use GPT-4 to generate a workflow graph from events"""
    
    # Check client
    client = get_openai_client()
    if isinstance(client, MockOpenAI):
        # Return static mock
        return {
            "nodes": [{"id": "1", "step": "Mock Step", "owner": "System", "description": "OpenAI Key Missing"}],
            "edges": []
        }

    # Prepare prompt for GPT-4
    events_text = "\n".join([
        f"- [{event['timestamp']}] {event['actor']} ({event['source']}): {event['text']}"
        for event in events[:50]
    ])
    
    prompt = f"""Analyze events and generate workflow graph JSON (nodes, edges).
Events:
{events_text}
Return JSON strictly."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a workflow analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        workflow_text = response.choices[0].message.content.strip()
        # Parse logic same as before...
        if "```json" in workflow_text:
            workflow_text = workflow_text.split("```json")[1].split("```")[0].strip()
        elif "```" in workflow_text:
            workflow_text = workflow_text.split("```")[1].split("```")[0].strip()
            
        return json.loads(workflow_text)
    except Exception as e:
        print(f"GPT-4 Error: {e}")
        # Return visible error node so user knows why graph is empty
        return {
            "nodes": [
                {
                    "id": "error_node", 
                    "step": "Generation Failed",
                    "owner": "System",
                    "description": f"Error: {str(e)}",
                    "type": "process",
                    "data": {"label": "Generation Failed", "description": str(e)}
                }
            ], 
            "edges": []
        }


def infer_workflow(team_id: str, user_id: str = None) -> Dict[str, Any]:
    """Main inference logic with UUID validation"""
    try:
        # 1. Initialize Repo
        repo = PersistenceRepository()
        
        # 2. Resolve Real DB UUID from User
        # This prevents "invalid input syntax for type uuid" errors if team_id is 'team123'
        real_team_id = team_id
        if user_id:
            real_team_id = repo.get_or_create_team(f"Team {user_id[:4]}", user_id)
        
        print(f"[Inference] Processing for team: {real_team_id}")
            
        # 3. Fetch Events (Using REAL UUID)
        events = fetch_all_events(real_team_id)
        if not events:
            return {"message": "No events found", "workflow": None}
            
        # 4. Ingest Signals (Using REAL UUID)
        signal_ids = repo.ingest_signals(real_team_id, events)
        
        # 5. Create Run
        run_id = repo.create_inference_run(real_team_id, "manual_dashboard", {"model": "gpt-4"})
        repo.link_signals_to_run(run_id, signal_ids)
        
        # 6. LLM Generation
        workflow_graph = generate_workflow_graph_with_llm(events)
        
        # 7. Save Workflow (Commit Artifact)
        persisted_wf_id = repo.save_workflow(real_team_id, run_id, workflow_graph)
        
        # 8. Complete Run
        repo.complete_inference_run(run_id, "success")
        
        workflow_graph["workflow_id"] = persisted_wf_id
        workflow_graph["team_id"] = real_team_id
        return workflow_graph
        
    except Exception as e:
        print(f"[Inference Error]: {e}")
        raise e

def generate_sop_document(team_id: str, workflow_id: str) -> str:
    """Generate SOP"""
    # Simply use LLM to generate dummy SOP for now if no vectordb
    return "# Generated SOP\n\n(ChromaDB disabled, using template)\n\n## Procedure..."

def query_similar_events(team_id: str, query: str) -> List:
    return []
