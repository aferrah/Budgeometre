# Budgeomètre

Application web de gestion de budget personnel développée avec Flask. Suivez vos dépenses, définissez des objectifs d'épargne et visualisez vos finances en temps réel avec des graphiques interactifs.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-Latest-green.svg)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791.svg)

---

## Table des Matières

- [À propos](#à-propos)
- [Fonctionnalités principales](#fonctionnalités-principales)
- [Technologies utilisées](#technologies-utilisées)
- [Architecture](#architecture)
- [Structure du projet](#structure-du-projet)
- [Déploiement Kubernetes](#déploiement-kubernetes)
- [Guide d'utilisation](#guide-dutilisation)
  - [Gestion des catégories](#1-gestion-des-catégories)
  - [Gestion des transactions](#2-gestion-des-transactions)
  - [Objectifs d'épargne](#3-objectifs-dépargne)
  - [Archives mensuelles](#4-archives-mensuelles)

---

## À propos

**Budgeomètre** est une application web de gestion budgétaire qui permet de gérer efficacement vos finances personnelles. L'application utilise une architecture microservices déployée sur Kubernetes avec PostgreSQL pour stocker les catégories, transactions et objectifs d'épargne.

## Fonctionnalités principales

- **Gestion des catégories** : Créez et personnalisez vos catégories de dépenses avec des couleurs distinctives et des limites de budget mensuelles
- **Suivi des transactions** : Enregistrez facilement vos revenus et dépenses avec des descriptions détaillées
- **Tableaux de bord interactifs** : Visualisez vos statistiques financières avec des graphiques dynamiques
- **Objectifs d'épargne** : Définissez et suivez vos objectifs financiers avec des indicateurs de progression
- **Archives mensuelles** : Conservez un historique complet de vos finances et consultez vos données passées
- **Filtrage et tri avancés** : Recherchez et organisez vos transactions selon différents critères
- **Interface responsive** : Accédez à vos données depuis n'importe quel appareil

## Technologies utilisées

- **Backend** : Flask (Python)
- **Base de données** : PostgreSQL
- **Frontend** : HTML5, CSS3, JavaScript
- **Visualisation** : Graphiques interactifs (Chart.js ou équivalent)
- **Orchestration** : Kubernetes / Minikube
- **Architecture** : Microservices (Gateway, Service Écriture, Service Lecture)

---

## Architecture

Le projet Budgeomètre utilise une **architecture microservices** basée sur le pattern **CQRS** (Command Query Responsibility Segregation) qui sépare les opérations de lecture et d'écriture pour optimiser les performances et la scalabilité.

### Schéma d'architecture

<p align="center">
  <img
    src="https://github.com/user-attachments/assets/237feff4-17f7-4608-96ef-86cfed2a3815"
    alt="archi_Budgeometre_k8s"
    width="400"
    style="border-radius: 16px;"
  />
</p>

---
### Architecture Kubernetes
<p align="center">
  <img
    width="482" 
    height="1501" 
    alt="archi_microservices" 
    src="https://github.com/user-attachments/assets/d3d3c88d-513b-49f8-8888-114f6f94cc20"
    style="border-radius: 16px;3
</p>

<br><br>


### Flux de données

1. **L'utilisateur** accède à l'interface via le **Gateway** (port 5000)
2. Le **Gateway** affiche l'interface web (HTML/CSS/JS)
3. Pour les **opérations de lecture** : Gateway → Service Lecture → PostgreSQL → Retour
4. Pour les **opérations d'écriture** : Gateway → Service Écriture → PostgreSQL → Retour
5. Tous les services communiquent sur le réseau **budgeometre-network**

### Composants

#### Gateway

La Gateway constitue le **point d’entrée unique** de l’application. Elle est responsable de la gestion de l’interface utilisateur, notamment le rendu des templates HTML, et joue un rôle central dans l’orchestration des requêtes en les redirigeant vers les services appropriés. Elle expose le **port 5000** afin de permettre l’accès à l’application.

#### Service Écriture

Ce service est dédié à la gestion de toutes les **opérations d’écriture**, incluant la création, la mise à jour et la suppression des données (CREATE, UPDATE, DELETE). Il traite les modifications liées aux catégories, aux transactions et aux objectifs, garantissant ainsi la cohérence des données métier. Il est accessible via le **port 5001**.

#### Service Lecture

Optimisé pour les **opérations de consultation (READ)**, ce service se concentre sur la lecture des données et la génération des statistiques ainsi que des tableaux de bord. Il prend également en charge la gestion des archives et de l’historique, offrant une vue analytique complète des données. Il expose le **port 5002**.

#### Base de données PostgreSQL

La base de données PostgreSQL assure le **stockage persistant** de l’ensemble des données de l’application. Elle est déployée sous forme de **StatefulSet** afin de garantir la persistance et la stabilité des données, même en cas de redémarrage des pods. Elle expose le **port 5432**.

---

## Structure du projet

Le projet Budgeomètre suit une architecture microservices organisée en plusieurs modules distincts. Le **gateway** gère l'interface utilisateur et orchestre les requêtes, le **service écriture** traite toutes les opérations de création, modification et suppression, tandis que le **service lecture** optimise les requêtes de consultation. Cette séparation permet une meilleure scalabilité et maintenabilité du code.

```
Budgeometre/
├── cleanup.sh                    
├── deploy.sh                     
├── docker-compose.yml            
├── README.md                    
├── requirements.txt              
│
├── database/                    
│   ├── init.sql                 
│   └── seed_data.sql           
│
├── gateway/                    
│   ├── app.py                 
│   ├── config.py                
│   ├── Dockerfile              
│   ├── requirements.txt          
│   ├── routes/                   
│   │   ├── __init__.py
│   │   └── views.py             
│   ├── static/                  
│   │   ├── css/                
│   │   ├── js/                   
│   │   └── widget/              
│   └── templates/                
│       ├── base.html           
│       ├── index.html            
│       ├── add-expense.html      
│       ├── archive-detail.html   
│       ├── archives.html         
│       ├── budget-dashboard.html 
│       ├── categories.html      
│       ├── detail-depense.html 
│       ├── mes-depenses.html    
│       ├── mes-objectifs.html    
│       ├── modifier-categorie.html    
│       └── modifier-transaction.html  
│
├── services/                    
│   ├── ecriture/                 
│   │   ├── app.py                
│   │   ├── routes.py            
│   │   ├── seed_data.py        
│   │   ├── Dockerfile            
│   │   └── requirements.txt      
│   └── lecture/                  
│       ├── app.py                
│       ├── routes.py             
│       ├── Dockerfile            
│       └── requirements.txt   
│
├── shared/                      
│   ├── config.py                 
│   ├── extensions.py             
│   └── models/                   
│       ├── __init__.py
│       ├── archive.py            
│       ├── categorie.py         
│       ├── objectif.py           
│       └── transaction.py        
│
└── k8s/                          
    ├── README.md                
    ├── namespace.yaml           
    ├── configmap.yaml            
    ├── secret.yaml               
    ├── postgres-init-configmap.yaml   
    ├── postgres-statefulset.yaml      
    ├── postgres-deployment.yaml      
    ├── postgres-service.yaml         
    ├── postgres-pvc.yaml             
    ├── ecriture-deployment.yaml      
    ├── ecriture-service.yaml        
    ├── lecture-deployment.yaml       
    ├── lecture-service.yaml         
    ├── gateway-deployment.yaml       
    ├── gateway-service.yaml          
    ├── ingress.yaml                 
    ├── hpa.yaml                      
    └── network-policy.yaml           
```

---

## Déploiement Kubernetes

#### Prérequis

- Minikube installé
- Docker installé (Docker Desktop sur Windows)e
- kubectl installé et configuré

Si vous êtes sur Windows, assurez-vous que Docker Desktop est installé et lancé avant de lancer le script de déploiement.

#### Déploiement automatique avec le script

Le script `deploy.sh` automatise l'ensemble du déploiement sur Kubernetes :

```bash
./deploy.sh
```

Ce script effectue les opérations suivantes :

1. Démarre Minikube avec le driver Docker
2. Active les addons Ingress et metrics-server
3. Configure Docker pour utiliser le daemon Minikube
4. Build les images Docker des microservices :
   - Gateway
   - Service Écriture
   - Service Lecture
5. Déploie les ressources Kubernetes dans l'ordre :
   - Namespace `budgeometre`
   - ConfigMap et Secret
   - PostgreSQL (StatefulSet)
   - Services Écriture et Lecture
   - Gateway
   - Ingress
   - HPA (Horizontal Pod Autoscaler)
   - Network Policy
6. Attend que tous les pods soient prêts
7. Affiche le statut du déploiement

#### Accéder à l'application

**Option 1 : Port forwarding (recommandé pour Windows)**

La méthode la plus simple sur Windows est d'utiliser le port forwarding kubectl :

```bash
# Forward le port 80 du gateway vers le port 8080 local
kubectl port-forward -n budgeometre service/gateway 8080:5000
```

Ouvrez ensuite votre navigateur et accédez à : **http://localhost:8080**

**Option 2 : Configuration DNS avec le fichier hosts et minikube tunnel**

Sur Windows avec le driver Docker, l'IP de Minikube n'est pas directement accessible. Il faut utiliser `minikube tunnel` pour créer un pont réseau :

```powershell
# 1- Activer l'addon Ingress si pas déjà fait
minikube addons enable ingress

# 2- Lancer minikube tunnel dans un terminal séparé (en administrateur)
minikube tunnel
```
<img width="548" height="223" alt="image" src="https://github.com/user-attachments/assets/0891f80a-81f3-439e-8c2e-c607299c5218" />


**Important** : Laissez ce terminal ouvert tant que vous voulez accéder à l'application.

```powershell
# 3- Ouvrir le fichier hosts en administrateur
notepad C:\Windows\System32\drivers\etc\hosts

# 4- Ajouter cette ligne à la fin (notez 127.0.0.1, pas l'IP de Minikube)
127.0.0.1 budgeometre.local
```

```powershell
# 5- Vider le cache DNS
ipconfig /flushdns
```

Accédez ensuite à : **http://budgeometre.local**
</br>
<img width="628" height="482" alt="image" src="https://github.com/user-attachments/assets/2aebcaec-afb5-47d2-ab09-a1174e3dfeee" />


> **Note** : Cette méthode nécessite de laisser `minikube tunnel` actif en arrière-plan. Si vous préférez une solution sans tunnel, utilisez l'Option 1 (port-forwarding) qui est plus simple et tout aussi efficace.

**Option 3 : Accès direct via minikube service (alternative)**

```bash
minikube service gateway -n budgeometre
```

Cette commande ouvre automatiquement votre navigateur avec l'URL correcte.

#### Peupler la base de données avec 6 mois de données de test

Pour faciliter les tests et la démonstration, un script Python permet d'injecter automatiquement 6 mois de données réalistes dans la base PostgreSQL.

**Contenu injecté :**
- 9 catégories (Alimentation, Transport, Loisirs, Logement, Santé, Shopping, Abonnements, Salaire, Autre)
- Transactions mensuelles variées (revenus, dépenses fixes et variables)
- 3 objectifs d'épargne avec progression
- Archives mensuelles pour chaque mois

**Exécuter le script :**

```bash
# 1. Identifier le pod du service écriture
kubectl get pods -n budgeometre | grep ecriture

# 2. Exécuter le script de seed
kubectl exec -it <nom-du-pod-ecriture> -n budgeometre -- python seed_data.py
```

Le script affiche sa progression et confirme la création de chaque élément :

<img width="490" height="365" alt="image" src="https://github.com/user-attachments/assets/d6705b9f-2168-4c8f-baf1-7965ff7483c0" />

Rafraîchissez ensuite l'application dans votre navigateur pour voir les données.

#### Vérifier le déploiement

```bash
# Voir les pods
kubectl get pods -n budgeometre

# Voir les services
kubectl get services -n budgeometre

# Voir l'ingress
kubectl get ingress -n budgeometre

# Voir les logs d'un pod
kubectl logs <nom-du-pod> -n budgeometre
```

#### Nettoyer le déploiement

Pour supprimer l'application de Kubernetes :

```bash
./cleanup.sh
```

Ou manuellement :

```bash
kubectl delete namespace budgeometre
minikube stop
```

---

## Guide d'utilisation

### 1. Gestion des Catégories

#### 1.1 Créer une catégorie

Renseigner le nom, la description et la couleur puis appuyer sur **+**.

<img width="1340" height="494" alt="image" src="https://github.com/user-attachments/assets/743b6a20-e7db-4480-92d7-f24366e714c8" />

On peut rajouter une limite de budget mensuel en cochant la case **Définir une limite de budget mensuel**.
Si la limite dépasse notre revenu, le message suivant apparaît:

<img width="1340" height="252" alt="image" src="https://github.com/user-attachments/assets/c15f8559-3a4c-444c-be67-192c34b122e6" />


#### 1.2 Modifier ou supprimer une catégorie

Supprimez la catégorie en sélectionnant sur la corbeille.

<img width="1616" height="223" alt="image" src="https://github.com/user-attachments/assets/1463f2c3-2b42-4cf0-a399-04ed569e6107" />

Celle-ci doit être absente de la liste des catégories après coup.

Modifiez la en sélectionnant le crayon.


#### 1.3 Consulter les statistiques par catégorie

Les statistiques des dépenses sont visibles depuis **budget dashboard**.

<img width="600" height="838" alt="image" src="https://github.com/user-attachments/assets/c6335070-adb0-4193-b20d-60f2a4e1fc97" />

Pour accéder aux statistiques individuelles des catégories, survolez la catégorie sur le graphe:

<img width="600" height="818" alt="image" src="https://github.com/user-attachments/assets/ed90b30a-193b-49fc-aee1-e250561fea06" />

Vous aurez alors accès aux statistiques pour cette catégories.

<img width="600" height="859" alt="image" src="https://github.com/user-attachments/assets/dd2a19fe-6e87-45e4-ab8e-e6cf3ae77432" />

---

### 2. Gestion des transactions
Pour ajouter une dépense ou un revenu, se rendre sur la page d'accueil et cliquer sur le bouton **Ajouter une transaction** :

<img width="600" height="215" alt="image" src="https://github.com/user-attachments/assets/43def96e-a3a8-4120-a5fb-f0a024587762" />


#### 2.1 Enregistrer un revenu

Pour ajouter un revenu, cliquez sur l'onglet **Revenu**, renseignez les informations requises, puis cliquez sur **Enregistrer** :

<img width="500" height="811" alt="image" src="https://github.com/user-attachments/assets/ed463ce8-62ee-4d9a-85ca-1a1c3104ea21" />

#### 2.2 Enregistrer une dépense

Pour ajouter une dépense, cliquez sur l'onglet **Dépense**, renseignez les informations requises (montant, catégorie, date, description), puis cliquez sur **Enregistrer** :

<img width="500" height="756" alt="image" src="https://github.com/user-attachments/assets/3a01ce3e-ce3c-4dc3-90d6-6f68307330b1" />

#### 2.3 Consulter l'historique des transactions

La page d'accueil affiche automatiquement toutes les transactions des 3 derniers mois dans un tableau récapitulatif :
<img width="600" height="827" alt="image" src="https://github.com/user-attachments/assets/1d429150-2fb1-4e2c-b06e-a930c23d7953" />


#### 2.4 Filtrer et trier les transactions

Vous pouvez facilement organiser vos transactions à l'aide des outils de tri et de filtrage :
<img width="600" height="205" alt="image" src="https://github.com/user-attachments/assets/69777ffb-4a7d-452e-bfa7-aa12999fc882" />

- **Tri** : Cliquez sur l'en-tête d'une colonne pour trier les données
- **Filtrage** : Utilisez la barre de recherche pour filtrer par mot-clé

---

### 3. Objectifs d'Épargne

#### 3.1 Définir un objectif d'épargne

Pour créer un nouvel objectif, renseignez les informations suivantes :

- **Montant cible** : Le montant que vous souhaitez atteindre
- **Description** : L'objectif de cette épargne
- **Fréquence** : Périodicité de contribution (mensuelle, hebdomadaire, etc.)
- **Catégorie associée** : La catégorie budgétaire liée à cet objectif

Cliquez ensuite sur le bouton **Ajouter** pour enregistrer votre objectif.

<img width="600" height="1218" alt="image" src="https://github.com/user-attachments/assets/2131d045-7e76-4164-97c2-5ddf4804cf4e" />


#### 3.2 Suivre vos objectifs d'épargne

Tous vos objectifs d'épargne sont regroupés et suivis sur la page **Mes Objectifs d'Épargne**. Vous y trouverez pour chaque objectif :

L'objectif que vous venez de renseigner doit se retrouver sur la page **Mes Objectifs d'épargne**

<img width="600" height="590" alt="image" src="https://github.com/user-attachments/assets/18803176-83a5-46ec-848b-da833e2dd6ac" />

---

### 4. Archives Mensuelles

#### 4.0 Accéder aux archives

Pour consulter l'historique de vos transactions au-delà des 3 derniers mois, utilisez la fonctionnalité **Archives mensuelles** : 

<img width="600" height="166" alt="image" src="https://github.com/user-attachments/assets/2418a748-c0b2-44e0-aaa3-652108043484" />


Sélectionnez le mois que vous souhaitez archiver, puis cliquez sur le bouton **Archiver** :

<img width="600" height="499" alt="image" src="https://github.com/user-attachments/assets/5f773730-7844-4e44-bf4d-7fbb35d6a9b3" />


#### 4.1 Consulter les détails d'une archive

Pour accéder aux informations détaillées d'un mois archivé, cliquez sur le bouton **Voir les détails** :

<img width="600" height="306" alt="image" src="https://github.com/user-attachments/assets/c24fde91-f9fa-439c-a28a-7ba9a4f6a0a6" />


#### 4.2 Masquer ou afficher une archive

Pour masquer une archive, cliquer sur le bouton avec l’icône d’oeil barré :

<img width="600" height="360" alt="image" src="https://github.com/user-attachments/assets/1689ffcc-e117-4918-90d3-2758ae0b2d27" />

Pour démasquer une archive, cliquer sur le bouton oeil.

Résultat :

<img width="600" height="237" alt="image" src="https://github.com/user-attachments/assets/e5924db5-f385-4203-a092-556c67feec04" />


#### 4.3 Supprimer définitivement une archive

Pour supprimer de manière permanente une archive et toutes ses données associées, cliquez sur l'icône de corbeille :

<img width="1248" height="360" alt="image" src="https://github.com/user-attachments/assets/63c4e552-0406-44a4-8b24-a107c2b0a290" />


> **Attention** : Cette action est irréversible. Elle supprime définitivement toutes les données du mois sélectionné de la base de données. Une confirmation vous sera demandée pour éviter toute suppression accidentelle.

---

## Licence

Ce projet est sous licence MIT.

## Équipe de développement

**Télécom SudParis - FISA 2A**

- TRIKI Wassim
- PRETI- -LEVY Ruben
- MARTIN Claire
- HAMIDI Issam
- BURET Amélie
- FERRAH Anas

*Projet réalisé en 2025-2026*











