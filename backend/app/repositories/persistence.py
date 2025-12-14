from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from uuid import UUID
from app.core.database import get_supabase_client

class PersistenceRepository:
    def __init__(self):
        self.db = get_supabase_client()
        if not self.db:
            raise Exception("Database connection not initialized. Check SUPABASE_URL and SUPABASE_SERVICE_KEY.")

    # --- TEAMS ---
    def get_or_create_team(self, team_name: str, owner_id: str) -> str:
        """Ensures a team exists and returns its UUID"""
        # Check existing
        res = self.db.table("teams").select("id").eq("owner_id", owner_id).execute()
        if res.data:
            return res.data[0]["id"]
        
        # Create new
        data = {
            "name": team_name,
            "owner_id": owner_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        res = self.db.table("teams").insert(data).execute()
        return res.data[0]["id"]

    # --- RAW SIGNALS ---
    def ingest_signals(self, team_id: str, signals: List[Dict[str, Any]]) -> List[str]:
        """
        Batch insert raw signals.
        Returns list of inserted Signal IDs.
        """
        if not signals:
            return []

        prepared_rows = []
        for s in signals:
            prepared_rows.append({
                "team_id": team_id,
                "source": s.get("source", "manual"),
                "external_id": s.get("id"), # Slack ts or Jira id
                "actor": s.get("actor", "unknown"),
                "content": s.get("text", ""),
                "metadata": s.get("metadata", {}),
                "embedding": s.get("embedding"), # Support for Vector Search
                "occurred_at": s.get("timestamp") or datetime.now(timezone.utc).isoformat()
            })

        # Upsert to handle duplicates safely (on conflict do nothing usually, but Supabase insert doesn't support 'ignore' easily without RPC)
        # We used UNIQUE constraint in SQL.
        # upsert=True will update them. Ideally we simply want to ignore.
        try:
            res = self.db.table("raw_signals").upsert(prepared_rows, on_conflict="team_id,source,external_id").execute()
            return [row["id"] for row in res.data]
        except Exception as e:
            print(f"[DB Error] Ingest Signals: {e}")
            raise e

    def search_signals(self, team_id: str, vector: List[float], limit: int = 5, threshold: float = 0.7) -> List[Dict]:
        """
        RAG: Search for similar signals using Vector Similarity.
        Requires 'match_signals' DB function.
        """
        try:
            res = self.db.rpc("match_signals", {
                "query_embedding": vector,
                "match_threshold": threshold,
                "match_count": limit,
                "filter_team_id": team_id
            }).execute()
            return res.data
        except Exception as e:
            print(f"[DB Error] Vector Search: {e}")
            return []

    # --- INFERENCE RUNS ---
    def create_inference_run(self, team_id: str, trigger_type: str, config: Dict = {}) -> str:
        """Starts a new Audit Log entry. Returns Run ID."""
        data = {
            "team_id": team_id,
            "trigger_type": trigger_type,
            "status": "processing",
            "model_config": config,
            "started_at": datetime.now(timezone.utc).isoformat()
        }
        res = self.db.table("inference_runs").insert(data).execute()
        return res.data[0]["id"]

    def complete_inference_run(self, run_id: str, status: str = "completed"):
        """Updates the status of the run."""
        self.db.table("inference_runs").update({
            "status": status,
            "completed_at": datetime.now(timezone.utc).isoformat()
        }).eq("id", run_id).execute()

    # --- JOIN TABLE ---
    def link_signals_to_run(self, run_id: str, signal_ids: List[str]):
        """Populates the inference_run_signals join table."""
        if not signal_ids:
            return
        
        rows = [{"inference_run_id": run_id, "signal_id": s_id} for s_id in signal_ids]
        self.db.table("inference_run_signals").insert(rows).execute()

    # --- WORKFLOWS ---
    def save_workflow(self, team_id: str, run_id: str, workflow_graph: Dict) -> str:
        """
        Saves the workflow and its nodes/edges.
        This handles the Write Transaction logic (Active flag management).
        """
        # 1. Create Workflow Record
        workflow_data = {
            "team_id": team_id,
            "inference_run_id": run_id,
            "title": workflow_graph.get("title", "Generated Workflow"),
            "is_active": False # Default to false, allow user to 'Activate' later? Or True for MVP? 
                               # Requirement: "Rollback...". Let's set True for now and handle the Unique Constraint logic.
        }
        
        # De-activate previous active workflow (Manual logic because partial index prevents insert if we don't unset first)
        # Ideally this should be a stored proc.
        # For Phase 1 Code: We will fetch the current active one, set it false, then insert new one as true.
        # This is a race condition risk but acceptable for MVP Phase 1.
        
        try:
            # Unset active
            self.db.table("workflows").update({"is_active": False}).eq("team_id", team_id).eq("is_active", True).execute()
            
            # Insert new as Active
            workflow_data["is_active"] = True
            w_res = self.db.table("workflows").insert(workflow_data).execute()
            workflow_id = w_res.data[0]["id"]
            
            # 2. Insert Nodes
            nodes = workflow_graph.get("nodes", [])
            if nodes:
                node_rows = []
                for n in nodes:
                    node_rows.append({
                        "workflow_id": workflow_id,
                        "step_id": n["id"],
                        "label": n["data"].get("label", "Untitled"),
                        "type": n.get("type", "process"),
                        "description": n["data"].get("description", ""),
                        "actor": n["data"].get("actor", ""),
                        "metadata": n["data"]
                    })
                self.db.table("workflow_nodes").insert(node_rows).execute()
                
            # 3. Insert Edges
            edges = workflow_graph.get("edges", [])
            if edges:
                edge_rows = []
                for e in edges:
                    edge_rows.append({
                        "workflow_id": workflow_id,
                        "source_step_id": e["source"],
                        "target_step_id": e["target"],
                        "label": e.get("label", ""),
                        "condition": "" 
                    })
                self.db.table("workflow_edges").insert(edge_rows).execute()
            
            return workflow_id
            
        except Exception as e:
            print(f"[DB Error] Save Workflow Failed: {e}")
            # If workflow was created, we might want to delete it?
            # Or reliance on 'inference_run' status=failed is enough.
    def _assemble_workflow_graph(self, workflow: Dict) -> Dict:
        """Helper to reconstruct graph from DB row"""
        wf_id = workflow["id"]
        
        # Get Nodes
        n_res = self.db.table("workflow_nodes").select("*").eq("workflow_id", wf_id).execute()
        nodes = []
        for row in n_res.data:
            nodes.append({
                "id": row["step_id"],
                "type": row["type"],
                "data": {
                    "label": row["label"],
                    "description": row["description"],
                    "actor": row["actor"],
                    **row["metadata"]
                }
            })
            
        # Get Edges
        e_res = self.db.table("workflow_edges").select("*").eq("workflow_id", wf_id).execute()
        edges = []
        for row in e_res.data:
            edges.append({
                "source": row["source_step_id"],
                "target": row["target_step_id"],
                "label": row["label"]
            })
            
        return {
            "workflow_id": wf_id,
            "team_id": workflow["team_id"],
            "title": workflow["title"],
            "created_at": workflow["created_at"],
            "is_active": workflow["is_active"],
            "nodes": nodes,
            "edges": edges
        }

    def get_active_workflow(self, team_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves the currently active workflow graph."""
        try:
            w_res = self.db.table("workflows").select("*")\
                .eq("team_id", team_id)\
                .eq("is_active", True)\
                .maybe_single()\
                .execute()
            
            if not w_res.data: return None
            return self._assemble_workflow_graph(w_res.data)
        except Exception as e:
            print(f"[DB Error] Get Active Workflow: {e}")
            return None

    def get_workflow_history(self, team_id: str, limit: int = 20) -> List[Dict]:
        """Fetch list of workflow summaries"""
        try:
            res = self.db.table("workflows")\
                .select("id, title, created_at, is_active")\
                .eq("team_id", team_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            return res.data
        except Exception as e:
            print(f"[DB Error] History: {e}")
            return []

    def get_workflow_by_id(self, workflow_id: str, team_id: str) -> Optional[Dict]:
        """Fetch specific workflow version"""
        try:
            # Enforce team ownership
            w_res = self.db.table("workflows").select("*").eq("id", workflow_id).eq("team_id", team_id).maybe_single().execute()
            if not w_res.data: return None
            return self._assemble_workflow_graph(w_res.data)
        except Exception as e:
            print(f"[DB Error] Get By ID: {e}")
            return None
