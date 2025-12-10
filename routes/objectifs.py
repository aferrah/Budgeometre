from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from extensions import db
from models import Objectif, Categorie, Transaction

objectifs_bp = Blueprint('objectifs', __name__)


def get_or_create_epargne_cat():
    cat = Categorie.query.filter_by(nom="Épargne").first()
    if not cat:
        cat = Categorie(nom="Épargne", description="Transferts vers épargne", couleur="#f59e0b")
        db.session.add(cat)
        db.session.commit()
    return cat


@objectifs_bp.route("/mes-objectifs", methods=["GET", "POST"])
def mes_objectifs():
    if request.method == "POST":
        montant_str = request.form.get("montant")
        categorie_str = request.form.get("categorie")
        if montant_str and categorie_str:
            try:
                new_obj = Objectif(
                    montant=float(montant_str), epargne_actuelle=0,
                    description=request.form.get("description"),
                    frequence=request.form.get("frequence"),
                    idCategorie=int(categorie_str), dateDebut=datetime.utcnow()
                )
                db.session.add(new_obj)
                db.session.commit()
                flash("Objectif ajouté avec succès", "success")
            except ValueError:
                pass
        return redirect(url_for("objectifs.mes_objectifs"))

    objectifs = Objectif.query.all()
    objectifs_status = []
    for obj in objectifs:
        epargne = float(obj.epargne_actuelle or 0)
        montant_cible = float(obj.montant)
        objectifs_status.append((obj, epargne, montant_cible,
            (epargne / montant_cible * 100) if montant_cible > 0 else 0,
            "Atteint" if epargne >= montant_cible else "En cours"))
    return render_template("mes-objectifs.html", objectifs_status=objectifs_status, categories=Categorie.query.all())


@objectifs_bp.route("/objectif/<int:id>/ajouter", methods=["POST"])
def ajouter_epargne(id):
    objectif = Objectif.query.get_or_404(id)
    try:
        montant = float(request.form.get("montant", 0))
    except:
        return redirect(url_for("objectifs.mes_objectifs"))

    total_rev = float(db.session.query(db.func.coalesce(db.func.sum(Transaction.montant), 0)).filter(Transaction.montant > 0).scalar())
    total_dep = float(db.session.query(db.func.coalesce(db.func.sum(Transaction.montant), 0)).filter(Transaction.montant < 0).scalar())
    solde = total_rev + total_dep

    if montant > solde:
        flash(f"Solde insuffisant ! Vous avez {solde:.2f}€ disponible.", "error")
        return redirect(url_for("objectifs.mes_objectifs"))

    cat = get_or_create_epargne_cat()
    db.session.add(Transaction(montant=-montant, titre=f"Épargne: {objectif.description or 'Objectif'}",
        commentaire="Transfert vers épargne", dateTransaction=datetime.utcnow(), idCategorie=cat.idCategorie))
    objectif.epargne_actuelle = float(objectif.epargne_actuelle or 0) + montant
    db.session.commit()
    flash(f"{montant:.2f}€ transféré vers votre épargne !", "success")
    return redirect(url_for("objectifs.mes_objectifs"))


@objectifs_bp.route("/objectif/<int:id>/retirer", methods=["POST"])
def retirer_epargne(id):
    objectif = Objectif.query.get_or_404(id)
    try:
        montant = float(request.form.get("montant", 0))
    except:
        return redirect(url_for("objectifs.mes_objectifs"))

    epargne = float(objectif.epargne_actuelle or 0)
    if montant > epargne:
        flash(f"Épargne insuffisante ! Vous avez {epargne:.2f}€.", "error")
        return redirect(url_for("objectifs.mes_objectifs"))

    cat = get_or_create_epargne_cat()
    db.session.add(Transaction(montant=montant, titre=f"Retrait épargne: {objectif.description or 'Objectif'}",
        commentaire="Retrait depuis épargne", dateTransaction=datetime.utcnow(), idCategorie=cat.idCategorie))
    objectif.epargne_actuelle = epargne - montant
    db.session.commit()
    flash(f"{montant:.2f}€ retiré !", "success")
    return redirect(url_for("objectifs.mes_objectifs"))


@objectifs_bp.route("/objectif/<int:id>/recuperer", methods=["POST"])
def recuperer_epargne(id):
    objectif = Objectif.query.get_or_404(id)
    epargne = float(objectif.epargne_actuelle or 0)
    if epargne <= 0:
        flash("Aucune épargne à récupérer.", "error")
        return redirect(url_for("objectifs.mes_objectifs"))

    cat = get_or_create_epargne_cat()
    db.session.add(Transaction(montant=epargne, titre=f"Récupération: {objectif.description or 'Objectif'}",
        commentaire="Récupération totale", dateTransaction=datetime.utcnow(), idCategorie=cat.idCategorie))
    db.session.delete(objectif)
    db.session.commit()
    flash(f"{epargne:.2f}€ récupéré ! Objectif d'épargne supprimé.", "success")
    return redirect(url_for("objectifs.mes_objectifs"))


@objectifs_bp.route("/objectif/<int:id>/supprimer", methods=["POST"])
def supprimer_objectif(id):
    objectif = Objectif.query.get_or_404(id)
    epargne = float(objectif.epargne_actuelle or 0)
    if epargne > 0:
        cat = get_or_create_epargne_cat()
        db.session.add(Transaction(montant=epargne, titre=f"Suppression: {objectif.description or 'Objectif'}",
            commentaire="Récupération suite à suppression", dateTransaction=datetime.utcnow(), idCategorie=cat.idCategorie))
        flash(f"Objectif supprimé. {epargne:.2f}€ retransféré.", "success")
    else:
        flash("Objectif supprimé.", "success")
    db.session.delete(objectif)
    db.session.commit()
    return redirect(url_for("objectifs.mes_objectifs"))
