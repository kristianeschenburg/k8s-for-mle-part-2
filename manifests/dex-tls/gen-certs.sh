#!/usr/bin/env bash
# Generates a throwaway CA and a Dex serving cert for the kind cluster.
#
# The cert's SAN is `kind-control-plane` because that is the issuer host:
# the API server resolves it via Docker DNS (it runs on the node's network),
# and the Mac resolves it via /etc/hosts -> 127.0.0.1 (port 32000 is mapped
# in cluster.yaml). Run this BEFORE `kind create cluster`, since cluster.yaml
# mounts ca.crt into the control-plane node.
set -euo pipefail
cd "$(dirname "$0")"

openssl req -x509 -newkey rsa:2048 -nodes -days 365 \
  -keyout ca.key -out ca.crt -subj "/CN=kind-dex-ca"

openssl req -newkey rsa:2048 -nodes \
  -keyout tls.key -out tls.csr -subj "/CN=kind-control-plane"

openssl x509 -req -in tls.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
  -days 365 -out tls.crt \
  -extfile <(printf "subjectAltName=DNS:kind-control-plane,DNS:localhost,IP:127.0.0.1\nextendedKeyUsage=serverAuth")

rm -f tls.csr ca.srl
echo "wrote $(pwd)/{ca.crt,ca.key,tls.crt,tls.key}"
