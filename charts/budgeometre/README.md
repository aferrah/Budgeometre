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

```bash
minikube addons enable ingress
```

Cette commande active un contrôleur dans Minikube pour transformer les noms de domaine en accès vers les services internes.

#### 2) Préparation des images

A garder ouvert dans un terminal séparé.

```bash
eval $(minikube docker-env)
```


#### 3) Déploiement du Chart

```bash
helm install budgeometre ./budgeometre-chart
```

#### 4) Accès à l'application

Dans un terminal séparé, lancez le tunnel.

```bash
minikube tunnel
```

L'application est alors accessible sur : **http://budgeometre.local**


---

## Maintenance et debug

#### 1) État global du cluster

```bash
kubectl get all -n budgeometre
```

#### 2) Surveiller l'autoscaling

```bash
kubectl get hpa -n budgeometre
```
