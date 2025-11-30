#!/bin/bash
# verification-script.sh

echo "🔍 Verificando estado del stack de monitoreo..."

# Verificar pods
kubectl get pods -n monitoring

# Verificar servicios
kubectl get svc -n monitoring

# Verificar ingress
kubectl get ingress -n monitoring

# Verificar ServiceMonitors
kubectl get servicemonitors -n monitoring

# Verificar métricas de ArgoCD
kubectl port-forward -n argocd svc/argocd-server 8080:80 2>/dev/null &
sleep 2
curl -s http://localhost:8080/metrics | head -10
kill %1

echo "✅ Verificación completada"