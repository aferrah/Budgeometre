
from flask import Flask
from config import Config
from extensions import db
from routes import register_blueprints
from datetime import datetime
from models import Categorie, Transaction, ArchiveMensuelle

NOM_CATEGORIE_REPORT = "Solde précédent"


def initialiser_report_et_categorie(app):
    """
    Vérifie et crée la catégorie de report, puis insère la transaction de report
    si elle n'existe pas pour le mois en cours.
    """
    with app.app_context():
        categorie_report = Categorie.query.filter_by(nom=NOM_CATEGORIE_REPORT).first()

        if not categorie_report:
            print(f"Création de la catégorie: {NOM_CATEGORIE_REPORT}")
            categorie_report = Categorie(
                nom=NOM_CATEGORIE_REPORT,
                description="Transaction de solde reporté, créée au démarrage de l'application.",
                couleur="#cccccc"
            )
            db.session.add(categorie_report)
            db.session.commit()
            categorie_report = Categorie.query.filter_by(nom=NOM_CATEGORIE_REPORT).first()

        ID_CATEGORIE_REPORT = categorie_report.idCategorie

        now = datetime.utcnow()
        start_of_month = datetime(now.year, now.month, 1)

        report_existe = Transaction.query.filter(
            Transaction.idCategorie == ID_CATEGORIE_REPORT,
            Transaction.dateTransaction >= start_of_month
        ).first()

        if report_existe:
            return

        derniere_archive = ArchiveMensuelle.query.order_by(
            ArchiveMensuelle.annee.desc(),
            ArchiveMensuelle.mois.desc()
        ).first()

        solde_a_reporter = 0.0

        if derniere_archive:
            solde_a_reporter = float(derniere_archive.solde_final)

        if solde_a_reporter != 0.0:
            print(f"Insertion de la transaction de report ({solde_a_reporter:.2f} €) pour le mois actuel.")

            transaction_report = Transaction(
                montant=solde_a_reporter,
                dateTransaction=start_of_month,
                titre=NOM_CATEGORIE_REPORT,
                commentaire=f"Solde reporté au lancement de l'application.",
                idCategorie=ID_CATEGORIE_REPORT
            )
            db.session.add(transaction_report)
            db.session.commit()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    register_blueprints(app)
    return app


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        initialiser_report_et_categorie(app)
    app.run(debug=True)