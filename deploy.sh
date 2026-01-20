#!/bin/bash

cat << "EOF"
  ____            _                                 _            
 |  _ \          | |                               | |           
 | |_) |_   _  __| | __ _  ___  ___  _ __ ___   ___| |_ _ __ ___ 
 |  _ <| | | |/ _` |/ _` |/ _ \/ _ \| '_ ` _ \ / _ \ __| '__/ _ \
 | |_) | |_| | (_| | (_| |  __/ (_) | | | | | |  __/ |_| | |  __/
 |____/ \__,_|\__,_|\__, |\___|\___/|_| |_| |_|\___|\__|_|  \___|
                     __/ |                                        
                    |___/                                         
EOF

echo "=========================================="
echo "  Déploiement Budgeomètre sur Minikube"
echo "=========================================="

# 1. Démarrer Minikube
echo ""
echo ">>> Démarrage de Minikube..."
minikube start --driver=docker

# 2. Activer Ingress
echo ""
echo ">>> Activation de l'Ingress..."
minikube addons enable ingress
minikube addons enable metrics-server

# 3. Configurer Docker pour Minikube
echo ""
echo ">>> Configuration de Docker..."
eval $(minikube docker-env)

# 4. Build des images
echo ""
echo ">>> Build des images Docker..."

echo "  - Gateway..."
docker build -t gateway:latest -f gateway/Dockerfile .

echo "  - Ecriture..."
docker build -t ecriture-service:latest -f services/ecriture/Dockerfile .

echo "  - Lecture..."
docker build -t lecture-service:latest -f services/lecture/Dockerfile .

# 5. Vérifier les images
echo ""
echo ">>> Images créées :"
docker images | grep -E "gateway|ecriture|lecture"

# 6. Déployer sur Kubernetes
echo ""
echo ">>> Déploiement Kubernetes..."

echo "  - Namespace..."
kubectl apply -f k8s/namespace.yaml

echo "  - ConfigMap & Secret..."
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/postgres-init-configmap.yaml

echo "  - PostgreSQL..."
kubectl apply -f k8s/postgres-statefulset.yaml

echo "  - Attente PostgreSQL..."
kubectl wait --for=condition=ready pod -l app=postgres -n budgeometre --timeout=180s

echo "  - Services Ecriture & Lecture..."
kubectl apply -f k8s/ecriture-deployment.yaml
kubectl apply -f k8s/lecture-deployment.yaml

echo "  - Attente services..."
kubectl wait --for=condition=ready pod -l app=ecriture-service -n budgeometre --timeout=180s
kubectl wait --for=condition=ready pod -l app=lecture-service -n budgeometre --timeout=180s

echo "  - Gateway..."
kubectl apply -f k8s/gateway-deployment.yaml

echo "  - Attente Gateway..."
kubectl wait --for=condition=ready pod -l app=gateway -n budgeometre --timeout=180s

echo "  - Ingress..."
kubectl apply -f k8s/ingress.yaml

echo "  - HPA..."
kubectl apply -f k8s/hpa.yaml

echo "  - Network Policy..."
kubectl apply -f k8s/network-policy.yaml

# 7. Afficher le statut
echo ""
echo "=========================================="
echo "  Statut du déploiement"
echo "=========================================="
echo ""
kubectl get pods -n budgeometre
echo ""
kubectl get services -n budgeometre
echo ""
kubectl get ingress -n budgeometre

# 8. Configurer /etc/hosts
echo ""
echo "=========================================="
echo "  Configuration accès"
echo "=========================================="
MINIKUBE_IP=$(minikube ip)
echo ""
echo ">>> Exécutez cette commande pour ajouter l'entrée DNS :"
echo ""
echo "echo \"$MINIKUBE_IP budgeometre.local\" | sudo tee -a /etc/hosts"
echo ""
echo ">>> Puis accédez à : http://budgeometre.local"
echo ""
echo "=========================================="
echo "  Déploiement terminé !"
echo "=========================================="