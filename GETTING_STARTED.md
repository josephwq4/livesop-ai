# 🚀 Getting Started with LiveSOP AI

Welcome! This guide will help you get LiveSOP AI up and running in minutes.

## ⚡ Quick Start (5 Minutes)

### Step 1: Run Setup Script
Open PowerShell or Command Prompt in the project folder and run:
```bash
setup.bat
```

This automatically:
- ✅ Creates Python virtual environment
- ✅ Installs all backend dependencies
- ✅ Installs all frontend dependencies
- ✅ Creates .env configuration files

### Step 2: Add Your OpenAI API Key

1. Get your API key from: https://platform.openai.com/api-keys
2. Open `backend/.env` in a text editor
3. Replace `your_openai_api_key_here` with your actual key:
   ```
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
   ```
4. Save the file

### Step 3: Start the Application
```bash
start.bat
```

This opens two terminal windows:
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:3000

### Step 4: Use the Application

1. **Open your browser** to http://localhost:3000
2. **Login** with any credentials (demo mode)
3. **Go to Integrations** page
4. **Upload a CSV** or use mock data
5. **Go to Dashboard** and click "Run Inference"
6. **View your workflow** in Cards, Flowchart, or SOP view!

## 📊 Sample CSV Data

Create a file called `sample_data.csv`:

```csv
text,actor,timestamp
"Customer reported login issue via email",Support Team,2024-01-15T09:00:00
"Created Jira ticket PROJ-123 for login bug",Product Manager,2024-01-15T09:15:00
"Assigned ticket to engineering team",Product Manager,2024-01-15T09:20:00
"Started investigating the issue",Developer,2024-01-15T10:00:00
"Found root cause in authentication service",Developer,2024-01-15T11:30:00
"Created PR #456 with fix",Developer,2024-01-15T14:00:00
"Reviewed and approved PR",Senior Engineer,2024-01-15T15:00:00
"Deployed fix to production",DevOps,2024-01-15T16:00:00
"Notified customer that issue is resolved",Support Team,2024-01-15T16:30:00
"Closed Jira ticket PROJ-123",Product Manager,2024-01-15T17:00:00
```

Upload this in the Integrations page to see a real workflow!

## 🎯 What You Can Do

### 1. **View Workflows in 3 Ways**

**Cards View** - List of workflow steps with descriptions
- See each step clearly
- Click "Run" to execute automations
- View owner and timestamp

**Flowchart View** - Interactive visual graph
- Drag nodes around
- Zoom in/out
- See workflow relationships

**SOP View** - Auto-generated documentation
- Markdown formatted
- Step-by-step procedures
- Best practices included

### 2. **Run AI Inference**

Click "Run Inference" to:
- Analyze all imported activities
- Generate workflow graph using GPT-4
- Create embeddings for semantic search
- Store in vector database

### 3. **Execute Automations**

Click "Run" on any workflow step to:
- Execute the automation
- See real-time results
- Track in automation history

### 4. **Connect Integrations**

**Slack** - Import team messages
- Get bot token from Slack workspace
- Enter channel names
- Import conversations

**Jira** - Sync project issues
- Get API key from Jira
- Enter project key
- Import tickets

**Gmail** - Import emails
- Set up OAuth credentials
- Choose label/folder
- Import threads

**CSV** - Upload custom data
- Use template format
- Drag and drop file
- Import instantly

## 🔧 Troubleshooting

### Backend won't start
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend won't start
```bash
cd frontend
npm install
npm run dev
```

### OpenAI API errors
- Check your API key is correct
- Ensure you have credits: https://platform.openai.com/usage
- The app works with mock data if API key is missing

### Port already in use
- Backend: Change port in command: `uvicorn app.main:app --reload --port 8001`
- Frontend: Change port in `vite.config.js`

## 📚 Learn More

- **Full Documentation**: See `README.md`
- **Project Overview**: See `PROJECT_SUMMARY.md`
- **API Documentation**: http://localhost:8000/docs
- **Architecture Diagram**: See generated image

## 🎨 Customization

### Change Team ID
Edit in `Dashboard.jsx` and `Integrations.jsx`:
```javascript
const teamId = 'your-team-id';
```

### Modify Workflow Prompts
Edit `backend/app/services/workflow_inference.py`:
```python
prompt = "Your custom prompt here..."
```

### Customize UI Colors
Edit `frontend/tailwind.config.js`:
```javascript
colors: {
  primary: '#your-color',
}
```

## 🚀 Next Steps

1. **Add Real Integrations**
   - Set up Slack bot
   - Configure Jira API
   - Enable Gmail OAuth

2. **Deploy to Production**
   - Backend: Render, Railway, Heroku
   - Frontend: Vercel, Netlify
   - Database: PostgreSQL

3. **Add Authentication**
   - Implement JWT tokens
   - Add user registration
   - Protect routes

4. **Enhance AI**
   - Fine-tune prompts
   - Add more context
   - Create templates

## 💡 Tips

- **Start Simple**: Use CSV import first to understand the workflow
- **Iterate**: Run inference multiple times as you add more data
- **Explore**: Try all three views (Cards, Flowchart, SOP)
- **Customize**: Modify prompts to match your team's language
- **Scale**: Add more integrations as you grow

## 🎉 You're Ready!

Your LiveSOP AI platform is now running. Start by:
1. Uploading sample CSV data
2. Running inference
3. Exploring the generated workflows
4. Executing automations

**Have fun automating your workflows! 🚀**

---

Need help? Check the documentation or create an issue on GitHub.
