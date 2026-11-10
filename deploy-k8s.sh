#!/usr/bin/env bash
set -e

echo "========================================================"
echo "Deploying Innefu Labs RAG Platform to Kubernetes..."
echo "========================================================"

echo "Applying manifests via Kustomize..."
kubectl apply -k k8s/

echo ""
echo "Checking rollout status..."
kubectl rollout status deployment/rag-backend -n rag-system
kubectl rollout status deployment/rag-frontend -n rag-system

echo ""
echo "Active Pods and Services in 'rag-system':"
kubectl get pods,svc -n rag-system

echo ""
echo "To access the frontend locally:"
echo "  kubectl port-forward svc/rag-frontend 3000:80 -n rag-system"
echo "To access the FastAPI docs:"
echo "  kubectl port-forward svc/rag-backend 8000:8000 -n rag-system"
