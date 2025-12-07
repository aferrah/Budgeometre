from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
from sqlalchemy import func
from collections import defaultdict
import os

app = Flask(__name__)

CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})

# =============================================================================
# CONFIGURATION SQLITE
# =============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get('DB_PATH', os.path.join(BASE_DIR, '..', 'database', 'budgeometre.db'))

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =============================================================================
# MODELES
# =============================================================================

class Categorie(db.Model):
    __tablename__ = "categorie"
    id_categorie = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    transactions = db.relationship("Transaction", back_populates="categorie")
    objectifs = db.relationship("Objectif", back_populates="categorie")

    def to_dict(self):
        return {
            "id": self.id_categorie,
            "nom": self.nom,
            "description": self.description,
            "nb_transactions": len(self.transactions)
        }

    def to_dict_with_transactions(self):
        return {
            "id": self.id_categorie,
            "nom": self.nom,
            "description": self.description,
            "nb_transactions": len(self.transactions),
            "transactions": [t.to_dict() for t in sorted(
                self.transactions,
                key=lambda x: x.date_transaction,
                reverse=True
            )[:3]]
        }


class Transaction(db.Model):
    __tablename__ = "transaction"
    id_transaction = db.Column(db.Integer, primary_key=True)
    montant = db.Column(db.Numeric(15, 2), nullable=False)
    date_transaction = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    titre = db.Column(db.String(100), nullable=False)
    commentaire = db.Column(db.String(255))
    id_categorie = db.Column(
        db.Integer,
        db.ForeignKey("categorie.id_categorie"),
        nullable=False,
    )
    categorie = db.relationship("Categorie", back_populates="transactions")

    def to_dict(self):
        return {
            "id": self.id_transaction,
            "titre": self.titre,
            "montant": float(self.montant),
            "date": self.date_transaction.isoformat(),
            "dateFormatted": self.date_transaction.strftime('%d/%m/%Y'),
            "commentaire": self.commentaire,
            "categorie": {
                "id": self.categorie.id_categorie,
                "nom": self.categorie.nom
            }
        }


class Objectif(db.Model):
    __tablename__ = "objectif"
    id_objectif = db.Column(db.Integer, primary_key=True)
    montant = db.Column(db.Numeric(15, 2), nullable=False)
    description = db.Column(db.String(255))
    frequence = db.Column(db.String(20))
    date_debut = db.Column(db.DateTime)
    date_fin = db.Column(db.DateTime)
    id_categorie = db.Column(
        db.Integer,
        db.ForeignKey("categorie.id_categorie"),
        nullable=False,
    )
    categorie = db.relationship("Categorie", back_populates="objectifs")

    def to_dict(self):
        return {
            "id": self.id_objectif,
            "montant": float(self.montant),
            "description": self.description,
            "frequence": self.frequence,
            "categorie": self.categorie.nom
        }


# =============================================================================
# HELPERS
# =============================================================================

def get_stats(start_date, end_date=None):
    query_dep = db.session.query(func.coalesce(func.sum(Transaction.montant), 0)).filter(
        Transaction.montant < 0,
        Transaction.date_transaction >= start_date
    )
    query_rev = db.session.query(func.coalesce(func.sum(Transaction.montant), 0)).filter(
        Transaction.montant > 0,
        Transaction.date_transaction >= start_date
    )
    if end_date:
        query_dep = query_dep.filter(Transaction.date_transaction < end_date)
        query_rev = query_rev.filter(Transaction.date_transaction < end_date)

    return float(-query_dep.scalar()), float(query_rev.scalar())


def get_depenses_par_cat(start_date):
    result = (
        db.session.query(Categorie.nom, Categorie.id_categorie, func.coalesce(func.sum(Transaction.montant), 0))
        .join(Transaction)
        .filter(Transaction.montant < 0, Transaction.date_transaction >= start_date)
        .group_by(Categorie.id_categorie)
        .all()
    )
    return {nom: {"montant": float(-montant), "id": id_cat} for nom, id_cat, montant in result}


# =============================================================================
# API ROUTES - HEALTH CHECK
# =============================================================================

@app.route("/api/health", methods=["GET"])
def health_check():
    try:
        db.session.execute(db.text('SELECT 1'))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return jsonify({
        "status": "ok",
        "database": db_status,
        "database_type": "SQLite",
        "database_path": DB_PATH,
        "timestamp": datetime.utcnow().isoformat()
    })


# =============================================================================
# API ROUTES - SOLDE
# =============================================================================

@app.route("/api/solde", methods=["GET"])
def api_solde():
    total_revenus = db.session.query(
        db.func.coalesce(db.func.sum(Transaction.montant), 0)
    ).filter(Transaction.montant > 0).scalar()

    total_depenses_raw = db.session.query(
        db.func.coalesce(db.func.sum(Transaction.montant), 0)
    ).filter(Transaction.montant < 0).scalar()

    total_revenus = float(total_revenus)
    total_depenses = float(-total_depenses_raw)
    solde = total_revenus - total_depenses

    return jsonify({
        "solde": solde,
        "revenus": total_revenus,
        "depenses": total_depenses
    })


# =============================================================================
# API ROUTES - TRANSACTIONS
# =============================================================================

@app.route("/api/transactions", methods=["GET"])
def api_get_transactions():
    limit = request.args.get("limit", 10, type=int)
    offset = request.args.get("offset", 0, type=int)
    categorie_id = request.args.get("categorie_id", type=int)

    query = Transaction.query

    if categorie_id:
        query = query.filter(Transaction.id_categorie == categorie_id)

    transactions = query.order_by(
        Transaction.date_transaction.desc()
    ).offset(offset).limit(limit).all()

    total = query.count()

    return jsonify({
        "transactions": [t.to_dict() for t in transactions],
        "total": total,
        "limit": limit,
        "offset": offset
    })


@app.route("/api/transactions", methods=["POST"])
def api_create_transaction():
    data = request.json

    if not data:
        return jsonify({"error": "Donnees manquantes"}), 400

    titre = data.get("titre") or data.get("label") or "Transaction"
    montant_raw = data.get("montant") or data.get("amount") or 0
    type_transaction = data.get("type", "depense")

    try:
        montant = float(montant_raw)
    except ValueError:
        return jsonify({"error": "Montant invalide"}), 400

    if type_transaction == "depense":
        montant = -abs(montant)
    else:
        montant = abs(montant)

    commentaire = data.get("commentaire") or data.get("comment")
    date_str = data.get("date")

    if date_str:
        try:
            date_tx = datetime.fromisoformat(date_str)
        except Exception:
            date_tx = datetime.utcnow()
    else:
        date_tx = datetime.utcnow()

    cat_id = data.get("categorie_id") or data.get("category")
    categorie = None

    if cat_id:
        try:
            categorie = Categorie.query.get(int(cat_id))
        except Exception:
            categorie = None

    if not categorie:
        categorie = Categorie.query.filter_by(nom="Autre").first()
        if not categorie:
            categorie = Categorie(nom="Autre", description="Categorie par defaut")
            db.session.add(categorie)
            db.session.commit()

    tr = Transaction(
        montant=montant,
        titre=titre,
        commentaire=commentaire,
        date_transaction=date_tx,
        categorie=categorie,
    )
    db.session.add(tr)
    db.session.commit()

    return jsonify({
        "success": True,
        "transaction": tr.to_dict()
    }), 201


@app.route("/api/transactions/<int:id>", methods=["DELETE"])
def api_delete_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    db.session.delete(transaction)
    db.session.commit()
    return jsonify({"success": True, "message": "Transaction supprimee"})


# =============================================================================
# API ROUTES - CATEGORIES
# =============================================================================

@app.route("/api/categories", methods=["GET"])
def api_get_categories():
    with_transactions = request.args.get("with_transactions", "false").lower() == "true"
    categories = Categorie.query.order_by(Categorie.nom).all()

    if with_transactions:
        return jsonify([c.to_dict_with_transactions() for c in categories])
    return jsonify([c.to_dict() for c in categories])


@app.route("/api/categories", methods=["POST"])
def api_create_category():
    data = request.json

    if not data or not data.get("nom"):
        return jsonify({"error": "Nom de categorie requis"}), 400

    nom = data.get("nom")
    description = data.get("description", "")

    existante = Categorie.query.filter_by(nom=nom).first()
    if existante:
        return jsonify({"error": "Cette categorie existe deja"}), 409

    nouvelle_cat = Categorie(nom=nom, description=description)
    db.session.add(nouvelle_cat)
    db.session.commit()

    return jsonify({
        "success": True,
        "categorie": nouvelle_cat.to_dict()
    }), 201


@app.route("/api/categories/<int:id>", methods=["DELETE"])
def api_delete_category(id):
    categorie = Categorie.query.get_or_404(id)

    if categorie.transactions:
        return jsonify({
            "error": "Impossible de supprimer : des transactions sont liees"
        }), 400

    db.session.delete(categorie)
    db.session.commit()
    return jsonify({"success": True, "message": "Categorie supprimee"})


# =============================================================================
# API ROUTES - DASHBOARD
# =============================================================================

@app.route("/api/dashboard", methods=["GET"])
def api_dashboard():
    now = datetime.utcnow()

    start_month = datetime(now.year, now.month, 1)
    dep_mois, rev_mois = get_stats(start_month)

    trimestre = (now.month - 1) // 3
    start_quarter = datetime(now.year, trimestre * 3 + 1, 1)
    dep_trim, rev_trim = get_stats(start_quarter)

    start_year = datetime(now.year, 1, 1)
    dep_annee, rev_annee = get_stats(start_year)

    cat_mois = get_depenses_par_cat(start_month)
    cat_trim = get_depenses_par_cat(start_quarter)
    cat_annee = get_depenses_par_cat(start_year)

    objectifs = Objectif.query.all()
    nb_objectifs = len(objectifs)
    objectifs_respectes = 0

    for obj in objectifs:
        dep_cat = db.session.query(func.coalesce(func.sum(Transaction.montant), 0)).filter(
            Transaction.id_categorie == obj.id_categorie,
            Transaction.montant < 0,
            Transaction.date_transaction >= start_month
        ).scalar()
        if float(-dep_cat) <= float(obj.montant):
            objectifs_respectes += 1

    ratio_objectifs = int(round(100 * objectifs_respectes / nb_objectifs)) if nb_objectifs > 0 else 0

    evol_mois_labels, evol_mois_dep, evol_mois_rev = [], [], []
    for i in range(5, -1, -1):
        d = now - timedelta(days=i * 30)
        m_start = datetime(d.year, d.month, 1)
        m_end = datetime(d.year + (1 if d.month == 12 else 0), (d.month % 12) + 1, 1)
        dep, rev = get_stats(m_start, m_end)
        evol_mois_labels.append(d.strftime('%b'))
        evol_mois_dep.append(dep)
        evol_mois_rev.append(rev)

    evol_trim_labels, evol_trim_dep, evol_trim_rev = [], [], []
    for i in range(3, -1, -1):
        t = (now.month - 1) // 3 + 1 - i
        a = now.year
        while t <= 0:
            t += 4
            a -= 1
        t_start = datetime(a, (t - 1) * 3 + 1, 1)
        t_end = datetime(a + (1 if t == 4 else 0), (t * 3 % 12) + 1, 1)
        dep, rev = get_stats(t_start, t_end)
        evol_trim_labels.append(f"T{t} {a}")
        evol_trim_dep.append(dep)
        evol_trim_rev.append(rev)

    evol_annee_labels, evol_annee_dep, evol_annee_rev = [], [], []
    for i in range(2, -1, -1):
        a = now.year - i
        dep, rev = get_stats(datetime(a, 1, 1), datetime(a + 1, 1, 1))
        evol_annee_labels.append(str(a))
        evol_annee_dep.append(dep)
        evol_annee_rev.append(rev)

    return jsonify({
        "month": {
            "depenses": dep_mois,
            "revenus": rev_mois,
            "solde": rev_mois - dep_mois,
            "categories": cat_mois,
            "label": "ce mois",
            "evolution": {
                "labels": evol_mois_labels,
                "depenses": evol_mois_dep,
                "revenus": evol_mois_rev
            }
        },
        "quarter": {
            "depenses": dep_trim,
            "revenus": rev_trim,
            "solde": rev_trim - dep_trim,
            "categories": cat_trim,
            "label": "ce trimestre",
            "evolution": {
                "labels": evol_trim_labels,
                "depenses": evol_trim_dep,
                "revenus": evol_trim_rev
            }
        },
        "year": {
            "depenses": dep_annee,
            "revenus": rev_annee,
            "solde": rev_annee - dep_annee,
            "categories": cat_annee,
            "label": "cette annee",
            "evolution": {
                "labels": evol_annee_labels,
                "depenses": evol_annee_dep,
                "revenus": evol_annee_rev
            }
        },
        "objectifs": {
            "respectes": objectifs_respectes,
            "total": nb_objectifs,
            "ratio": ratio_objectifs
        }
    })


# =============================================================================
# API ROUTES - DEPENSES PAR CATEGORIE
# =============================================================================

@app.route("/api/categories/<int:id>/depenses", methods=["GET"])
def api_depenses_categorie(id):
    categorie = Categorie.query.get_or_404(id)

    transactions = Transaction.query.filter(
        Transaction.id_categorie == id,
        Transaction.montant < 0
    ).order_by(Transaction.date_transaction.desc()).all()

    now = datetime.utcnow()

    depenses_par_mois = defaultdict(float)
    for t in transactions:
        mois_key = t.date_transaction.strftime('%Y-%m')
        depenses_par_mois[mois_key] += float(-t.montant)

    mois_labels, mois_data = [], []
    for i in range(11, -1, -1):
        date = now - timedelta(days=i * 30)
        mois_key = date.strftime('%Y-%m')
        mois_label = date.strftime('%b %Y')
        mois_labels.append(mois_label)
        mois_data.append(depenses_par_mois.get(mois_key, 0))

    depenses_par_trimestre = defaultdict(float)
    for t in transactions:
        annee = t.date_transaction.year
        trimestre = (t.date_transaction.month - 1) // 3 + 1
        trim_key = f"{annee}-T{trimestre}"
        depenses_par_trimestre[trim_key] += float(-t.montant)

    trimestre_labels, trimestre_data = [], []
    trimestre_actuel = (now.month - 1) // 3 + 1
    annee_actuelle = now.year

    for i in range(3, -1, -1):
        t = trimestre_actuel - i
        a = annee_actuelle
        while t <= 0:
            t += 4
            a -= 1
        trim_key = f"{a}-T{t}"
        trimestre_labels.append(f"T{t} {a}")
        trimestre_data.append(depenses_par_trimestre.get(trim_key, 0))

    depenses_par_annee = defaultdict(float)
    for t in transactions:
        annee_key = str(t.date_transaction.year)
        depenses_par_annee[annee_key] += float(-t.montant)

    annee_labels, annee_data = [], []
    for i in range(2, -1, -1):
        a = now.year - i
        annee_labels.append(str(a))
        annee_data.append(depenses_par_annee.get(str(a), 0))

    total_depenses = sum(float(-t.montant) for t in transactions)

    return jsonify({
        "categorie": categorie.to_dict(),
        "total_depenses": total_depenses,
        "transactions": [t.to_dict() for t in transactions[:10]],
        "evolution": {
            "mois": {"labels": mois_labels, "data": mois_data},
            "trimestre": {"labels": trimestre_labels, "data": trimestre_data},
            "annee": {"labels": annee_labels, "data": annee_data}
        }
    })


# =============================================================================
# API ROUTES - OBJECTIFS
# =============================================================================

@app.route("/api/objectifs", methods=["GET"])
def api_get_objectifs():
    objectifs = Objectif.query.all()
    return jsonify([o.to_dict() for o in objectifs])


@app.route("/api/objectifs", methods=["POST"])
def api_create_objectif():
    data = request.json

    if not data:
        return jsonify({"error": "Donnees manquantes"}), 400

    montant = data.get("montant")
    categorie_id = data.get("categorie_id")

    if not montant or not categorie_id:
        return jsonify({"error": "Montant et categorie requis"}), 400

    categorie = Categorie.query.get(categorie_id)
    if not categorie:
        return jsonify({"error": "Categorie introuvable"}), 404

    objectif = Objectif(
        montant=montant,
        description=data.get("description"),
        frequence=data.get("frequence", "mensuel"),
        id_categorie=categorie_id
    )
    db.session.add(objectif)
    db.session.commit()

    return jsonify({
        "success": True,
        "objectif": objectif.to_dict()
    }), 201


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    # Creer le dossier database si necessaire
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    with app.app_context():
        db.create_all()

    print("=" * 60)
    print("BUDGEOMETRE - API Backend")
    print("=" * 60)
    print(f"Database: SQLite ({DB_PATH})")
    print(f"API: http://localhost:5000")
    print("=" * 60)

    app.run(debug=True, port=5000, host='0.0.0.0')