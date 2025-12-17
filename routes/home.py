
from flask import Blueprint, render_template
from datetime import datetime, timedelta
from extensions import db
from models import Transaction, Objectif

home_bp = Blueprint('home', __name__)


@home_bp.route("/")
def home():
    now = datetime.utcnow()
    date_limite = now - timedelta(days=90)
    start_of_month = datetime(now.year, now.month, 1)

    transactions = Transaction.query.filter(
        Transaction.dateTransaction >= date_limite
    ).order_by(Transaction.dateTransaction.desc()).all()


    total_revenus = db.session.query(
        db.func.coalesce(db.func.sum(Transaction.montant), 0)
    ).filter(
        Transaction.montant > 0,
        Transaction.dateTransaction >= start_of_month
    ).scalar()

    total_depenses_raw = db.session.query(
        db.func.coalesce(db.func.sum(Transaction.montant), 0)
    ).filter(
        Transaction.montant < 0,
        Transaction.dateTransaction >= start_of_month
    ).scalar()

    total_epargne = db.session.query(
        db.func.coalesce(db.func.sum(Objectif.epargne_actuelle), 0)
    ).scalar()

    total_epargne = float(total_epargne)
    total_revenus = float(total_revenus)
    total_depenses = float(-total_depenses_raw)

    argentActuel = total_revenus - total_depenses


    nb_anciennes = Transaction.query.filter(Transaction.dateTransaction < date_limite).count()

    return render_template(
        "index.html",
        transactions=transactions,
        argentActuel=argentActuel,
        total_revenus=total_revenus,
        total_depenses=total_depenses,
        total_epargne=total_epargne,
        nb_anciennes=nb_anciennes
    )