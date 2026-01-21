from datetime import datetime
from shared.extensions import db


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

    def to_dict(self):
        return {
            'idTransaction': self.idTransaction,
            'montant': float(self.montant),
            'dateTransaction': self.dateTransaction.isoformat() if self.dateTransaction else None,
            'titre': self.titre,
            'commentaire': self.commentaire,
            'idCategorie': self.idCategorie,
            'categorie': self.categorie.to_dict() if self.categorie else None
        }