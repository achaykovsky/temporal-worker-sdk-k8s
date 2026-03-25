#!/usr/bin/env bash
# Idempotent kubectl apply for namespace temporal (K8-05). Requires postgres Secret before first run.
# Optional: ./scripts/deploy.sh --with-hpa  (or DEPLOY_CALCULATOR_HPA=1)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NS=temporal
WITH_HPA=false
if [[ "${1:-}" == "--with-hpa" ]] || [[ "${DEPLOY_CALCULATOR_HPA:-}" == "1" ]]; then
  WITH_HPA=true
fi

if ! kubectl cluster-info >/dev/null 2>&1; then
  echo "error: kubectl cannot reach a cluster. Point kubeconfig at minikube (e.g. minikube start, then kubectl config current-context)." >&2
  exit 1
fi

if ! kubectl -n "$NS" get secret postgres-credentials >/dev/null 2>&1; then
  echo "error: Secret ${NS}/postgres-credentials not found." >&2
  echo "Create credentials first, for example:" >&2
  echo "  kubectl -n ${NS} create secret generic postgres-credentials \\" >&2
  echo "    --from-literal=POSTGRES_USER=temporal \\" >&2
  echo "    --from-literal=POSTGRES_PASSWORD='<strong-password>'" >&2
  echo "See k8s/postgres-secret.yaml.example (do not commit real passwords)." >&2
  exit 1
fi

kubectl apply -f "$ROOT/k8s/namespace.yaml"
kubectl apply -f "$ROOT/k8s/temporal-dynamic-config.yaml"
kubectl apply -f "$ROOT/k8s/postgres.yaml"
kubectl apply -f "$ROOT/k8s/temporal.yaml"
kubectl apply -f "$ROOT/k8s/calculator-worker-configmap.yaml"
kubectl apply -f "$ROOT/k8s/workers.yaml"

if [[ "${WITH_HPA}" == "true" ]]; then
  kubectl apply -f "$ROOT/k8s/calculator-worker-add-hpa.yaml"
  echo "ok: HPA applied (calculator-worker-add). Requires metrics-server — see README Autoscaling (bonus)."
fi

echo "ok: manifests applied to namespace ${NS}. kubectl -n ${NS} get pods"
