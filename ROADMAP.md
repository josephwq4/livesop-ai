# LiveSOP AI Roadmap & Feature Status

## 🟢 Current Status (Ready for Early Access)

**Core Platform**
- [x] **Event Ingestion**: Slack, Jira, Gmail, CSV.
- [x] **AI Inference**: GPT-4 based workflow extraction.
- [x] **Persistence**: Full Supabase PostgreSQL storage with History.
- [x] **Real-Time**: WebSocket updates for new signals.

**Agentic Capabilities**
- [x] **Automations**: One-click execution (Post to Slack, Create Jira Ticket).
- [x] **Memory**: Vector embeddings generated for all incoming data.

**User Experience**
- [x] **Dashboard**: Interactive Graph & Kanban views.
- [x] **History**: Time-travel to previous workflow versions.
- [x] **Skeletons**: polished loading states.

---

## 🟡 Upcoming (Phase 5+)

**1. Smart Context / RAG (In Progress)**
- *Goal*: Enable the AI to "remember" past incidents and suggest solutions based on history.
- *Tech*: pgvector similarity search on `raw_signals`.

**2. Multi-User Authentication**
- *Goal*: Secure login for enterprise teams.
- *Tech*: Supabase Auth integration.

**3. Auto-Pilot Mode**
- *Goal*: Set specific workflow nodes to run automatically without human approval.
- *Tech*: Background job scheduler + Confidence Thresholds.

**4. Webhooks**
- *Goal*: Real-time, push-based data ingestion.
- *Tech*: Public API endpoints for Slack/Jira webhooks.
