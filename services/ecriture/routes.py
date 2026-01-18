from flask import Blueprint, jsonify, request
from datetime import datetime
from collections import defaultdict
from shared.extensions import db
from shared.models import Transaction, Categorie, Objectif, ArchiveMensuelle
import json

ecriture_bp = Blueprint('ecriture', __name__)

def get_epargne_cat():
    c = Categorie.query.filter_by(nom='Épargne').first()
    if not c:
        c = Categorie(nom='Épargne', description='Transferts vers épargne', couleur='#f59e0b')
        db.session.add(c)
        db.session.commit()
    return c

@ecriture_bp.route('/transactions', methods=['POST'])
def add_transaction():
    d = request.json
    m = float(d.get('montant', 0))
    m = -abs(m) if d.get('type') == 'depense' else abs(m)
    cat = Categorie.query.get(d.get('idCategorie')) if d.get('idCategorie') else None
    if not cat:
        cat = Categorie.query.filter_by(nom='Autre').first()
        if not cat:
            cat = Categorie(nom='Autre', couleur='#64748b')
            db.session.add(cat)
            db.session.commit()
    t = Transaction(montant=m, titre=d.get('titre','Dépense'), commentaire=d.get('commentaire'), dateTransaction=datetime.fromisoformat(d['date']) if d.get('date') else datetime.utcnow(), idCategorie=cat.idCategorie)
    db.session.add(t)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Transaction ajoutée'})

@ecriture_bp.route('/transactions/<int:id>', methods=['PUT'])
def update_transaction(id):
    t = Transaction.query.get_or_404(id)
    if t.categorie and t.categorie.nom == 'Épargne':
        return jsonify({'success': False, 'message': 'Transaction épargne non modifiable'}), 400
    d = request.json
    m = float(d.get('montant', 0))
    t.montant = -abs(m) if d.get('type') == 'depense' else abs(m)
    t.titre = d.get('titre', t.titre)
    t.commentaire = d.get('commentaire')
    if d.get('date'):
        t.dateTransaction = datetime.fromisoformat(d['date'])
    if d.get('idCategorie'):
        t.idCategorie = d['idCategorie']
    db.session.commit()
    return jsonify({'success': True, 'message': 'Transaction modifiée'})

@ecriture_bp.route('/transactions/<int:id>', methods=['DELETE'])
def delete_transaction(id):
    t = Transaction.query.get_or_404(id)
    if t.categorie and t.categorie.nom == 'Épargne':
        return jsonify({'success': False, 'message': 'Transaction épargne non supprimable'}), 400
    db.session.delete(t)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Transaction supprimée'})

@ecriture_bp.route('/categories', methods=['POST'])
def add_categorie():
    d = request.json
    if Categorie.query.filter_by(nom=d.get('nom')).first():
        return jsonify({'success': False, 'message': 'Catégorie existe déjà'}), 400
    c = Categorie(nom=d['nom'], description=d.get('description',''), couleur=d.get('couleur','#8b5cf6'), limite_budget=float(d.get('limite_budget', 0) or 0))
    db.session.add(c)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Catégorie ajoutée'})

@ecriture_bp.route('/categories/<int:id>', methods=['PUT'])
def update_categorie(id):
    c = Categorie.query.get_or_404(id)
    d = request.json
    c.nom = d.get('nom', c.nom)
    c.description = d.get('description', '')
    c.couleur = d.get('couleur', '#8b5cf6')
    c.limite_budget = float(d.get('limite_budget', 0) or 0)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Catégorie modifiée'})

@ecriture_bp.route('/categories/<int:id>', methods=['DELETE'])
def delete_categorie(id):
    c = Categorie.query.get_or_404(id)
    if c.transactions:
        return jsonify({'success': False, 'message': f'{len(c.transactions)} transactions liées'}), 400
    db.session.delete(c)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Catégorie supprimée'})

@ecriture_bp.route('/objectifs', methods=['POST'])
def add_objectif():
    d = request.json
    o = Objectif(montant=float(d['montant']), description=d.get('description'), frequence=d.get('frequence','mensuel'), idCategorie=int(d['idCategorie']), dateDebut=datetime.utcnow())
    db.session.add(o)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Objectif ajouté'})

@ecriture_bp.route('/objectifs/<int:id>/ajouter', methods=['POST'])
def ajouter_epargne(id):
    o = Objectif.query.get_or_404(id)
    m = float(request.json.get('montant', 0))
    solde = float(db.session.query(db.func.coalesce(db.func.sum(Transaction.montant), 0)).scalar() or 0)
    if m > solde:
        return jsonify({'success': False, 'message': f'Solde insuffisant ({solde:.2f}€)'}), 400
    c = get_epargne_cat()
    db.session.add(Transaction(montant=-m, titre=f"Épargne: {o.description or 'Objectif'}", idCategorie=c.idCategorie))
    o.epargne_actuelle = float(o.epargne_actuelle or 0) + m
    db.session.commit()
    return jsonify({'success': True, 'message': f'{m:.2f}€ ajouté'})

@ecriture_bp.route('/objectifs/<int:id>/retirer', methods=['POST'])
def retirer_epargne(id):
    o = Objectif.query.get_or_404(id)
    m = float(request.json.get('montant', 0))
    e = float(o.epargne_actuelle or 0)
    if m > e:
        return jsonify({'success': False, 'message': f'Épargne insuffisante ({e:.2f}€)'}), 400
    c = get_epargne_cat()
    db.session.add(Transaction(montant=m, titre=f"Retrait: {o.description or 'Objectif'}", idCategorie=c.idCategorie))
    o.epargne_actuelle = e - m
    db.session.commit()
    return jsonify({'success': True, 'message': f'{m:.2f}€ retiré'})

@ecriture_bp.route('/objectifs/<int:id>/recuperer', methods=['POST'])
def recuperer_epargne(id):
    o = Objectif.query.get_or_404(id)
    e = float(o.epargne_actuelle or 0)
    if e <= 0:
        return jsonify({'success': False, 'message': 'Aucune épargne'}), 400
    c = get_epargne_cat()
    db.session.add(Transaction(montant=e, titre=f"Récupération: {o.description}", idCategorie=c.idCategorie))
    db.session.delete(o)
    db.session.commit()
    return jsonify({'success': True, 'message': f'{e:.2f}€ récupéré'})

@ecriture_bp.route('/objectifs/<int:id>', methods=['DELETE'])
def delete_objectif(id):
    o = Objectif.query.get_or_404(id)
    e = float(o.epargne_actuelle or 0)
    if e > 0:
        c = get_epargne_cat()
        db.session.add(Transaction(montant=e, titre=f"Suppression: {o.description}", idCategorie=c.idCategorie))
    db.session.delete(o)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Objectif supprimé'})

@ecriture_bp.route('/archives', methods=['POST'])
def archiver_mois():
    d = request.json
    now = datetime.utcnow()
    mois = int(d.get('mois') or (12 if now.month == 1 else now.month - 1))
    annee = int(d.get('annee') or (now.year - 1 if now.month == 1 else now.year))
    if ArchiveMensuelle.query.filter_by(annee=annee, mois=mois).first():
        return jsonify({'success': False, 'message': 'Archive existe déjà'}), 400
    debut = datetime(annee, mois, 1)
    fin = datetime(annee + 1, 1, 1) if mois == 12 else datetime(annee, mois + 1, 1)
    trans = Transaction.query.filter(Transaction.dateTransaction >= debut, Transaction.dateTransaction < fin).all()
    rev = sum(float(t.montant) for t in trans if t.montant > 0)
    dep = sum(float(-t.montant) for t in trans if t.montant < 0)
    stats = defaultdict(lambda: {'nom': '', 'couleur': '#8b5cf6', 'depenses': 0, 'revenus': 0, 'nb_transactions': 0})
    tdata = []
    for t in trans:
        stats[t.idCategorie]['nom'] = t.categorie.nom
        stats[t.idCategorie]['couleur'] = t.categorie.couleur or '#8b5cf6'
        stats[t.idCategorie]['nb_transactions'] += 1
        if t.montant < 0:
            stats[t.idCategorie]['depenses'] += float(-t.montant)
        else:
            stats[t.idCategorie]['revenus'] += float(t.montant)
        tdata.append({'titre': t.titre, 'montant': float(t.montant), 'date': t.dateTransaction.strftime('%Y-%m-%d'), 'categorie': t.categorie.nom, 'commentaire': t.commentaire or ''})
    a = ArchiveMensuelle(annee=annee, mois=mois, total_revenus=rev, total_depenses=dep, total_epargne=float(db.session.query(db.func.coalesce(db.func.sum(Objectif.epargne_actuelle), 0)).scalar() or 0), solde_final=rev - dep, donnees_json=json.dumps({'transactions': tdata, 'categories': dict(stats), 'stats': {'nb_transactions': len(trans), 'nb_depenses': sum(1 for t in trans if t.montant < 0), 'nb_revenus': sum(1 for t in trans if t.montant > 0)}}))
    db.session.add(a)
    db.session.commit()
    return jsonify({'success': True, 'message': f'Archive {mois}/{annee} créée'})

@ecriture_bp.route('/archives/<int:id>/toggle-masquer', methods=['POST'])
def toggle_masquer(id):
    a = ArchiveMensuelle.query.get_or_404(id)
    a.masquee = not a.masquee
    db.session.commit()
    return jsonify({'success': True, 'masquee': a.masquee, 'message': 'Masquée' if a.masquee else 'Affichée'})

@ecriture_bp.route('/archives/<int:id>', methods=['DELETE'])
def delete_archive(id):
    a = ArchiveMensuelle.query.get_or_404(id)
    db.session.delete(a)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Archive supprimée'})