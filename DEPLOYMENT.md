# Deploying the last30days Streamlit UI Online

This guide covers putting the simple Streamlit UI (`app.py`) online so your team can use it in a browser.

---

## Fix: "Unable to deploy" (code not connected to GitHub)

Streamlit Community Cloud only deploys from a **published** GitHub repo. If you see "The app's code is not connected to a remote GitHub repository", do one of the following.

### Option A: You have push access to the current repo

Your project is already cloned from `https://github.com/mvanhorn/last30days-skill`. If that’s your repo (or you have write access), publish your branch:

```bash
cd "/Users/katarina/Library/CloudStorage/GoogleDrive-katarina@stayoasi.com/.shortcut-targets-by-id/19RUGQKXlYdrxEOCv7aG01vkUh32uF95n/magic boxes/last30days-skill"

# Add the files needed for deployment
git add app.py requirements.txt .gitignore DEPLOYMENT.md TOOL_EXPLANATION.md
git add scripts/lib/render.py   # if you want to include your change

# Commit and push
git commit -m "Add Streamlit UI and deployment files"
git push origin main
```

Then in [share.streamlit.io](https://share.streamlit.io): **New app** → choose **mvanhorn/last30days-skill**, branch **main**, main file **app.py** → Deploy.

### Option B: You need your own repo (fork or new repo)

If you don’t have push access to `mvanhorn/last30days-skill`, use your own GitHub repo:

1. **Fork** the repo on GitHub (Fork button on github.com/mvanhorn/last30days-skill), or create a **new** empty repo under your account.
2. Add your repo as a remote and push:

```bash
cd "/Users/katarina/Library/CloudStorage/GoogleDrive-katarina@stayoasi.com/.shortcut-targets-by-id/19RUGQKXlYdrxEOCv7aG01vkUh32uF95n/magic boxes/last30days-skill"

# Add deployment files
git add app.py requirements.txt .gitignore DEPLOYMENT.md TOOL_EXPLANATION.md
git add scripts/lib/render.py   # optional
git commit -m "Add Streamlit UI and deployment files"

# Add YOUR GitHub repo (replace YOUR_USERNAME and YOUR_REPO with your values)
git remote add myorigin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push your branch so Streamlit can see it
git push -u myorigin main
```

3. In [share.streamlit.io](https://share.streamlit.io): **New app** → choose **YOUR_USERNAME/YOUR_REPO**, branch **main**, main file **app.py** → Deploy.

After the branch is pushed, Streamlit will be able to connect to the repo and deployment should succeed.

---

## 1. Run Locally First

```bash
cd /path/to/last30days-skill
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501. Enter a topic and run research to confirm everything works.

---

## 2. Deploy to Streamlit Community Cloud (Free)

Streamlit Community Cloud runs your app in the cloud and gives you a public URL.

### Steps

1. **Push your repo to GitHub**  
   Your project (including `app.py`, `scripts/`, `requirements.txt`) must be in a GitHub repo.

2. **Go to [share.streamlit.io](https://share.streamlit.io)**  
   Sign in with GitHub.

3. **New app**
   - **Repository:** `your-username/your-repo`
   - **Branch:** `main` (or your default)
   - **Main file path:** `app.py`
   - **App URL:** optional subpath, e.g. `last30days`

4. **Secrets (API keys)**  
   In the app dashboard: **Settings → Secrets**. Add:

   ```toml
   OPENAI_API_KEY = "sk-..."
   XAI_API_KEY = "xai-..."
   ```

   The app reads these and passes them into the research script so Reddit and X search work in the cloud.

5. **Deploy**  
   Click **Deploy**. First run may take a few minutes (install + cold start). Your app will be at:

   `https://your-app-name.streamlit.app`

### Notes for Streamlit Cloud

- **Timeout:** Long-running research (e.g. `--deep`) may hit Streamlit’s request timeout; prefer **Quick** or **Default** for shared use.
- **Secrets:** Never commit `.env` or real keys to the repo; use only Streamlit Secrets.
- **Python version:** You can add a `runtime.txt` with e.g. `python-3.11` if you need a specific version.

---

## 3. Alternative: Run on Your Own Server

You can run Streamlit on a VPS (e.g. AWS, DigitalOcean, a company server).

### Basic run

```bash
cd /path/to/last30days-skill
pip install -r requirements.txt
# API keys: create ~/.config/last30days/.env with OPENAI_API_KEY, XAI_API_KEY
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

- `--server.address 0.0.0.0` makes the app reachable from other machines.
- Use a process manager (systemd, supervisor) or reverse proxy (nginx) and HTTPS in production.

### Using the same .env as the CLI

If the server has `~/.config/last30days/.env` with `OPENAI_API_KEY` and `XAI_API_KEY`, the subprocess started by `app.py` will inherit the environment and the script will read that file (via its own logic). So you don’t need to set secrets again in Streamlit if that user’s `.env` is already in place.

---

## 4. Summary

| Goal | Option |
|------|--------|
| Quick share with team | Deploy to **Streamlit Community Cloud** (GitHub + Secrets). |
| Full control / private | Run **Streamlit on your own server** with `.env` or env vars. |
| Local only | `streamlit run app.py` on your machine. |

The app is a thin UI around `scripts/last30days.py`: same behavior, same config (env or Streamlit secrets), so your team uses the same “last30days” research from the browser.
