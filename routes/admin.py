import random
from flask import Blueprint, redirect, url_for, flash
from datetime import datetime, timedelta
from extensions import db
from models import Categorie, Transaction, Objectif, ArchiveMensuelle

admin_bp = Blueprint('admin', __name__)


@admin_bp.route("/reinitialiser-bdd")
def reinitialiser_bdd():
    try:
        ArchiveMensuelle.query.delete()
        Transaction.query.delete()
        Objectif.query.delete()
        Categorie.query.delete()
        db.session.commit()
        flash("Base de données réinitialisée", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Erreur: {e}", "error")
    return redirect(url_for("home.home"))


@admin_bp.route("/reset-and-init")
def reset_and_init():
    db.drop_all()
    db.create_all()
    return redirect(url_for('admin.init_test_archives'))


@admin_bp.route("/init-test")
def init_test():
    cats = [Categorie(nom="Alimentation", description="Courses"), Categorie(nom="Transport", description="Déplacements"), Categorie(nom="Loisirs", description="Activités")]
    db.session.add_all(cats)
    db.session.commit()
    for t in [("Courses", -45.30, cats[0]), ("Restaurant", -28.50, cats[0]), ("Essence", -60, cats[1]), ("Bus", -15, cats[1]), ("Cinéma", -12, cats[2])]:
        db.session.add(Transaction(titre=t[0], montant=t[1], categorie=t[2]))
    db.session.commit()
    return "Données de test ajoutées"


@admin_bp.route("/init-test-archives")
def init_test_archives():
    cats_config = [("Alimentation", "#ef4444", 400), ("Transport", "#3b82f6", 150), ("Loisirs", "#a855f7", 200),
        ("Logement", "#f59e0b", 800), ("Santé", "#14b8a6", 100), ("Shopping", "#ec4899", 150), ("Salaire", "#10b981", None)]
    cats = {}
    for nom, couleur, limite in cats_config:
        cat = Categorie.query.filter_by(nom=nom).first() or Categorie(nom=nom, couleur=couleur, limite_budget=limite)
        if not cat.idCategorie: db.session.add(cat)
        cats[nom] = cat
    db.session.commit()

    trans_types = {"Alimentation": [("Supermarché", 35, 80), ("Restaurant", 20, 60)], "Transport": [("Essence", 40, 70), ("Parking", 5, 15)],
        "Loisirs": [("Cinéma", 10, 25), ("Sport", 20, 50)], "Logement": [("Loyer", 600, 900), ("Électricité", 40, 80)],
        "Santé": [("Pharmacie", 10, 40)], "Shopping": [("Vêtements", 30, 100)]}

    now, nb = datetime.utcnow(), 0
    for i in range(6):
        d = datetime(now.year, now.month, 1) - timedelta(days=i * 30)
        db.session.add(Transaction(titre="Salaire", montant=random.uniform(2200, 2800), dateTransaction=datetime(d.year, d.month, random.randint(1, 5)), categorie=cats["Salaire"]))
        nb += 1
        for titre, mn, mx in trans_types["Logement"]:
            db.session.add(Transaction(titre=titre, montant=-random.uniform(mn, mx), dateTransaction=datetime(d.year, d.month, random.randint(1, 10)), categorie=cats["Logement"]))
            nb += 1
        for _ in range(random.randint(15, 25)):
            cat_nom = random.choice(["Alimentation", "Transport", "Loisirs", "Santé", "Shopping"])
            titre, mn, mx = random.choice(trans_types[cat_nom])
            db.session.add(Transaction(titre=titre, montant=-random.uniform(mn, mx), dateTransaction=datetime(d.year, d.month, random.randint(1, 28)), categorie=cats[cat_nom]))
            nb += 1
    db.session.commit()
    return f"{nb} transactions créées sur 6 mois"
