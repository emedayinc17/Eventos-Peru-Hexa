#!/bin/bash

echo "🔧 Configurando RBAC para Grafana..."

# Crear ClusterRole y ClusterRoleBinding para el Service Account existente
kubectl apply -f - <<EOF
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: grafana-read-only
rules:
- apiGroups: [""]
  resources:
  - nodes
  - nodes/proxy
  - services
  - endpoints
  - pods
  - configmaps
  verbs: ["get", "list", "watch"]
- apiGroups: ["extensions", "networking.k8s.io"]
  resources:
  - ingresses
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources:
  - deployments
  - statefulsets
  - daemonsets
  - replicasets
  verbs: ["get", "list", "watch"]
- nonResourceURLs: ["/metrics", "/api/*", "/apis/*"]
  verbs: ["get"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: grafana-read-only-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: grafana-read-only
subjects:
- kind: ServiceAccount
  name: prometheus-grafana
  namespace: monitoring
EOF

echo "✅ RBAC configurado!"