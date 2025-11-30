Admin service token
===================

This folder contains the k8s secret used by the Gateway to perform internal admin calls.

Important:
- Do not commit production secrets into the repository.
- The `admin-service-token` secret should contain a JWT signed with the same `JWT_SECRET`
  used by the IAM service and validators (algorithm HS256 by default).
- If you prefer, leave the secret absent: the Gateway will then forward the incoming
  `Authorization` header instead of using a fixed admin token.

How to generate & apply a valid admin token (example):

1. Find an IAM pod in the `eventos-peru` namespace:

```bash
kubectl -n eventos-peru get pods | grep iam
# pick the pod name, e.g. iam-service-xxxxx
```

2. Generate a token inside the IAM pod (preferred, avoids exposing the secret locally):

```bash
IAM_POD=iam-service-xxxxx
kubectl -n eventos-peru exec -it $IAM_POD -- python3 - <<'PY'
import os, time
from jose import jwt
secret = os.environ.get('JWT_SECRET')
if not secret:
  print('JWT_SECRET not found in pod environment')
  raise SystemExit(1)
payload = {'sub':'admin','role':'ADMIN','iat':int(time.time()),'exp':int(time.time())+3600}
print(jwt.encode(payload, secret, algorithm='HS256'))
PY
```

3. Apply the token as a Kubernetes secret:

```bash
kubectl -n eventos-peru create secret generic admin-service-token \
  --from-literal=token="$TOKEN" --dry-run=client -o yaml | kubectl apply -f -
```

Replace `$TOKEN` with the string printed by the Python snippet.

If you are deploying via ArgoCD/Vault, prefer storing the `admin-service-token` value in Vault and
configure a Vault Agent or templating mechanism to inject it into the `admin-service-token` Secret
in the cluster during deployment.
