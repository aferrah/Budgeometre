# Budgeomètre - Déploiement Kubernetes (helm)

---

## Table des Matières

- [Prérequis](#prérequis)
- [Installation Rapide](#installation-rapide)
- [Structure du Chart](#structure-du-chart)
- [Sécurité et Réseau](#sécurité-et-réseau)
- [Maintenance](#maintenance)


---

## Prérequis

- **Minikube** opérationnel.
- **Helm v3** installé.
- **Ingress Nginx** activé : `minikube addons enable ingress`.
- **Démon Docker** pointé sur Minikube : `eval $(minikube docker-env)`.

---

## Installation Rapide

#### 1) On lance le cluster

```bash
minikube start
```



#### 2) Préparation des images

A garder ouvert dans un terminal séparé.

```bash
eval $(minikube docker-env)
```


#### 3) Déploiement du Chart

```bash
helm install budgeometre ./charts/budgeometre -n budgeometre-v2 --create-namespace
```
On injecte ensuite les images (chaque commande doit être lancée seule)

```bash
minikube image load gateway:latest
```

```bash
minikube image load ecriture-service:latest
```

```bash
minikube image load lecture-service:latest
```


#### 4) Accès à l'application

Dans un terminal séparé, lancez le tunnel.

```bash
minikube tunnel
```
Dans un second:

```bash
kubectl port-forward service/gateway 8080:5000 -n budgeometre-v2
```

L'application est alors accessible sur : **http://localhost:8080**


---

## Maintenance et debug

#### 1) État global du cluster

```bash
kubectl get all -n budgeometre-v2
```

#### 2) Surveiller l'autoscaling

```bash
kubectl get hpa -n budgeometre-v2
```

#### 3) Vérifier les services

```bash
kubectl get pods -n budgeometre-v2
```
