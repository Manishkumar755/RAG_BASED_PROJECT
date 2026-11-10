# 🛡️ Innefu Labs Enterprise RAG Platform

> Full-Stack **Retrieval-Augmented Generation (RAG)** System featuring a modern **React Frontend**, a high-performance **FastAPI Backend**, local **Dense Vector + BM25 Hybrid Search**, **Docker Containerization**, and production-grade **Kubernetes Orchestration**.

---

## 🏛️ System Architecture Overview

```
                      ┌──────────────────────────────────────┐
                      │    Client Browser / User             │
                      └──────────────────┬───────────────────┘
                                         │ HTTP (Port 3000 / 80)
                                         ▼
                 ┌─────────────────────────────────────────────────┐
                 │       React 18 Frontend (Vite + Nginx)          │
                 │  - Interactive AI Chat & Provenance Citations   │
                 │  - Search Mode Switcher (Hybrid / Vector / BM25)│
                 │  - Document Explorer & Telemetry Panel          │
                 └───────────────────────┬─────────────────────────┘
                                         │ Reverse Proxy /api/ (Port 8000)
                                         ▼
                 ┌─────────────────────────────────────────────────┐
                 │          FastAPI REST API Server                │
                 │  - /chat, /search, /documents, /health          │
                 │  - Liveness & Readiness Probes                  │
                 └───────────────────────┬─────────────────────────┘
                                         │ Internal Orchestration
                                         ▼
         ┌─────────────────────────────────────────────────────────────────┐
         │                    Core RAG Engine Layer                        │
         │  ┌────────────────────────┐    ┌─────────────────────────────┐  │
         │  │ 🛡️ Safety Guardrails    │    │ 🔍 Hybrid Search Engine      │  │
         │  │ (Anti-Injection/Refuse)│    │ (Dense Cosine + BM25 RRF)   │  │
         │  └────────────────────────┘    └──────────────┬──────────────┘  │
         │                                               │                 │
         │                ┌──────────────────────────────┴──────────────┐  │
         │                ▼                                             ▼  │
         │  ┌───────────────────────────┐         ┌─────────────────────┐  │
         │  │ Local Dense Embedder      │         │ BM25 Okapi Index    │  │
         │  │ (384-dim Normalization)   │         │ (Lexical Inverted)  │  │
         │  └─────────────┬─────────────┘         └──────────┬──────────┘  │
         │                ▼                                  ▼             │
         │  ┌───────────────────────────────────────────────────────────┐  │
         │  │ Vector Store & Structured Innefu Knowledge Base (.json)   │  │
         │  └───────────────────────────────────────────────────────────┘  │
         └─────────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
RAG_BASED_PROJECT/
├── frontend/                         # Modern React 18 Web UI
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx           # Brand header & live status indicator
│   │   │   ├── Sidebar.jsx          # Mode toggle, Top-K slider & presets
│   │   │   ├── ChatView.jsx         # Chat stream, citations & chunk viewer
│   │   │   ├── DocumentExplorer.jsx # Knowledge document grid & search
│   │   │   └── SearchTestView.jsx   # Raw retrieval score inspection
│   │   ├── api.js                   # Backend API client
│   │   ├── index.css                # Enterprise cyber design system
│   │   ├── App.jsx                  # Main application state
│   │   └── main.jsx                 # Entrypoint
│   ├── nginx.conf                   # Nginx reverse proxy & SPA router
│   ├── Dockerfile                   # Multi-stage Node + Nginx build
│   └── package.json                 # React 18 + Vite dependencies
├── rag/                             # Core Python RAG Engine
│   ├── embeddings.py                # 384-dim normalized vector embeddings
│   ├── bm25.py                      # Lexical BM25 Okapi keyword search
│   ├── vector_store.py              # Cosine similarity vector index
│   ├── hybrid_search.py             # Reciprocal Rank Fusion (RRF)
│   ├── guardrails.py                # Safety gating & injection detector
│   └── engine.py                    # Answer synthesis & coordinator
├── data/
│   ├── knowledge_base/              # Source Markdown documents
│   └── vector_store/                # Pre-indexed vector points (JSON)
├── k8s/                             # Production Kubernetes Manifests
│   ├── namespace.yaml               # Isolated 'rag-system' namespace
│   ├── configmap.yaml               # Runtime configurations
│   ├── backend-deployment.yaml      # 2-replica FastAPI Deployment & Service
│   ├── frontend-deployment.yaml     # 2-replica React Deployment & Service
│   ├── ingress.yaml                 # Nginx Ingress Controller routing
│   ├── hpa.yaml                     # Horizontal Pod Autoscalers (CPU/Mem)
│   ├── kustomization.yaml           # 1-command Kustomize bundle
│   └── README.md                    # Kubernetes operations guide
├── api.py                           # FastAPI REST API server
├── app.py                           # Streamlit alternative interface
├── evaluate.py                      # 30-Question benchmark evaluator
├── Dockerfile                       # Python 3.11 Backend Docker image
├── docker-compose.yml               # Multi-container local orchestration
├── deploy-docker.bat / .sh          # One-click Docker runner
├── deploy-k8s.bat / .sh             # One-click Kubernetes deployer
├── requirements.txt                 # Backend dependencies
└── README.md                        # Documentation
```

---

## 🚀 Quickstart: Docker Compose (Recommended)

Run the complete fullstack application (FastAPI backend + React frontend) with a single command:

### On Windows:
```cmd
deploy-docker.bat
```
Or directly with Docker Compose:
```bash
docker-compose up --build -d
```

### URLs after launch:
- **React Frontend**: [http://localhost:3000](http://localhost:3000)
- **FastAPI Backend**: [http://localhost:8000](http://localhost:8000)
- **Interactive OpenAPI/Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Backend Health Probe**: [http://localhost:8000/health](http://localhost:8000/health)

---

## ☸️ Production Deployment: Kubernetes

The `k8s/` directory contains complete, production-ready manifests configured with:
- **High Availability**: 2 replicas for backend and frontend with zero-downtime rolling updates.
- **Probes**: Configured Liveness (`/health`, `/healthz`) and Readiness probes.
- **Autoscaling**: Horizontal Pod Autoscaler (HPA) scaling pods up to 10 instances on traffic spikes.
- **Ingress**: Reverse proxy rules routing `/api` traffic to backend pods and `/` traffic to frontend pods.

### 1-Command Deploy:
```bash
kubectl apply -k k8s/
```

### Accessing via Port-Forward:
```bash
# Frontend
kubectl port-forward svc/rag-frontend 3000:80 -n rag-system

# Backend
kubectl port-forward svc/rag-backend 8000:8000 -n rag-system
```

Detailed instructions for Minikube, Kind, AWS EKS, and GCP GKE are documented in [`k8s/README.md`](file:///c:/Users/manis/Downloads/RAG_BASED_PROJECT/k8s/README.md).

---

## 💻 Local Development (Without Containers)

### 1. Run the FastAPI Backend:
```bash
# Install Python requirements
pip install -r requirements.txt

# Start FastAPI server
python api.py
```
Backend runs at `http://localhost:8000`.

### 2. Run the React Frontend:
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at `http://localhost:3000` with hot module replacement (HMR).

---

## 🧪 Testing & Evaluation

### Run Pytest Suite:
```bash
python -m pytest tests/test_rag.py -v
```
All 16 unit and integration tests verify:
- Vector generation & cosine similarity calculations
- BM25 tokenization and score rank ordering
- Hybrid Reciprocal Rank Fusion (RRF)
- Guardrail injection detection and safety refusals
- Full end-to-end RAG synthesis & citations

### Run Benchmark Evaluation:
```bash
python evaluate.py
```
Evaluates the RAG system against 30 benchmark questions:
- **MRR@3 (Mean Reciprocal Rank)**: `0.9800`
- **Recall@3**: `100.0%`
- **Citation Accuracy**: `100.0%`
- **Safety / Refusal Accuracy**: `100.0%`
