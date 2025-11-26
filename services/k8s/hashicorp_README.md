# Vault / HashiCorp - Guía para Eventos-Peru

Este documento recoge comandos y pasos actualizados para inicializar Vault, crear la policy/role para Kubernetes, y escribir los secretos (KV v2) que usan los servicios del proyecto.

Contenido
- Inicializar y Unseal
- Habilitar KV v2 y auth/kubernetes
- Policy y Role para `eventos-peru-role`
- Comandos `vault kv put` / `vault kv patch` por servicio (valores de ejemplo)
- Cómo inyectar secrets en Kubernetes (Vault Agent annotations) y alternativas
- Qué variables poner en Vault vs ConfigMap
- Checklist de verificación antes de sincronizar ArgoCD

---

## 1) Inicializar Vault (ejemplo local / single-node)

```bash
# Inicializar (solo 1 key-share en dev)
vault operator init -key-shares=1 -key-threshold=1

# Guarda las claves y root token en un lugar seguro.
# Unseal (usar el unseal key dev):
vault operator unseal <UNSEAL_KEY_1>

# Establecer VAULT_ADDR y VAULT_TOKEN (root) en la sesión
export VAULT_ADDR="http://127.0.0.1:8200"
export VAULT_TOKEN="<INITIAL_ROOT_TOKEN>"
vault status
```

En clúster (si Vault corre en Kubernetes) ejecuta desde un pod que tenga `vault` CLI:

```bash
kubectl -n vault exec -it statefulset/vault -c vault -- sh
export VAULT_ADDR="http://vault.vault.svc:8200"
export VAULT_TOKEN="<INITIAL_ROOT_TOKEN>"
vault operator unseal <UNSEAL_KEY_1>
vault status
```

---

## 2) Habilitar KV v2 y Kubernetes Auth

```bash
# Habilitar KV v2 (si no está habilitado)
vault secrets enable -path=kv kv-v2

# Habilitar auth/kubernetes
vault auth enable kubernetes

# Configurar conexión entre Vault y Kubernetes (ejecutar desde pod dentro del cluster)
vault write auth/kubernetes/config \
  token_reviewer_jwt="$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" \
  kubernetes_host="https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_SERVICE_PORT" \
  kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt \
  issuer="https://kubernetes.default.svc.cluster.local"
```

---

## 3) Crear policy y role para los pods

Policy mínima (`eventos-peru-app`) que permite leer los paths `kv/data/eventos-peru/*` (KV v2):

```bash
vault policy write eventos-peru-app - <<'EOF'
path "kv/data/eventos-peru/*" {
  capabilities = ["read"]
}
path "kv/metadata/eventos-peru/*" {
  capabilities = ["list"]
}
EOF
```

Crear el rol Kubernetes que vincula el ServiceAccount `app-eventos` (namespace `eventos-peru`) con la policy:

```bash
vault write auth/kubernetes/role/eventos-peru-role \
  bound_service_account_names=app-eventos \
  bound_service_account_namespaces=eventos-peru \
  policies=eventos-peru-app \
  ttl=24h \
  audiences=vault

# Verificar
vault read auth/kubernetes/role/eventos-peru-role
```

---

## 4) Escribir secretos (ejemplos) — KV v2

NOTA: en KV v2 la ruta que usa `vault kv put kv/eventos-peru/service` escribe `kv/data/eventos-peru/service` internamente. Los templates de Vault Agent en las Deployments leen `.Data.data.<KEY>`.

Ejemplos (ajusta valores según tu entorno):

### IAM
```bash
vault kv put kv/eventos-peru/iam \
  APP_ENV=prod \
  DB_HOST='mysql.eventos-peru.svc.cluster.local' \
  DB_PORT='3306' \
  DB_USER='app_iam' \
  DB_PASS='IAM_2025' \
  DB_NAME='ev_iam' \
  JWT_SECRET='<JWT_SECRET_IAM>' \
  ACCESS_TOKEN_EXPIRE_MINUTES='60'
```

### Catálogo
```bash
vault kv put kv/eventos-peru/catalogo \
  APP_ENV='prod' \
  DB_HOST='mysql.eventos-peru.svc.cluster.local' \
  DB_PORT='3306' \
  DB_USER='app_catalogo' \
  DB_PASS='Catalogo_2025' \
  DB_NAME='ev_catalogo' \
  JWT_SECRET='<JWT_SECRET_COMMON>' \
  ACCESS_TOKEN_EXPIRE_MINUTES='60'
```

### Proveedores
```bash
vault kv put kv/eventos-peru/proveedores \
  APP_ENV='prod' \
  DB_HOST='mysql.eventos-peru.svc.cluster.local' \
  DB_PORT='3306' \
  DB_USER='app_proveedores' \
  DB_PASS='Proveedores_2025' \
  DB_NAME='ev_proveedores' \
  JWT_SECRET='<JWT_SECRET_COMMON>' \
  INTERNAL_SERVICE_TOKEN='<INTERNAL_TOKEN_PROD>' \
  ACCESS_TOKEN_EXPIRE_MINUTES='60'
```

### Contratación
```bash
vault kv put kv/eventos-peru/contratacion \
  APP_ENV='prod' \
  DB_HOST='mysql.eventos-peru.svc.cluster.local' \
  DB_PORT='3306' \
  DB_USER='app_contratacion' \
  DB_PASS='Contrata_2025' \
  DB_NAME='ev_contratacion' \
  JWT_SECRET='<JWT_SECRET_COMMON>' \
  INTERNAL_SERVICE_TOKEN='<INTERNAL_TOKEN_PROD>' \
  ACCESS_TOKEN_EXPIRE_MINUTES='60'
```

Recomendación: usa un JWT_SECRET distinto en producción o un secreto compartido seguro; aquí usamos `<JWT_SECRET_COMMON>` como ejemplo.

---

## 5) Inyección en Kubernetes (Vault Agent — ejemplos)

En los `Deployment` del repo ya se usa este patrón: anotaciones `vault.hashicorp.com/agent-inject` + `agent-inject-template-config` que escriben un archivo con el contenido de secrets.

Ejemplo de anotaciones mínimas (ya presentes en `deploy-svc.yaml`):

```yaml
annotations:
  vault.hashicorp.com/agent-inject: "true"
  vault.hashicorp.com/role: "eventos-peru-role"
  vault.hashicorp.com/agent-inject-secret-config: "kv/data/eventos-peru/proveedores"
  vault.hashicorp.com/agent-inject-template-config: |
    {{- with secret "kv/data/eventos-peru/proveedores" -}}
    APP_ENV='{{ .Data.data.APP_ENV }}'
    DB_HOST='{{ .Data.data.DB_HOST }}'
    DB_PORT='{{ .Data.data.DB_PORT }}'
    DB_USER='{{ .Data.data.DB_USER }}'
    DB_PASS='{{ .Data.data.DB_PASS }}'
    DB_NAME='{{ .Data.data.DB_NAME }}'
    JWT_SECRET='{{ .Data.data.JWT_SECRET }}'
    INTERNAL_SERVICE_TOKEN='{{ .Data.data.INTERNAL_SERVICE_TOKEN }}'
    {{- end }}
```

Al iniciar el contenedor, el Vault Agent crea el archivo (por ejemplo `/vault/secrets/config`). En algunos `Deployment` (ej. `iam`) el `command` de arranque hace `. /vault/secrets/config` para exportar variables como variables de entorno antes de arrancar `uvicorn`.

Puntos a considerar:
- Asegúrate que el `agent-inject-secret-config` apunta a `kv/data/...` (KV v2) y que las plantillas usan `.Data.data.<KEY>`.
- Si tu contenedor no sourcea el archivo, puede lanzar as-sidecar env via `envFrom` con `projected` volume o usar Vault CSI provider o External Secrets Operator.

Alternativas:
- Vault CSI Provider: monta secrets como `Secrets` de Kubernetes directamente. 
- External Secrets Operator: sincroniza secrets desde Vault a Kubernetes `Secret` (útil si prefieres manejar `envFrom: secretRef`).

---

## 6) ¿Qué variables deben ir a Vault y cuáles pueden quedarse en ConfigMap?

Regla general: secrets (credenciales y tokens) → Vault; configuraciones no sensibles → ConfigMap.

Variables recomendadas en Vault (por servicio)
- DB_PASS
- DB_USER (recomendado)
- JWT_SECRET
- INTERNAL_SERVICE_TOKEN
- VAULT_* (solo en entorno local; en k8s usar Vault Agent)

Variables que pueden quedarse en ConfigMap / manifest (no sensibles)
- CORS_ORIGINS
- BASE_PATH, SERVICE_NAME, PORT, VERSION, APP_ENV
- PROVEEDORES_SERVICE_URL / CATALOGO_SERVICE_URL
- SCHEMA_*

Cómo representarlo en k8s:
- ConfigMap para valores no sensibles, inyectado con `envFrom: configMapRef`.
- Secrets sensibles: inyectados por Vault Agent (como en los `deploy-svc.yaml`) o por ExternalSecrets.

Ejemplo breve de `ConfigMap` (no sensible):

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: frontend-config
  namespace: eventos-peru
data:
  CORS_ORIGINS: "http://localhost:3000"
  BASE_PATH: "/catalogo"
```

---

## 7) Checklist antes de sincronizar ArgoCD

1. Comprobar que las imágenes con tag `1` existen en DockerHub (`docker pull emeday17/eventos-catalogo:1`).
2. Verificar que `kv` contiene los secrets: `vault kv get kv/eventos-peru/iam` etc.
3. Comprobar que la `policy` y `role` existen:
   - `vault policy read eventos-peru-app`
   - `vault read auth/kubernetes/role/eventos-peru-role`
4. Revisar `ingressClassName` y `host` en `ingress.yaml`.
5. Sincronizar ArgoCD (o `kubectl apply -k services/k8s/argocd/overlays/dev`) y observar:
   - `kubectl -n eventos-peru rollout status deploy/<service>`
   - `kubectl -n eventos-peru logs deploy/<pod>` si falla.

---

## 8) Comandos de verificación / debugging

```bash
vault kv get kv/eventos-peru/proveedores
vault kv get kv/eventos-peru/iam
kubectl -n eventos-peru get pods
kubectl -n eventos-peru describe pod <pod-name>
kubectl -n eventos-peru logs deploy/<deployment-name> -c app
```

---

## 9) Buenas prácticas

- No commitees `.env` con secretos; mantener `.env.example` en el repo y añadir `.env` a `.gitignore`.
- Usa valores distintos entre entornos (dev/prod) y tags de imágenes con fecha/sha para trazabilidad.
- Documenta la ruta exacta en Vault (p. ej. `kv/eventos-peru/<service>`) y quién tiene acceso.

---

Si quieres, puedo:
- Generar `*.env.example` para cada servicio y reemplazar valores sensibles en los `.env` actuales por placeholders (no sobrescribo sin tu confirmación). 
- Añadir ejemplos de External Secrets Operator / Vault CSI provider si prefieres esa integración.

Fin.
