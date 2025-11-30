#!/usr/bin/env bash
set -euo pipefail

# generate_and_test_jwt.sh
# Usage: ./generate_and_test_jwt.sh [--pod POD] [--user-id ID] [--email EMAIL] [--base-url URL] [--namespace NS]
#
# This script will:
# - find an IAM pod in the `eventos-peru` namespace (or use provided pod)
# - try to generate a HS256 JWT inside the IAM pod (preferred)
# - if that fails, retrieve the `JWT_SECRET` and generate a token locally using OpenSSL
# - call `/api/iam/me` and a couple downstream endpoints to validate acceptance
#
# Note: the script prints the token to stdout. Keep terminal output private.

NAMESPACE="eventos-peru"
POD=""
USER_ID=""
EMAIL="demo@eventos.pe"
BASE_URL="https://eventos.emeday.inc/api"

function usage() {
  cat <<EOF
Usage: $0 [--pod POD] [--user-id ID] [--email EMAIL] [--base-url URL] [--namespace NS]

Defaults:
  namespace: ${NAMESPACE}
  email: ${EMAIL}
  base-url: ${BASE_URL}

Example:
  $0 --user-id b66484e8-e668-40bc-adfb-12da3e6d1615
EOF
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --pod) POD="$2"; shift 2 ;;
    --user-id) USER_ID="$2"; shift 2 ;;
    --email) EMAIL="$2"; shift 2 ;;
    --base-url) BASE_URL="$2"; shift 2 ;;
    --namespace) NAMESPACE="$2"; shift 2 ;;
    -h|--help) usage ;;
    *) echo "Unknown arg: $1"; usage ;;
  esac
done

# find IAM pod if not provided
if [[ -z "$POD" ]]; then
  POD=$(kubectl -n "$NAMESPACE" get pods -o name 2>/dev/null | grep -E 'iam-service|/iam-' | head -n1 | cut -d'/' -f2 || true)
  if [[ -z "$POD" ]]; then
    echo "Could not find an IAM pod in namespace $NAMESPACE. Please pass --pod POD" >&2
    exit 2
  fi
fi

echo "Using IAM pod: $POD"

# helper: base64url encode
function b64url() {
  # input via stdin
  openssl base64 -A | tr '+/' '_-' | tr -d '='
}

# Try generating token inside pod with Python+PyJWT
echo "Attempting to generate JWT inside pod..."
set +e
IN_POD_TOKEN=$(kubectl -n "$NAMESPACE" exec "$POD" -- python3 - <<'PY' 2>/dev/null
import os, time
try:
  import jwt
except Exception:
  raise SystemExit(2)
secret = os.environ.get('JWT_SECRET') or ''
if not secret:
  # try reading from /vault/secrets/config if env not set
  try:
    with open('/vault/secrets/config','r') as f:
      for line in f:
        if line.startswith('JWT_SECRET'):
          _,val=line.split('=',1)
          secret=val.strip().strip('"')
  except Exception:
    pass
if not secret:
  raise SystemExit(3)
payload={
  'sub': os.environ.get('DEMO_USER_ID','') or '"REPLACE_ME"',
  'email': os.environ.get('DEMO_USER_EMAIL','') or 'demo@eventos.pe',
  'iat': int(time.time()),
  'exp': int(time.time())+3600
}
token=jwt.encode(payload, secret, algorithm='HS256')
print(token)
PY
)
RET=$?
set -e

if [[ $RET -eq 0 && -n "$IN_POD_TOKEN" ]]; then
  TOKEN="$IN_POD_TOKEN"
  echo "Token generated inside pod."
else
  echo "In-pod generation failed (code $RET). Falling back to secret-extraction and local signing."
  # extract secret
  JWT_SECRET=$(kubectl -n "$NAMESPACE" exec "$POD" -- printenv JWT_SECRET 2>/dev/null || true)
  if [[ -z "$JWT_SECRET" ]]; then
    # try reading file
    JWT_SECRET=$(kubectl -n "$NAMESPACE" exec "$POD" -- bash -lc "grep '^JWT_SECRET' /vault/secrets/config | cut -d'=' -f2- | tr -d '\"' || true" 2>/dev/null || true)
  fi
  if [[ -z "$JWT_SECRET" ]]; then
    echo "Unable to obtain JWT_SECRET from pod. Aborting." >&2
    exit 3
  fi

  # Build header and payload
  IAT=$(date +%s)
  EXP=$((IAT + 3600))
  if [[ -z "$USER_ID" || "$USER_ID" == "" ]]; then
    # try to discover demo id from DB via mysql pod? Skip and use email only
    echo "No --user-id provided; payload.sub will be empty (some validators only need exp/sub)."
    USER_ID=""
  fi

  HDR='{"alg":"HS256","typ":"JWT"}'
  if [[ -n "$USER_ID" ]]; then
    PAYLOAD=$(printf '{"sub":"%s","email":"%s","iat":%s,"exp":%s}' "$USER_ID" "$EMAIL" "$IAT" "$EXP")
  else
    PAYLOAD=$(printf '{"email":"%s","iat":%s,"exp":%s}' "$EMAIL" "$IAT" "$EXP")
  fi

  HDR_B64=$(printf '%s' "$HDR" | b64url)
  PAY_B64=$(printf '%s' "$PAYLOAD" | b64url)

  SIG=$(printf '%s.%s' "$HDR_B64" "$PAY_B64" | openssl dgst -sha256 -hmac "$JWT_SECRET" -binary | openssl base64 -A | tr '+/' '_-' | tr -d '=')

  TOKEN="$HDR_B64.$PAY_B64.$SIG"
  echo "Token signed locally using extracted secret."
fi

echo
echo "----- BEGIN TOKEN -----"
echo "$TOKEN"
echo "----- END TOKEN -----"
echo

echo "Testing endpoints with the token against $BASE_URL"

curl -s -w "\n-- HTTP STATUS: %{http_code}\n" -H "Authorization: Bearer $TOKEN" "$BASE_URL/iam/me"
printf "\n-- Contratacion --\n"
curl -s -w "\n-- HTTP STATUS: %{http_code}\n" -H "Authorization: Bearer $TOKEN" "$BASE_URL/contratacion/pedidos/mios"
printf "\n-- Proveedores (admin) --\n"
curl -s -w "\n-- HTTP STATUS: %{http_code}\n" -H "Authorization: Bearer $TOKEN" "$BASE_URL/proveedores/v1/admin/proveedores"

printf "\nDone. If downstream services return 401, check that their pods have the same JWT_SECRET and JWT_ALG=HS256.\n"
