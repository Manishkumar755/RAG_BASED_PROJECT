# ☸️ Kubernetes Deployment Guide for RAG Platform

This directory contains production-grade Kubernetes manifests for deploying the Innefu Labs RAG Platform (FastAPI Backend + React Frontend + Ingress + HPA Autoscaling).

---

## 📁 Manifest Architecture

| File | Resource | Description |
|---|---|---|
| `namespace.yaml` | `Namespace` | Creates isolated `rag-system` namespace |
| `configmap.yaml` | `ConfigMap` | Stores environment configuration for backend and frontend |
| `backend-deployment.yaml` | `Deployment` & `Service` | 2-replica FastAPI RAG API with health probes & ClusterIP |
| `frontend-deployment.yaml` | `Deployment` & `Service` | 2-replica React Nginx UI with LoadBalancer & NodePort (30080) |
| `ingress.yaml` | `Ingress` | Nginx Ingress routing `/api` to backend and `/` to frontend |
| `hpa.yaml` | `HorizontalPodAutoscaler` | Auto-scales pods from 2 to 10 based on CPU & Memory usage |
| `kustomization.yaml` | `Kustomization` | Bundles all manifests for 1-command deployment |

---

## 🚀 Quick Deployment Options

### Option 1: One-Command Kustomize Deploy

```bash
kubectl apply -k k8s/
```

Verify the deployment:
```bash
kubectl get pods -n rag-system
kubectl get svc -n rag-system
```

---

### Option 2: Step-by-Step Manifest Apply

```bash
# 1. Create Namespace & ConfigMap
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml

# 2. Deploy Backend & Frontend
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml

# 3. Apply Ingress & Autoscaler
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml
```

---

## 🐳 Building & Loading Local Images (Minikube / Kind)

Before deploying to local clusters, build and tag the container images:

### Using Minikube:
```bash
# Point your shell to minikube's Docker daemon
eval $(minikube docker-env)

# Build images directly into minikube
docker build -t rag-backend:latest .
docker build -t rag-frontend:latest ./frontend
```

### Using Kind:
```bash
# Build locally
docker build -t rag-backend:latest .
docker build -t rag-frontend:latest ./frontend

# Load into Kind cluster
kind load docker-image rag-backend:latest
kind load docker-image rag-frontend:latest
```

---

## 🌐 Accessing the Application

### Via NodePort (Port 30080):
- **Frontend UI**: `http://<node-ip>:30080` (or `http://localhost:30080` on Docker Desktop)

### Via Kubectl Port-Forward:
```bash
# Forward React Frontend
kubectl port-forward svc/rag-frontend 3000:80 -n rag-system

# Forward FastAPI Backend
kubectl port-forward svc/rag-backend 8000:8000 -n rag-system
```
- Open UI: `http://localhost:3000`
- Open API Docs: `http://localhost:8000/docs`

---

## 🧹 Teardown / Cleanup

To delete all resources and clean up:
```bash
kubectl delete -k k8s/
```
Or delete the entire namespace:
```bash
kubectl delete namespace rag-system
```
