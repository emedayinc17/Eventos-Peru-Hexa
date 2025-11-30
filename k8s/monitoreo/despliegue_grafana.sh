#!/bin/bash

# Configuración
NAMESPACE="monitoring"
GRAFANA_USER="emeday"
GRAFANA_PASSWORD="Evoluti0n"
DOMAIN="emeday.inc"
INGRESS_CLASS="nginx"

echo "🚀 Iniciando despliegue del stack de monitoreo..."
echo "📊 Namespace: $NAMESPACE"
echo "👤 Usuario: $GRAFANA_USER"
echo "🔐 Password: $GRAFANA_PASSWORD"
echo "🌐 Dominio: $DOMAIN"
echo "🔗 Ingress Class: $INGRESS_CLASS"

# Crear namespace
echo "📁 Creando namespace..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Agregar repositorios de Helm
echo "📦 Agregando repositorios Helm..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Desplegar Prometheus Stack integrado con tu ingress existente
echo "🔴 Desplegando Stack de Monitoreo..."
cat <<EOF | helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
    --namespace $NAMESPACE \
    --values -
grafana:
  enabled: true
  adminUser: "$GRAFANA_USER"
  adminPassword: "$GRAFANA_PASSWORD"
  
  # Servicio ClusterIP (sin LoadBalancer)
  service:
    type: ClusterIP
    port: 3000
    targetPort: 3000
  
  # Ingress configurado como tus otros servicios
  ingress:
    enabled: true
    ingressClassName: $INGRESS_CLASS
    hosts:
      - grafana.$DOMAIN
    paths:
      - /
    pathType: Prefix
    annotations:
      nginx.ingress.kubernetes.io/rewrite-target: /
      nginx.ingress.kubernetes.io/proxy-body-size: "50m"
  
  # Persistencia
  persistence:
    enabled: true
    size: 5Gi
    accessModes:
      - ReadWriteOnce
  
  # Dashboards automáticos
  dashboardProviders:
    dashboardproviders.yaml:
      apiVersion: 1
      providers:
      - name: 'default'
        orgId: 1
        folder: ''
        type: file
        disableDeletion: false
        editable: true
        options:
          path: /var/lib/grafana/dashboards/default
  
  # Datasources pre-configuradas
  datasources:
    datasources.yaml:
      apiVersion: 1
      datasources:
      - name: Prometheus
        type: prometheus
        url: http://prometheus-server.$NAMESPACE.svc.cluster.local:9090
        access: proxy
        isDefault: true
      - name: Kubernetes
        type: prometheus
        url: https://kubernetes.default.svc:443
        access: proxy
        basicAuth: true
        basicAuthUser: internal
        withCredentials: true
        isDefault: false
        jsonData:
          tlsSkipVerify: true
          httpHeaderName1: "Authorization"
        secureJsonData:
          httpHeaderValue1: "Bearer \$(KUBE_TOKEN)"

# Configuración de Prometheus
prometheus:
  enabled: true
  
  # Servicio ClusterIP para Prometheus
  service:
    type: ClusterIP
    port: 9090
  
  # Ingress para Prometheus UI
  ingress:
    enabled: true
    ingressClassName: $INGRESS_CLASS
    hosts:
      - prometheus.$DOMAIN
    paths:
      - /
    pathType: Prefix
    annotations:
      nginx.ingress.kubernetes.io/rewrite-target: /
      nginx.ingress.kubernetes.io/auth-type: basic
      nginx.ingress.kubernetes.io/auth-secret: prometheus-basic-auth
      nginx.ingress.kubernetes.io/auth-realm: "Authentication Required"
  
  prometheusSpec:
    serviceMonitorSelectorNilUsesHelmValues: false
    podMonitorSelectorNilUsesHelmValues: false
    retention: 10d
    retentionSize: "5GB"
    
    # Recursos optimizados
    resources:
      requests:
        memory: 512Mi
        cpu: 300m
      limits:
        memory: 2Gi
        cpu: 1000m
    
    # Persistencia
    storageSpec:
      volumeClaimTemplate:
        spec:
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 5Gi

# Alertmanager (opcional)
alertmanager:
  enabled: true
  service:
    type: ClusterIP
  ingress:
    enabled: true
    ingressClassName: $INGRESS_CLASS
    hosts:
      - alertmanager.$DOMAIN
    paths:
      - /
    pathType: Prefix

# Componentes del stack
kubeApiServer:
  enabled: true
kubelet:
  enabled: true
kubeControllerManager:
  enabled: true
coreDns:
  enabled: true
kubeEtcd:
  enabled: false  # Deshabilitado por seguridad
kubeProxy:
  enabled: true
kubeStateMetrics:
  enabled: true
nodeExporter:
  enabled: true

# Configuración global
global:
  scrape_interval: 30s
  evaluation_interval: 30s
EOF

# Esperar a que los pods estén running
echo "⏳ Esperando a que los pods estén listos..."
sleep 30
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=grafana -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=ready pod -l app=prometheus -n $NAMESPACE --timeout=300s

# Configurar ServiceMonitor para ArgoCD
echo "🔧 Configurando monitoreo para ArgoCD..."
cat <<EOF | kubectl apply -f -
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: argocd-metrics
  namespace: $NAMESPACE
  labels:
    release: prometheus
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: argocd-server
  namespaceSelector:
    matchNames:
    - argocd
  endpoints:
  - port: server
    interval: 30s
    path: /metrics
    honorLabels: true
    relabelings:
    - sourceLabels: [__meta_kubernetes_pod_name]
      targetLabel: pod_name
EOF

# ServiceMonitor para aplicaciones en eventos-peru
echo "🔍 Configurando monitoreo para aplicaciones de eventos-peru..."
cat <<EOF | kubectl apply -f -
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: eventos-peru-apps
  namespace: $NAMESPACE
  labels:
    release: prometheus
spec:
  selector:
    matchLabels:
      app.kubernetes.io/part-of: eventos-peru
  namespaceSelector:
    matchNames:
    - eventos-peru
  endpoints:
  - port: http
    interval: 30s
    path: /metrics
  - port: https
    interval: 30s
    path: /metrics
    scheme: https
    tlsConfig:
      insecureSkipVerify: true
EOF

# ServiceMonitor para todos los servicios con anotaciones específicas
cat <<EOF | kubectl apply -f -
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: kubernetes-services
  namespace: $NAMESPACE
  labels:
    release: prometheus
spec:
  selector:
    matchExpressions:
    - key: prometheus.io/scrape
      operator: Exists
  namespaceSelector:
    any: true
  endpoints:
  - port: http-metrics
    interval: 30s
    path: /metrics
  - port: https-metrics
    interval: 30s
    path: /metrics
    scheme: https
    tlsConfig:
      insecureSkipVerify: true
EOF

# Habilitar métricas en ArgoCD si existe
echo "📊 Configurando métricas en ArgoCD..."
kubectl patch configmap argocd-cm -n argocd --type merge -p '{"data":{"metrics.enabled":"true"}}' 2>/dev/null && \
kubectl rollout restart deployment argocd-server -n argocd && \
echo "✅ ArgoCD metrics habilitadas" || echo "⚠️  ArgoCD no encontrado, omitiendo"

# Crear secret para autenticación básica de Prometheus
echo "🔐 Configurando autenticación para Prometheus..."
kubectl create secret generic prometheus-basic-auth \
  --namespace $NAMESPACE \
  --from-literal=auth="$GRAFANA_USER:$(openssl passwd -apr1 $GRAFANA_PASSWORD)" \
  --dry-run=client -o yaml | kubectl apply -f -

# Verificar despliegue
echo "✅ Verificando despliegue..."
kubectl get pods -n $NAMESPACE
kubectl get ingress -n $NAMESPACE

# Mostrar URLs de acceso
echo ""
echo "🎉 ¡Despliegue completado!"
echo "📊 URLs de acceso:"
echo "   Grafana:     https://grafana.$DOMAIN"
echo "   Prometheus:  https://prometheus.$DOMAIN"
echo "   Alertmanager: https://alertmanager.$DOMAIN"
echo ""
echo "👤 Credenciales:"
echo "   Usuario: $GRAFANA_USER"
echo "   Password: $GRAFANA_PASSWORD"
echo ""
echo "🔧 Para ver el estado: kubectl get all -n $NAMESPACE"
echo "🔍 Para ver logs: kubectl logs -l app.kubernetes.io/name=grafana -n $NAMESPACE"