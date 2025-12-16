# Phase C: Demo Readiness Checklist

## ✅ Pre-Demo Setup (15 minutes)

### 1. Database Preparation
- [ ] Run this SQL to enable one node for auto-execution:
```sql
-- Enable Auto-Run for the first Jira-related node
UPDATE workflow_nodes 
SET auto_run_enabled = true 
WHERE (label ILIKE '%jira%' OR label ILIKE '%ticket%' OR label ILIKE '%escalat%')
AND workflow_id IN (
  SELECT id FROM workflows WHERE is_active = true LIMIT 1
)
LIMIT 1;

-- Verify it worked
SELECT step_id, label, auto_run_enabled 
FROM workflow_nodes 
WHERE auto_run_enabled = true;
```

### 2. Environment Variables Check
- [ ] `SLACK_TOKEN` is set and valid
- [ ] `SLACK_SIGNING_SECRET` is set (for webhooks)
- [ ] `JIRA_PROJECT` is set to your test project
- [ ] `JIRA_API_KEY` or credentials are configured
- [ ] `OPENAI_API_KEY` is set and has credits

### 3. Slack Webhook Setup
- [ ] Webhook URL configured: `https://your-backend.onrender.com/webhooks/slack`
- [ ] Subscribed to `message.channels` event
- [ ] Test channel is being monitored
- [ ] Bot is added to the test channel

### 4. Frontend Preparation
- [ ] Log in to https://livesopai.vercel.app
- [ ] Navigate to Dashboard
- [ ] Verify you see at least one workflow
- [ ] Check that Live Feed view is accessible

### 5. Recording Setup
- [ ] Screen recording software ready
- [ ] Microphone tested
- [ ] Browser at 100% zoom
- [ ] Close unnecessary tabs/windows
- [ ] Prepare demo Slack message

---

## 🎬 Demo Flow (Quick Reference)

### Act 1: Problem (30s)
**Show**: Slack channel with multiple messages
**Say**: "Support teams handle hundreds of messages daily"

### Act 2: Trigger (45s)
**Do**: Send critical message in Slack
**Show**: Live Feed updates with new escalation
**Say**: "LiveSOP detected this in real-time"

### Act 3: Trust (60s)
**Do**: Click escalation row → Trust Panel opens
**Show**: Confidence, Rationale, Source, Action
**Say**: "Full transparency - here's why and what happened"

### Act 4: Proof (30s)
**Show**: Jira ticket that was auto-created
**Say**: "It actually worked - ticket created with full context"

### Act 5: Control (45s)
**Show**: Hero stats, safety toggles
**Say**: "You're in control - global kill switch + per-node flags"

### Act 6: Vision (30s)
**Show**: Workflow visualization
**Say**: "One automation today, full workflow tomorrow"

**Total**: 3-5 minutes

---

## 🐛 Known Issues to Avoid

### Issue 1: Webhook Delay
**Problem**: Live Feed doesn't update immediately
**Workaround**: Wait 3-5 seconds after sending Slack message before switching to dashboard
**Fix**: Mention "real-time processing" but don't promise instant

### Issue 2: Low Confidence
**Problem**: AI gives < 90% confidence, nothing executes
**Workaround**: Use very explicit trigger words: "critical", "urgent", "escalation", "bug", "timeout"
**Fix**: Pre-test your demo message to ensure it triggers

### Issue 3: Node Not Enabled
**Problem**: Evaluation happens but no execution
**Workaround**: Run the SQL above to enable at least one node
**Fix**: Check `workflow_nodes.auto_run_enabled` before demo

### Issue 4: Empty Live Feed
**Problem**: No historical data to show
**Workaround**: Run a test automation before the demo to populate feed
**Fix**: This is actually fine - shows "clean slate" for new users

---

## 📸 Screenshot Capture Guide

### Required Shots (in order)

1. **Slack Chaos** (`01_slack_chaos.png`)
   - Zoom: 100%
   - Crop: Show 5-10 messages
   - Highlight: Mix of routine + critical

2. **Trigger Message** (`02_slack_trigger.png`)
   - Zoom: 110% (make text readable)
   - Crop: Just the critical message
   - Highlight: Use Slack's highlight feature

3. **Live Feed** (`03_live_feed_entry.png`)
   - Zoom: 100%
   - Crop: Full dashboard with Live Feed visible
   - Highlight: The new entry (maybe add arrow in post)

4. **Trust Panel - Confidence** (`04_trust_panel_confidence.png`)
   - Zoom: 110%
   - Crop: Just the confidence section
   - Highlight: The 95% indicator

5. **Trust Panel - Rationale** (`05_trust_panel_rationale.png`)
   - Zoom: 110%
   - Crop: The reasoning text
   - Highlight: Key phrases

6. **Trust Panel - Source** (`06_trust_panel_source.png`)
   - Zoom: 110%
   - Crop: Source context + link
   - Highlight: "View in Slack" button

7. **Trust Panel - Action** (`07_trust_panel_action.png`)
   - Zoom: 110%
   - Crop: Action taken section
   - Highlight: Jira ticket link

8. **Jira Ticket** (`08_jira_ticket_created.png`)
   - Zoom: 100%
   - Crop: Full ticket view
   - Highlight: Title, description, timestamp

9. **Hero Stats** (`09_hero_stats.png`)
   - Zoom: 100%
   - Crop: Top section of dashboard
   - Highlight: The three stat cards

10. **Safety Controls** (`10_safety_controls.png`)
    - Zoom: 110%
    - Crop: Trust Panel toggle section
    - Highlight: The Auto-Pilot toggle

11. **Workflow Overview** (`11_workflow_overview.png`)
    - Zoom: 90% (fit more on screen)
    - Crop: Full workflow visualization
    - Highlight: Multiple nodes

---

## 🎥 Recording Tips

### Before Recording
- [ ] Close all notifications
- [ ] Set "Do Not Disturb" mode
- [ ] Clear browser history/cache
- [ ] Use incognito/private window (clean UI)
- [ ] Prepare script notes on second monitor

### During Recording
- [ ] Speak slowly and clearly
- [ ] Pause 2 seconds between major actions
- [ ] Use mouse to point at important elements
- [ ] Don't rush - let viewers absorb information
- [ ] If you make a mistake, pause and restart that section

### After Recording
- [ ] Add captions/subtitles
- [ ] Add arrows/highlights in post-production
- [ ] Add background music (subtle, not distracting)
- [ ] Export in 1080p minimum
- [ ] Test on mobile to ensure text is readable

---

## 🎯 Key Metrics to Highlight

### Speed
- "Signal to action in **under 5 seconds**"
- "Real-time monitoring, instant response"

### Accuracy
- "**95% confidence** - not guessing, high certainty"
- "Only executes when AI is sure"

### Transparency
- "**Full audit trail** - every decision explained"
- "Click to see exactly why"

### Control
- "**Global kill switch** - stop everything instantly"
- "**Per-node control** - enable only what you trust"

### Impact
- "**0.25 hours saved** per automation"
- "Scales to hundreds of automations"

---

## 🚨 Emergency Backup Plan

### If Live Demo Fails

**Option 1**: Pre-recorded Video
- Have a backup recording ready
- "Let me show you a quick video of this in action"
- Narrate over the video

**Option 2**: Screenshot Walkthrough
- Use the 11 screenshots as slides
- Walk through the flow manually
- "Here's what happens when..."

**Option 3**: Database Direct Query
- Show the `inference_runs` table in Supabase
- Prove the system is logging everything
- "The automation happened, here's the audit trail"

---

## ✅ Post-Demo Verification

After completing the demo, verify:

- [ ] Jira ticket was actually created
- [ ] Live Feed shows the entry
- [ ] Trust Panel displays all data correctly
- [ ] Hero stats incremented
- [ ] No errors in backend logs
- [ ] Webhook is still active

---

## 📊 Demo Success Criteria

### Minimum Viable Demo
- ✅ One Slack message triggers one automation
- ✅ Live Feed shows the event
- ✅ Trust Panel explains the decision
- ✅ Jira ticket is created
- ✅ Safety controls are demonstrated

### Ideal Demo
- ✅ All of the above, plus:
- ✅ Multiple workflow nodes visible
- ✅ Hero stats show meaningful numbers
- ✅ Smooth transitions between screens
- ✅ Clear, confident narration
- ✅ Professional recording quality

### Stretch Goals
- ✅ Live demo (not pre-recorded)
- ✅ Multiple automations in sequence
- ✅ Show low-confidence signal being filtered
- ✅ Demonstrate global kill switch in action
- ✅ Q&A without breaking flow

---

## 🎤 Narration Script (Memorize)

### Opening Hook
"What if your support team never missed a critical escalation, and you could trust the AI to handle it?"

### Problem Statement
"Every day, support teams handle hundreds of messages. Some are routine, but buried in the noise are critical issues that need immediate action."

### Solution Introduction
"LiveSOP monitors your channels in real-time, using AI to detect patterns that matter."

### Trust Building
"Here's where trust is built. You can see exactly why the AI made this decision, what it did, and you have full control."

### Proof Point
"Let's verify. The ticket was created automatically, with full context from the original message."

### Control Emphasis
"Here's what makes this safe for production. You have multiple layers of control."

### Vision Casting
"This is just one workflow. LiveSOP learns your team's patterns and automates the repetitive work."

### Closing
"LiveSOP: Turn support chaos into reliable operations. AI you can trust, because you're always in control."

---

## 🔧 Quick Fixes for Common Demo Issues

### Issue: "Live Feed is empty"
**Fix**: Run a test automation 5 minutes before demo

### Issue: "Confidence is too low"
**Fix**: Use stronger trigger words in your demo message

### Issue: "Jira ticket doesn't create"
**Fix**: Check JIRA_PROJECT env var, test Jira API beforehand

### Issue: "Trust Panel doesn't open"
**Fix**: Ensure inference_runs has model_config data

### Issue: "Webhook doesn't trigger"
**Fix**: Verify Slack app is installed and webhook URL is correct

---

Ready to record? Follow this checklist and you'll have a compelling, trust-building demo that converts prospects into users.
