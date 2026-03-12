#!/usr/bin/env bash
# =============================================================
# setup-argocd.sh
# Instala e configura ArgoCD em um cluster K3s/K8s
# Uso: ./scripts/setup-argocd.sh
# =============================================================

set -euo pipefail

ARGOCD_NAMESPACE="argocd"
ARGOCD_VERSION="stable"

echo "============================================"
echo " Instalando ArgoCD no cluster"
echo "============================================"

# 1. Criar namespace
echo "[1/5] Criando namespace $ARGOCD_NAMESPACE..."
kubectl create namespace "$ARGOCD_NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# 2. Instalar ArgoCD
echo "[2/5] Instalando ArgoCD ($ARGOCD_VERSION)..."
kubectl apply -n "$ARGOCD_NAMESPACE" \
    -f "https://raw.githubusercontent.com/argoproj/argo-cd/${ARGOCD_VERSION}/manifests/install.yaml"

# 3. Aguardar pods ficarem prontos
echo "[3/5] Aguardando pods ficarem prontos..."
kubectl wait --for=condition=available deployment/argocd-server \
    -n "$ARGOCD_NAMESPACE" --timeout=300s

# 4. Obter senha inicial do admin
echo "[4/5] Obtendo senha inicial do admin..."
ADMIN_PASSWORD=$(kubectl -n "$ARGOCD_NAMESPACE" get secret argocd-initial-admin-secret \
    -o jsonpath="{.data.password}" | base64 -d)
echo "  Usuario: admin"
echo "  Senha:   $ADMIN_PASSWORD"

# 5. Aplicar AppProject e Applications
echo "[5/5] Aplicando manifests do ArgoCD..."
kubectl apply -f argocd/project.yaml
kubectl apply -f argocd/application.yaml

echo ""
echo "============================================"
echo " ArgoCD instalado com sucesso!"
echo "============================================"
echo ""
echo "Para acessar a UI do ArgoCD:"
echo "  kubectl port-forward svc/argocd-server -n argocd 8443:443"
echo "  Abrir: https://localhost:8443"
echo ""
echo "Para login via CLI:"
echo "  argocd login localhost:8443 --username admin --password '$ADMIN_PASSWORD'"
