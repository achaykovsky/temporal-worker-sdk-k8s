# Idempotent kubectl apply for namespace temporal (K8-05). Requires postgres Secret before first run.
param(
    [switch]$ApplyHpa
)

$Root = Split-Path -Parent $PSScriptRoot
$Ns = 'temporal'

kubectl cluster-info *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host 'error: kubectl cannot reach a cluster. Point kubeconfig at minikube (e.g. minikube start).' -ForegroundColor Red
    exit 1
}

kubectl -n $Ns get secret postgres-credentials *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host 'error: Secret temporal/postgres-credentials not found.' -ForegroundColor Red
    Write-Host @'
Create credentials first, for example:
  kubectl -n temporal create secret generic postgres-credentials `
    --from-literal=POSTGRES_USER=temporal `
    --from-literal=POSTGRES_PASSWORD='<strong-password>'
See k8s/postgres-secret.yaml.example (do not commit real passwords).
'@
    exit 1
}

$files = @(
    "$Root/k8s/namespace.yaml",
    "$Root/k8s/temporal-dynamic-config.yaml",
    "$Root/k8s/postgres.yaml",
    "$Root/k8s/temporal.yaml",
    "$Root/k8s/calculator-worker-configmap.yaml",
    "$Root/k8s/workers.yaml"
)

foreach ($f in $files) {
    kubectl apply -f $f
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if ($ApplyHpa) {
    kubectl apply -f "$Root/k8s/calculator-worker-add-hpa.yaml"
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host 'ok: HPA applied (calculator-worker-add). Requires metrics-server — see README Autoscaling (bonus).'
}

Write-Host "ok: manifests applied to namespace $Ns. kubectl -n $Ns get pods"
