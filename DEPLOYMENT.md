# Deploying the last30days Streamlit UI Online

This guide covers putting the simple Streamlit UI (`app.py`) online so your team can use it in a browser.

---

## Where to set login (email + password) and make the app public

### Where to edit secrets (login + API keys)

1. Open **[share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub.
2. Click your app (e.g. **30d-research** or whatever you named it).
3. In the app menu, click **⚙️ Settings** (or **Manage app** → **Settings**).
4. In the left sidebar, click **Secrets**.
5. In the **Secrets** text box, add your keys. Example so that **only @stayoasi.com emails** can log in with **one shared password**:

   ```toml
   AUTH_PASSWORD = "your_actual_password_here"
   AUTH_EMAIL_DOMAIN = "stayoasi.com"
   OPENAI_API_KEY = "sk-..."
   XAI_API_KEY = "xai-..."
   ```

   Replace `your_actual_password_here` with the password you’ll give your team. Replace the API key values if you use Reddit/X. Save (e.g. **Save** or **Update**). The app will reload and from then on visitors will see a login screen: they must enter an email ending in `@stayoasi.com` and that password.

### How to make the app public (public URL, still protected by login)

1. **Make the GitHub repo public**  
   On GitHub: open your repo (e.g. **Oasi-LLC/30d-research**) → **Settings** → scroll to **Danger Zone** → **Change repository visibility** → **Make public**.  
   Then your app on Streamlit Community Cloud is reachable by anyone with the link (e.g. `https://your-app-name.streamlit.app`). They still cannot use the app until they sign in with an @stayoasi.com email and the shared password.

2. **If the repo is already public**  
   You don’t need to change anything. The app is already public; only people who pass the login (email domain + password) can use it.

You don’t edit login or API keys in the code or in GitHub for this — only in **Streamlit → your app → Settings → Secrets** as above.

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

5. **Protect with login (optional)**  
   You can deploy the app **publicly** (public URL) and still restrict access with a login. In **Settings → Secrets**, add one of the following.

   **Option A – Single shared password**  
   Anyone who knows this password can sign in:

   ```toml
   AUTH_PASSWORD = "your_shared_password_here"
   ```

   **Option B – Only @stayoasi.com emails + one shared password**  
   Only people with an email ending in `@stayoasi.com` can sign in, and they all use the same password. In **Settings → Secrets** add:

   ```toml
   AUTH_PASSWORD = "your_shared_password_here"
   AUTH_EMAIL_DOMAIN = "stayoasi.com"
   ```

   Replace `your_shared_password_here` with the actual password you’ll give your team. Users will see a form asking for their email and that password; only emails like `katarina@stayoasi.com` will be accepted.

   **Option C – Multiple users (username/email + password)**  
   Each user has their own login. Add a secret `AUTH_CREDENTIALS_JSON` with a JSON string (one line, no line breaks). Example for two users:

   ```toml
   AUTH_CREDENTIALS_JSON = "{\"usernames\":{\"alice\":{\"name\":\"Alice\",\"email\":\"alice@example.com\",\"password\":\"plain_password_or_bcrypt_hash\"},\"bob\":{\"name\":\"Bob\",\"email\":\"bob@example.com\",\"password\":\"another_password\"}}}"
   ```

   - Passwords can be **plain text**; the app hashes them with bcrypt. For extra security you can pre-hash and store bcrypt hashes.
   - Optional: set `AUTH_COOKIE_KEY` to a long random string so session cookies are signed (e.g. `openssl rand -hex 32`).

   If none of these auth secrets are set, the app is **open** (no login), which is fine for local use.

6. **Deploy**  
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
| Public URL but restricted access | Set **AUTH_PASSWORD** or **AUTH_CREDENTIALS_JSON** in Secrets → login required. |
| Full control / private | Run **Streamlit on your own server** with `.env` or env vars. |
| Local only | `streamlit run app.py` on your machine (no secrets → no login). |

The app is a thin UI around `scripts/last30days.py`: same behavior, same config (env or Streamlit secrets), so your team uses the same “last30days” research from the browser.
