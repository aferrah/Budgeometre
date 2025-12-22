from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from extensions import db
from models import Transaction, Categorie

transactions_bp = Blueprint('transactions', __name__)


@transactions_bp.route("/add-expense", methods=["GET", "POST"])
def add_expense():
    if request.method == "GET":
        categories = Categorie.query.order_by(Categorie.nom).all()
        return render_template("add-expense.html", categories=categories)

    titre = request.form.get("label") or "Dépense"
    montant_raw = request.form.get("amount") or "0"
    type_transaction = request.form.get("type", "depense")

    try:
        montant = float(montant_raw)
    except ValueError:
        montant = 0.0
    montant = -abs(montant) if type_transaction == "depense" else abs(montant)

    commentaire = request.form.get("comment")
    date_str = request.form.get("date")
    try:
        date_tx = datetime.fromisoformat(date_str) if date_str else datetime.utcnow()
    except:
        date_tx = datetime.utcnow()

    cat_id = request.form.get("category")
    categorie = None
    if cat_id:
        try:
            categorie = Categorie.query.get(int(cat_id))
        except:
            pass

    if not categorie:
        categorie = Categorie.query.filter_by(nom="Autre").first()
        if not categorie:
            categorie = Categorie(nom="Autre", description="Catégorie par défaut", couleur="#64748b")
            db.session.add(categorie)
            db.session.commit()

    tr = Transaction(montant=montant, titre=titre, commentaire=commentaire, dateTransaction=date_tx, categorie=categorie)
    db.session.add(tr)
    db.session.commit()
    flash("Transaction ajoutée avec succès", "success")
    return redirect(url_for("home.home"))


@transactions_bp.route("/transaction/<int:id>/modifier", methods=["GET", "POST"])
def modifier_transaction(id):
    transaction = Transaction.query.get_or_404(id)

    if transaction.categorie and transaction.categorie.nom == "Épargne":
        flash("Les transactions d'épargne ne peuvent pas être modifiées.", "error")
        return redirect(url_for("home.home"))

    if request.method == "GET":
        categories = Categorie.query.order_by(Categorie.nom).all()
        return render_template("modifier-transaction.html", transaction=transaction, categories=categories)

    titre = request.form.get("label") or "Dépense"
    montant_raw = request.form.get("amount") or "0"
    type_transaction = request.form.get("type", "depense")

    try:
        montant = float(montant_raw)
    except ValueError:
        montant = 0.0
    montant = -abs(montant) if type_transaction == "depense" else abs(montant)

    commentaire = request.form.get("comment")
    date_str = request.form.get("date")
    try:
        date_tx = datetime.fromisoformat(date_str) if date_str else transaction.dateTransaction
    except:
        date_tx = transaction.dateTransaction

    cat_id = request.form.get("category")
    if cat_id:
        try:
            categorie = Categorie.query.get(int(cat_id))
            if categorie:
                transaction.idCategorie = categorie.idCategorie
        except:
            pass

    transaction.titre = titre
    transaction.montant = montant
    transaction.commentaire = commentaire
    transaction.dateTransaction = date_tx
    db.session.commit()
    flash("Transaction modifiée avec succès", "success")
    return redirect(url_for("home.home"))


@transactions_bp.route("/transaction/<int:id>/supprimer", methods=["POST"])
def supprimer_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    if transaction.categorie and transaction.categorie.nom == "Épargne":
        flash("Les transactions d'épargne ne peuvent pas être supprimées.", "error")
        return redirect(url_for("home.home"))
    db.session.delete(transaction)
    db.session.commit()
    flash("Transaction supprimée avec succès", "success")
    return redirect(url_for("home.home"))


@transactions_bp.route("/transactions")
def list_transactions():
    transactions = Transaction.query.order_by(Transaction.dateTransaction.desc()).all()
    lignes = [f"{t.dateTransaction} - {t.titre} : {t.montant}€ (cat: {t.categorie.nom})" for t in transactions]
    return "<br>".join(lignes) if lignes else "Aucune transaction."
