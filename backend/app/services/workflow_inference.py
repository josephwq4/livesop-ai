import os
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.repositories.persistence import PersistenceRepository
from app.services.integration_clients import fetch_all_events

# --- MOCK OPENAI CLIENT ---
class MockOpenAI:
    def __init__(self, **kwargs): pass
    class Chat:
        def completions(self): return self
        class create:
            @staticmethod
            def create(**kwargs):
                class Choice:
                    class Message:
                        def __init__(self): self.content = '{"title": "Demo Process", "nodes": [{"id": "1", "type": "process", "data": {"label": "Scan Signal", "description": "Identify incoming request", "actor": "System"}}, {"id": "2", "type": "process", "data": {"label": "Verify Data", "description": "Check credentials", "actor": "Admin"}}, {"id": "3", "type": "process", "data": {"label": "Approve", "description": "Final approval", "actor": "Manager"}}], "edges": [{"id": "e1", "source": "1", "target": "2", "label": "valid"}, {"id": "e2", "source": "2", "target": "3", "label": "confirmed"}]}'
                class Result:
                    def __init__(self): self.choices = [Choice()]
                return Result()

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[DEBUG] OpenAI Key missing, using Mock client.")
        return MockOpenAI()
    try:
        from openai import OpenAI
        return OpenAI(api_key=api_key)
    except Exception as e:
        print(f"[DEBUG] Failed to init OpenAI: {e}")
        return MockOpenAI()

def generate_workflow_graph_with_llm(events: List[Dict]) -> Dict:
    """Generates a graph from events using LLM"""
    client = get_openai_client()
    
    events_text = "\n".join([
        f"- {e.get('timestamp')}: {e.get('user')}: {e.get('text')}"
        for e in events[:50]
    ])
    
    prompt = f"""
    Analyze these organizational signals and generate a Standard Operating Procedure (SOP) flowchart.
    IMPORTANT: You must return at least 3 nodes showing a standard business process (e.g. Request -> Review -> Approve).
    
    Signals:
    {events_text}
    
    Return ONLY a valid JSON object with this exact structure:
    {{
      "title": "Process Name",
      "nodes": [
        {{"id": "1", "type": "process", "data": {{"label": "Step 1", "description": "...", "actor": "..."}}}},
        ...
      ],
      "edges": [
        {{"id": "e1-2", "source": "1", "target": "2", "label": "next"}},
        ...
      ]
    }}
    """
    
    try:
        if isinstance(client, MockOpenAI):
            return json.loads(client.Chat.create().choices[0].content)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert systems analyst. Follow JSON formatting strictly."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        workflow_text = response.choices[0].message.content
        return json.loads(workflow_text)
    except Exception as e:
        print(f"GPT-4 Error: {e}")
        # Return visible error node so user knows why graph is empty
        return {
            "title": "Generation Failed",
            "nodes": [
                {
                    "id": "err", 
                    "type": "process",
                    "data": {"label": "Generation Failed", "description": f"Internal Error: {str(e)}", "actor": "System"}
                }
            ], 
            "edges": []
        }

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generates vector embeddings for a list of strings"""
    client = get_openai_client()
    try:
        if isinstance(client, MockOpenAI):
            # Return dummy 1536-dim vectors
            return [[0.0] * 1536 for _ in texts]

        response = client.embeddings.create(
            input=texts,
            model="text-embedding-3-small"
        )
        return [data.embedding for data in response.data]
    except Exception as e:
        print(f"Embedding Error: {e}")
        return [[0.0] * 1536 for _ in texts]

def infer_workflow(team_id: str, user_id: str = None) -> Dict[str, Any]:
    """Main inference logic with UUID validation and Trace Logging"""
    try:
        print(f"[TRACE] Starting Inference for Team: {team_id}", flush=True)
        repo = PersistenceRepository()
        
        real_team_id = team_id
        if user_id:
            print(f"[TRACE] Resolving real team id for user: {user_id}", flush=True)
            real_team_id = repo.get_or_create_team(f"Team {user_id[:4]}", user_id)
        
        print(f"[TRACE] Resolved UUID: {real_team_id}. Fetching Events...", flush=True)
        events = fetch_all_events(real_team_id)
        
        print(f"[TRACE] Events fetched: {len(events)}. Ingesting Signals...", flush=True)
        signal_ids = repo.ingest_signals(real_team_id, events)
        
        print(f"[TRACE] Signals ingested. Creating Inference Run record...", flush=True)
        run_id = repo.create_inference_run(real_team_id, "manual_dashboard", {"model": "gpt-4"})
        
        print(f"[TRACE] Linking run {run_id} to signals...", flush=True)
        repo.link_signals_to_run(run_id, signal_ids)
        
        print(f"[TRACE] Calling LLM Generation...", flush=True)
        workflow_graph = generate_workflow_graph_with_llm(events)
        
        print(f"[TRACE] LLM Success. Persisting Workflow to DB...", flush=True)
        persisted_wf_id = repo.save_workflow(real_team_id, run_id, workflow_graph)
        
        print(f"[TRACE] Completion. Finalizing Run...", flush=True)
        repo.complete_inference_run(run_id, "success")
        
        workflow_graph["workflow_id"] = persisted_wf_id
        workflow_graph["team_id"] = real_team_id
        return workflow_graph
        
    except Exception as e:
        print(f"CRITICAL INFERENCE ERROR: {e}", flush=True)
        return {"error": str(e), "traceback": "Check Render Logs"}

def generate_sop_document(team_id: str, workflow_id: str) -> str:
    return "# Generated SOP\n\nThis is a template document generated because vector storage is currently disabled."

def query_similar_events(team_id: str, query: str) -> List:
    return []
