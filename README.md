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

**1) Ajout des dépenses**
**2) Affichage des dépenses**
**3) Ajout des revenus**
**4) Gestion des catégories**
**5) Ajout d'objectifs**

