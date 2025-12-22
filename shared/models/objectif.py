from shared.extensions import db


class Objectif(db.Model):
    __tablename__ = "OBJECTIF"
    idObjectif = db.Column(db.Integer, primary_key=True)
    montant = db.Column(db.Numeric(15, 2), nullable=False)
    epargne_actuelle = db.Column(db.Numeric(15, 2), default=0)
    description = db.Column(db.String(255))
    frequence = db.Column(db.String(20))
    dateDebut = db.Column(db.DateTime)
    dateFin = db.Column(db.DateTime)
    idCategorie = db.Column(db.Integer, db.ForeignKey("CATEGORIE.idCategorie"), nullable=False)

    categorie = db.relationship("Categorie", back_populates="objectifs")

    def __repr__(self):
        return f"<Objectif {self.description} {self.montant}>"
