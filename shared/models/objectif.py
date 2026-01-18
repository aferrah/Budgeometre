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

    def to_dict(self):
        return {
            'idObjectif': self.idObjectif,
            'montant': float(self.montant) if self.montant else 0,
            'epargne_actuelle': float(self.epargne_actuelle) if self.epargne_actuelle else 0,
            'description': self.description,
            'frequence': self.frequence,
            'dateDebut': self.dateDebut.isoformat() if self.dateDebut else None,
            'dateFin': self.dateFin.isoformat() if self.dateFin else None,
            'idCategorie': self.idCategorie,
            'categorie': self.categorie.to_dict() if self.categorie else None
        }