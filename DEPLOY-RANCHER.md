# Déploiement sur Cluster Rancher Distant

Ce guide explique comment déployer l'application Budgeomètre sur un cluster Kubernetes Rancher distant.

## Prérequis

1. **Docker Hub Account**
   - Créer un compte sur [hub.docker.com](https://hub.docker.com)
   - Se connecter: `docker login`

2. **Configuration kubectl**
   - Vérifier la connexion au cluster Rancher:
     ```bash
     kubectl config use-context local
     kubectl get nodes
     ```

## Étapes de Déploiement

### 1. Configuration Docker Hub

Avant le déploiement, configurez votre nom d'utilisateur Docker Hub:

```bash
export DOCKER_USERNAME="votre-username-dockerhub"
```

**Ou** éditez directement le script [deploy-rancher.sh](deploy-rancher.sh) ligne 14:
```bash
DOCKER_USERNAME="${DOCKER_USERNAME:-votre-username-dockerhub}"
```

### 2. Connexion à Docker Hub

```bash
docker login
```

Entrez votre username et password Docker Hub.

### 3. Vérification du cluster

Assurez-vous d'être connecté au bon cluster:

```bash
kubectl config current-context
# Devrait afficher: local

kubectl get nodes
# Devrait lister les nœuds du cluster Rancher
```

### 4. Lancement du déploiement

```bash
# Rendre le script exécutable
chmod +x deploy-rancher.sh

# Lancer le déploiement
./deploy-rancher.sh
```

Le script va:
1. Vérifier la connexion au cluster
2. Builder les 3 images Docker (gateway, écriture, lecture)
3. Pousser les images vers Docker Hub
4. Créer des manifests Kubernetes adaptés
5. Déployer l'application sur le cluster
6. Attendre que tous les pods soient prêts

### 5. Vérification du déploiement

```bash
# Vérifier les pods
kubectl get pods -n budgeometre

# Vérifier les services
kubectl get services -n budgeometre

# Vérifier les HPA
kubectl get hpa -n budgeometre
```

## Accès à l'application

### Option 1: Port Forwarding (Recommandé)

```bash
kubectl port-forward -n budgeometre service/gateway 8080:80
```

Accédez à: **http://localhost:8080**

### Option 2: Via Ingress

Si un Ingress est configuré sur votre cluster:

```bash
# Récupérer l'URL de l'Ingress
kubectl get ingress -n budgeometre

# Ou via Rancher UI
# Aller dans: Workloads > Load Balancing
```

## Troubleshooting

### Images Docker non trouvées

Vérifiez que votre DOCKER_USERNAME est correct:
```bash
echo $DOCKER_USERNAME
```

### Permission denied sur Docker Hub

Reconnectez-vous:
```bash
docker logout
docker login
```

### Pods en erreur ImagePullBackOff

Les images ne sont pas accessibles. Vérifiez:
```bash
# Vérifier que les images existent sur Docker Hub
docker search votre-username/budgeometre-gateway

# Vérifier les logs du pod
kubectl logs -n budgeometre <pod-name>
```

### Cluster non accessible

Vérifiez votre contexte kubectl:
```bash
kubectl config get-contexts
kubectl config use-context local
```

## Nettoyage

Pour supprimer l'application:

```bash
kubectl delete namespace budgeometre
```

## Différences avec le déploiement Minikube

| Aspect | Minikube (local) | Rancher (distant) |
|--------|------------------|-------------------|
| Images | Locales (`imagePullPolicy: Never`) | Docker Hub (`imagePullPolicy: Always`) |
| Registry | Daemon Docker Minikube | Docker Hub public |
| Commandes | `minikube start`, `minikube addons` | Commandes kubectl uniquement |
| Accès | `minikube tunnel` ou port-forward | Ingress ou port-forward |

## Scripts disponibles

- [deploy.sh](deploy.sh) - Déploiement local sur Minikube
- **[deploy-rancher.sh](deploy-rancher.sh)** - Déploiement sur cluster Rancher distant
- [cleanup.sh](cleanup.sh) - Nettoyage des ressources
