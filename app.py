from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func

app = Flask(__name__)

# --- CONFIG BD ---
# Fichier SQLite local : budget.db dans ton projet
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///budget.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# --- MODELES BD ---

class Categorie(db.Model):
    __tablename__ = "CATEGORIE"

    idCategorie = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))

    transactions = db.relationship("Transaction", back_populates="categorie")
    objectifs = db.relationship("Objectif", back_populates="categorie")

    def __repr__(self):
        return f"<Categorie {self.nom}>"


class Transaction(db.Model):
    __tablename__ = "TRANSACTION"

    idTransaction = db.Column(db.Integer, primary_key=True)
    montant = db.Column(db.Numeric(15, 2), nullable=False)
    dateTransaction = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    titre = db.Column(db.String(100), nullable=False)
    commentaire = db.Column(db.String(255))

    idCategorie = db.Column(
        db.Integer,
        db.ForeignKey("CATEGORIE.idCategorie", ondelete="RESTRICT"),
        nullable=False,
    )

    categorie = db.relationship("Categorie", back_populates="transactions")

    __table_args__ = (
        db.Index("idx_transaction_date", "dateTransaction"),
        db.Index("idx_transaction_categorie", "idCategorie"),
    )

    def __repr__(self):
        return f"<Transaction {self.titre} {self.montant} {self.commentaire}>"


class Objectif(db.Model):
    __tablename__ = "OBJECTIF"

    idObjectif = db.Column(db.Integer, primary_key=True)
    montant = db.Column(db.Numeric(15, 2), nullable=False)
    description = db.Column(db.String(255))
    frequence = db.Column(db.String(20))  # 'mensuel', 'annuel', etc.
    dateDebut = db.Column(db.DateTime)
    dateFin = db.Column(db.DateTime)

    idCategorie = db.Column(
        db.Integer,
        db.ForeignKey("CATEGORIE.idCategorie", ondelete="RESTRICT"),
        nullable=False,
    )

    categorie = db.relationship("Categorie", back_populates="objectifs")

    def __repr__(self):
        return f"<Objectif {self.description} {self.montant}>"


# --- ROUTES FLASK SIMPLES ---

@app.route("/")
def home():
    argentInitial = 2000
    # Récupère des données depuis la base et les envoie au template
    # - dernières transactions (10)
    transactions = (
        Transaction.query.order_by(Transaction.dateTransaction.desc()).limit(10).all()
    )

    # - somme totale des transactions (montants négatifs = dépenses)
    total_transactions = db.session.query(db.func.coalesce(db.func.sum(Transaction.montant), 0)).scalar()
    
    # - argentActuel = argentInitial + somme des transactions
    argentActuel = float(argentInitial) + float(total_transactions) if total_transactions is not None else float(argentInitial)

    # - totaux par catégorie (nom, somme)
    category_totals = (
        db.session.query(Categorie.nom, db.func.coalesce(db.func.sum(Transaction.montant), 0))
        .join(Transaction)
        .group_by(Categorie.idCategorie)
        .all()
    )

    # - objectifs
    objectifs = Objectif.query.all()

    # - somme des objectifs (pour l'UI)
    objectif_total = db.session.query(db.func.coalesce(db.func.sum(Objectif.montant), 0)).scalar()

    return render_template(
        "index.html",
        transactions=transactions,
        argentInitial=argentInitial,
        argentActuel=argentActuel,
        objectifEpargne=float(objectif_total) if objectif_total is not None else 0.0,
        category_totals=category_totals,
        objectifs=objectifs,
    )


@app.route("/init-test")
def init_test():
    """Crée plusieurs catégories, transactions et objectifs pour tester."""
    # 1) Créer les catégories
    cat_alimentation = Categorie(nom="Alimentation", description="Courses, restos, etc.")
    cat_transport = Categorie(nom="Transport", description="Essence, transports publics")
    cat_loisirs = Categorie(nom="Loisirs", description="Cinéma, activités")
    
    db.session.add_all([cat_alimentation, cat_transport, cat_loisirs])
    db.session.commit()

    # 2) Créer plusieurs transactions
    transactions_data = [
        Transaction(titre="Courses supermarché", montant=-45.30, categorie=cat_alimentation, commentaire="Courses hebdo"),
        Transaction(titre="Restaurant", montant=-28.50, categorie=cat_alimentation, commentaire="Déjeuner en famille"),
        Transaction(titre="Essence", montant=-60.00, categorie=cat_transport, commentaire="Plein d'essence"),
        Transaction(titre="Ticket bus", montant=-15.00, categorie=cat_transport, commentaire="Abonnement mensuel"),
        Transaction(titre="Cinéma", montant=-12.00, categorie=cat_loisirs, commentaire="Film avec amis"),
        Transaction(titre="Courses Leclerc", montant=-38.75, categorie=cat_alimentation, commentaire="Courses principales"),
        Transaction(titre="Café", montant=-5.50, categorie=cat_alimentation, commentaire="Pause café au travail"),
    ]
    
    for tr in transactions_data:
        db.session.add(tr)
    db.session.commit()

    # 3) Créer des objectifs
    obj_alimentation = Objectif(
        montant=250,
        description="Budget alimentation mensuel",
        frequence="mensuel",
        categorie=cat_alimentation,
    )
    obj_transport = Objectif(
        montant=150,
        description="Budget transport mensuel",
        frequence="mensuel",
        categorie=cat_transport,
    )
    
    db.session.add_all([obj_alimentation, obj_transport])
    db.session.commit()

    return "Données de test ajoutées ✅ (3 catégories, 7 transactions, 2 objectifs)"


@app.route("/transactions")
def list_transactions():
    """Afficher toutes les transactions en texte brut."""
    transactions = Transaction.query.order_by(Transaction.dateTransaction.desc()).all()
    lignes = []
    for t in transactions:
        lignes.append(f"{t.dateTransaction} - {t.titre} : {t.montant}€ (cat: {t.categorie.nom})")
    return "<br>".join(lignes) if lignes else "Aucune transaction pour l'instant."

'''@app.route("/mes-depenses", methods=["GET", "POST"])
def mes_depenses():
    # --- 1) Traitement du formulaire (POST) ---
    if request.method == "POST":
        titre = request.form.get("titre")
        montant = request.form.get("montant")
        categorie_id = request.form.get("idCategorie")

        # Vérification basique
        if not titre or not montant or not categorie_id:
            return "Erreur : tous les champs sont obligatoires.", 400

        # Validation des types
        try:
            montant = float(montant)
            categorie_id = int(categorie_id)
        except ValueError:
            return "Erreur : montant ou catégorie invalide.", 400

        # Création de la transaction
        nouvelle_transaction = Transaction(
            titre=titre,
            montant=montant,
            idCategorie=categorie_id
        )
        db.session.add(nouvelle_transaction)
        db.session.commit()

        # Redirection après ajout
        return redirect(url_for("mes_depenses"))

    # --- 2) Affichage (GET) ---
    transactions = (
        Transaction.query
        .order_by(Transaction.dateTransaction.desc())
        .all()
    )
    categories = Categorie.query.order_by(Categorie.nom).all()

    return render_template(
        "mes_depenses.html",
        transactions=transactions,
        categories=categories
    )'''

@app.route("/mes-depenses")
def mes_depenses():
    now = datetime.utcnow()
    start_of_month = datetime(now.year, now.month, 1)

    # Total dépenses (montants négatifs) du mois
    total_depenses_raw = db.session.query(
        func.coalesce(func.sum(Transaction.montant), 0)
    ).filter(
        Transaction.montant < 0,
        Transaction.dateTransaction >= start_of_month
    ).scalar()

    # Total revenus (montants positifs) du mois
    total_revenus_raw = db.session.query(
        func.coalesce(func.sum(Transaction.montant), 0)
    ).filter(
        Transaction.montant > 0,
        Transaction.dateTransaction >= start_of_month
    ).scalar()

    total_depenses = float(-total_depenses_raw)  # on affiche un nombre positif
    total_revenus = float(total_revenus_raw)
    solde = total_revenus - total_depenses

    # Dépenses par catégorie pour le mois courant
    depenses_par_categorie = (
        db.session.query(
            Categorie.nom,
            func.coalesce(func.sum(Transaction.montant), 0)
        )
        .join(Transaction)
        .filter(
            Transaction.montant < 0,
            Transaction.dateTransaction >= start_of_month
        )
        .group_by(Categorie.idCategorie)
        .all()
    )

    # On transforme en dict { "Logement": 1045.0, ... } avec valeurs positives
    depenses_par_categorie_dict = {
        nom: float(-montant) for nom, montant in depenses_par_categorie
    }

    # Objectifs (très simple : on regarde si les dépenses de la catégorie dépassent l'objectif mensuel)
    objectifs = Objectif.query.all()
    nb_objectifs = len(objectifs)
    objectifs_respectes = 0

    for obj in objectifs:
        depense_cat_raw = db.session.query(
            func.coalesce(func.sum(Transaction.montant), 0)
        ).filter(
            Transaction.idCategorie == obj.idCategorie,
            Transaction.montant < 0,
            Transaction.dateTransaction >= start_of_month
        ).scalar()

        depense_cat = float(-depense_cat_raw)
        if depense_cat <= float(obj.montant):
            objectifs_respectes += 1

    ratio_objectifs = int(
        round(100 * objectifs_respectes / nb_objectifs)
    ) if nb_objectifs > 0 else 0

    return render_template(
        "budget-dashboard.html",
        total_depenses=total_depenses,
        total_revenus=total_revenus,
        solde=solde,
        objectifs_respectes=objectifs_respectes,
        nb_objectifs=nb_objectifs,
        ratio_objectifs=ratio_objectifs,
        depenses_par_categorie_dict=depenses_par_categorie_dict,
    )




# --- LANCEMENT DE L'APP ---

if __name__ == "__main__":
    with app.app_context():
        # crée les tables si elles n'existent pas
        db.create_all()
    app.run(debug=True)