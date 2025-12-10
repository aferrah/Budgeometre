from extensions import db


class Categorie(db.Model):
    __tablename__ = "CATEGORIE"
    idCategorie = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    couleur = db.Column(db.String(7), default="#8b5cf6")
    limite_budget = db.Column(db.Numeric(15, 2), default=0)
    transactions = db.relationship("Transaction", back_populates="categorie")
    objectifs = db.relationship("Objectif", back_populates="categorie")

    def __repr__(self):
        return f"<Categorie {self.nom}>"
