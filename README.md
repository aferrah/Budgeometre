# Budgeometre

Application web de gestion de budget personnel développée avec Flask. Suivez vos dépenses, définissez des objectifs d'épargne et visualisez vos finances en temps réel avec des graphiques interactifs.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-Latest-green.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)

---

## Table des Matières

- [À propos](#à-propos)
- [Fonctionnalités principales](#fonctionnalités-principales)
- [Technologies utilisées](#technologies-utilisées)
- [Installation](#installation)
- [Guide d'utilisation](#guide-dutilisation)
  - [Gestion des catégories](#1-gestion-des-catégories)
  - [Gestion des transactions](#2-gestion-des-transactions)
  - [Objectifs d'épargne](#3-objectifs-dépargne)
  - [Archives mensuelles](#4-archives-mensuelles)

---

## À propos

**Budgeomètre** est une application web de gestion budgétaire qui permet de gérer efficacement vos finances personnelles. L'application stocke vos données dans une base SQLite locale (`budget.db`) incluant les catégories, transactions et objectifs d'épargne.

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
- **Base de données** : SQLite
- **Frontend** : HTML5, CSS3, JavaScript
- **Visualisation** : Graphiques interactifs (Chart.js ou équivalent)

---

## Installation

### Prérequis

- Python 3.8 ou version supérieure
- pip (gestionnaire de paquets Python)
- Git (optionnel)

#### 1) Installer les dépendances


```bash

pip install -r requirements.txt --break-system-packages
```

#### 2) Démarrer l'application (création automatique de la BD)

```bash

python3 app.py

```

La commande ci-dessus crée automatiquement les tables SQLite (fichier `budget.db`) et démarre un serveur de développement sur `http://127.0.0.1:5000`.


#### 3) Importer des données de test


Pour peupler rapidement la base avec des catégories, transactions et objectifs d'exemple, ouvrez dans votre navigateur :

```

http://127.0.0.1:5000/init-test-archives

```



Le point d'entrée `/init-test-archives` ajoute plusieurs catégories, transactions et objectifs sur 6 mois.



#### 4) Voir le site



Après avoir importé les données, visitez :


```

http://127.0.0.1:5000/

```



La page affiche les dernières transactions et un aperçu (pie-chart) calculé à partir des valeurs passées par le backend.


#### 5) Réinitialiser la base


Pour repartir de zéro, arrêtez le serveur et supprimez le fichier `budget.db` puis relancez `python3 app.py` et (optionnel) `/init-test-archives`.


```bash

rm budget.db

python3 app.py

```

Il vous est également possible de réinitialiser la base de donnés en cliquant sur le menu hamburger, puis de cliquer sur l'option **Réinitialiser la BDD** :

<img width="250" height="577" alt="image" src="https://github.com/user-attachments/assets/b3e8e2c5-184f-45f8-a3a0-39a1ba3844da" />


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
*
## Licence

Ce projet est sous licence MIT.

## Auteurs

TRIKI Wassim, PRETI- -LEVY Ruben, MARTIN Claire, HAMIDI Issam, BURET Amélie, FERRAH Anas



