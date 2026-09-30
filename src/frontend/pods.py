"""
Lists pods through the Kubernetes API using the frontend's own ServiceAccount.

This is the ServiceAccount RBAC demo: the frontend's Role lets it list pods in
its own namespace only, so every other namespace should come back 403.
"""
import os

from kubernetes import client, config
from kubernetes.client.exceptions import ApiException
from kubernetes.config.config_exception import ConfigException

from constants import DEFAULT_POD_PANEL_NAMESPACES

# Injected via the downward API (fieldRef: metadata.namespace).
POD_NAMESPACE = os.environ.get('POD_NAMESPACE')
POD_PANEL_NAMESPACES = os.environ.get('POD_PANEL_NAMESPACES', DEFAULT_POD_PANEL_NAMESPACES)


def pod_panel_namespaces():
    others = [ns.strip() for ns in POD_PANEL_NAMESPACES.split(',') if ns.strip()]
    return [POD_NAMESPACE, *others] if POD_NAMESPACE else others


def list_pods(namespace: str):
    """
    List pods in a namespace. Returns human-readable lines, including failures.
    """
    # Kubernetes sets this in every pod; outside a cluster (docker-compose)
    # there is no API server to ask.
    if 'KUBERNETES_SERVICE_HOST' not in os.environ:
        return [f'{namespace}: not running in a cluster']

    try:
        config.load_incluster_config()
    except ConfigException:
        return [f'{namespace}: no ServiceAccount token mounted']

    try:
        pods = client.CoreV1Api().list_namespaced_pod(namespace)
    except ApiException as e:
        return [f'{namespace}: {e.status} {e.reason}']

    if not pods.items:
        return [f'{namespace}: no pods']
    return [f'{namespace}/{p.metadata.name}: {p.status.phase}' for p in pods.items]
