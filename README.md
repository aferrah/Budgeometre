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

### 2. Transactions

#### 2.1 Ajout des revenus

#### 2.2 Ajout des dépenses

Pour ajouter une dépense, se rendre la page d'accueil et cliquer sur le bouton **Ajouter un transaction** :

<img width="1352" height="366" alt="image" src="https://github.com/user-attachments/assets/e05b0fe0-822f-4a96-9e39-2f15f8da0348" />

#### 2.3 Affichage des dépenses

### 3. Objectifs d'épargne

#### 3.1 Ajout d'objectifs d'épargne

### 4. Archives mensuelles

