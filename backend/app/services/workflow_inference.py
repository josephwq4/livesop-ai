import os
import json
from typing import List, Dict, Any
from datetime import datetime
from openai import OpenAI

# try:
#     import chromadb
#     from chromadb.config import Settings
#     CHROMADB_AVAILABLE = True
# except ImportError:
#     CHROMADB_AVAILABLE = False
#     print("ChromaDB not available - using in-memory storage")

CHROMADB_AVAILABLE = False

from app.services.integration_clients import fetch_all_events


# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "sk-test-key"))

# Initialize ChromaDB for vector storage (if available)
if CHROMADB_AVAILABLE:
    chroma_client = chromadb.Client(Settings(
        anonymized_telemetry=False,
        allow_reset=True
    ))
else:
    chroma_client = None


def get_or_create_collection(team_id: str):
    """Get or create a ChromaDB collection for a team"""
    if not CHROMADB_AVAILABLE or chroma_client is None:
        return None
    collection_name = f"team_{team_id}_workflows"
    try:
        collection = chroma_client.get_collection(name=collection_name)
    except:
        collection = chroma_client.create_collection(
            name=collection_name,
            metadata={"team_id": team_id}
        )
    return collection


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Generate embeddings using OpenAI"""
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "sk-test-key":
        # Return mock embeddings for MVP
        import random
        return [[random.random() for _ in range(1536)] for _ in texts]
    
    try:
        response = client.embeddings.create(
            input=texts,
            model="text-embedding-3-small"
        )
        return [item.embedding for item in response.data]
    except Exception as e:
        print(f"OpenAI Embedding Error: {e}")
        # Return mock embeddings as fallback
        import random
        return [[random.random() for _ in range(1536)] for _ in texts]


def store_events_in_vector_db(team_id: str, events: List[Dict[str, Any]]):
    """Store events with embeddings in ChromaDB"""
    if not events or not CHROMADB_AVAILABLE:
        return
    
    collection = get_or_create_collection(team_id)
    if collection is None:
        return
    
    # Generate embeddings for all event texts
    texts = [event["text"] for event in events]
    embeddings = generate_embeddings(texts)
    
    # Prepare data for ChromaDB
    ids = [event["id"] for event in events]
    metadatas = [
        {
            "timestamp": event["timestamp"],
            "actor": event["actor"],
            "source": event["source"],
            "team_id": event["team_id"]
        }
        for event in events
    ]
    
    # Upsert into ChromaDB
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )


def query_similar_events(team_id: str, query_text: str, n_results: int = 10) -> List[Dict[str, Any]]:
    """Query similar events from vector DB"""
    if not CHROMADB_AVAILABLE:
        return {"documents": [], "metadatas": [], "distances": []}
    
    collection = get_or_create_collection(team_id)
    if collection is None:
        return {"documents": [], "metadatas": [], "distances": []}
    
    # Generate embedding for query
    query_embedding = generate_embeddings([query_text])[0]
    
    # Query ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    
    return results


def generate_workflow_graph_with_llm(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Use GPT-4 to generate a workflow graph from events"""
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "sk-test-key":
        # Return mock workflow for MVP
        return {
            "nodes": [
                {
                    "id": "step_1",
                    "step": "Feature Request Received",
                    "owner": "Product Team",
                    "description": "Client submits feature request via email or Slack"
                },
                {
                    "id": "step_2",
                    "step": "Create Jira Ticket",
                    "owner": "Product Manager",
                    "description": "PM creates and prioritizes Jira ticket"
                },
                {
                    "id": "step_3",
                    "step": "Development",
                    "owner": "Engineering Team",
                    "description": "Developers implement the feature"
                },
                {
                    "id": "step_4",
                    "step": "Code Review",
                    "owner": "Senior Engineer",
                    "description": "PR review and approval"
                },
                {
                    "id": "step_5",
                    "step": "Deployment",
                    "owner": "DevOps",
                    "description": "Deploy to production"
                }
            ],
            "edges": [
                {"source": "step_1", "target": "step_2", "label": "creates"},
                {"source": "step_2", "target": "step_3", "label": "assigned to"},
                {"source": "step_3", "target": "step_4", "label": "submits for"},
                {"source": "step_4", "target": "step_5", "label": "approved for"}
            ]
        }
    
    # Prepare prompt for GPT-4
    events_text = "\n".join([
        f"- [{event['timestamp']}] {event['actor']} ({event['source']}): {event['text']}"
        for event in events[:50]  # Limit to 50 events to avoid token limits
    ])
    
    prompt = f"""Analyze the following team activity events and generate a workflow graph that represents the team's standard operating procedure.

Events:
{events_text}

Generate a JSON workflow graph with the following structure:
{{
  "nodes": [
    {{"id": "step_1", "step": "Step Name", "owner": "Role/Person", "description": "What happens in this step"}},
    ...
  ],
  "edges": [
    {{"source": "step_1", "target": "step_2", "label": "relationship"}},
    ...
  ]
}}

Focus on identifying:
1. Recurring patterns and sequences
2. Key decision points
3. Handoffs between team members
4. Common workflows (e.g., bug fixes, feature development, customer requests)

Return ONLY the JSON, no additional text."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at analyzing team workflows and creating process documentation."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        workflow_text = response.choices[0].message.content.strip()
        
        # Extract JSON from response (in case there's extra text)
        if "```json" in workflow_text:
            workflow_text = workflow_text.split("```json")[1].split("```")[0].strip()
        elif "```" in workflow_text:
            workflow_text = workflow_text.split("```")[1].split("```")[0].strip()
        
        workflow_graph = json.loads(workflow_text)
        return workflow_graph
        
    except Exception as e:
        print(f"GPT-4 Workflow Generation Error: {e}")
        # Return mock workflow as fallback
        return generate_workflow_graph_with_llm([])


from app.repositories.persistence import PersistenceRepository

def infer_workflow(team_id: str, user_id: str = None) -> Dict[str, Any]:
    """
    Main function to infer workflow from team activities with Full Persistence.
    
    args:
        team_id (str): The logical team ID (or 'default').
        user_id (str): The Authed User ID (Required for DB Team resolution).
    """
    # 1. Initialize Repo
    repo = PersistenceRepository()
    
    # 2. Resolve Real DB Team ID
    # If we have a user_id, we ensure they have a team in the DB.
    # If not, we fallback to the passed team_id (assuming it's a UUID for now, or failing).
    real_team_id = team_id
    if user_id:
        # Create/Get team owned by this user
        real_team_id = repo.get_or_create_team(f"Team {user_id[:4]}", user_id)
    
    print(f"[Inference] Object resolved to Team UUID: {real_team_id}")

    # 3. Fetch Events (Integration Layer)
    # Note: fetch_all_events currently uses env vars. It doesn't use DB stored creds yet.
    # In Phase 2, we will load credentials from DB. For now, it works for the single configured user.
    events = fetch_all_events(team_id) # API Clients work on env vars
    
    if not events:
        return {
            "team_id": real_team_id,
            "workflow_id": None,
            "nodes": [],
            "edges": [],
            "message": "No events found. Please connect integrations."
        }

    # Generate Embeddings for Semantic Search
    try:
        print(f"[Inference] Generating embeddings for {len(events)} events...")
        texts = [e["text"] for e in events]
        # Use existing helper to get vectors
        vectors = generate_embeddings(texts)
        if len(vectors) == len(events):
            for i, vec in enumerate(vectors):
                events[i]["embedding"] = vec
        else:
            print(f"[Warn] Embedding count mismatch. Skipping.")
    except Exception as e:
        print(f"[Warn] Embedding generation failed: {e}")
        
    try:
        # 4. Ingest Raw Signals (Persist the Data Lake)
        # Map events to repo format (lists of dicts)
        # Our fetch_all_events format aligns with repo.ingest_signals expectation.
        signal_ids = repo.ingest_signals(real_team_id, events)
        print(f"[Persistence] Ingested {len(signal_ids)} signals.")
        
        # 5. Create Inference Run (Audit Log)
        run_id = repo.create_inference_run(real_team_id, "manual_dashboard", {"model": "gpt-4", "event_count": len(events)})
        print(f"[Persistence] Started Run: {run_id}")
        
        # 6. Link Signals to Run (Provenance)
        repo.link_signals_to_run(run_id, signal_ids)
        
        # Vector Store (Phase 2 - Disabled/Optional)
        # store_events_in_vector_db(real_team_id, events)
        
        # 7. Generate Workflow Graph (LLM)
        workflow_graph = generate_workflow_graph_with_llm(events)
        
        # 8. Save Workflow (Commit Artifact)
        persisted_wf_id = repo.save_workflow(real_team_id, run_id, workflow_graph)
        print(f"[Persistence] Saved Workflow {persisted_wf_id}")
        
        # 9. Complete Run
        repo.complete_inference_run(run_id, "success")
        
        # 10. Return Result (Enriched with DB ID)
        workflow_graph["team_id"] = real_team_id
        workflow_graph["workflow_id"] = persisted_wf_id
        workflow_graph["created_at"] = datetime.now().isoformat()
        
        return workflow_graph

    except Exception as e:
        print(f"[CRITICAL] Inference/Persistence Failed: {e}")
        # Phase 1: We just log raw error to console.
        # In future, update run status to 'failed'
        if 'run_id' in locals():
            repo.complete_inference_run(run_id, "failed")
        raise e


def generate_sop_document(team_id: str, workflow_id: str) -> str:
    """Generate a living SOP document from workflow"""
    # Query workflow from vector DB or cache
    if not CHROMADB_AVAILABLE:
        # Return default SOP if ChromaDB not available
        events_text = "Sample team activities"
    else:
        collection = get_or_create_collection(team_id)
        if collection is None:
            events_text = "Sample team activities"
        else:
            # Get all events
            all_events = collection.get()
            
            if not all_events["documents"]:
                return "No workflow data available to generate SOP."
            
            # Prepare prompt for SOP generation
            events_text = "\n".join([
                f"- {doc}" for doc in all_events["documents"][:100]
            ])
    
    prompt = f"""Based on the following team activities, generate a comprehensive Standard Operating Procedure (SOP) document.

Team Activities:
{events_text}

Create a detailed SOP that includes:
1. Overview and Purpose
2. Step-by-step procedures
3. Roles and Responsibilities
4. Best Practices
5. Common Issues and Solutions

Format the SOP in Markdown."""

    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "sk-test-key":
        return """# Standard Operating Procedure: Feature Development Workflow

## Overview
This SOP outlines the standard process for developing and deploying new features.

## Procedure

### 1. Feature Request
- **Owner**: Product Team
- **Action**: Receive and document feature requests from clients
- **Tools**: Email, Slack

### 2. Ticket Creation
- **Owner**: Product Manager
- **Action**: Create Jira ticket with requirements and priority
- **Tools**: Jira

### 3. Development
- **Owner**: Engineering Team
- **Action**: Implement feature according to specifications
- **Tools**: IDE, Git

### 4. Code Review
- **Owner**: Senior Engineer
- **Action**: Review code for quality and standards
- **Tools**: GitHub, GitLab

### 5. Deployment
- **Owner**: DevOps Team
- **Action**: Deploy to production environment
- **Tools**: CI/CD Pipeline

## Best Practices
- Always document decisions in Jira
- Communicate blockers in daily standup
- Follow code review checklist

## Common Issues
- **Issue**: Unclear requirements
- **Solution**: Schedule clarification meeting with PM
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert technical writer specializing in creating clear, actionable SOPs."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=3000
        )
        
        sop_document = response.choices[0].message.content
        return sop_document
        
    except Exception as e:
        print(f"SOP Generation Error: {e}")
        return "Error generating SOP document."
