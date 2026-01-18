from flask import Blueprint, jsonify
from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy import func
from shared.extensions import db
from shared.models import Transaction, Categorie, Objectif, ArchiveMensuelle
import json

lecture_bp = Blueprint('lecture', __name__)


@lecture_bp.route('/home')
def get_home():
    now = datetime.utcnow()
    date_limite = now - timedelta(days=90)
    start_of_month = datetime(now.year, now.month, 1)
    transactions = Transaction.query.filter(Transaction.dateTransaction >= date_limite).order_by(
        Transaction.dateTransaction.desc()).all()

    # Exclure la catégorie Épargne des calculs revenus/dépenses affichés
    cat_epargne = Categorie.query.filter_by(nom='Épargne').first()
    epargne_id = cat_epargne.idCategorie if cat_epargne else -1

    # Revenus = transactions positives hors épargne
    total_revenus = float(db.session.query(db.func.coalesce(db.func.sum(Transaction.montant), 0)).filter(
        Transaction.montant > 0,
        Transaction.dateTransaction >= start_of_month,
        Transaction.idCategorie != epargne_id
    ).scalar() or 0)

    # Dépenses = transactions négatives hors épargne
    total_depenses_raw = float(db.session.query(db.func.coalesce(db.func.sum(Transaction.montant), 0)).filter(
        Transaction.montant < 0,
        Transaction.dateTransaction >= start_of_month,
        Transaction.idCategorie != epargne_id
    ).scalar() or 0)

    # Argent actuel = TOUTES les transactions du mois (y compris épargne)
    argent_actuel = float(db.session.query(db.func.coalesce(db.func.sum(Transaction.montant), 0)).filter(
        Transaction.dateTransaction >= start_of_month
    ).scalar() or 0)

    total_epargne = float(db.session.query(db.func.coalesce(db.func.sum(Objectif.epargne_actuelle), 0)).scalar() or 0)
    return jsonify({'transactions': [t.to_dict() for t in transactions], 'argentActuel': argent_actuel,
                    'total_revenus': total_revenus, 'total_depenses': abs(total_depenses_raw),
                    'total_epargne': total_epargne,
                    'nb_anciennes': Transaction.query.filter(Transaction.dateTransaction < date_limite).count()})


@lecture_bp.route('/categories')
def get_categories():
    now = datetime.utcnow()
    start_month = datetime(now.year, now.month, 1)
    categories = Categorie.query.order_by(Categorie.nom).all()
    result = []
    for cat in categories:
        dep = float(-(db.session.query(db.func.coalesce(db.func.sum(Transaction.montant), 0)).filter(
            Transaction.idCategorie == cat.idCategorie, Transaction.montant < 0,
            Transaction.dateTransaction >= start_month).scalar() or 0))
        d = cat.to_dict()
        d['depenses_mois'] = dep
        d['pourcentage'] = (dep / float(cat.limite_budget) * 100) if cat.limite_budget and float(
            cat.limite_budget) > 0 else 0
        d['nb_transactions'] = len(cat.transactions)
        # Inclure les transactions pour l'affichage dans le dropdown
        d['transactions'] = [t.to_dict() for t in
                             sorted(cat.transactions, key=lambda x: x.dateTransaction, reverse=True)]
        result.append(d)
    return jsonify({'categories': result, 'total_revenus': float(
        db.session.query(db.func.coalesce(db.func.sum(Transaction.montant), 0)).filter(
            Transaction.montant > 0).scalar() or 0)})


@lecture_bp.route('/categories/<int:id>')
def get_categorie(id):
    return jsonify(Categorie.query.get_or_404(id).to_dict())


@lecture_bp.route('/add-expense/data')
def get_add_expense_data():
    return jsonify({'categories': [c.to_dict() for c in Categorie.query.order_by(Categorie.nom).all()]})


@lecture_bp.route('/depenses-categorie/<int:id>')
def get_depenses_categorie(id):
    cat = Categorie.query.get_or_404(id)
    trans = Transaction.query.filter(Transaction.idCategorie == id, Transaction.montant < 0).order_by(
        Transaction.dateTransaction.desc()).all()
    now = datetime.utcnow()
    par_mois = defaultdict(float)
    for t in trans:
        par_mois[t.dateTransaction.strftime('%Y-%m')] += float(-t.montant)
    mois_labels, mois_data = [], []
    for i in range(11, -1, -1):
        d = now - timedelta(days=i * 30)
        mois_labels.append(d.strftime('%b %Y'))
        mois_data.append(par_mois.get(d.strftime('%Y-%m'), 0))
    return jsonify({'categorie': cat.to_dict(), 'transactions': [t.to_dict() for t in trans[:10]],
                    'total_depenses': sum(float(-t.montant) for t in trans), 'mois_labels': mois_labels,
                    'mois_data': mois_data, 'trimestre_labels': [], 'trimestre_data': [], 'annee_labels': [],
                    'annee_data': []})


@lecture_bp.route('/transactions')
def get_transactions():
    return jsonify([t.to_dict() for t in Transaction.query.order_by(Transaction.dateTransaction.desc()).all()])


@lecture_bp.route('/transactions/<int:id>')
def get_transaction(id):
    return jsonify({'transaction': Transaction.query.get_or_404(id).to_dict(),
                    'categories': [c.to_dict() for c in Categorie.query.order_by(Categorie.nom).all()]})


@lecture_bp.route('/objectifs')
def get_objectifs():
    result = []
    for o in Objectif.query.all():
        d = o.to_dict()
        d['epargne'] = float(o.epargne_actuelle or 0)
        d['montant_cible'] = float(o.montant)
        d['pourcentage'] = (d['epargne'] / d['montant_cible'] * 100) if d['montant_cible'] > 0 else 0
        d['status'] = 'Atteint' if d['epargne'] >= d['montant_cible'] else 'En cours'
        result.append(d)
    return jsonify({'objectifs_status': result, 'categories': [c.to_dict() for c in Categorie.query.all()]})


@lecture_bp.route('/archives')
def get_archives():
    archives = ArchiveMensuelle.query.order_by(ArchiveMensuelle.annee.desc(), ArchiveMensuelle.mois.desc()).all()
    now = datetime.utcnow()
    existantes = {(a.annee, a.mois) for a in archives}
    dispo = [{'annee': y, 'mois': m} for y, m in
             sorted({(t.dateTransaction.year, t.dateTransaction.month) for t in Transaction.query.all()}, reverse=True)
             if (y, m) not in existantes and (y < now.year or m < now.month)]
    return jsonify({'archives': [a.to_dict() for a in archives], 'mois_disponibles': dispo})


@lecture_bp.route('/archives/<int:id>')
def get_archive(id):
    a = ArchiveMensuelle.query.get_or_404(id)
    noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre',
            'Novembre', 'Décembre']
    return jsonify({'archive': a.to_dict(), 'donnees': json.loads(a.donnees_json or '{}'), 'nom_mois': noms[a.mois]})


@lecture_bp.route('/dashboard')
def get_dashboard():
    now = datetime.utcnow()

    # Exclure la catégorie Épargne
    cat_epargne = Categorie.query.filter_by(nom='Épargne').first()
    epargne_id = cat_epargne.idCategorie if cat_epargne else -1

    def stats(start, end=None):
        qd = db.session.query(func.coalesce(func.sum(Transaction.montant), 0)).filter(
            Transaction.montant < 0,
            Transaction.dateTransaction >= start,
            Transaction.idCategorie != epargne_id
        )
        qr = db.session.query(func.coalesce(func.sum(Transaction.montant), 0)).filter(
            Transaction.montant > 0,
            Transaction.dateTransaction >= start,
            Transaction.idCategorie != epargne_id
        )
        if end:
            qd, qr = qd.filter(Transaction.dateTransaction < end), qr.filter(Transaction.dateTransaction < end)
        return float(-(qd.scalar() or 0)), float(qr.scalar() or 0)

    def cat_dep(start):
        r = db.session.query(Categorie.nom, func.coalesce(func.sum(Transaction.montant), 0)).join(Transaction).filter(
            Transaction.montant < 0,
            Transaction.dateTransaction >= start,
            Transaction.idCategorie != epargne_id
        ).group_by(Categorie.idCategorie).all()
        return {n: float(-m) for n, m in r}

    sm, sq, sy = datetime(now.year, now.month, 1), datetime(now.year, ((now.month - 1) // 3) * 3 + 1, 1), datetime(
        now.year, 1, 1)
    dm, rm = stats(sm)
    dt, rt = stats(sq)
    da, ra = stats(sy)
    cats = Categorie.query.all()
    ids, colors = {c.nom: c.idCategorie for c in cats}, {c.nom: c.couleur or '#8b5cf6' for c in cats}
    nb, ok, alerts = 0, 0, []
    for c in cats:
        if c.nom == 'Épargne':
            continue  # Ignorer la catégorie Épargne
        if c.limite_budget and float(c.limite_budget) > 0:
            nb += 1
            d = float(-(db.session.query(func.coalesce(func.sum(Transaction.montant), 0)).filter(
                Transaction.idCategorie == c.idCategorie, Transaction.montant < 0,
                Transaction.dateTransaction >= sm).scalar() or 0))
            if d <= float(c.limite_budget):
                ok += 1
            p = d / float(c.limite_budget) * 100
            if p >= 100:
                alerts.append({'type': 'danger', 'category': c.nom, 'message': f'Dépassé ({p:.0f}%)'})
            elif p >= 80:
                alerts.append({'type': 'warning', 'category': c.nom, 'message': f'{p:.0f}% utilisé'})
    el, ed, er = [], [], []
    for i in range(5, -1, -1):
        d = now - timedelta(days=i * 30)
        s, e = datetime(d.year, d.month, 1), datetime(d.year + (1 if d.month == 12 else 0), (d.month % 12) + 1, 1)
        dep, rev = stats(s, e)
        el.append(d.strftime('%b'))
        ed.append(dep)
        er.append(rev)
    return jsonify(
        {'dep_mois': dm, 'rev_mois': rm, 'solde_mois': rm - dm, 'cat_mois': cat_dep(sm), 'dep_trim': dt, 'rev_trim': rt,
         'solde_trim': rt - dt, 'cat_trim': cat_dep(sq), 'dep_annee': da, 'rev_annee': ra, 'solde_annee': ra - da,
         'cat_annee': cat_dep(sy), 'objectifs_respectes': ok, 'nb_objectifs': nb,
         'ratio_objectifs': int(100 * ok / nb) if nb else 0, 'evol_mois_labels': el, 'evol_mois_dep': ed,
         'evol_mois_rev': er, 'evol_trim_labels': [], 'evol_trim_dep': [], 'evol_trim_rev': [], 'evol_annee_labels': [],
         'evol_annee_dep': [], 'evol_annee_rev': [], 'categories_ids': ids, 'categories_colors': colors,
         'budget_alerts': alerts})