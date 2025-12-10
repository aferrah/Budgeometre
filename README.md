# Budgeomètre



---



## **Table des Matières**

1. [Développement local](#développement-local)
2. [Fonctionnalités](#fonctionnalités)



---



## Développement local



Ce projet Flask stocke des `Categorie`, `Transaction` et `Objectif` dans une base SQLite locale (`budget.db`).



**But de ce README :** expliquer comment installer les dépendances, démarrer l'application et importer des données de test via la page `/init-test`.



**Prerequis :**

- Python 3.8+ installé

- `git` (optionnel)





**1) Installer les dépendances**



```bash

pip install -r requirements.txt --break-system-packages

```



**2) Démarrer l'application (création automatique de la BD)**



```bash

python3 app.py

```



La commande ci-dessus crée automatiquement les tables SQLite (fichier `budget.db`) et démarre un serveur de développement sur `http://127.0.0.1:5000`.



**3) Importer des données de test**



Pour peupler rapidement la base avec des catégories, transactions et objectifs d'exemple, ouvrez dans votre navigateur :



```

http://127.0.0.1:5000/init-test

```



Le point d'entrée `/init-test` ajoute plusieurs catégories, transactions et objectifs et renvoie un message de confirmation.



**4) Voir le site**



Après avoir importé les données, visitez :



```

http://127.0.0.1:5000/

```



La page affiche les dernières transactions et un aperçu (pie-chart) calculé à partir des valeurs passées par le backend.



**5) Réinitialiser la base**



Pour repartir de zéro, arrêtez le serveur et supprimez le fichier `budget.db` puis relancez `python3 app.py` et (optionnel) `/init-test`.



```bash

rm budget.db

python3 app.py

```



## Fonctionnalités

### 1. Catégorie

#### 1.1 Ajout des catégories

Renseigner le nom, la description et la couleur puis appuyer sur **+**.

<img width="1340" height="494" alt="image" src="https://github.com/user-attachments/assets/743b6a20-e7db-4480-92d7-f24366e714c8" />

On peut rajouter une limite de budget mensuel en cochant la case **Définir une limite de budget mensuel**.
Si la limite dépasse notre revenu, le message suivant apparaît:

<img width="1340" height="252" alt="image" src="https://github.com/user-attachments/assets/c15f8559-3a4c-444c-be67-192c34b122e6" />


#### 1.2 Supprimer / modifier une catégorie

Supprimez la catégorie en sélectionnant sur la corbeille.

<img width="1616" height="223" alt="image" src="https://github.com/user-attachments/assets/1463f2c3-2b42-4cf0-a399-04ed569e6107" />

Celle-ci doit être absente de la liste des catégories après coup.

Modifiez la en sélectionnant le crayon.


#### 1.3 Statistiques par catégorie

Les statistiques des dépenses sont visibles depuis **budget dashboard**.

<img width="1213" height="838" alt="image" src="https://github.com/user-attachments/assets/c6335070-adb0-4193-b20d-60f2a4e1fc97" />

Pour accéder aux statistiques individuelles des catégories, survolez la catégorie sur le graphe:

<img width="1168" height="818" alt="image" src="https://github.com/user-attachments/assets/ed90b30a-193b-49fc-aee1-e250561fea06" />

Vous aurez alors accès aux statistiques pour cette catégories.

<img width="1961" height="859" alt="image" src="https://github.com/user-attachments/assets/dd2a19fe-6e87-45e4-ab8e-e6cf3ae77432" />

---

### 2. Transactions
Pour ajouter une dépense ou un revenu, se rendre sur la page d'accueil et cliquer sur le bouton **Ajouter une transaction** :

<img width="600" height="215" alt="image" src="https://github.com/user-attachments/assets/43def96e-a3a8-4120-a5fb-f0a024587762" />


#### 2.1 Ajout des revenus

Pour ajouter un revenu, cliquer sur le bouton **Revenu**, remplir les informations puis cliquer sur le bouton **Enregistrer** :

<img width="600" height="811" alt="image" src="https://github.com/user-attachments/assets/ed463ce8-62ee-4d9a-85ca-1a1c3104ea21" />

#### 2.2 Ajout des dépenses



#### 2.3 Affichage des dépenses


#### 2.4 Filtrage par date

### 3. Objectifs d'épargne

#### 3.1 Ajout d'objectifs d'épargne

### 4. Archives mensuelles

