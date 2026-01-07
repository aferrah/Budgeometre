#!/bin/bash

set -e

echo "  Nettoyage du déploiement Budgeomètre"
echo "=========================================="

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Demander confirmation
echo ""
read -p "Êtes-vous sûr de vouloir supprimer tout le déploiement ? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_warn "Nettoyage annulé"
    exit 0
fi

echo ""
echo " Suppression des ressources Kubernetes..."

# Supprimer le namespace (cela supprime tout ce qui est dedans)
kubectl delete namespace budgeometre --timeout=60s

log_info "Namespace budgeometre supprimé"

# Vérifier qu'il n'y a plus de ressources
echo ""
echo "Vérification..."
REMAINING=$(kubectl get all -n budgeometre 2>&1 || true)
if [[ $REMAINING == *"No resources found"* ]] || [[ $REMAINING == *"not found"* ]]; then
    log_info "Toutes les ressources ont été supprimées"
else
    log_warn "Il reste peut-être des ressources, vérifiez manuellement"
fi

echo ""
echo " Nettoyage terminé!"
echo ""
echo " Pour redéployer: ./deploy.sh"
echo " Pour arrêter Minikube: minikube stop"
echo " Pour supprimer Minikube: minikube delete"
echo ""