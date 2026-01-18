from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
import requests
from datetime import datetime

home_bp = Blueprint('home', __name__)
transactions_bp = Blueprint('transactions', __name__)
categories_bp = Blueprint('categories', __name__)
objectifs_bp = Blueprint('objectifs', __name__)
archives_bp = Blueprint('archives', __name__)
dashboard_bp = Blueprint('dashboard', __name__)

def api_get(endpoint):
    try:
        r = requests.get(f"{current_app.config['LECTURE_URL']}/api{endpoint}", timeout=10)
        if not r.ok:
            current_app.logger.error(f"GET {endpoint} failed: {r.status_code} - {r.text}")
        return r.json() if r.ok else {}
    except Exception as e:
        current_app.logger.error(f"GET {endpoint} error: {e}")
        return {}

def api_post(endpoint, data=None):
    try:
        r = requests.post(f"{current_app.config['ECRITURE_URL']}/api{endpoint}", json=data or {}, timeout=10)
        if not r.ok:
            current_app.logger.error(f"POST {endpoint} failed: {r.status_code} - {r.text}")
        return r.json()
    except Exception as e:
        current_app.logger.error(f"POST {endpoint} error: {e}")
        return {'success': False, 'message': f'Erreur connexion: {str(e)}'}

def api_put(endpoint, data):
    try:
        r = requests.put(f"{current_app.config['ECRITURE_URL']}/api{endpoint}", json=data, timeout=10)
        if not r.ok:
            current_app.logger.error(f"PUT {endpoint} failed: {r.status_code} - {r.text}")
        return r.json()
    except Exception as e:
        current_app.logger.error(f"PUT {endpoint} error: {e}")
        return {'success': False, 'message': f'Erreur connexion: {str(e)}'}

def api_delete(endpoint):
    try:
        r = requests.delete(f"{current_app.config['ECRITURE_URL']}/api{endpoint}", timeout=10)
        if not r.ok:
            current_app.logger.error(f"DELETE {endpoint} failed: {r.status_code} - {r.text}")
        return r.json()
    except Exception as e:
        current_app.logger.error(f"DELETE {endpoint} error: {e}")
        return {'success': False, 'message': f'Erreur connexion: {str(e)}'}

class Proxy:
    def __init__(self, d):
        for k, v in (d or {}).items():
            if isinstance(v, dict):
                v = Proxy(v)
            elif isinstance(v, list):
                v = [Proxy(i) if isinstance(i, dict) else i for i in v]
            setattr(self, k, v)
        if 'dateTransaction' in (d or {}) and d['dateTransaction']:
            try:
                self.dateTransaction = datetime.fromisoformat(d['dateTransaction'].replace('Z',''))
            except:
                self.dateTransaction = datetime.utcnow()
        if 'dateArchivage' in (d or {}) and d['dateArchivage']:
            try:
                self.dateArchivage = datetime.fromisoformat(d['dateArchivage'].replace('Z',''))
            except:
                self.dateArchivage = datetime.utcnow()
        if 'dateDebut' in (d or {}) and d['dateDebut']:
            try:
                self.dateDebut = datetime.fromisoformat(d['dateDebut'].replace('Z',''))
            except:
                self.dateDebut = datetime.utcnow()
        if not hasattr(self, 'transactions'):
            self.transactions = []

@home_bp.route('/')
def home():
    d = api_get('/home')
    return render_template('index.html', transactions=[Proxy(t) for t in d.get('transactions', [])],
        argentActuel=d.get('argentActuel', 0), total_revenus=d.get('total_revenus', 0),
        total_depenses=d.get('total_depenses', 0), total_epargne=d.get('total_epargne', 0),
        nb_anciennes=d.get('nb_anciennes', 0))

@transactions_bp.route('/add-expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'GET':
        d = api_get('/add-expense/data')
        return render_template('add-expense.html', categories=[Proxy(c) for c in d.get('categories', [])])
    r = api_post('/transactions', {'titre': request.form.get('label'), 'montant': request.form.get('amount'),
        'type': request.form.get('type', 'depense'), 'commentaire': request.form.get('comment'),
        'date': request.form.get('date'), 'idCategorie': request.form.get('category')})
    flash(r.get('message', 'OK'), 'success' if r.get('success') else 'error')
    return redirect(url_for('home.home'))

@transactions_bp.route('/transaction/<int:id>/modifier', methods=['GET', 'POST'])
def modifier_transaction(id):
    if request.method == 'GET':
        d = api_get(f'/transactions/{id}')
        return render_template('modifier-transaction.html', transaction=Proxy(d.get('transaction', {})),
            categories=[Proxy(c) for c in d.get('categories', [])])
    r = api_put(f'/transactions/{id}', {'titre': request.form.get('label'), 'montant': request.form.get('amount'),
        'type': request.form.get('type'), 'commentaire': request.form.get('comment'),
        'date': request.form.get('date'), 'idCategorie': request.form.get('category')})
    flash(r.get('message', 'OK'), 'success' if r.get('success') else 'error')
    return redirect(url_for('home.home'))

@transactions_bp.route('/transaction/<int:id>/supprimer', methods=['POST'])
def supprimer_transaction(id):
    r = api_delete(f'/transactions/{id}')
    flash(r.get('message', 'OK'), 'success' if r.get('success') else 'error')
    return redirect(url_for('home.home'))

@categories_bp.route('/categories', methods=['GET', 'POST'])
def categories():
    if request.method == 'POST':
        r = api_post('/categories', {'nom': request.form.get('nom'), 'description': request.form.get('description'),
            'couleur': request.form.get('couleur'), 'limite_budget': request.form.get('limite_budget')})
        flash(r.get('message', 'OK'), 'success' if r.get('success') else 'error')
        return redirect(url_for('categories.categories'))
    d = api_get('/categories')
    return render_template('categories.html', categories=[Proxy(c) for c in d.get('categories', [])],
        total_revenus=d.get('total_revenus', 0))

@categories_bp.route('/categories/<int:id>/modifier', methods=['GET', 'POST'])
def modifier_categorie(id):
    if request.method == 'GET':
        return render_template('modifier-categorie.html', categorie=Proxy(api_get(f'/categories/{id}')))
    r = api_put(f'/categories/{id}', {'nom': request.form.get('nom'), 'description': request.form.get('description'),
        'couleur': request.form.get('couleur'), 'limite_budget': request.form.get('limite_budget')})
    flash(r.get('message', 'OK'), 'success' if r.get('success') else 'error')
    return redirect(url_for('categories.categories'))

@categories_bp.route('/categories/delete/<int:id>', methods=['POST'])
def delete_category(id):
    r = api_delete(f'/categories/{id}')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(r)
    flash(r.get('message', 'OK'), 'success' if r.get('success') else 'error')
    return redirect(url_for('categories.categories'))

@categories_bp.route('/depenses-categorie/<int:id>')
def depenses_categorie(id):
    d = api_get(f'/depenses-categorie/{id}')
    return render_template('detail-depense.html', categorie=Proxy(d.get('categorie', {})),
        transactions=[Proxy(t) for t in d.get('transactions', [])], total_depenses=d.get('total_depenses', 0),
        mois_labels=d.get('mois_labels', []), mois_data=d.get('mois_data', []),
        trimestre_labels=d.get('trimestre_labels', []), trimestre_data=d.get('trimestre_data', []),
        annee_labels=d.get('annee_labels', []), annee_data=d.get('annee_data', []))

@objectifs_bp.route('/mes-objectifs', methods=['GET', 'POST'])
def mes_objectifs():
    if request.method == 'POST':
        r = api_post('/objectifs', {'montant': request.form.get('montant'), 'description': request.form.get('description'),
            'frequence': request.form.get('frequence'), 'idCategorie': request.form.get('categorie')})
        flash(r.get('message', 'OK'), 'success' if r.get('success') else 'error')
        return redirect(url_for('objectifs.mes_objectifs'))
    d = api_get('/objectifs')
    status = [(Proxy(o), o.get('epargne',0), o.get('montant_cible',0), o.get('pourcentage',0), o.get('status',''))
              for o in d.get('objectifs_status', [])]
    return render_template('mes-objectifs.html', objectifs_status=status, categories=[Proxy(c) for c in d.get('categories', [])])

@objectifs_bp.route('/objectif/<int:id>/ajouter', methods=['POST'])
def ajouter_epargne(id):
    r = api_post(f'/objectifs/{id}/ajouter', {'montant': request.form.get('montant')})
    flash(r.get('message', 'OK'), 'success' if r.get('success') else 'error')
    return redirect(url_for('objectifs.mes_objectifs'))

@objectifs_bp.route('/objectif/<int:id>/retirer', methods=['POST'])
def retirer_epargne(id):
    r = api_post(f'/objectifs/{id}/retirer', {'montant': request.form.get('montant')})
    flash(r.get('message', 'OK'), 'success' if r.get('success') else 'error')
    return redirect(url_for('objectifs.mes_objectifs'))

@objectifs_bp.route('/objectif/<int:id>/recuperer', methods=['POST'])
def recuperer_epargne(id):
    r = api_post(f'/objectifs/{id}/recuperer')
    flash(r.get('message', 'OK'), 'success' if r.get('success') else 'error')
    return redirect(url_for('objectifs.mes_objectifs'))

@objectifs_bp.route('/objectif/<int:id>/supprimer', methods=['POST'])
def supprimer_objectif(id):
    r = api_delete(f'/objectifs/{id}')
    flash(r.get('message', 'OK'), 'success' if r.get('success') else 'error')
    return redirect(url_for('objectifs.mes_objectifs'))

@archives_bp.route('/archives')
def archives():
    d = api_get('/archives')
    return render_template('archives.html', archives=[Proxy(a) for a in d.get('archives', [])],
        mois_disponibles=d.get('mois_disponibles', []))

@archives_bp.route('/archiver-mois', methods=['POST'])
def archiver_mois():
    r = api_post('/archives', {'mois': request.form.get('mois'), 'annee': request.form.get('annee')})
    flash(r.get('message', 'OK'), 'success' if r.get('success') else 'warning')
    return redirect(url_for('archives.archives'))

@archives_bp.route('/archives/<int:id>')
def voir_archive(id):
    d = api_get(f'/archives/{id}')
    return render_template('archive-detail.html', archive=Proxy(d.get('archive', {})),
        donnees=d.get('donnees', {}), nom_mois=d.get('nom_mois', ''))

@archives_bp.route('/archives/<int:id>/toggle-masquer', methods=['POST'])
def toggle_masquer_archive(id):
    r = api_post(f'/archives/{id}/toggle-masquer')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(r)
    flash(r.get('message', 'OK'), 'success')
    return redirect(url_for('archives.archives'))

@archives_bp.route('/archives/<int:id>/supprimer', methods=['POST'])
def supprimer_archive(id):
    r = api_delete(f'/archives/{id}')
    flash(r.get('message', 'OK'), 'success')
    return redirect(url_for('archives.archives'))

@dashboard_bp.route('/dashboard')
def budget_dashboard():
    d = api_get('/dashboard')
    return render_template('budget-dashboard.html', **d)

@home_bp.route('/init-test-db')
def init_test_db():
    """Initialise la base avec des données de test sur 6 mois"""
    r = api_post('/init-test-db')
    flash(r.get('message', 'OK'), 'success' if r.get('success') else 'error')
    return redirect(url_for('home.home'))