from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta
from collections import defaultdict
from extensions import db
from models import Categorie, Transaction

categories_bp = Blueprint('categories', __name__)


@categories_bp.route("/categories", methods=["GET", "POST"])
def categories():
    if request.method == "POST":
        nom = request.form.get("nom")
        description = request.form.get("description", "")
        couleur = request.form.get("couleur", "#8b5cf6")
        limite_budget_raw = request.form.get("limite_budget", "0")
        try:
            limite_budget = float(limite_budget_raw) if limite_budget_raw else 0
        except ValueError:
            limite_budget = 0

        if nom and not Categorie.query.filter_by(nom=nom).first():
            nouvelle_cat = Categorie(nom=nom, description=description, couleur=couleur, limite_budget=limite_budget)
            db.session.add(nouvelle_cat)
            db.session.commit()
            flash("Catégorie ajoutée avec succès", "success")
        return redirect(url_for("categories.categories"))

    now = datetime.utcnow()
    start_month = datetime(now.year, now.month, 1)
    toutes_categories = Categorie.query.order_by(Categorie.nom).all()

    for cat in toutes_categories:
        depenses_mois = db.session.query(db.func.coalesce(db.func.sum(Transaction.montant), 0)).filter(
            Transaction.idCategorie == cat.idCategorie, Transaction.montant < 0, Transaction.dateTransaction >= start_month
        ).scalar()
        cat.depenses_mois = float(-depenses_mois)
        cat.pourcentage = (cat.depenses_mois / float(cat.limite_budget)) * 100 if cat.limite_budget and cat.limite_budget > 0 else 0

    total_revenus = float(db.session.query(db.func.coalesce(db.func.sum(Transaction.montant), 0)).filter(Transaction.montant > 0).scalar())
    return render_template("categories.html", categories=toutes_categories, total_revenus=total_revenus)


@categories_bp.route("/categories/<int:id>/modifier", methods=["GET", "POST"])
def modifier_categorie(id):
    categorie = Categorie.query.get_or_404(id)
    if request.method == "GET":
        return render_template("modifier-categorie.html", categorie=categorie)

    nom = request.form.get("nom")
    if nom and not Categorie.query.filter(Categorie.nom == nom, Categorie.idCategorie != id).first():
        categorie.nom = nom
        categorie.description = request.form.get("description", "")
        categorie.couleur = request.form.get("couleur", "#8b5cf6")
        try:
            categorie.limite_budget = float(request.form.get("limite_budget", "0") or "0")
        except:
            categorie.limite_budget = 0
        db.session.commit()
        flash("Catégorie modifiée avec succès", "success")
    return redirect(url_for("categories.categories"))


@categories_bp.route("/categories/delete/<int:id>", methods=["POST"])
def delete_category(id):
    from flask import jsonify
    categorie = Categorie.query.get_or_404(id)
    
    if not categorie.transactions:
        nom = categorie.nom
        db.session.delete(categorie)
        db.session.commit()
        message = f"Catégorie '{nom}' supprimée avec succès"
        success = True
    else:
        nb_transactions = len(categorie.transactions)
        message = f"Impossible de supprimer '{categorie.nom}' : {nb_transactions} transaction(s) liée(s)"
        success = False
    
    # Si c'est une requête AJAX, retourner JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': success,
            'message': message
        })
    
    # Sinon, comportement classique
    flash(message, "success" if success else "error")
    return redirect(url_for("categories.categories"))


@categories_bp.route("/depenses-categorie/<int:id>")
def depenses_categorie(id):
    categorie = Categorie.query.get_or_404(id)
    transactions = Transaction.query.filter(Transaction.idCategorie == id, Transaction.montant < 0).order_by(Transaction.dateTransaction.desc()).all()
    now = datetime.utcnow()

    depenses_par_mois = defaultdict(float)
    for t in transactions:
        depenses_par_mois[t.dateTransaction.strftime('%Y-%m')] += float(-t.montant)

    mois_labels, mois_data = [], []
    for i in range(11, -1, -1):
        date = now - timedelta(days=i * 30)
        mois_labels.append(date.strftime('%b %Y'))
        mois_data.append(depenses_par_mois.get(date.strftime('%Y-%m'), 0))

    depenses_par_trimestre = defaultdict(float)
    for t in transactions:
        trim_key = f"{t.dateTransaction.year}-T{(t.dateTransaction.month - 1) // 3 + 1}"
        depenses_par_trimestre[trim_key] += float(-t.montant)

    trimestre_labels, trimestre_data = [], []
    for i in range(3, -1, -1):
        t = (now.month - 1) // 3 + 1 - i
        a = now.year
        while t <= 0:
            t += 4
            a -= 1
        trimestre_labels.append(f"T{t} {a}")
        trimestre_data.append(depenses_par_trimestre.get(f"{a}-T{t}", 0))

    depenses_par_annee = defaultdict(float)
    for t in transactions:
        depenses_par_annee[str(t.dateTransaction.year)] += float(-t.montant)

    annee_labels = [str(now.year - i) for i in range(2, -1, -1)]
    annee_data = [depenses_par_annee.get(a, 0) for a in annee_labels]

    return render_template("detail-depense.html", categorie=categorie, transactions=transactions[:10],
        total_depenses=sum(float(-t.montant) for t in transactions),
        mois_labels=mois_labels, mois_data=mois_data,
        trimestre_labels=trimestre_labels, trimestre_data=trimestre_data,
        annee_labels=annee_labels, annee_data=annee_data)
