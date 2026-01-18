import sys

sys.path.insert(0, '/app')

from flask import Flask
from datetime import datetime
from shared.config import Config
from shared.extensions import db
from routes import ecriture_bp

NOM_CATEGORIE_REPORT = "Solde précédent"


def initialiser_report_et_categorie(app):
    """
    Vérifie et crée la catégorie de report, puis insère la transaction de report
    si elle n'existe pas pour le mois en cours.
    """
    # Import ici pour éviter les imports circulaires
    from shared.models import Categorie, Transaction, ArchiveMensuelle

    with app.app_context():
        # 1. Créer la catégorie "Solde précédent" si elle n'existe pas
        categorie_report = Categorie.query.filter_by(nom=NOM_CATEGORIE_REPORT).first()
        if not categorie_report:
            print(f"[INIT] Création de la catégorie: {NOM_CATEGORIE_REPORT}")
            categorie_report = Categorie(
                nom=NOM_CATEGORIE_REPORT,
                description="Transaction de solde reporté, créée au démarrage de l'application.",
                couleur="#cccccc"
            )
            db.session.add(categorie_report)
            db.session.commit()
            categorie_report = Categorie.query.filter_by(nom=NOM_CATEGORIE_REPORT).first()

        ID_CATEGORIE_REPORT = categorie_report.idCategorie

        # 2. Vérifier si une transaction de report existe déjà pour ce mois
        now = datetime.utcnow()
        start_of_month = datetime(now.year, now.month, 1)

        report_existe = Transaction.query.filter(
            Transaction.idCategorie == ID_CATEGORIE_REPORT,
            Transaction.dateTransaction >= start_of_month
        ).first()

        if report_existe:
            print(f"[INIT] Transaction de report déjà existante pour {now.month}/{now.year}")
            return

        # 3. Récupérer le solde de la dernière archive
        derniere_archive = ArchiveMensuelle.query.order_by(
            ArchiveMensuelle.annee.desc(),
            ArchiveMensuelle.mois.desc()
        ).first()

        solde_a_reporter = 0.0
        if derniere_archive:
            solde_a_reporter = float(derniere_archive.solde_final or 0)

        # 4. Créer la transaction de report si le solde n'est pas nul
        if solde_a_reporter != 0.0:
            print(
                f"[INIT] Insertion de la transaction de report ({solde_a_reporter:.2f} €) pour {now.month}/{now.year}")
            transaction_report = Transaction(
                montant=solde_a_reporter,
                dateTransaction=start_of_month,
                titre=NOM_CATEGORIE_REPORT,
                commentaire=f"Solde reporté automatiquement depuis l'archive précédente.",
                idCategorie=ID_CATEGORIE_REPORT
            )
            db.session.add(transaction_report)
            db.session.commit()
        else:
            print(f"[INIT] Aucun solde à reporter (solde = 0 ou pas d'archive)")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    app.register_blueprint(ecriture_bp, url_prefix='/api')

    return app


app = create_app()

# Initialiser le report au démarrage (après création de l'app)
with app.app_context():
    try:
        initialiser_report_et_categorie(app)
    except Exception as e:
        print(f"[INIT] Erreur lors de l'initialisation du report: {e}")


# Endpoint de health check pour Kubernetes
@app.route('/health')
def health():
    return {'status': 'healthy'}, 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)