# LiveSOP AI - Phase C: Canonical Demo Script
# Signal → Decision → Action → Explanation → Control

## Demo Narrative: "From Chaos to Confidence"

**Hook**: "What if your support team never missed an escalation, and you could trust the AI to handle it?"

**Duration**: 3-5 minutes

**Target Audience**: CS Leaders, Support Ops, Technical Decision Makers

---

## Pre-Demo Setup Checklist

### Backend Preparation
- [ ] Ensure at least one workflow with 2-3 nodes exists
- [ ] Enable Auto-Run for ONE node (e.g., "Create Jira Ticket")
- [ ] Verify global Auto-Pilot is enabled
- [ ] Clear old test data from Live Feed (optional for clean demo)

### Frontend Preparation
- [ ] Log in to dashboard
- [ ] Have Slack workspace open in another tab
- [ ] Have Jira project open in another tab
- [ ] Prepare demo message: "Critical payment gateway timeout - customer can't checkout"

### Recording Setup
- [ ] Screen recording software ready (OBS, Loom, or QuickTime)
- [ ] Microphone tested
- [ ] Browser zoom at 100%
- [ ] Hide bookmarks bar for clean UI

---

## Act 1: The Problem (30 seconds)

### Scene 1: Slack Chaos
**Screen**: Slack channel (#support-tier3)

**Narration**:
> "Every day, your support team handles hundreds of messages. Some are routine. 
> But buried in the noise are critical escalations that need immediate action."

**Action**:
1. Show Slack channel with multiple messages
2. Scroll through to show volume
3. Highlight the problem: "How do you catch every critical issue?"

**Screenshot**: `01_slack_chaos.png`
- Capture: Busy Slack channel with mixed messages

---

## Act 2: The Signal (45 seconds)

### Scene 2: The Trigger Event
**Screen**: Split view - Slack + LiveSOP Dashboard

**Narration**:
> "Watch what happens when a critical issue arrives. LiveSOP is monitoring 
> your channels in real-time, using AI to detect patterns that matter."

**Action**:
1. Send message in Slack:
   ```
   @channel Critical issue - payment gateway timing out. 
   Multiple customers reporting they can't complete checkout. 
   Error code: GATEWAY_TIMEOUT_500
   ```

2. **Pause for 2-3 seconds** (let webhook process)

3. Switch to LiveSOP Dashboard

**Screenshot**: `02_slack_trigger.png`
- Capture: The critical message in Slack

---

## Act 3: The Decision (60 seconds)

### Scene 3: Live Feed - Transparency in Action
**Screen**: LiveSOP Dashboard - Live Feed view

**Narration**:
> "Within seconds, LiveSOP's AI analyzed the message. It identified this as 
> a Tier-3 escalation with 95% confidence. Here's the transparency you need."

**Action**:
1. Point to Live Feed - new entry appears
2. Highlight key elements:
   - **Time**: "Just now"
   - **Channel**: "#support-tier3"
   - **Customer**: "alice.smith"
   - **Confidence**: "95%" (green bar)
   - **Action**: "Create Jira Ticket"
   - **Status**: "Completed" (green checkmark)

3. **Click on the row** to open Trust Panel

**Screenshot**: `03_live_feed_entry.png`
- Capture: Live Feed with the new escalation highlighted

---

### Scene 4: Trust Panel - The "Why"
**Screen**: Trust Panel (slides in from right)

**Narration**:
> "This is where trust is built. You can see exactly why the AI made this decision, 
> what it did, and you have full control."

**Action**:
1. Walk through each section of Trust Panel:

   **Confidence Score**:
   - Point to 95% indicator
   - "The AI is highly certain this needs attention"

   **Rationale**:
   - Read aloud: "Detected payment system failure with customer impact. 
     Keywords: 'critical', 'timeout', 'can't checkout' match Tier-3 escalation pattern."
   - "Clear reasoning, not a black box"

   **Source Context**:
   - Show original message
   - Show channel: #support-tier3
   - Click "View in Slack" link (opens Slack to exact message)
   - "Full traceability back to the source"

   **Action Taken**:
   - "Created Jira Ticket: PROJ-1234"
   - Click link to show actual Jira ticket
   - "Automation happened, but you can verify"

   **Auto-Pilot Toggle**:
   - Point to toggle switch
   - "You're in control. Disable this pattern anytime."

2. Close Trust Panel

**Screenshots**:
- `04_trust_panel_confidence.png` - Confidence section
- `05_trust_panel_rationale.png` - Reasoning section
- `06_trust_panel_source.png` - Source context
- `07_trust_panel_action.png` - Action taken

---

## Act 4: The Proof (30 seconds)

### Scene 5: Verification - It Actually Worked
**Screen**: Jira project board

**Narration**:
> "Let's verify. The ticket was created automatically, with full context 
> from the original Slack message."

**Action**:
1. Switch to Jira
2. Show newly created ticket:
   - **Title**: "[Auto] Critical Payment Gateway Issue"
   - **Description**: Contains original Slack message + reasoning
   - **Priority**: High
   - **Assignee**: (your team's default)
   - **Created**: "Just now"

3. Point out: "Your team can start working immediately. No context lost."

**Screenshot**: `08_jira_ticket_created.png`
- Capture: The auto-created Jira ticket

---

## Act 5: The Control (45 seconds)

### Scene 6: Safety Controls - You're the Boss
**Screen**: LiveSOP Dashboard - Settings (or demonstrate via Trust Panel)

**Narration**:
> "Here's what makes this safe for production. You have multiple layers of control."

**Action**:
1. Show **Hero Stats** at top of dashboard:
   - "Escalations Detected: 1"
   - "Auto-Resolutions: 1"
   - "Hours Saved: ~0.25h"
   - "Measurable impact, transparent metrics"

2. Demonstrate **Global Kill Switch** (optional - can just explain):
   - "If you ever need to pause everything, one click stops all automations"
   - "Your safety net is always there"

3. Demonstrate **Per-Node Control** via Trust Panel:
   - "Each workflow step can be enabled or disabled independently"
   - "Start with one automation, expand as you build trust"

4. Show **Confidence Threshold**:
   - "Only high-confidence signals (90%+) trigger actions"
   - "Low-confidence signals are logged but don't execute"
   - "You see everything, but only trust acts on certainty"

**Screenshots**:
- `09_hero_stats.png` - Dashboard metrics
- `10_safety_controls.png` - Settings or Trust Panel toggle

---

## Act 6: The Vision (30 seconds)

### Scene 7: The Bigger Picture
**Screen**: Dashboard - Workflow view (Cards or Flowchart)

**Narration**:
> "This is just one workflow. LiveSOP learns your team's patterns and automates 
> the repetitive work, so your team can focus on what matters: your customers."

**Action**:
1. Show the workflow visualization
2. Point to multiple nodes:
   - "Each step is a pattern LiveSOP discovered"
   - "Each can be automated when you're ready"

3. End on the value proposition:
   - "From signal to action in seconds"
   - "Full transparency and control"
   - "Your team's expertise, amplified by AI"

**Screenshot**: `11_workflow_overview.png`
- Capture: Full workflow visualization

---

## Closing (15 seconds)

**Screen**: Dashboard overview

**Narration**:
> "LiveSOP: Turn support chaos into reliable operations. 
> AI you can trust, because you're always in control."

**Call to Action**:
- "Start your free trial at livesopai.com"
- "Questions? Book a demo with our team"

---

## Recording Outline for Screen Capture

### Full Demo (3-5 min)
```
00:00 - 00:30  | Slack chaos (problem setup)
00:30 - 01:15  | Send trigger message + show Live Feed
01:15 - 02:45  | Trust Panel walkthrough (the "why")
02:45 - 03:15  | Jira verification (the proof)
03:15 - 04:00  | Safety controls (the control)
04:00 - 04:30  | Workflow overview (the vision)
04:30 - 04:45  | Closing + CTA
```

### Short Demo (90 sec)
```
00:00 - 00:15  | Problem: "Support teams miss critical issues"
00:15 - 00:30  | Trigger: Send Slack message
00:30 - 01:00  | Solution: Show Live Feed + Trust Panel
01:00 - 01:15  | Proof: Jira ticket created
01:15 - 01:30  | Control: "You're always in charge"
```

### Micro Demo (30 sec - for social)
```
00:00 - 00:05  | Hook: "Watch this"
00:05 - 00:10  | Slack message sent
00:10 - 00:20  | Live Feed + "95% confidence, auto-created ticket"
00:20 - 00:25  | Jira ticket shown
00:25 - 00:30  | "AI you can trust. Try LiveSOP."
```

---

## Screenshot Checklist

Required screenshots for marketing/docs:

- [ ] `01_slack_chaos.png` - Busy support channel
- [ ] `02_slack_trigger.png` - Critical message sent
- [ ] `03_live_feed_entry.png` - New escalation in Live Feed
- [ ] `04_trust_panel_confidence.png` - 95% confidence indicator
- [ ] `05_trust_panel_rationale.png` - AI reasoning
- [ ] `06_trust_panel_source.png` - Source context + link
- [ ] `07_trust_panel_action.png` - Action taken + result
- [ ] `08_jira_ticket_created.png` - Auto-created ticket
- [ ] `09_hero_stats.png` - Dashboard metrics
- [ ] `10_safety_controls.png` - Control toggles
- [ ] `11_workflow_overview.png` - Full workflow viz

---

## Key Talking Points (Memorize These)

### Trust Builders
1. **"95% confidence"** - Not guessing, high certainty
2. **"Here's why"** - Clear reasoning, not a black box
3. **"View in Slack"** - Full traceability
4. **"You're in control"** - Kill switch + per-node toggles
5. **"It actually worked"** - Show the Jira ticket

### Objection Handlers
- **"What if it makes a mistake?"**
  → "Only 90%+ confidence executes. You can disable any pattern instantly."

- **"How do I know why it did that?"**
  → "Every decision shows full reasoning and source context."

- **"What if I want to turn it off?"**
  → "Global kill switch stops everything. Per-node control for fine-tuning."

- **"Is my data safe?"**
  → "Enterprise-grade security. Your data never trains our models."

---

## Demo Environment Setup Commands

### Enable Auto-Run for Demo Node
```bash
# Via Supabase SQL Editor
UPDATE workflow_nodes 
SET auto_run_enabled = true 
WHERE label ILIKE '%jira%' OR label ILIKE '%ticket%'
LIMIT 1;
```

### Clear Old Test Data (Optional)
```bash
# Only if you want a clean Live Feed for demo
DELETE FROM inference_runs 
WHERE team_id = 'YOUR_TEAM_ID' 
AND started_at < NOW() - INTERVAL '1 hour';
```

### Verify Setup
```bash
# Check global Auto-Pilot is enabled
SELECT auto_pilot_enabled FROM teams WHERE id = 'YOUR_TEAM_ID';

# Check which nodes are enabled
SELECT step_id, label, auto_run_enabled 
FROM workflow_nodes 
WHERE workflow_id IN (
  SELECT id FROM workflows WHERE team_id = 'YOUR_TEAM_ID' AND is_active = true
);
```

---

## Post-Demo Follow-Up

### For Prospects
- Send recording link
- Share screenshot deck
- Offer personalized demo with their data
- Provide trial signup link

### For Investors
- Emphasize metrics: "X escalations, Y auto-resolutions, Z hours saved"
- Show audit trail: "Full compliance, every decision logged"
- Highlight safety: "Production-ready controls from day one"

### For Press/Media
- Focus on trust narrative: "AI you can verify"
- Emphasize human-in-the-loop: "Augments teams, doesn't replace"
- Provide customer testimonial (when available)

---

## Troubleshooting

### If Live Feed doesn't update:
- Check backend logs in Render
- Verify webhook is configured in Slack
- Ensure global Auto-Pilot is enabled
- Check confidence threshold (must be >= 0.9)

### If Jira ticket doesn't create:
- Verify JIRA_PROJECT env var is set
- Check Jira API credentials
- Look for error in backend logs
- Ensure node has auto_run_enabled = true

### If Trust Panel doesn't show data:
- Verify inference_runs has the entry
- Check model_config JSON has all fields
- Ensure signal was linked via inference_run_signals

---

## Success Metrics

After demo, you should be able to show:

✅ **Speed**: Signal to action in < 5 seconds
✅ **Accuracy**: 90%+ confidence on critical escalations
✅ **Transparency**: Full reasoning + source for every decision
✅ **Control**: Multiple safety layers demonstrated
✅ **Impact**: Measurable time savings (even with 1 automation)

---

## Next: Phase D (Future)

After this demo is polished:
- User onboarding flow
- Multi-workflow support
- Advanced analytics dashboard
- Stripe billing integration
- Customer testimonials

But for now: **Nail this demo. Make it unforgettable.**
