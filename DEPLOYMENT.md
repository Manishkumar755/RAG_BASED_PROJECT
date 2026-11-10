# 🚀 Complete Deployment Guide: GitHub $\to$ Render (FastAPI) $\to$ Vercel (React)

This guide walks you through deploying your full-stack RAG platform step-by-step:
1. **GitHub**: Pushing the codebase.
2. **Render**: Deploying the FastAPI + RAG Backend.
3. **Vercel**: Deploying the React Frontend.
4. **CORS**: Ensuring seamless browser-to-backend communication.

---

## 1️⃣ Step 1: Push Code to GitHub

### 1. Create a New Repository on GitHub
1. Go to [https://github.com/new](https://github.com/new).
2. Repository name: e.g. `rag-platform` (or `RAG_BASED_PROJECT`).
3. Set to **Public** or **Private**.
4. **Do NOT** initialize with a README, .gitignore, or license (we already have them).
5. Click **Create repository**.
6. Copy your repository HTTPS URL (e.g., `https://github.com/Manishkumar755/rag-platform.git`).

### 2. Push to GitHub
Run the interactive helper script:
```cmd
push-to-github.bat
```
*Or execute manually in your terminal:*
```bash
git remote add origin https://github.com/Manishkumar755/rag-platform.git
git branch -M main
git push -u origin main
```

---

## 2️⃣ Step 2: Deploy FastAPI Backend on Render

Render hosts the Python FastAPI server and runs the RAG retrieval engine.

### Method A: 1-Click Render Blueprint (Easiest)
1. Go to [https://dashboard.render.com/blueprints](https://dashboard.render.com/blueprints).
2. Click **New Blueprint Instance**.
3. Select your GitHub repository (`rag-platform`).
4. Render will automatically detect [`render.yaml`](file:///c:/Users/manis/Downloads/RAG_BASED_PROJECT/render.yaml) and configure:
   - **Service Name**: `innefu-rag-backend`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`
   - **Health Probe**: `/health`
5. Click **Apply**.
6. Once deployed, note down your Render service URL:
   `https://innefu-rag-backend.onrender.com`

---

### Method B: Manual Web Service Setup on Render
1. Go to [https://dashboard.render.com](https://dashboard.render.com) $\to$ **New +** $\to$ **Web Service**.
2. Connect your GitHub repository.
3. Configure the following settings:
   - **Name**: `innefu-rag-backend`
   - **Region**: Oregon (US West) or closest to you
   - **Branch**: `main`
   - **Root Directory**: *(leave blank)*
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
4. Under **Environment Variables**, add:
   | Key | Value | Description |
   |---|---|---|
   | `PYTHON_VERSION` | `3.11.9` | Ensures modern Python runtime |
   | `CORS_ORIGINS` | `*` | Permits cross-origin requests |
5. Under **Advanced**, set **Health Check Path** to `/health`.
6. Click **Create Web Service**.
7. Wait ~2 minutes for the build to finish. Test the health probe in your browser:
   `https://<your-render-name>.onrender.com/health`

---

## 3️⃣ Step 3: Deploy React Frontend on Vercel

### 1. Import Repository into Vercel
1. Go to [https://vercel.com/new](https://vercel.com/new).
2. Authorize GitHub and find your `rag-platform` repository.
3. Click **Import**.

### 2. Configure Project Settings
- **Project Name**: `rag-frontend` (or your choice)
- **Framework Preset**: `Vite`
- **Root Directory**: Click *Edit* and select **`frontend`** (or leave `./` since root [`vercel.json`](file:///c:/Users/manis/Downloads/RAG_BASED_PROJECT/vercel.json) is pre-configured).
- **Build and Output Settings**:
  - Build Command: `npm run build`
  - Output Directory: `dist`
  - Install Command: `npm install`

### 3. Set the Backend API Environment Variable (Crucial)
Expand **Environment Variables** and add:
- **Key**: `VITE_API_URL`
- **Value**: `https://<your-render-name>.onrender.com` *(your live Render backend URL from Step 2, no trailing slash)*

### 4. Deploy!
1. Click **Deploy**.
2. Within 60 seconds, Vercel will build and assign you a live domain:
   `https://rag-frontend-xxx.vercel.app`

---

## 4️⃣ Step 4: Verify CORS & End-to-End Operation

### Why CORS Works Out-of-the-Box:
In [`api.py`](file:///c:/Users/manis/Downloads/RAG_BASED_PROJECT/api.py), we configured FastAPI's `CORSMiddleware` with:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",  # Permits all Vercel domains and previews
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
1. **Any Vercel domain** (`https://*.vercel.app`) is automatically matched by the regex and permitted.
2. **Custom domains** can be supplied anytime in Render's environment settings under `CORS_ORIGINS` (comma-separated, e.g. `https://mycustomdomain.com,https://rag-frontend.vercel.app`).
3. **Local development** (`http://localhost:3000`) works with zero friction.

### Live Verification Checklist:
1. Open your Vercel URL: `https://rag-frontend-xxx.vercel.app`.
2. Notice the top-right indicator: it will show a glowing green **"FastAPI Online"** badge once connected to Render.
3. Click one of the preset questions (e.g. *"What is Sarvagata AI and how is it positioned?"*).
4. Verify that:
   - Grounded response appears.
   - Citations with official URLs are clickable.
   - Retrieved chunks drawer expands and shows ranking scores.
