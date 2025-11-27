from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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
        return f"<Transaction {self.titre} {self.montant}>"


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
    # Affiche le fichier `templates/index.html`
    return render_template("index.html")


@app.route("/init-test")
def init_test():
    """Crée une catégorie + transaction + objectif pour tester."""
    # 1) créer une catégorie
    cat = Categorie(nom="Alimentation", description="Courses, restos, etc.")
    db.session.add(cat)
    db.session.commit()

    # 2) créer une transaction liée à cette catégorie
    tr = Transaction(
        montant=-25.50,
        titre="Courses",
        categorie=cat,
    )
    db.session.add(tr)
    db.session.commit()

    # 3) créer un objectif lié à cette catégorie
    obj = Objectif(
        montant=200,
        description="Budget courses mensuel",
        frequence="mensuel",
        categorie=cat,
    )
    db.session.add(obj)
    db.session.commit()

    return "Données de test ajoutées ✅"


@app.route("/transactions")
def list_transactions():
    """Afficher toutes les transactions en texte brut."""
    transactions = Transaction.query.order_by(Transaction.dateTransaction.desc()).all()
    lignes = []
    for t in transactions:
        lignes.append(f"{t.dateTransaction} - {t.titre} : {t.montant}€ (cat: {t.categorie.nom})")
    return "<br>".join(lignes) if lignes else "Aucune transaction pour l'instant."


# --- LANCEMENT DE L'APP ---

if __name__ == "__main__":
    with app.app_context():
        # crée les tables si elles n'existent pas
        db.create_all()
    app.run(debug=True)