#!/bin/bash

set -e

echo " Déploiement de Budgeomètre sur Kubernetes/Minikube"
echo "======================================================"

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
log_info() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Vérifier que minikube est démarré
echo ""
echo " Vérification des prérequis..."
if ! minikube status &> /dev/null; then
    log_warn "Minikube n'est pas démarré. Démarrage..."
    minikube start --driver=docker
    log_info "Minikube démarré"
else
    log_info "Minikube est déjà démarré"
fi

# Configurer Docker pour utiliser le daemon Minikube
echo ""
echo " Configuration de Docker..."
eval $(minikube docker-env)
log_info "Docker configuré pour utiliser le daemon Minikube"

# Build des images Docker
echo ""
echo "  Build des images Docker..."

echo "  - Build gateway..."
docker build -t gateway:latest ./gateway
log_info "Image gateway:latest créée"

echo "  - Build ecriture-service..."
docker build -t ecriture-service:latest ./services/ecriture
log_info "Image ecriture-service:latest créée"

echo "  - Build lecture-service..."
docker build -t lecture-service:latest ./services/lecture
log_info "Image lecture-service:latest créée"

# Vérifier les images
echo ""
echo " Vérification des images..."
docker images | grep -E "gateway|ecriture|lecture" || log_error "Aucune image trouvée"

# Créer le dossier k8s s'il n'existe pas
mkdir -p k8s

# Déploiement Kubernetes
echo ""
echo "  Déploiement sur Kubernetes..."

echo "  1. Création du namespace..."
kubectl apply -f k8s/namespace.yaml
log_info "Namespace créé"

echo "  2. Création des ConfigMaps et Secrets..."
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/postgres-init-configmap.yaml
log_info "ConfigMaps et Secrets créés"

echo "  3. Création du PVC PostgreSQL..."
kubectl apply -f k8s/postgres-pvc.yaml
log_info "PVC créé"

echo "  4. Déploiement de PostgreSQL..."
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml
log_info "PostgreSQL déployé"

echo "  5. Attente du démarrage de PostgreSQL..."
kubectl wait --for=condition=ready pod -l app=postgres -n budgeometre --timeout=120s
log_info "PostgreSQL est prêt"

echo "  6. Déploiement du service Écriture..."
kubectl apply -f k8s/ecriture-deployment.yaml
kubectl apply -f k8s/ecriture-service.yaml
log_info "Service Écriture déployé"

echo "  7. Déploiement du service Lecture..."
kubectl apply -f k8s/lecture-deployment.yaml
kubectl apply -f k8s/lecture-service.yaml
log_info "Service Lecture déployé"

echo "  8. Attente du démarrage des services..."
kubectl wait --for=condition=ready pod -l app=ecriture-service -n budgeometre --timeout=120s
kubectl wait --for=condition=ready pod -l app=lecture-service -n budgeometre --timeout=120s
log_info "Services Écriture et Lecture sont prêts"

echo "  9. Déploiement du Gateway..."
kubectl apply -f k8s/gateway-deployment.yaml
kubectl apply -f k8s/gateway-service.yaml
log_info "Gateway déployé"

echo "  10. Attente du démarrage du Gateway..."
kubectl wait --for=condition=ready pod -l app=gateway -n budgeometre --timeout=120s
log_info "Gateway est prêt"

# Afficher le statut
echo ""
echo "Statut du déploiement:"
echo "========================"
kubectl get pods -n budgeometre
echo ""
kubectl get services -n budgeometre

# Obtenir l'URL d'accès
echo ""
echo " Accès à l'application:"
echo "========================="
APP_URL=$(minikube service gateway -n budgeometre --url)
log_info "Application accessible sur: $APP_URL"

echo ""
echo "Déploiement terminé avec succès!"
echo ""
echo " Commandes utiles:"
echo "   - Voir les logs du gateway:    kubectl logs -f deployment/gateway -n budgeometre"
echo "   - Voir les logs de l'écriture: kubectl logs -f deployment/ecriture-service -n budgeometre"
echo "   - Voir les logs de la lecture: kubectl logs -f deployment/lecture-service -n budgeometre"
echo "   - Dashboard Kubernetes:        minikube dashboard"
echo "   - Port-forward (alt):          kubectl port-forward service/gateway 5000:5000 -n budgeometre"
echo ""