# ANCIEN READ ME    


# Déploiement Kubernetes

## Prérequis

- Minikube installé et démarré
- Docker installé
- kubectl installé et configuré



## Déploiement

### 1. Démarrer Minikube

```bash
minikube start --driver=docker
```

### 2. Configurer Docker pour utiliser le daemon Minikube

```bash
eval $(minikube docker-env)
```

### 3. Build les images Docker

```bash
# Gateway
docker build -t gateway:latest ./gateway

# Service Écriture
docker build -t ecriture-service:latest ./services/ecriture

# Service Lecture
docker build -t lecture-service:latest ./services/lecture
```

### 4. Vérifier que les images sont dans Minikube

```bash
docker images | grep -E "gateway|ecriture|lecture"
```

### 5. Appliquer les manifests Kubernetes (dans l'ordre)

```bash
# Créer le namespace
kubectl apply -f k8s/namespace.yaml

# Créer les ConfigMaps et Secrets
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/postgres-init-configmap.yaml

# Créer le PVC pour PostgreSQL
kubectl apply -f k8s/postgres-pvc.yaml

# Déployer PostgreSQL
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml

# Attendre que PostgreSQL soit ready
kubectl wait --for=condition=ready pod -l app=postgres -n budgeometre --timeout=120s

# Déployer les services
kubectl apply -f k8s/ecriture-deployment.yaml
kubectl apply -f k8s/ecriture-service.yaml
kubectl apply -f k8s/lecture-deployment.yaml
kubectl apply -f k8s/lecture-service.yaml

# Attendre que les services soient ready
kubectl wait --for=condition=ready pod -l app=ecriture-service -n budgeometre --timeout=120s
kubectl wait --for=condition=ready pod -l app=lecture-service -n budgeometre --timeout=120s

# Déployer le gateway
kubectl apply -f k8s/gateway-deployment.yaml
kubectl apply -f k8s/gateway-service.yaml
```

### 6. Ou tout déployer d'un coup

```bash
kubectl apply -f k8s/
```

## Vérification du déploiement

### Vérifier les pods

```bash
kubectl get pods -n budgeometre
```

Résultat attendu:
```
NAME                                READY   STATUS    RESTARTS   AGE
postgres-xxxxxxxxx-xxxxx            1/1     Running   0          2m
ecriture-service-xxxxxxxxx-xxxxx    1/1     Running   0          1m
ecriture-service-xxxxxxxxx-xxxxx    1/1     Running   0          1m
lecture-service-xxxxxxxxx-xxxxx     1/1     Running   0          1m
lecture-service-xxxxxxxxx-xxxxx     1/1     Running   0          1m
gateway-xxxxxxxxx-xxxxx             1/1     Running   0          1m
gateway-xxxxxxxxx-xxxxx             1/1     Running   0          1m
```

### Vérifier les services

```bash
kubectl get services -n budgeometre
```

### Vérifier les logs

```bash
# Logs du gateway
kubectl logs -f deployment/gateway -n budgeometre

# Logs du service écriture
kubectl logs -f deployment/ecriture-service -n budgeometre

# Logs du service lecture
kubectl logs -f deployment/lecture-service -n budgeometre

# Logs de PostgreSQL
kubectl logs -f deployment/postgres -n budgeometre
```

## Accéder à l'application

### Via NodePort

```bash
# Obtenir l'URL
minikube service gateway -n budgeometre --url
```

L'application sera accessible sur: `http://<MINIKUBE_IP>:30000`

### Via Port-Forward (alternative)

```bash
kubectl port-forward service/gateway 5000:5000 -n budgeometre
```

L'application sera accessible sur: `http://localhost:5000`

## Commandes utiles

### Restart un deployment

```bash
kubectl rollout restart deployment/gateway -n budgeometre
kubectl rollout restart deployment/ecriture-service -n budgeometre
kubectl rollout restart deployment/lecture-service -n budgeometre
```

### Scaler un deployment

```bash
kubectl scale deployment/gateway --replicas=3 -n budgeometre
```

### Voir les détails d'un pod

```bash
kubectl describe pod <POD_NAME> -n budgeometre
```

### Accéder à un pod en shell

```bash
kubectl exec -it <POD_NAME> -n budgeometre -- /bin/sh
```

### Voir les events

```bash
kubectl get events -n budgeometre --sort-by='.lastTimestamp'
```

## Nettoyage

### Supprimer tout le déploiement

```bash
kubectl delete namespace budgeometre
```

### Ou supprimer fichier par fichier

```bash
kubectl delete -f k8s/
```

### Arrêter Minikube

```bash
minikube stop
```

### Supprimer Minikube

```bash
minikube delete
```

## Modifier les secrets

Pour changer les mots de passe et secrets:

1. Éditer le fichier `k8s/secret.yaml`
2. Mettre à jour aussi `k8s/configmap.yaml` si nécessaire
3. Réappliquer:

```bash
kubectl delete secret budgeometre-secrets -n budgeometre
kubectl apply -f k8s/secret.yaml
kubectl rollout restart deployment/postgres -n budgeometre
kubectl rollout restart deployment/ecriture-service -n budgeometre
kubectl rollout restart deployment/lecture-service -n budgeometre
kubectl rollout restart deployment/gateway -n budgeometre
```

## Monitoring

### Dashboard Kubernetes

```bash
minikube dashboard
```

### Voir les ressources utilisées

```bash
kubectl top pods -n budgeometre
kubectl top nodes
```

##  Troubleshooting

### Les pods ne démarrent pas

```bash
# Vérifier les events
kubectl get events -n budgeometre --sort-by='.lastTimestamp'

# Vérifier les logs
kubectl logs <POD_NAME> -n budgeometre

# Décrire le pod pour voir les erreurs
kubectl describe pod <POD_NAME> -n budgeometre
```

### Les images ne sont pas trouvées

```bash
# Vérifier que vous utilisez le daemon Docker de Minikube
eval $(minikube docker-env)

# Rebuild les images
docker build -t gateway:latest ./gateway
docker build -t ecriture-service:latest ./services/ecriture
docker build -t lecture-service:latest ./services/lecture
```

### PostgreSQL ne démarre pas

```bash
# Vérifier le PVC
kubectl get pvc -n budgeometre

# Vérifier les logs
kubectl logs deployment/postgres -n budgeometre

# Supprimer et recréer
kubectl delete deployment postgres -n budgeometre
kubectl delete pvc postgres-pvc -n budgeometre
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/postgres-deployment.yaml
```

##  Notes importantes

- **ImagePullPolicy**: Configuré sur `Never` pour utiliser les images locales de Minikube
- **NodePort**: Le gateway est exposé sur le port 30000
- **Réplicas**: 2 réplicas pour gateway, écriture et lecture (scalabilité)
- **Health checks**: Configurés sur tous les services
- **Init containers**: Attendent que les dépendances soient prêtes avant de démarrer

## Workflow de développement

1. Faire vos modifications de code
2. Rebuild l'image Docker concernée
3. Restart le deployment correspondant
4. Vérifier les logs

```bash
# Exemple pour le gateway
docker build -t gateway:latest ./gateway
kubectl rollout restart deployment/gateway -n budgeometre
kubectl logs -f deployment/gateway -n budgeometre
```