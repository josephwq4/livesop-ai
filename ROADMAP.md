# LiveSOP AI Roadmap & Feature Status

## 🟢 Current Status (Ready for Early Access)

**Core Platform**
- [x] **Event Ingestion**: Slack, Jira, Gmail, CSV.
- [x] **AI Inference**: GPT-4 based workflow extraction.
- [x] **Persistence**: Full Supabase PostgreSQL storage with History.
- [x] **Real-Time**: WebSocket updates for new signals.
- [x] **Auth**: Enterprise Multi-User Authentication (Supabase).

**Agentic Capabilities**
- [x] **Automations**: One-click execution (Post to Slack, Create Jira Ticket).
- [x] **Memory (RAG)**: Semantic Search over historical context.
- [x] **Auto-Pilot Config**: Toggle nodes to run automatically.

**User Experience**
- [x] **Dashboard**: Interactive Graph & Kanban views.
- [x] **History**: Time-travel to previous workflow versions.
- [x] **Lifecycle**: Landing Page, Settings, User Profile.

---

## 🟡 Upcoming (Phase 8+)

**1. Real-Time Webhooks**
- *Goal*: Eliminate manual fetching. Listen to Slack/Jira events in real-time.
- *Tech*: Public API endpoints + Signature Verification.

**2. Auto-Pilot Engine**
- *Goal*: Background workers that execute "Auto-Pilot" nodes without user intervention.
- *Tech*: Async Task Queue (Celery/Arq) or Cron-based runner.

**3. Advanced SOP Editor**
- *Goal*: Allow manual editing of the generated SOP markdown.

