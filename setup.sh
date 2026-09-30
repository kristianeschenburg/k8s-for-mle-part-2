#!/usr/bin/env bash
# Brings up the part-2 kind cluster, exposed through the Gateway API (Envoy Gateway).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
MANIFESTS="$ROOT/manifests"
SRC="$ROOT/src"
ENVOY_GATEWAY_VERSION=v1.9.1
# the fx-rates IP written in config-map.yaml and network-policies.yaml,
# swapped for the container's real IP at apply time
FX_PLACEHOLDER_IP=172.18.0.100

cd "$MANIFESTS"

# cluster.yaml mounts dex-tls/ca.crt into the control-plane, so the certs must exist first
if [ ! -f dex-tls/ca.crt ]; then
  ./dex-tls/gen-certs.sh
fi

# create the Kind cluster
if ! kind get clusters | grep -qx kind; then
  kind create cluster --config cluster.yaml
fi

# get the Envoy proxy for the Gateway
kubectl apply --server-side --force-conflicts \
  -f "https://github.com/envoyproxy/gateway/releases/download/${ENVOY_GATEWAY_VERSION}/install.yaml"
kubectl wait --timeout=5m -n envoy-gateway-system deployment/envoy-gateway --for=condition=Available

# build the docker images and load them into the Kind cluster
(cd "$SRC" && docker compose build)
kind load docker-image user-backend:latest salary-backend:latest part-2-frontend:latest

# fx-rates stands in for a service outside the cluster, as a plain container on the kind network.
# Docker rejects --ip there (kind's network has no user-configured subnet), so use whatever IP it assigns.
docker rm -f fx-rates >/dev/null 2>&1 || true
docker run -d --name fx-rates --network kind \
  -v "$SRC/fx_rates:/usr/share/nginx/html:ro" \
  --restart unless-stopped \
  nginx:alpine
FX_IP=$(docker inspect -f '{{.NetworkSettings.Networks.kind.IPAddress}}' fx-rates)
echo "fx-rates is at $FX_IP"

# create the namespaces
kubectl apply -f namespace.yaml

# create the Dex mocked OIDC provider service
kubectl apply -f dex.yaml
# create a ConfigMap from the Dex configuration and a secret from the TLS cert, in the Dex namespace
kubectl create configmap dex-config -n dex --from-file=config.yaml=dex-config.yaml \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl create secret tls dex-tls -n dex --cert=dex-tls/tls.crt --key=dex-tls/tls.key \
  --dry-run=client -o yaml | kubectl apply -f -

# create ConfigMap resources in platform and client-a namespaces
sed "s/${FX_PLACEHOLDER_IP}/${FX_IP}/g" config-map.yaml | kubectl apply -f -
# create roles and service accounts
kubectl apply -f roles.yaml
# create cluster roles and cluster role bindings
kubectl apply -f cluster-rbac.yaml
# create all services
kubectl apply -f services.yaml
# create the network policies
sed "s/${FX_PLACEHOLDER_IP}/${FX_IP}/g" network-policies.yaml | kubectl apply -f -
# create the deployments
kubectl apply -f deployment.yaml

# create the Gateway and the routes that attach to it
kubectl apply -f gateway.yaml
kubectl apply -f httproute.yaml

kubectl rollout status -n dex deployment/dex --timeout=3m
kubectl wait --for=condition=Ready pods --all -n platform --timeout=3m
kubectl wait --for=condition=Ready pods --all -n client-a --timeout=3m
kubectl wait --for=condition=Programmed gateway/apps -n platform --timeout=3m

echo
if ! grep -q "apps.part-2.test" /etc/hosts; then
  echo "Add the gateway hostname to /etc/hosts:"
  echo "  echo '127.0.0.1 apps.part-2.test' | sudo tee -a /etc/hosts"
fi
if ! grep -q "kind-control-plane" /etc/hosts; then
  echo "For kubectl OIDC login through Dex, also add:"
  echo "  echo '127.0.0.1 kind-control-plane' | sudo tee -a /etc/hosts"
fi
echo "Frontend: http://apps.part-2.test:8080/frontend/"
