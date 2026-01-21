from datetime import datetime
from shared.extensions import db


class ArchiveMensuelle(db.Model):
    __tablename__ = "ARCHIVE_MENSUELLE"
    idArchive = db.Column(db.Integer, primary_key=True)
    annee = db.Column(db.Integer, nullable=False)
    mois = db.Column(db.Integer, nullable=False)
    dateArchivage = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    masquee = db.Column(db.Boolean, default=False)

    total_revenus = db.Column(db.Numeric(15, 2), default=0)
    total_depenses = db.Column(db.Numeric(15, 2), default=0)
    total_epargne = db.Column(db.Numeric(15, 2), default=0)
    solde_final = db.Column(db.Numeric(15, 2), default=0)
    donnees_json = db.Column(db.Text)

    __table_args__ = (
        db.UniqueConstraint('annee', 'mois', name='unique_mois_annee'),
        db.Index("idx_archive_date", "annee", "mois"),
    )

    def __repr__(self):
        return f"<ArchiveMensuelle {self.mois}/{self.annee}>"

    def to_dict(self):
        return {
            'idArchive': self.idArchive,
            'annee': self.annee,
            'mois': self.mois,
            'dateArchivage': self.dateArchivage.isoformat() if self.dateArchivage else None,
            'masquee': self.masquee,
            'total_revenus': float(self.total_revenus) if self.total_revenus else 0,
            'total_depenses': float(self.total_depenses) if self.total_depenses else 0,
            'total_epargne': float(self.total_epargne) if self.total_epargne else 0,
            'solde_final': float(self.solde_final) if self.solde_final else 0
        }