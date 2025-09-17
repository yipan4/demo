# Live Demo (Power Automate): Push → GitHub Actions → Teams

This guide uses **Power Automate** as a webhook bridge to post messages into **Microsoft Teams** when your GitHub Action fails or succeeds.

## Overview
- First push: pipeline fails (missing `requests`) → Power Automate posts a **red** alert to Teams.
- Second push: after fix → Power Automate posts a **green** success message.

---

## 1) Create the Power Automate Flow
1. Go to **https://make.powerautomate.com** → **Create** → **Instant cloud flow** → **Skip** → Add trigger **When an HTTP request is received**.
2. In the trigger, click **Use sample payload to generate schema** and paste:
   ```json
   {
     "title": "CI Failure: org/repo (main)",
     "text": "Build failed.",
     "color": "D93F0B",
     "run_url": "https://github.com/org/repo/actions/runs/123",
     "repo": "org/repo",
     "branch": "main",
     "status": "failure"
   }
   ```
   This generates a schema similar to:
   ```json
   {
     "type": "object",
     "properties": {
       "title": {"type": "string"},
       "text": {"type": "string"},
       "color": {"type": "string"},
       "run_url": {"type": "string"},
       "repo": {"type": "string"},
       "branch": {"type": "string"},
       "status": {"type": "string"}
     },
     "required": ["title", "text", "status"]
   }
   ```
3. **Add a new step**: **Microsoft Teams → Post message in a chat or channel**.
   - **Post as**: Flow bot
   - **Post in**: Channel
   - **Team**: *(choose your team)*
   - **Channel**: *(choose your channel)*
   - **Message** (click in the box and compose using dynamic content):
     ```
     🧪 **@{triggerBody()?['title']}**

     @{triggerBody()?['text']}

     • Repo: @{triggerBody()?['repo']}  
     • Branch: @{triggerBody()?['branch']}  
     • Run: @{triggerBody()?['run_url']}
     ```
4. (Optional) Add a **Condition** on `status` to decorate messages:
   - If `status == failure` → prepend "❌"; else → "✅".
5. **Add a final step**: **Response**
   - **Status Code**: `200`
   - **Body**: `{ "ok": true }`
6. **Save** the flow, then **copy** the **HTTP POST URL** shown on the trigger card.

---

## 2) Add the Flow URL to GitHub Secrets
In your GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**
- **Name**: `PA_FLOW_URL`
- **Value**: *(paste the HTTP POST URL from the Flow trigger)*

---

## 3) First Push (Fail → Teams alert)
From the repository root that contains this folder structure:
```bash
git init && git add . && git commit -m "demo: initial"
git branch -M main
git remote add origin https://github.com/<org-or-user>/<repo>.git
git push -u origin main
```
- The **CI** workflow runs and the **Run app** step fails (missing `requests`).
- The **Notify Power Automate** step still executes and POSTs to your Flow.
- Power Automate posts the message to your Teams channel.

---

## 4) Second Push (Fix → Teams success)
Apply the suggested fix by replacing the file contents of `app/requirements.txt` with:
```diff
-flask==0.12
+flask==2.3.3
+requests==2.31.0
```
Then:
```bash
git add app/requirements.txt
git commit -m "fix: add requests and upgrade flask"
git push
```
- The run passes and Power Automate posts a green success message.

---

## 5) Notes & Tips
- The job uses `continue-on-error: true` on the run step so the notification step can post to Flow regardless of outcome; we then enforce failure to keep the run status accurate.
- You can customize the Flow message or add **Adaptive Cards** later.
- The Flow URL is secret—rotate or delete it after the demo.
- If posting fails, check the **Run URL** in the Teams message to debug the pipeline quickly.

---

## Files in this demo
- `.github/workflows/ci.yml` – CI job that calls Power Automate
- `app/app.py` – minimal script importing `requests`
- `app/requirements.txt` – outdated/missing dependency (forces failure)
- `app/requirements_fixed.txt` – "AI suggested" fix
- `logs/mock_jenkins_failure.log` – optional talking point
- `ai/notes.md` – optional talking points
