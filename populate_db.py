#!/usr/bin/env python3
import requests
import random
import json
import time
import re
from datetime import datetime, timedelta

def create_category(name, description="", color="#8b5cf6"):
    """Crée une catégorie si elle n'existe pas déjà"""
    try:
        data = {
            'nom': name,
            'description': description,
            'couleur': color
        }
        response = requests.post('http://localhost:8080/categories', data=data, timeout=5, allow_redirects=False)
        return response.status_code in [200, 302]
    except Exception as e:
        print(f"Erreur lors de la création de la catégorie {name}: {e}")
        return False

def delete_all_transactions():
    """Supprime toutes les données de la base via SQL direct"""
    import subprocess
    try:
        print("  Connexion à postgres et suppression des données...")
        
        # Commandes SQL pour vider TOUTES les tables
        sql_commands = '''
        DELETE FROM "TRANSACTION";
        DELETE FROM "OBJECTIF";
        DELETE FROM "ARCHIVE_MENSUELLE";
        DELETE FROM "CATEGORIE" WHERE nom != 'Solde précédent';
        '''
        
        # Exécuter via kubectl exec sur le pod postgres
        result = subprocess.run([
            'kubectl', 'exec', '-n', 'u-grp5', 'postgres-0', '--',
            'psql', '-U', 'budgeometre_user', '-d', 'budgeometre_db', '-c', sql_commands
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            lines = [l for l in result.stdout.strip().split('\n') if l.strip()]
            print(f"  ✓ {' | '.join(lines)}")
            return True
        else:
            print(f"  ✗ Erreur SQL: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"  ✗ Erreur: {e}")
        return False

def get_categories():
    """Récupère les catégories depuis le formulaire HTML"""
    try:
        response = requests.get('http://localhost:8080/add-expense', timeout=5)
        # Extraire les options du select des catégories
        pattern = r'<option value="(\d+)">([^<]+)</option>'
        matches = re.findall(pattern, response.text)
        # Créer un mapping nom -> id
        category_map = {name.strip(): int(id_val) for id_val, name in matches}
        return category_map
    except Exception as e:
        print(f"Erreur lors de la récupération des catégories: {e}")
        return {}

def initialize_categories():
    """Crée toutes les catégories nécessaires"""
    categories_to_create = {
        "Alimentation": ("#22c55e", "Courses, restaurants, nourriture"),
        "Transport": ("#3b82f6", "Essence, transports en commun"),
        "Logement": ("#f59e0b", "Loyer, charges, factures logement"),
        "Loisirs": ("#a855f7", "Sorties, divertissements, hobbies"),
        "Sante": ("#ef4444", "Médecin, pharmacie, soins"),
        "Shopping": ("#ec4899", "Vêtements, équipements, achats"),
        "Factures": ("#f97316", "Abonnements, assurances, impôts"),
        "Salaire": ("#10b981", "Revenus du travail"),
        "Autres": ("#64748b", "Dépenses diverses")
    }
    
    print("\n>>> Création des catégories nécessaires...")
    created = 0
    for name, (color, desc) in categories_to_create.items():
        if create_category(name, desc, color):
            created += 1
            print(f"  ✓ {name}")
        else:
            print(f"  - {name} (existe déjà ou erreur)")
    
    # Attendre que les catégories soient bien enregistrées
    time.sleep(2)
    
    print(f"OK {created} nouvelles catégories créées\n")
    return True

def create_transaction(date, amount, label, category_id):
    """Crée une transaction via le formulaire web"""
    try:
        transaction_type = 'revenu' if amount > 0 else 'depense'
        data = {
            'date': date,
            'amount': abs(amount),
            'label': label,
            'type': transaction_type,
            'category': category_id,
            'comment': ''
        }
        response = requests.post('http://localhost:8080/add-expense', data=data, timeout=5, allow_redirects=False)
        return response.status_code in [200, 302]  # 302 = redirect après succès
    except Exception as e:
        print(f"Erreur lors de la création: {e}")
        return False

def generate_transactions(months=3):
    descriptions = {
        "Alimentation": ["Supermarche Carrefour", "Restaurant", "Boulangerie", "Marche", "Lidl"],
        "Transport": ["Essence Total", "Pass Navigo", "Uber", "SNCF", "Parking"],
        "Logement": ["Loyer", "EDF", "Eau Veolia", "Internet Orange", "Assurance habitation"],
        "Loisirs": ["Cinema UGC", "Netflix", "Salle de sport", "Concert", "Livre"],
        "Sante": ["Pharmacie", "Medecin generaliste", "Mutuelle", "Dentiste", "Opticien"],
        "Shopping": ["Zara", "H&M", "Amazon", "Ikea", "Sephora"],
        "Factures": ["Forfait mobile", "Spotify", "Assurance voiture", "Impots", "Banque"],
        "Salaire": ["Salaire mensuel"],
        "Autres": ["Cadeau anniversaire", "Coiffeur", "Pressing", "Frais bancaires"]
    }
    
    transactions = []
    start_date = datetime.now() - timedelta(days=months * 30)
    current_month = None
    
    for day in range(months * 30):
        current_date = start_date + timedelta(days=day)
        
        # Nouveau mois: réinitialiser le budget
        if current_date.day == 1:
            current_month = current_date.month
            # Salaire fixe de 2500€
            transactions.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "montant": 2500,
                "description": "Salaire mensuel",
                "categorie": "Salaire"
            })
        
        # Dépenses fixes mensuelles
        if current_date.day == 5:
            # Loyer fixe
            transactions.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "montant": -850,
                "description": "Loyer",
                "categorie": "Logement"
            })
        
        if current_date.day == 10:
            # Factures fixes
            transactions.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "montant": -49.99,
                "description": "Forfait mobile",
                "categorie": "Factures"
            })
            transactions.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "montant": -39.99,
                "description": "Internet Orange",
                "categorie": "Logement"
            })
        
        if current_date.day == 15:
            # EDF
            transactions.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "montant": -random.randint(60, 90),
                "description": "EDF",
                "categorie": "Logement"
            })
            # Assurance
            transactions.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "montant": -35,
                "description": "Assurance habitation",
                "categorie": "Logement"
            })
        
        if current_date.day == 20:
            # Abonnements
            transactions.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "montant": -15.99,
                "description": "Netflix",
                "categorie": "Loisirs"
            })
            transactions.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "montant": -9.99,
                "description": "Spotify",
                "categorie": "Factures"
            })
        
        # Dépenses quotidiennes variables
        # Alimentation: environ 300€/mois (10€/jour en moyenne)
        if random.random() < 0.7:  # 70% des jours
            transactions.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "montant": -random.randint(5, 25),
                "description": random.choice(descriptions["Alimentation"]),
                "categorie": "Alimentation"
            })
        
        # Transport: quelques fois par semaine
        if random.random() < 0.3:  # 30% des jours
            transactions.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "montant": -random.randint(5, 40),
                "description": random.choice(descriptions["Transport"]),
                "categorie": "Transport"
            })
        
        # Loisirs: occasionnel
        if random.random() < 0.15:  # 15% des jours
            transactions.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "montant": -random.randint(10, 50),
                "description": random.choice(descriptions["Loisirs"]),
                "categorie": "Loisirs"
            })
        
        # Shopping: quelques fois par mois
        if random.random() < 0.08:  # ~2-3 fois/mois
            transactions.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "montant": -random.randint(20, 80),
                "description": random.choice(descriptions["Shopping"]),
                "categorie": "Shopping"
            })
        
        # Santé: rare mais peut être cher
        if random.random() < 0.05:  # ~1-2 fois/mois
            transactions.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "montant": -random.randint(15, 60),
                "description": random.choice(descriptions["Sante"]),
                "categorie": "Sante"
            })
        
        # Autres: très occasionnel
        if random.random() < 0.06:
            transactions.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "montant": -random.randint(10, 40),
                "description": random.choice(descriptions["Autres"]),
                "categorie": "Autres"
            })
    
    return transactions

def main():
    print("=" * 50)
    print("  Population de la base de donnees")
    print("=" * 50)
    
    print("\n>>> Verification du port-forward...")
    print("Assurez-vous que le port-forward est actif:")
    print("    kubectl port-forward -n u-grp5 service/gateway 8080:5000")
    
    response = input("\nLe port-forward est-il actif ? (y/n) ")
    if response.lower() != 'y':
        print("\nLancez d'abord le port-forward:")
        print("   kubectl port-forward -n u-grp5 service/gateway 8080:5000")
        print("\nPuis relancez ce script.")
        return 1
    
    # Suppression de toutes les données de la BD
    print("\n>>> Suppression des donnees existantes...")
    if not delete_all_transactions():
        print("ERREUR lors de la suppression")
        return 1
    print("OK Donnees supprimees")
    
    # Créer les catégories d'abord
    if not initialize_categories():
        print("ERREUR: Impossible de créer les catégories")
        return 1
    
    print(">>> Recuperation des categories depuis l'API...")
    category_map = get_categories()
    if not category_map:
        print("ERREUR: Impossible de recuperer les categories")
        return 1
    print(f"OK {len(category_map)} categories trouvees:")
    for name, id_val in category_map.items():
        print(f"  - {name}: {id_val}")
    
    months = 3
    print(f"\n>>> Generation de {months} mois de transactions...")
    transactions = generate_transactions(months)
    print(f"OK {len(transactions)} transactions generees")
    
    print("\n>>> Insertion des transactions dans la base de donnees...")
    success = 0
    failed = 0
    
    for i, transaction in enumerate(transactions):
        # Récupérer l'ID de la catégorie
        category_id = category_map.get(transaction["categorie"])
        if category_id is None:
            print(f"ERREUR: Categorie '{transaction['categorie']}' non trouvee")
            failed += 1
            continue
            
        result = create_transaction(
            transaction["date"],
            transaction["montant"],
            transaction["description"],
            category_id
        )
        
        if result:
            success += 1
        else:
            failed += 1
        
        time.sleep(0.1)
        
        if (i + 1) % 20 == 0:
            print(f"  Progression: {i + 1}/{len(transactions)} transactions")
    
    print(f"\nOK Insertion terminee:")
    print(f"  - Reussies: {success}")
    print(f"  - Echouees: {failed}")
    
    print("\n" + "=" * 50)
    print("  Population terminee !")
    print("=" * 50)
    print("\nVous pouvez maintenant acceder a l'application:")
    print("  http://localhost:8080")

if __name__ == "__main__":
    exit(main())
