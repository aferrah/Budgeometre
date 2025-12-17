
from flask import Blueprint, render_template
from datetime import datetime, timedelta
from extensions import db
from models import Transaction, Objectif, ArchiveMensuelle

home_bp = Blueprint('home', __name__)


@home_bp.route("/")
def home():
    now = datetime.utcnow()
    date_limite = now - timedelta(days=90)
    start_of_month = datetime(now.year, now.month, 1)


    derniere_archive = ArchiveMensuelle.query.order_by(
        ArchiveMensuelle.annee.desc(),
        ArchiveMensuelle.mois.desc()
    ).first()

    solde_report = 0.0
    date_debut_calcul = start_of_month

    if derniere_archive:
        solde_report = float(derniere_archive.solde_final)

        annee = derniere_archive.annee
        mois = derniere_archive.mois

        if mois == 12:
            date_debut_calcul = datetime(annee + 1, 1, 1)
        else:
            date_debut_calcul = datetime(annee, mois + 1, 1)


    transactions = Transaction.query.filter(
        Transaction.dateTransaction >= date_limite
    ).order_by(Transaction.dateTransaction.desc()).all()

    total_revenus_mois = db.session.query(
        db.func.coalesce(db.func.sum(Transaction.montant), 0)
    ).filter(
        Transaction.montant > 0,
        Transaction.dateTransaction >= date_debut_calcul
    ).scalar()

    total_depenses_raw_mois = db.session.query(
        db.func.coalesce(db.func.sum(Transaction.montant), 0)
    ).filter(
        Transaction.montant < 0,
        Transaction.dateTransaction >= date_debut_calcul
    ).scalar()

    total_epargne = db.session.query(
        db.func.coalesce(db.func.sum(Objectif.epargne_actuelle), 0)
    ).scalar()

    total_epargne = float(total_epargne)

    total_revenus_mois = float(total_revenus_mois)
    total_depenses_mois = float(-total_depenses_raw_mois)


    total_revenus_ajuste = total_revenus_mois
    total_depenses_ajuste = total_depenses_mois

    if solde_report > 0:
        total_revenus_ajuste += solde_report
    else:
        total_depenses_ajuste += abs(solde_report)

    argentActuel = total_revenus_ajuste - total_depenses_ajuste


    nb_anciennes = Transaction.query.filter(Transaction.dateTransaction < date_limite).count()

    return render_template(
        "index.html",
        transactions=transactions,
        argentActuel=argentActuel,
        total_revenus=total_revenus_ajuste,
        total_depenses=total_depenses_ajuste,
        total_epargne=total_epargne,
        nb_anciennes=nb_anciennes
    )