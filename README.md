# LiveSOP AI

**AI-Powered Workflow Inference and Automation Platform**

LiveSOP AI observes team activities across Slack, Jira, Gmail, and CSV imports to automatically infer workflows, generate living SOPs, and provide one-click automations.

## 🚀 Features

- **🤖 AI Workflow Inference**: Automatically discover workflows from team activities using GPT-4
- **📊 Visual Workflow Graphs**: Interactive flowcharts powered by ReactFlow
- **📝 Living SOPs**: Auto-generated Standard Operating Procedures that evolve with your team
- **⚡ One-Click Automation**: Execute complex workflows with a single click
- **🔗 Multi-Platform Integration**: Slack, Jira, Gmail, and CSV imports
- **🎯 Vector Search**: Semantic search powered by OpenAI embeddings and ChromaDB
- **👥 Operator Personalization**: Learn preferred sequences and actions per user

## 🏗️ Architecture

### Backend
- **Framework**: FastAPI
- **AI**: OpenAI GPT-4 + text-embedding-3-small
- **Vector DB**: ChromaDB
- **Integrations**: Slack SDK, Jira API, Gmail API

### Frontend
- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS
- **Visualization**: ReactFlow
- **Routing**: React Router

## 📦 Installation

### Prerequisites
- Python 3.9+
- Node.js 18+
- OpenAI API key

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env
# Edit .env and add your API keys

# Run the server
uvicorn app.main:app --reload
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
copy .env.example .env
# Edit .env if needed

# Run the development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 🔑 Configuration

### Backend Environment Variables

Create a `.env` file in the `backend` directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
SLACK_TOKEN=your_slack_token_here
JIRA_API_KEY=your_jira_api_key_here
JIRA_SERVER=https://your-domain.atlassian.net
JIRA_PROJECT=PROJECT
GMAIL_CREDENTIALS=your_gmail_credentials_json_here
```

### Frontend Environment Variables

Create a `.env` file in the `frontend` directory:

```env
VITE_API_URL=http://localhost:8000
```

## 📖 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Workflows
- `GET /workflows/{team_id}/workflows` - Get inferred workflows
- `POST /workflows/{team_id}/infer` - Run workflow inference
- `GET /workflows/{team_id}/sop` - Generate SOP document
- `GET /workflows/{team_id}/search` - Semantic search

#### Automations
- `POST /automations/{team_id}/run/{workflow_id}` - Execute automation
- `GET /automations/{team_id}/history` - Get automation history
- `POST /automations/{team_id}/schedule/{workflow_id}` - Schedule automation

#### Integrations
- `GET /integrations/slack` - Fetch Slack events
- `GET /integrations/jira` - Fetch Jira issues
- `GET /integrations/gmail` - Fetch Gmail threads
- `POST /integrations/csv/upload` - Upload CSV data

## 🎯 Usage

### 1. Connect Integrations
Configure your Slack, Jira, and Gmail credentials in the `.env` file or upload CSV data.

### 2. Run Inference
Click "Run Inference" in the dashboard to analyze team activities and generate workflows.

### 3. View Workflows
Switch between three views:
- **Cards**: List view with workflow steps
- **Flowchart**: Visual workflow graph
- **SOP**: Generated documentation

### 4. Execute Automations
Click "Run" on any workflow step to execute the automation.

## 🛠️ Development

### Backend Structure
```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── routes/              # API endpoints
│   │   ├── integrations.py
│   │   ├── workflows.py
│   │   └── automations.py
│   ├── services/            # Business logic
│   │   ├── workflow_inference.py
│   │   ├── integration_clients.py
│   │   └── automation_runner.py
│   └── models/              # Data models
│       └── workflow.py
└── requirements.txt
```

### Frontend Structure
```
frontend/
├── src/
│   ├── pages/              # Page components
│   │   ├── Dashboard.jsx
│   │   └── Login.jsx
│   ├── components/         # Reusable components
│   │   ├── WorkflowCard.jsx
│   │   └── FlowChart.jsx
│   └── services/           # API client
│       └── api.js
└── package.json
```

## 🚢 Deployment

### Backend Deployment (Render, Railway, etc.)

```bash
# Build command
pip install -r requirements.txt

# Start command
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Frontend Deployment (Vercel, Netlify, etc.)

```bash
# Build command
npm run build

# Output directory
dist
```

## 🔐 Security Notes

- Never commit `.env` files
- Use environment variables for all sensitive data
- Implement proper authentication in production
- Set specific CORS origins in production
- Use HTTPS in production

## 📊 MVP Features

✅ Workflow Inference from Slack/Jira/Gmail  
✅ AI-powered workflow graph generation  
✅ **Persistent Database Storage (Supabase)**  
✅ **Real-Time Signal Updates**  
✅ **Workflow Version History**  
✅ Living SOP document creation  
✅ One-click automation execution (Jira/Slack)  
✅ Vector DB storage for context  
✅ Interactive workflow visualization  
✅ Multi-tenant architecture  
✅ CSV data import  

## 🎯 Next Steps

- [ ] Add user authentication (JWT, OAuth)
- [ ] Implement real-time collaboration
- [ ] Add webhook support for integrations
- [ ] Create workflow templates library
- [ ] Add analytics and insights dashboard
- [ ] Implement role-based access control
- [ ] Add notification system
- [ ] Create mobile app

## 📝 License

MIT License - feel free to use this project for your own purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ using FastAPI, React, and OpenAI**
