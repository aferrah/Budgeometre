#!/usr/bin/env python3
import subprocess
import random
import json
import time
from datetime import datetime, timedelta

def run_command(cmd, capture=True):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture, text=True, check=False)
        return result.stdout.strip() if capture else None
    except Exception as e:
        print(f"Erreur: {e}")
        return None

def create_transaction(date, amount, description, category):
    data = {
        "date": date,
        "montant": amount,
        "description": description,
        "categorie": category
    }
    cmd = f'curl -s -X POST http://localhost:8080/transactions -H "Content-Type: application/json" -d \'{json.dumps(data)}\''
    return run_command(cmd)

def generate_transactions(months=3):
    categories = ["Alimentation", "Transport", "Logement", "Loisirs", "Sante", "Shopping", "Factures", "Salaire", "Autres"]
    
    descriptions = {
        "Alimentation": ["Supermarche", "Restaurant", "Boulangerie", "Marche", "Fast-food"],
        "Transport": ["Essence", "Metro", "Bus", "Train", "Parking"],
        "Logement": ["Loyer", "Electricite", "Eau", "Internet", "Assurance"],
        "Loisirs": ["Cinema", "Concert", "Sport", "Livre", "Streaming"],
        "Sante": ["Pharmacie", "Medecin", "Dentiste", "Opticien", "Mutuelle"],
        "Shopping": ["Vetements", "Chaussures", "Electronique", "Decoration", "Cosmetiques"],
        "Factures": ["Telephone", "Assurance", "Impots", "Abonnement", "Banque"],
        "Salaire": ["Salaire mensuel", "Prime", "Remboursement"],
        "Autres": ["Cadeau", "Don", "Divers", "Frais bancaires"]
    }
    
    transactions = []
    start_date = datetime.now() - timedelta(days=months * 30)
    
    for day in range(months * 30):
        current_date = start_date + timedelta(days=day)
        
        if current_date.day == 1:
            transactions.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "montant": random.randint(2500, 3500),
                "description": "Salaire mensuel",
                "categorie": "Salaire"
            })
        
        if current_date.day == 5:
            transactions.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "montant": -random.randint(800, 1200),
                "description": "Loyer",
                "categorie": "Logement"
            })
        
        num_transactions = random.randint(0, 1)
        for _ in range(num_transactions):
            category = random.choice([c for c in categories if c not in ["Salaire"]])
            description = random.choice(descriptions[category])
            
            amount_ranges = {
                "Alimentation": (5, 100),
                "Transport": (5, 60),
                "Logement": (50, 200),
                "Loisirs": (10, 80),
                "Sante": (10, 150),
                "Shopping": (20, 200),
                "Factures": (20, 100),
                "Autres": (5, 50)
            }
            
            min_amt, max_amt = amount_ranges.get(category, (10, 50))
            amount = -random.randint(min_amt, max_amt)
            
            transactions.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "montant": amount,
                "description": description,
                "categorie": category
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
    
    months = 3
    print(f"\n>>> Generation de {months} mois de transactions...")
    transactions = generate_transactions(months)
    print(f"OK {len(transactions)} transactions generees")
    
    print("\n>>> Insertion des transactions dans la base de donnees...")
    success = 0
    failed = 0
    
    for i, transaction in enumerate(transactions):
        result = create_transaction(
            transaction["date"],
            transaction["montant"],
            transaction["description"],
            transaction["categorie"]
        )
        
        if result is not None:
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
