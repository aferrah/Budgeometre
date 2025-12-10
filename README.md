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

---

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

<img width="600" height="838" alt="image" src="https://github.com/user-attachments/assets/c6335070-adb0-4193-b20d-60f2a4e1fc97" />

Pour accéder aux statistiques individuelles des catégories, survolez la catégorie sur le graphe:

<img width="600" height="818" alt="image" src="https://github.com/user-attachments/assets/ed90b30a-193b-49fc-aee1-e250561fea06" />

Vous aurez alors accès aux statistiques pour cette catégories.

<img width="600" height="859" alt="image" src="https://github.com/user-attachments/assets/dd2a19fe-6e87-45e4-ab8e-e6cf3ae77432" />

---

### 2. Transactions
Pour ajouter une dépense ou un revenu, se rendre sur la page d'accueil et cliquer sur le bouton **Ajouter une transaction** :

<img width="600" height="215" alt="image" src="https://github.com/user-attachments/assets/43def96e-a3a8-4120-a5fb-f0a024587762" />


#### 2.1 Ajout des revenus

Pour ajouter un revenu, cliquer sur le bouton **Revenu**, remplir les informations puis cliquer sur le bouton **Enregistrer** :

<img width="500" height="811" alt="image" src="https://github.com/user-attachments/assets/ed463ce8-62ee-4d9a-85ca-1a1c3104ea21" />

#### 2.2 Ajout des dépenses

Pour ajouter un revenu, cliquer sur le bouton **Dépense**, remplir les informations puis cliquer sur le bouton **Enregistrer** :

<img width="500" height="756" alt="image" src="https://github.com/user-attachments/assets/3a01ce3e-ce3c-4dc3-90d6-6f68307330b1" />

#### 2.3 Affichage des dépenses

Les dépenses sur les 3 derniers mois s'affichent sur la page d'accueil (index.html) dans un tableau :
<img width="600" height="827" alt="image" src="https://github.com/user-attachments/assets/1d429150-2fb1-4e2c-b06e-a930c23d7953" />


#### 2.4 Filtrage du tableau dew dépenses

Il est possible de trier le tableau et de le filtrer selon différents critères :
<img width="600" height="205" alt="image" src="https://github.com/user-attachments/assets/69777ffb-4a7d-452e-bfa7-aa12999fc882" />

Il suffit de cliquer sur le haut du tableau pour trier et pour filtrer, utiliser la barre de recherche.

---

### 3. Objectifs d'épargne


#### 3.1 Ajout d'objectifs d'épargne

Renseignez:

- montant;
- description;
- fréquence;
- catégorie associée;

Puis cliquez sur **ajouter**.

<img width="600" height="1218" alt="image" src="https://github.com/user-attachments/assets/2131d045-7e76-4164-97c2-5ddf4804cf4e" />


#### 3.2 Visualisation des objectifs d'épargne

L'objectif que vous venez de renseigner doit se retrouver sur la page **Mes Objectifs d'épargne**

<img width="600" height="590" alt="image" src="https://github.com/user-attachments/assets/18803176-83a5-46ec-848b-da833e2dd6ac" />

---

### 4. Archives mensuelles

Si vous souhaitez accédez aux statistiques des transactions au-delà de 3mois, cliquez sur le bouton **Archives mensuelles** : 

<img width="600" height="166" alt="image" src="https://github.com/user-attachments/assets/2418a748-c0b2-44e0-aaa3-652108043484" />


Choisissez le mois à archiver puis cliquer sur le bouton **Archiver**  :

<img width="600" height="499" alt="image" src="https://github.com/user-attachments/assets/5f773730-7844-4e44-bf4d-7fbb35d6a9b3" />


#### 4.1 Voir les détails d'une archive

Pour voir les détails de l’archive, cliquer sur le bouton **Voir les détails**

<img width="600" height="306" alt="image" src="https://github.com/user-attachments/assets/c24fde91-f9fa-439c-a28a-7ba9a4f6a0a6" />


#### 4.2 Masquer une archive

Pour masquer une archive, cliquer sur le bouton avec l’icône d’oeil barré :

<img width="600" height="360" alt="image" src="https://github.com/user-attachments/assets/1689ffcc-e117-4918-90d3-2758ae0b2d27" />

Pour démasquer une archive, cliquer sur le bouton oeil.

Résultat :

<img width="600" height="237" alt="image" src="https://github.com/user-attachments/assets/e5924db5-f385-4203-a092-556c67feec04" />


#### 4.3 Suppression d'une archive : suppression des données pour un mois donné

Pour supprimer une archive, cliquer sur le bouton poubelle:

<img width="1248" height="360" alt="image" src="https://github.com/user-attachments/assets/63c4e552-0406-44a4-8b24-a107c2b0a290" />


> Attention : ce bouton supprime les données de la base de données, en même temps que l’archive, une confirmation vous sera alors demandée pour s’assurer que cela n’est pas une erreur.



