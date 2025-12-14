# 🚀 LiveSOP AI Deployment Guide

This guide will walk you through deploying the **LiveSOP AI** platform to a production environment. 

**Stack:**
- **Frontend**: Vercel (Free, Fast, optimized for React/Vite)
- **Backend**: Render (Free tier available, easy wrapper for Python/Docker)

---

## 🛠 Prerequisites

1.  **Git Account**: (GitHub, GitLab, or Bitbucket)
2.  **Vercel Account**: [Sign up here](https://vercel.com/signup)
3.  **Render Account**: [Sign up here](https://render.com/register)

---

## 📦 Step 1: Push Code to GitHub

Before deploying, your code needs to be on GitHub.

1.  **Create a New Repository** on GitHub (e.g., `livesop-ai`).
2.  **Initialize Git** locally if you haven't:
    ```bash
    git init
    git add .
    git commit -m "Initial commit - Ready for deployment"
    ```
3.  **Push to GitHub**:
    ```bash
    git branch -M main
    git remote add origin https://github.com/YOUR_USERNAME/livesop-ai.git
    git push -u origin main
    ```

---

## 🟢 Step 2: Deploy Backend to Render

1.  **Go to Render Dashboard**: Click **"New"** -> **"Web Service"**.
2.  **Connect GitHub**: Select your `livesop-ai` repository.
3.  **Configure Service**:
    *   **Name**: `livesop-backend` (or unique name)
    *   **Root Directory**: `backend` (⚠️ Important!)
    *   **Runtime**: `Python 3`
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `./start.sh`
4.  **Environment Variables**:
    *   Scroll down to "Environment Variables".
    *   Add `OPENAI_API_KEY` (Copy from your local `.env`).
    *   Add `PYTHON_VERSION` = `3.11.0`
5.  **Click "Create Web Service"**.

Wait for the deployment to finish (usually 2-3 minutes).
**Copy your Backend URL** (e.g., `https://livesop-backend-xyz.onrender.com`). You will need this for the frontend!

---

## 🔵 Step 3: Deploy Frontend to Vercel

1.  **Go to Vercel Dashboard**: Click **"Add New..."** -> **"Project"**.
2.  **Import Git Repository**: Select `livesop-ai`.
3.  **Configure Project**:
    *   **Root Directory**: Click "Edit" and select `frontend` (⚠️ Important!).
    *   **Framework Preset**: Vite (should auto-detect).
    *   **Build Command**: `npm run build`
4.  **Environment Variables**:
    *   Add a new variable: `VITE_API_URL`
    *   Value: Your Render Backend URL (e.g., `https://livesop-backend-xyz.onrender.com`)
    *   **Note**: Ensure there is NO trailing slash `/` at the end.
5.  **Click "Deploy"**.

Wait about 1 minute.
**Copy your Frontend URL** (e.g., `https://livesop-ai.vercel.app`).

---

## ⚙️ Step 4: Final Configuration (CORS)

Your backend currently blocks requests from unknown domains for security. You must allow your new Vercel domain.

1.  Go back to **Render Dashboard** -> Your Service -> **Environment**.
2.  Add a new variable:
    *   **Key**: `FRONTEND_URL`
    *   **Value**: Your Vercel URL (e.g., `https://livesop-ai.vercel.app`) - **no trailing slash!**
3.  **Save Changes**. Render will automatically redeploy.

*(Note: If you haven't implemented the `FRONTEND_URL` variable in your `main.py` yet, the default `["*"]` (allow all) might be active. It is safer to restrict it.)*

---

## ✅ Deployment Checklist

- [ ] Backend is running on Render (Health Check passes)
- [ ] Backend has `OPENAI_API_KEY` set
- [ ] Frontend is live on Vercel
- [ ] Frontend has `VITE_API_URL` pointing to backend
- [ ] You can log in and view the dashboard

---

## 🔗 Step 5: Configure Webhooks & Integrations

To enable Real-Time Auto-Pilot, you must configure Slack:

1.  **Render Environment Variables**:
    *   Add `SLACK_SIGNING_SECRET`: Get this from api.slack.com -> App Credentials.
    *   Add `SLACK_TOKEN`: Bot User OAuth Token (xoxb-...) for sending messages.
    *   Add `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`: For persistence.

2.  **Slack App Configuration**:
    *   Go to **Interactivity & Shortcuts** -> Enable.
    *   Go to **Event Subscriptions** -> Enable.
    *   **Request URL**: `https://your-backend.onrender.com/webhooks/slack`
    *   Subscribe to Bot Events: `message.channels`, `message.im`.
    *   **Reinstall App** to Workspace.

**🎉 You are LIVE!**
