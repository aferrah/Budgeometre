
import json
from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from collections import defaultdict
from extensions import db
from models import ArchiveMensuelle, Transaction, Objectif

archives_bp = Blueprint('archives', __name__)


@archives_bp.route("/archiver-mois", methods=["POST"])
def archiver_mois():
    now = datetime.utcnow()
    mois = int(request.form.get("mois") or (12 if now.month == 1 else now.month - 1))
    annee = int(request.form.get("annee") or (now.year - 1 if now.month == 1 else now.year))

    if ArchiveMensuelle.query.filter_by(annee=annee, mois=mois).first():
        flash(f"Archive {mois}/{annee} existe déjà", "warning")
        return redirect(url_for("archives.archives"))

    debut = datetime(annee, mois, 1)
    fin = datetime(annee + 1, 1, 1) if mois == 12 else datetime(annee, mois + 1, 1)
    trans = Transaction.query.filter(Transaction.dateTransaction >= debut, Transaction.dateTransaction < fin).all()

    derniere_archive_prec = ArchiveMensuelle.query.filter(
        db.or_(
            ArchiveMensuelle.annee < annee,
            db.and_(ArchiveMensuelle.annee == annee, ArchiveMensuelle.mois < mois)
        )
    ).order_by(ArchiveMensuelle.annee.desc(), ArchiveMensuelle.mois.desc()).first()

    solde_report_initial = float(derniere_archive_prec.solde_final) if derniere_archive_prec else 0.0

    total_rev = sum(float(t.montant) for t in trans if t.montant > 0)
    total_dep = sum(float(-t.montant) for t in trans if t.montant < 0)

    solde_final_archive = solde_report_initial + total_rev - total_dep

    stats_cat = defaultdict(
        lambda: {'nom': '', 'couleur': '#8b5cf6', 'depenses': 0, 'revenus': 0, 'nb_transactions': 0})
    trans_data = []
    for t in trans:
        stats_cat[t.idCategorie]['nom'] = t.categorie.nom
        stats_cat[t.idCategorie]['couleur'] = t.categorie.couleur or '#8b5cf6'
        stats_cat[t.idCategorie]['nb_transactions'] += 1
        if t.montant < 0:
            stats_cat[t.idCategorie]['depenses'] += float(-t.montant)
        else:
            stats_cat[t.idCategorie]['revenus'] += float(t.montant)
        trans_data.append(
            {'titre': t.titre, 'montant': float(t.montant), 'date': t.dateTransaction.strftime('%Y-%m-%d %H:%M:%S'),
             'categorie': t.categorie.nom, 'commentaire': t.commentaire or ''})

    archive = ArchiveMensuelle(annee=annee, mois=mois, total_revenus=total_rev, total_depenses=total_dep,
                               total_epargne=float(db.session.query(
                                   db.func.coalesce(db.func.sum(Objectif.epargne_actuelle), 0)).scalar()),
                               solde_final=solde_final_archive,
                               donnees_json=json.dumps({'transactions': trans_data, 'categories': dict(stats_cat),
                                                        'stats': {'nb_transactions': len(trans),
                                                                  'nb_depenses': sum(1 for t in trans if t.montant < 0),
                                                                  'nb_revenus': sum(
                                                                      1 for t in trans if t.montant > 0)}}))
    db.session.add(archive)


    db.session.commit()
    flash(f"Archive {mois}/{annee} créée", "success")
    return redirect(url_for("archives.archives"))


@archives_bp.route("/archives")
def archives():
    archives_list = ArchiveMensuelle.query.order_by(ArchiveMensuelle.annee.desc(), ArchiveMensuelle.mois.desc()).all()
    now = datetime.utcnow()
    existantes = {(a.annee, a.mois) for a in archives_list}
    mois_dispo = [{'annee': y, 'mois': m} for y, m in
                  sorted({(t.dateTransaction.year, t.dateTransaction.month) for t in Transaction.query.all()},
                         reverse=True)
                  if (y, m) not in existantes and (y < now.year or m < now.month)]
    return render_template("archives.html", archives=archives_list, mois_disponibles=mois_dispo)


@archives_bp.route("/archives/<int:id>")
def voir_archive(id):
    archive = ArchiveMensuelle.query.get_or_404(id)
    mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre',
                 'Novembre', 'Décembre']
    return render_template("archive-detail.html", archive=archive, donnees=json.loads(archive.donnees_json or '{}'),
                           nom_mois=mois_noms[archive.mois])


@archives_bp.route("/archives/<int:id>/toggle-masquer", methods=["POST"])
def toggle_masquer_archive(id):
    from flask import jsonify
    archive = ArchiveMensuelle.query.get_or_404(id)
    archive.masquee = not archive.masquee
    db.session.commit()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'masquee': archive.masquee,
            'message': "Archive masquée" if archive.masquee else "Archive affichée"
        })

    flash("Archive masquée" if archive.masquee else "Archive affichée", "success")
    return redirect(url_for("archives.archives"))


@archives_bp.route("/archives/<int:id>/supprimer", methods=["POST"])
def supprimer_archive(id):
    archive = ArchiveMensuelle.query.get_or_404(id)
    mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre',
                 'Novembre', 'Décembre']
    flash(f"Archive {mois_noms[archive.mois]} {archive.annee} supprimée", "success")
    db.session.delete(archive)
    db.session.commit()
    return redirect(url_for("archives.archives"))