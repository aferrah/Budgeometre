"""
Script de seed pour injecter 6 mois de données de test.
Usage: kubectl exec -it <pod-ecriture> -n budgeometre -- python seed_data.py
"""

import sys

sys.path.insert(0, '/app')

from datetime import datetime, timedelta
from random import randint, choice
from collections import defaultdict
import json

from shared.config import Config
from shared.extensions import db
from shared.models import Categorie, Transaction, Objectif, ArchiveMensuelle
from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app


def get_month_offset(now, months_back):
    """Calcule correctement le mois et l'année N mois en arrière."""
    year = now.year
    month = now.month - months_back
    while month <= 0:
        month += 12
        year -= 1
    return year, month


def seed_6_mois():
    print("[SEED] Début de l'injection des données de test sur 6 mois...")

    # 1. Créer les catégories
    categories_data = [
        {'nom': 'Alimentation', 'description': 'Courses et restaurants', 'couleur': '#ef4444', 'limite_budget': 400},
        {'nom': 'Transport', 'description': 'Métro, essence, parking', 'couleur': '#3b82f6', 'limite_budget': 150},
        {'nom': 'Loisirs', 'description': 'Sorties, cinéma, jeux', 'couleur': '#a855f7', 'limite_budget': 200},
        {'nom': 'Logement', 'description': 'Loyer et charges', 'couleur': '#f59e0b', 'limite_budget': 900},
        {'nom': 'Santé', 'description': 'Médecin, pharmacie', 'couleur': '#14b8a6', 'limite_budget': 100},
        {'nom': 'Shopping', 'description': 'Vêtements, électronique', 'couleur': '#ec4899', 'limite_budget': 150},
        {'nom': 'Abonnements', 'description': 'Netflix, Spotify, etc.', 'couleur': '#6366f1', 'limite_budget': 50},
        {'nom': 'Salaire', 'description': 'Revenus du travail', 'couleur': '#22c55e', 'limite_budget': 0},
        {'nom': 'Épargne', 'description': 'Transferts vers épargne', 'couleur': '#f59e0b', 'limite_budget': 0},
        {'nom': 'Autre', 'description': 'Dépenses diverses', 'couleur': '#64748b', 'limite_budget': 0},
    ]

    categories = {}
    for cat_data in categories_data:
        cat = Categorie.query.filter_by(nom=cat_data['nom']).first()
        if not cat:
            cat = Categorie(**cat_data)
            db.session.add(cat)
            db.session.commit()
            print(f"  ✓ Catégorie créée: {cat_data['nom']}")
        else:
            print(f"  → Catégorie existante: {cat_data['nom']}")
        categories[cat_data['nom']] = cat.idCategorie

    # 2. Templates de transactions
    transactions_templates = [
        # Revenus
        {'titre': 'Salaire', 'montant': 2500, 'categorie': 'Salaire', 'type': 'revenu', 'fixe': True, 'jour': 28},
        {'titre': 'Prime', 'montant': 500, 'categorie': 'Salaire', 'type': 'revenu', 'freq': 0.2},

        # Dépenses fixes
        {'titre': 'Loyer', 'montant': -850, 'categorie': 'Logement', 'fixe': True, 'jour': 5},
        {'titre': 'Électricité', 'montant': -65, 'categorie': 'Logement', 'fixe': True, 'jour': 10, 'var': 20},
        {'titre': 'Internet', 'montant': -35, 'categorie': 'Logement', 'fixe': True, 'jour': 8},
        {'titre': 'Navigo', 'montant': -86, 'categorie': 'Transport', 'fixe': True, 'jour': 1},
        {'titre': 'Netflix', 'montant': -18, 'categorie': 'Abonnements', 'fixe': True, 'jour': 15},
        {'titre': 'Spotify', 'montant': -10, 'categorie': 'Abonnements', 'fixe': True, 'jour': 15},
        {'titre': 'Salle de sport', 'montant': -30, 'categorie': 'Loisirs', 'fixe': True, 'jour': 5},

        # Dépenses variables
        {'titre': 'Courses Carrefour', 'montant': -85, 'categorie': 'Alimentation', 'var': 30},
        {'titre': 'Courses Lidl', 'montant': -45, 'categorie': 'Alimentation', 'var': 15},
        {'titre': 'Boulangerie', 'montant': -8, 'categorie': 'Alimentation', 'var': 5},
        {'titre': 'Restaurant', 'montant': -35, 'categorie': 'Alimentation', 'var': 20, 'freq': 0.7},
        {'titre': 'Uber Eats', 'montant': -22, 'categorie': 'Alimentation', 'var': 10, 'freq': 0.5},
        {'titre': 'Essence', 'montant': -60, 'categorie': 'Transport', 'var': 20, 'freq': 0.5},
        {'titre': 'Parking', 'montant': -12, 'categorie': 'Transport', 'var': 5, 'freq': 0.4},
        {'titre': 'Cinéma', 'montant': -14, 'categorie': 'Loisirs', 'var': 3, 'freq': 0.6},
        {'titre': 'Bar', 'montant': -25, 'categorie': 'Loisirs', 'var': 15, 'freq': 0.5},
        {'titre': 'Médecin', 'montant': -25, 'categorie': 'Santé', 'var': 0, 'freq': 0.3},
        {'titre': 'Pharmacie', 'montant': -18, 'categorie': 'Santé', 'var': 10, 'freq': 0.4},
        {'titre': 'Vêtements', 'montant': -55, 'categorie': 'Shopping', 'var': 30, 'freq': 0.4},
        {'titre': 'Amazon', 'montant': -40, 'categorie': 'Shopping', 'var': 25, 'freq': 0.5},
    ]

    now = datetime.utcnow()
    transactions_creees = 0

    # Générer les transactions pour les 6 derniers mois + mois courant
    for mois_offset in range(6, -1, -1):
        annee, mois = get_month_offset(now, mois_offset)

        print(f"\n[SEED] Mois {mois:02d}/{annee}...")

        for template in transactions_templates:
            freq = template.get('freq', 1.0)
            if randint(1, 100) > freq * 100:
                continue

            montant_base = template['montant']
            variation = template.get('var', 0)
            montant = montant_base + randint(-variation, variation) if variation else montant_base

            if template.get('fixe'):
                jour = min(template.get('jour', 5), 28)
            else:
                jour = randint(1, 28)

            date_transaction = datetime(annee, mois, jour)

            t = Transaction(
                titre=template['titre'],
                montant=montant,
                dateTransaction=date_transaction,
                commentaire="Données de test",
                idCategorie=categories[template['categorie']]
            )
            db.session.add(t)
            transactions_creees += 1

        # Quelques transactions diverses
        for _ in range(randint(3, 6)):
            t = Transaction(
                titre=choice(['Divers', 'Achat', 'Dépense']),
                montant=-randint(5, 40),
                dateTransaction=datetime(annee, mois, randint(1, 28)),
                commentaire="Dépense diverse",
                idCategorie=categories['Autre']
            )
            db.session.add(t)
            transactions_creees += 1

    db.session.commit()
    print(f"\n  ✓ {transactions_creees} transactions créées")

    # 3. Objectifs d'épargne avec transactions correspondantes
    print("\n[SEED] Création des objectifs d'épargne...")
    objectifs_data = [
        {'montant': 1000, 'description': 'Vacances été', 'frequence': 'mensuel', 'epargne_actuelle': 650},
        {'montant': 500, 'description': 'Nouveau téléphone', 'frequence': 'mensuel', 'epargne_actuelle': 320},
        {'montant': 5000, 'description': 'Apport voiture', 'frequence': 'mensuel', 'epargne_actuelle': 1200},
    ]

    for obj_data in objectifs_data:
        existing = Objectif.query.filter_by(description=obj_data['description']).first()
        if not existing:
            obj = Objectif(
                montant=obj_data['montant'],
                description=obj_data['description'],
                frequence=obj_data['frequence'],
                epargne_actuelle=obj_data['epargne_actuelle'],
                dateDebut=now - timedelta(days=90),
                idCategorie=categories['Autre']
            )
            db.session.add(obj)
            db.session.commit()

            # Créer la transaction d'épargne correspondante
            t = Transaction(
                titre=f"Épargne: {obj_data['description']}",
                montant=-obj_data['epargne_actuelle'],
                dateTransaction=now - timedelta(days=randint(10, 60)),
                commentaire="Transfert vers épargne",
                idCategorie=categories['Épargne']
            )
            db.session.add(t)
            print(f"  ✓ Objectif créé: {obj_data['description']} ({obj_data['epargne_actuelle']}€ épargnés)")
        else:
            print(f"  → Objectif existant: {obj_data['description']}")

    db.session.commit()

    # 4. Archives pour les mois passés (pas le mois courant)
    print("\n[SEED] Création des archives...")
    for mois_offset in range(6, 0, -1):
        annee, mois = get_month_offset(now, mois_offset)

        existing = ArchiveMensuelle.query.filter_by(annee=annee, mois=mois).first()
        if existing:
            print(f"  → Archive existante: {mois:02d}/{annee}")
            continue

        debut_mois = datetime(annee, mois, 1)
        if mois == 12:
            fin_mois = datetime(annee + 1, 1, 1)
        else:
            fin_mois = datetime(annee, mois + 1, 1)

        trans_mois = Transaction.query.filter(
            Transaction.dateTransaction >= debut_mois,
            Transaction.dateTransaction < fin_mois
        ).all()

        if not trans_mois:
            print(f"  ⚠ Pas de transactions pour {mois:02d}/{annee}, archive ignorée")
            continue

        revenus = sum(float(t.montant) for t in trans_mois if t.montant > 0)
        depenses = sum(float(-t.montant) for t in trans_mois if t.montant < 0)
        solde = revenus - depenses

        # Stats par catégorie
        stats_categories = defaultdict(lambda: {'nom': '', 'couleur': '#8b5cf6', 'depenses': 0, 'revenus': 0, 'nb_transactions': 0})
        for t in trans_mois:
            cat_id = t.idCategorie
            stats_categories[cat_id]['nom'] = t.categorie.nom if t.categorie else 'Autre'
            stats_categories[cat_id]['couleur'] = t.categorie.couleur if t.categorie else '#64748b'
            stats_categories[cat_id]['nb_transactions'] += 1
            if t.montant < 0:
                stats_categories[cat_id]['depenses'] += float(-t.montant)
            else:
                stats_categories[cat_id]['revenus'] += float(t.montant)

        donnees = {
            'transactions': [
                {
                    'titre': t.titre,
                    'montant': float(t.montant),
                    'date': t.dateTransaction.strftime('%Y-%m-%d'),
                    'categorie': t.categorie.nom if t.categorie else 'Autre',
                    'commentaire': t.commentaire or ''
                }
                for t in trans_mois
            ],
            'categories': {str(k): v for k, v in stats_categories.items()},
            'stats': {
                'nb_transactions': len(trans_mois),
                'nb_depenses': sum(1 for t in trans_mois if t.montant < 0),
                'nb_revenus': sum(1 for t in trans_mois if t.montant > 0)
            }
        }

        archive = ArchiveMensuelle(
            annee=annee,
            mois=mois,
            total_revenus=revenus,
            total_depenses=depenses,
            total_epargne=0,
            solde_final=solde,
            donnees_json=json.dumps(donnees, ensure_ascii=False)
        )
        db.session.add(archive)
        print(f"  ✓ Archive créée: {mois:02d}/{annee} ({len(trans_mois)} transactions, solde: {solde:.2f}€)")

    db.session.commit()
    print("\n[SEED] Injection terminée !")


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_6_mois()