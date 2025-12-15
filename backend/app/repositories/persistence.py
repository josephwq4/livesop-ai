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

        # Upsert to handle duplicates safely
        try:
            # We use upsert. If we want to detect strictly if it's new, we'd need 'ignoreDuplicates' or SQL insert.
            # But the requirement calls for checking idempotency at the trigger level too.
            # So upsert is fine for the data lake.
            res = self.db.table("raw_signals").upsert(prepared_rows, on_conflict="team_id,source,external_id").execute()
            return [row["id"] for row in res.data]
        except Exception as e:
            print(f"[DB Error] Ingest Signals: {e}")
            raise e

    def get_signal_by_id(self, signal_id: str) -> Optional[Dict]:
        """Fetch a specific signal by its UUID or external ID"""
        try:
            # Try by DB ID first
            res = self.db.table("raw_signals").select("*").eq("id", signal_id).maybe_single().execute()
            if not res.data:
                # Try by external ID (imperfect if multiples, but fallback)
                res = self.db.table("raw_signals").select("*").eq("external_id", signal_id).limit(1).execute()
                if not res.data: return None
                return res.data[0]
            return res.data
        except Exception as e:
            print(f"[DB Error] Get Signal: {e}")
            return None

    def check_idempotency_key(self, team_id: str, idempotency_key: str) -> bool:
        """
        Checks if a specific idempotency key (hash) has already been processed for Auto-Pilot.
        Returns True if duplicate exists.
        """
        try:
            # We look for a successful or processing run with this key in metadata
            # or we create a dedicated idempotency table.
            # For simplicity, we query 'inference_runs' model_config->idempotency_key
            # Note: JSON filtering in Supabase: model_config->>'idempotency_key'
            
            res = self.db.table("inference_runs").select("id")\
                .eq("team_id", team_id)\
                .eq("trigger_type", "auto_pilot_evaluation")\
                .eq("model_config->>idempotency_key", idempotency_key)\
                .limit(1).execute()
                
            return len(res.data) > 0
        except Exception as e:
            print(f"[DB Error] Idempotency Check: {e}")
            return False

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

    def update_node_metadata(self, node_id: str, metadata_update: Dict) -> bool:
        """Updates the metadata of a specific node (e.g. toggling auto-pilot)"""
        try:
            # 1. Fetch current metadata
            res = self.db.table("workflow_nodes").select("metadata").eq("step_id", node_id).single().execute()
            if not res.data:
                return False
            
            current_meta = res.data["metadata"] or {}
            # 2. Merge updates
            updated_meta = {**current_meta, **metadata_update}
            
            # 3. Save
            self.db.table("workflow_nodes").update({"metadata": updated_meta}).eq("step_id", node_id).execute()
            return True
        except Exception as e:
            print(f"[DB Error] Update Node: {e}")
            return False

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
