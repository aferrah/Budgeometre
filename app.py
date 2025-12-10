from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from datetime import timedelta
from sqlalchemy import func

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///budget.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "budgeometre_secret_2025"

db = SQLAlchemy(app)


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
    epargne_actuelle = db.Column(db.Numeric(15, 2), default=0)
    description = db.Column(db.String(255))
    frequence = db.Column(db.String(20))
    dateDebut = db.Column(db.DateTime)
    dateFin = db.Column(db.DateTime)
    idCategorie = db.Column(db.Integer, db.ForeignKey("CATEGORIE.idCategorie"), nullable=False)

    categorie = db.relationship("Categorie", back_populates="objectifs")

    def __repr__(self):
        return f"<Objectif {self.description} {self.montant}>"


class ArchiveMensuelle(db.Model):
    __tablename__ = "ARCHIVE_MENSUELLE"
    idArchive = db.Column(db.Integer, primary_key=True)
    annee = db.Column(db.Integer, nullable=False)
    mois = db.Column(db.Integer, nullable=False)
    dateArchivage = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    masquee = db.Column(db.Boolean, default=False)
    
    # Statistiques du mois
    total_revenus = db.Column(db.Numeric(15, 2), default=0)
    total_depenses = db.Column(db.Numeric(15, 2), default=0)
    total_epargne = db.Column(db.Numeric(15, 2), default=0)
    solde_final = db.Column(db.Numeric(15, 2), default=0)
    
    # Données JSON pour les transactions et stats détaillées
    donnees_json = db.Column(db.Text)
    
    __table_args__ = (
        db.UniqueConstraint('annee', 'mois', name='unique_mois_annee'),
        db.Index("idx_archive_date", "annee", "mois"),
    )

    def __repr__(self):
        return f"<ArchiveMensuelle {self.mois}/{self.annee}>"


@app.route("/")
def home():
    now = datetime.utcnow()

    # 1) Périodes temporelles
    # Transactions affichées : 3 derniers mois
    date_limite = now - timedelta(days=90)

    # Statistiques affichées dans la grosse carte : mois en cours
    start_of_month = datetime(now.year, now.month, 1)

    # 2) Transactions récentes (3 derniers mois)
    transactions = Transaction.query.filter(
        Transaction.dateTransaction >= date_limite
    ).order_by(
        Transaction.dateTransaction.desc()
    ).all()

    # 3) Statistiques du MOIS COURANT

    # Revenus du mois (montants positifs)
    total_revenus = db.session.query(
        db.func.coalesce(db.func.sum(Transaction.montant), 0)
    ).filter(
        Transaction.montant > 0,
        Transaction.dateTransaction >= start_of_month
    ).scalar()

    # Dépenses du mois (montants négatifs)
    total_depenses_raw = db.session.query(
        db.func.coalesce(db.func.sum(Transaction.montant), 0)
    ).filter(
        Transaction.montant < 0,
        Transaction.dateTransaction >= start_of_month
    ).scalar()

    # Total épargne : on garde la logique actuelle (somme de epargne_actuelle)
    total_epargne = db.session.query(
        db.func.coalesce(db.func.sum(Objectif.epargne_actuelle), 0)
    ).scalar()

    total_epargne = float(total_epargne)
    total_revenus = float(total_revenus)
    total_depenses = float(-total_depenses_raw)  # on remet en positif pour l'affichage
    argentActuel = total_revenus - total_depenses

    # 4) Nombre de transactions plus anciennes que 3 mois
    nb_anciennes = Transaction.query.filter(
        Transaction.dateTransaction < date_limite
    ).count()

    # 5) Envoi au template
    return render_template(
        "index.html",
        transactions=transactions,
        argentActuel=argentActuel,
        total_revenus=total_revenus,
        total_depenses=total_depenses,
        total_epargne=total_epargne,
        nb_anciennes=nb_anciennes
    )



@app.route("/add-expense", methods=["GET", "POST"])
def add_expense():
    if request.method == "GET":
        categories = Categorie.query.order_by(Categorie.nom).all()
        return render_template("add-expense.html", categories=categories)

    titre = request.form.get("label") or "Dépense"
    montant_raw = request.form.get("amount") or "0"
    type_transaction = request.form.get("type", "depense")

    try:
        montant = float(montant_raw)
    except ValueError:
        montant = 0.0
    if type_transaction == "depense":
        montant = -abs(montant)
    else:
        montant = abs(montant)

    commentaire = request.form.get("comment")
    date_str = request.form.get("date")
    if date_str:
        try:
            date_tx = datetime.fromisoformat(date_str)
        except Exception:
            date_tx = datetime.utcnow()
    else:
        date_tx = datetime.utcnow()

    cat_id = request.form.get("category")
    categorie = None
    if cat_id:
        try:
            categorie = Categorie.query.get(int(cat_id))
        except Exception:
            categorie = None

    if not categorie:
        categorie = Categorie.query.filter_by(nom="Autre").first()
        if not categorie:
            categorie = Categorie(nom="Autre", description="Catégorie par défaut", couleur="#64748b")
            db.session.add(categorie)
            db.session.commit()

    tr = Transaction(
        montant=montant,
        titre=titre,
        commentaire=commentaire,
        dateTransaction=date_tx,
        categorie=categorie,
    )
    db.session.add(tr)
    db.session.commit()
    
    flash("Transaction ajoutée avec succès", "success")

    return redirect(url_for("home"))


@app.route("/transaction/<int:id>/modifier", methods=["GET", "POST"])
def modifier_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    
    # Bloquer la modification des transactions d'épargne
    if transaction.categorie and transaction.categorie.nom == "Épargne":
        flash("Les transactions d'épargne ne peuvent pas être modifiées. Modifiez l'objectif depuis la page Objectifs.", "error")
        return redirect(url_for("home"))
    
    if request.method == "GET":
        categories = Categorie.query.order_by(Categorie.nom).all()
        return render_template("modifier-transaction.html", transaction=transaction, categories=categories)
    
    # POST - Mettre à jour la transaction
    titre = request.form.get("label") or "Dépense"
    montant_raw = request.form.get("amount") or "0"
    type_transaction = request.form.get("type", "depense")
    
    try:
        montant = float(montant_raw)
    except ValueError:
        montant = 0.0
    
    if type_transaction == "depense":
        montant = -abs(montant)
    else:
        montant = abs(montant)
    
    commentaire = request.form.get("comment")
    date_str = request.form.get("date")
    if date_str:
        try:
            date_tx = datetime.fromisoformat(date_str)
        except Exception:
            date_tx = transaction.dateTransaction
    else:
        date_tx = transaction.dateTransaction
    
    cat_id = request.form.get("category")
    if cat_id:
        try:
            categorie = Categorie.query.get(int(cat_id))
            if categorie:
                transaction.idCategorie = categorie.idCategorie
        except Exception:
            pass
    
    transaction.titre = titre
    transaction.montant = montant
    transaction.commentaire = commentaire
    transaction.dateTransaction = date_tx
    
    db.session.commit()
    flash("Transaction modifiée avec succès", "success")
    
    return redirect(url_for("home"))


@app.route("/transaction/<int:id>/supprimer", methods=["POST"])
def supprimer_transaction(id):
    transaction = Transaction.query.get_or_404(id)
    
    # Bloquer la suppression des transactions d'épargne
    if transaction.categorie and transaction.categorie.nom == "Épargne":
        flash("Les transactions d'épargne ne peuvent pas être supprimées. Gérez l'épargne depuis la page Objectifs.", "error")
        return redirect(url_for("home"))
    
    db.session.delete(transaction)
    db.session.commit()
    flash("Transaction supprimée avec succès", "success")
    return redirect(url_for("home"))


@app.route("/reinitialiser-bdd")
def reinitialiser_bdd():
    """Supprime toutes les données de la base de données"""
    try:
        # Supprimer toutes les archives
        ArchiveMensuelle.query.delete()
        
        # Supprimer toutes les transactions
        Transaction.query.delete()
        
        # Supprimer tous les objectifs
        Objectif.query.delete()
        
        # Supprimer toutes les catégories
        Categorie.query.delete()
        
        db.session.commit()
        
        flash("✅ Base de données réinitialisée avec succès. Toutes les données ont été supprimées.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Erreur lors de la réinitialisation : {str(e)}", "error")
    
    return redirect(url_for("home"))


@app.route("/reset-and-init")
def reset_and_init():
    """Réinitialise complètement la DB et génère des données de test"""
    try:
        # Supprimer toutes les données
        db.drop_all()
        # Recréer les tables
        db.create_all()
        # Rediriger vers la génération de données
        return redirect(url_for('init_test_archives'))
    except Exception as e:
        return f"❌ Erreur : {str(e)}"


@app.route("/init-test")
def init_test():
    cat_alimentation = Categorie(nom="Alimentation", description="Courses, restos, etc.")
    cat_transport = Categorie(nom="Transport", description="Essence, transports publics")
    cat_loisirs = Categorie(nom="Loisirs", description="Cinéma, activités")

    db.session.add_all([cat_alimentation, cat_transport, cat_loisirs])
    db.session.commit()

    transactions_data = [
        Transaction(titre="Courses supermarché", montant=-45.30, categorie=cat_alimentation,
                    commentaire="Courses hebdo"),
        Transaction(titre="Restaurant", montant=-28.50, categorie=cat_alimentation, commentaire="Déjeuner en famille"),
        Transaction(titre="Essence", montant=-60.00, categorie=cat_transport, commentaire="Plein d'essence"),
        Transaction(titre="Ticket bus", montant=-15.00, categorie=cat_transport, commentaire="Abonnement mensuel"),
        Transaction(titre="Cinéma", montant=-12.00, categorie=cat_loisirs, commentaire="Film avec amis"),
        Transaction(titre="Courses Leclerc", montant=-38.75, categorie=cat_alimentation,
                    commentaire="Courses principales"),
        Transaction(titre="Café", montant=-5.50, categorie=cat_alimentation, commentaire="Pause café au travail"),
    ]

    for tr in transactions_data:
        db.session.add(tr)
    db.session.commit()

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


@app.route("/init-test-archives")
def init_test_archives():
    """Crée des transactions sur plusieurs mois passés pour tester les archives"""
    from datetime import timedelta
    
    # Créer des catégories avec des couleurs variées
    categories_config = [
        {"nom": "Alimentation", "description": "Courses, restaurants", "couleur": "#ef4444", "limite": 400},
        {"nom": "Transport", "description": "Déplacements", "couleur": "#3b82f6", "limite": 150},
        {"nom": "Loisirs", "description": "Divertissements", "couleur": "#a855f7", "limite": 200},
        {"nom": "Logement", "description": "Loyer, charges", "couleur": "#f59e0b", "limite": 800},
        {"nom": "Santé", "description": "Médecin, pharmacie", "couleur": "#14b8a6", "limite": 100},
        {"nom": "Shopping", "description": "Vêtements, accessoires", "couleur": "#ec4899", "limite": 150},
        {"nom": "Salaire", "description": "Revenus mensuels", "couleur": "#10b981", "limite": None},
    ]
    
    categories = {}
    for config in categories_config:
        cat = Categorie.query.filter_by(nom=config["nom"]).first()
        if not cat:
            cat = Categorie(
                nom=config["nom"],
                description=config["description"],
                couleur=config["couleur"],
                limite_budget=config["limite"]
            )
            db.session.add(cat)
        else:
            # Mettre à jour la couleur et la limite si elles n'existent pas
            if not cat.couleur:
                cat.couleur = config["couleur"]
            if config["limite"] and not cat.limite_budget:
                cat.limite_budget = config["limite"]
        categories[config["nom"]] = cat
    
    db.session.commit()
    
    now = datetime.utcnow()
    nb_transactions = 0
    import random
    
    # Données pour générer des transactions variées
    transactions_types = {
        "Alimentation": [
            ("Supermarché", 35, 80),
            ("Boulangerie", 3, 10),
            ("Restaurant", 20, 60),
            ("Marché", 15, 40),
            ("Fast-food", 8, 20),
            ("Épicerie", 10, 30),
        ],
        "Transport": [
            ("Essence", 40, 70),
            ("Parking", 5, 15),
            ("Péage", 10, 25),
            ("Train", 15, 50),
            ("Taxi/Uber", 10, 35),
            ("Entretien voiture", 50, 150),
        ],
        "Loisirs": [
            ("Cinéma", 10, 25),
            ("Concert", 30, 80),
            ("Livre", 8, 25),
            ("Sortie bar", 15, 40),
            ("Netflix/Spotify", 10, 20),
            ("Sport", 20, 50),
        ],
        "Logement": [
            ("Loyer", 600, 900),
            ("Électricité", 40, 80),
            ("Eau", 20, 40),
            ("Internet", 30, 50),
            ("Assurance habitation", 15, 30),
        ],
        "Santé": [
            ("Pharmacie", 10, 40),
            ("Médecin", 25, 60),
            ("Dentiste", 50, 150),
            ("Optique", 80, 200),
        ],
        "Shopping": [
            ("Vêtements", 30, 100),
            ("Chaussures", 40, 120),
            ("Accessoires", 15, 60),
            ("Cosmétiques", 20, 50),
        ],
    }
    
    # Créer des transactions pour les 6 derniers mois
    for i in range(6):
        # Calculer le mois (mois actuel - i)
        mois_date = datetime(now.year, now.month, 1) - timedelta(days=i * 30)
        annee = mois_date.year
        mois = mois_date.month
        
        # Salaire en début de mois
        jour_salaire = random.randint(1, 5)
        salaire = Transaction(
            titre="Salaire mensuel",
            montant=random.uniform(2200, 2800),
            dateTransaction=datetime(annee, mois, jour_salaire, 9, 0),
            categorie=categories["Salaire"],
            commentaire="Virement employeur"
        )
        db.session.add(salaire)
        nb_transactions += 1
        
        # Transactions fixes mensuelles (loyer, charges)
        for titre_fixe, montant_min, montant_max in transactions_types["Logement"]:
            jour = random.randint(1, 10)
            trans = Transaction(
                titre=titre_fixe,
                montant=-random.uniform(montant_min, montant_max),
                dateTransaction=datetime(annee, mois, jour, random.randint(8, 20), random.randint(0, 59)),
                categorie=categories["Logement"]
            )
            db.session.add(trans)
            nb_transactions += 1
        
        # Transactions variables (15-25 par mois)
        nb_trans_variables = random.randint(15, 25)
        for _ in range(nb_trans_variables):
            # Choisir une catégorie aléatoire (pas Logement ni Salaire)
            cat_nom = random.choice(["Alimentation", "Transport", "Loisirs", "Santé", "Shopping"])
            titre, montant_min, montant_max = random.choice(transactions_types[cat_nom])
            
            jour = random.randint(1, 28)
            trans = Transaction(
                titre=titre,
                montant=-random.uniform(montant_min, montant_max),
                dateTransaction=datetime(annee, mois, jour, random.randint(8, 20), random.randint(0, 59)),
                categorie=categories[cat_nom]
            )
            db.session.add(trans)
            nb_transactions += 1
    
    db.session.commit()
    
    return f"✅ {nb_transactions} transactions créées sur 6 mois avec 7 catégories colorées et limites budgétaires !"


@app.route("/transactions")
def list_transactions():
    transactions = Transaction.query.order_by(Transaction.dateTransaction.desc()).all()
    lignes = []
    for t in transactions:
        lignes.append(f"{t.dateTransaction} - {t.titre} : {t.montant}€ (cat: {t.categorie.nom})")
    return "<br>".join(lignes) if lignes else "Aucune transaction pour l'instant."


@app.route("/dashboard")
def budget_dashboard():
    from datetime import timedelta
    from collections import defaultdict

    now = datetime.utcnow()

    def get_stats(start_date, end_date=None):
        query_dep = db.session.query(func.coalesce(func.sum(Transaction.montant), 0)).filter(
            Transaction.montant < 0,
            Transaction.dateTransaction >= start_date
        )
        query_rev = db.session.query(func.coalesce(func.sum(Transaction.montant), 0)).filter(
            Transaction.montant > 0,
            Transaction.dateTransaction >= start_date
        )
        if end_date:
            query_dep = query_dep.filter(Transaction.dateTransaction < end_date)
            query_rev = query_rev.filter(Transaction.dateTransaction < end_date)

        return float(-query_dep.scalar()), float(query_rev.scalar())

    start_month = datetime(now.year, now.month, 1)
    dep_mois, rev_mois = get_stats(start_month)

    trimestre = (now.month - 1) // 3
    start_quarter = datetime(now.year, trimestre * 3 + 1, 1)
    dep_trim, rev_trim = get_stats(start_quarter)

    start_year = datetime(now.year, 1, 1)
    dep_annee, rev_annee = get_stats(start_year)

    def get_depenses_par_cat(start_date):
        result = (
            db.session.query(Categorie.nom, func.coalesce(func.sum(Transaction.montant), 0))
            .join(Transaction)
            .filter(Transaction.montant < 0, Transaction.dateTransaction >= start_date)
            .group_by(Categorie.idCategorie)
            .all()
        )
        return {nom: float(-montant) for nom, montant in result}

    cat_mois = get_depenses_par_cat(start_month)
    cat_trim = get_depenses_par_cat(start_quarter)
    cat_annee = get_depenses_par_cat(start_year)

    all_categories = Categorie.query.all()
    categories_ids = {cat.nom: cat.idCategorie for cat in all_categories}
    categories_colors = {cat.nom: cat.couleur or '#8b5cf6' for cat in all_categories}

    # Calculer le nombre de budgets respectés (catégories avec limite)
    nb_budgets = 0
    budgets_respectes = 0
    for cat in all_categories:
        if cat.limite_budget and cat.limite_budget > 0:
            nb_budgets += 1
            dep_cat = db.session.query(func.coalesce(func.sum(Transaction.montant), 0)).filter(
                Transaction.idCategorie == cat.idCategorie,
                Transaction.montant < 0,
                Transaction.dateTransaction >= start_month
            ).scalar()
            if float(-dep_cat) <= float(cat.limite_budget):
                budgets_respectes += 1
    ratio_objectifs = int(round(100 * budgets_respectes / nb_budgets)) if nb_budgets > 0 else 0

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

    # Calculer les alertes budgétaires pour le mois en cours
    budget_alerts = []
    for cat in all_categories:
        if cat.limite_budget and cat.limite_budget > 0:
            depenses_cat_mois = db.session.query(
                func.coalesce(func.sum(Transaction.montant), 0)
            ).filter(
                Transaction.idCategorie == cat.idCategorie,
                Transaction.montant < 0,
                Transaction.dateTransaction >= start_month
            ).scalar()
            depenses_cat = float(-depenses_cat_mois)
            pourcentage = (depenses_cat / float(cat.limite_budget)) * 100
            
            if pourcentage >= 100:
                depassement = depenses_cat - float(cat.limite_budget)
                if depassement == 0:
                    message = 'Budget atteint !'
                else:
                    message = f'Budget dépassé de {depassement:.2f}€ ! ({pourcentage:.0f}%)'
                budget_alerts.append({
                    'type': 'danger',
                    'category': cat.nom,
                    'message': message
                })
            elif pourcentage >= 80:
                budget_alerts.append({
                    'type': 'warning',
                    'category': cat.nom,
                    'message': f'Vous avez utilisé {pourcentage:.0f}% de votre budget ({depenses_cat:.2f}€ / {float(cat.limite_budget):.2f}€)'
                })

    return render_template(
        "budget-dashboard.html",
        dep_mois=dep_mois, rev_mois=rev_mois, solde_mois=rev_mois - dep_mois, cat_mois=cat_mois,
        dep_trim=dep_trim, rev_trim=rev_trim, solde_trim=rev_trim - dep_trim, cat_trim=cat_trim,
        dep_annee=dep_annee, rev_annee=rev_annee, solde_annee=rev_annee - dep_annee, cat_annee=cat_annee,
        objectifs_respectes=budgets_respectes, nb_objectifs=nb_budgets, ratio_objectifs=ratio_objectifs,
        evol_mois_labels=evol_mois_labels, evol_mois_dep=evol_mois_dep, evol_mois_rev=evol_mois_rev,
        evol_trim_labels=evol_trim_labels, evol_trim_dep=evol_trim_dep, evol_trim_rev=evol_trim_rev,
        evol_annee_labels=evol_annee_labels, evol_annee_dep=evol_annee_dep, evol_annee_rev=evol_annee_rev,
        categories_ids=categories_ids,
        categories_colors=categories_colors,
        budget_alerts=budget_alerts,
    )


@app.route("/mes-objectifs", methods=["GET", "POST"])
def mes_objectifs():
    if request.method == "POST":
        montant_str = request.form.get("montant")
        categorie_str = request.form.get("categorie")

        if not montant_str or not categorie_str:
            return redirect(url_for("mes_objectifs"))

        try:
            montant = float(montant_str)
            categorie_id = int(categorie_str)
        except ValueError:
            return redirect(url_for("mes_objectifs"))

        description = request.form.get("description")
        frequence = request.form.get("frequence")

        new_obj = Objectif(
            montant=montant,
            epargne_actuelle=0,
            description=description,
            frequence=frequence,
            idCategorie=categorie_id,
            dateDebut=datetime.utcnow(),
        )

        db.session.add(new_obj)
        db.session.commit()
        
        flash("Objectif ajouté avec succès", "success")

        return redirect(url_for("mes_objectifs"))

    objectifs = Objectif.query.all()
    categories = Categorie.query.all()

    objectifs_status = []
    for obj in objectifs:
        epargne = float(obj.epargne_actuelle) if obj.epargne_actuelle else 0
        montant_cible = float(obj.montant)

        status = "Atteint" if epargne >= montant_cible else "En cours"
        pourcentage = (epargne / montant_cible * 100) if montant_cible > 0 else 0

        objectifs_status.append((obj, epargne, montant_cible, pourcentage, status))

    return render_template(
        "mes-objectifs.html",
        objectifs_status=objectifs_status,
        categories=categories
    )


@app.route("/objectif/<int:id>/ajouter", methods=["POST"])
def ajouter_epargne(id):
    objectif = Objectif.query.get_or_404(id)
    montant_str = request.form.get("montant")

    if not montant_str:
        return redirect(url_for("mes_objectifs", _anchor=f"objectif-{id}"))

    try:
        montant = float(montant_str)
    except ValueError:
        return redirect(url_for("mes_objectifs", _anchor=f"objectif-{id}"))

    # Calculer le solde actuel
    total_revenus = db.session.query(
        db.func.coalesce(db.func.sum(Transaction.montant), 0)
    ).filter(Transaction.montant > 0).scalar()

    total_depenses = db.session.query(
        db.func.coalesce(db.func.sum(Transaction.montant), 0)
    ).filter(Transaction.montant < 0).scalar()

    solde_actuel = float(total_revenus) + float(total_depenses)

    if montant > solde_actuel:
        flash(f"Solde insuffisant ! Vous avez {solde_actuel:.2f}€ disponible.", "error")
        return redirect(url_for("mes_objectifs", _anchor=f"objectif-{id}"))

    # Créer ou récupérer la catégorie "Épargne"
    cat_epargne = Categorie.query.filter_by(nom="Épargne").first()
    if not cat_epargne:
        cat_epargne = Categorie(nom="Épargne", description="Transferts vers épargne", couleur="#f59e0b")
        db.session.add(cat_epargne)
        db.session.commit()

    # Créer une transaction négative (retrait du solde)
    transaction = Transaction(
        montant=-montant,
        titre=f"Épargne: {objectif.description or 'Objectif'}",
        commentaire=f"Transfert vers objectif d'épargne",
        dateTransaction=datetime.utcnow(),
        idCategorie=cat_epargne.idCategorie
    )
    db.session.add(transaction)

    # Ajouter à l'épargne de l'objectif
    if objectif.epargne_actuelle is None:
        objectif.epargne_actuelle = 0
    objectif.epargne_actuelle = float(objectif.epargne_actuelle) + montant

    db.session.commit()

    flash(f"{montant:.2f}€ transféré vers votre épargne !", "success")
    return redirect(url_for("mes_objectifs", _anchor=f"objectif-{id}"))


@app.route("/objectif/<int:id>/retirer", methods=["POST"])
def retirer_epargne(id):
    objectif = Objectif.query.get_or_404(id)
    montant_str = request.form.get("montant")

    if not montant_str:
        return redirect(url_for("mes_objectifs", _anchor=f"objectif-{id}"))

    try:
        montant = float(montant_str)
    except ValueError:
        return redirect(url_for("mes_objectifs", _anchor=f"objectif-{id}"))

    epargne_actuelle = float(objectif.epargne_actuelle) if objectif.epargne_actuelle else 0

    if montant > epargne_actuelle:
        flash(f"Épargne insuffisante ! Vous avez {epargne_actuelle:.2f}€ dans cet objectif.", "error")
        return redirect(url_for("mes_objectifs", _anchor=f"objectif-{id}"))

    # Créer ou récupérer la catégorie "Épargne"
    cat_epargne = Categorie.query.filter_by(nom="Épargne").first()
    if not cat_epargne:
        cat_epargne = Categorie(nom="Épargne", description="Transferts vers épargne", couleur="#f59e0b")
        db.session.add(cat_epargne)
        db.session.commit()

    # Créer une transaction positive (retour vers solde)
    transaction = Transaction(
        montant=montant,
        titre=f"Retrait épargne: {objectif.description or 'Objectif'}",
        commentaire=f"Retrait depuis objectif d'épargne",
        dateTransaction=datetime.utcnow(),
        idCategorie=cat_epargne.idCategorie
    )
    db.session.add(transaction)

    # Retirer de l'épargne
    objectif.epargne_actuelle = epargne_actuelle - montant

    db.session.commit()

    flash(f"{montant:.2f}€ retransféré vers votre solde !", "success")
    return redirect(url_for("mes_objectifs", _anchor=f"objectif-{id}"))


@app.route("/objectif/<int:id>/recuperer", methods=["POST"])
def recuperer_epargne(id):
    objectif = Objectif.query.get_or_404(id)

    epargne_actuelle = float(objectif.epargne_actuelle) if objectif.epargne_actuelle else 0

    if epargne_actuelle <= 0:
        flash("Aucune épargne à récupérer.", "error")
        return redirect(url_for("mes_objectifs", _anchor=f"objectif-{id}"))

    # Créer ou récupérer la catégorie "Épargne"
    cat_epargne = Categorie.query.filter_by(nom="Épargne").first()
    if not cat_epargne:
        cat_epargne = Categorie(nom="Épargne", description="Transferts vers épargne", couleur="#f59e0b")
        db.session.add(cat_epargne)
        db.session.commit()

    # Créer une transaction positive (retour vers solde)
    transaction = Transaction(
        montant=epargne_actuelle,
        titre=f"Récupération épargne: {objectif.description or 'Objectif'}",
        commentaire=f"Objectif atteint - récupération totale",
        dateTransaction=datetime.utcnow(),
        idCategorie=cat_epargne.idCategorie
    )
    db.session.add(transaction)

    # Remettre l'épargne à zéro
    objectif.epargne_actuelle = 0

    db.session.commit()

    flash(f"{epargne_actuelle:.2f}€ récupéré sur votre solde principal !", "success")
    return redirect(url_for("mes_objectifs"))


@app.route("/objectif/<int:id>/supprimer", methods=["POST"])
def supprimer_objectif(id):
    objectif = Objectif.query.get_or_404(id)

    # Si l'objectif a de l'épargne, la remettre sur le solde
    epargne_actuelle = float(objectif.epargne_actuelle) if objectif.epargne_actuelle else 0

    if epargne_actuelle > 0:
        cat_epargne = Categorie.query.filter_by(nom="Épargne").first()
        if not cat_epargne:
            cat_epargne = Categorie(nom="Épargne", description="Transferts vers épargne", couleur="#f59e0b")
            db.session.add(cat_epargne)
            db.session.commit()

        transaction = Transaction(
            montant=epargne_actuelle,
            titre=f"Suppression objectif: {objectif.description or 'Objectif'}",
            commentaire=f"Récupération épargne suite à suppression",
            dateTransaction=datetime.utcnow(),
            idCategorie=cat_epargne.idCategorie
        )
        db.session.add(transaction)
        flash(f"Objectif supprimé. {epargne_actuelle:.2f}€ retransféré vers votre solde.", "success")
    else:
        flash("Objectif supprimé.", "success")

    db.session.delete(objectif)
    db.session.commit()
    return redirect(url_for("mes_objectifs"))


@app.route("/categories", methods=["GET", "POST"])
def categories():
    if request.method == "POST":
        nom = request.form.get("nom")
        description = request.form.get("description", "")
        couleur = request.form.get("couleur", "#8b5cf6")
        limite_budget_raw = request.form.get("limite_budget", "0")

        try:
            limite_budget = float(limite_budget_raw) if limite_budget_raw else 0
        except ValueError:
            limite_budget = 0

        # Calculer le revenu total pour la validation
        total_revenus = db.session.query(
            db.func.coalesce(db.func.sum(Transaction.montant), 0)
        ).filter(Transaction.montant > 0).scalar()
        total_revenus = float(total_revenus)

        # Vérifier si la limite dépasse le revenu
        if limite_budget > total_revenus and limite_budget > 0:
            flash(f"⚠️ Attention : La limite de {limite_budget:.2f}€ dépasse votre revenu total de {total_revenus:.2f}€", "warning")

        if nom:
            existante = Categorie.query.filter_by(nom=nom).first()
            if not existante:
                nouvelle_cat = Categorie(nom=nom, description=description, couleur=couleur, limite_budget=limite_budget)
                db.session.add(nouvelle_cat)
                db.session.commit()
                flash("Catégorie ajoutée avec succès", "success")

        return redirect(url_for("categories"))

    # Calculer les dépenses par catégorie pour le mois en cours
    from datetime import datetime
    now = datetime.utcnow()
    start_month = datetime(now.year, now.month, 1)

    toutes_categories = Categorie.query.order_by(Categorie.nom).all()
    
    # Calculer les statistiques pour chaque catégorie
    for cat in toutes_categories:
        depenses_mois = db.session.query(
            db.func.coalesce(db.func.sum(Transaction.montant), 0)
        ).filter(
            Transaction.idCategorie == cat.idCategorie,
            Transaction.montant < 0,
            Transaction.dateTransaction >= start_month
        ).scalar()
        
        cat.depenses_mois = float(-depenses_mois)
        
        # Calculer le pourcentage si une limite est définie
        if cat.limite_budget and cat.limite_budget > 0:
            cat.pourcentage = (cat.depenses_mois / float(cat.limite_budget)) * 100
        else:
            cat.pourcentage = 0

    # Calculer le revenu total pour l'affichage
    total_revenus = db.session.query(
        db.func.coalesce(db.func.sum(Transaction.montant), 0)
    ).filter(Transaction.montant > 0).scalar()

    return render_template("categories.html", categories=toutes_categories, total_revenus=float(total_revenus))


@app.route("/categories/<int:id>/modifier", methods=["GET", "POST"])
def modifier_categorie(id):
    categorie = Categorie.query.get_or_404(id)
    
    if request.method == "GET":
        return render_template("modifier-categorie.html", categorie=categorie)
    
    # POST - Mettre à jour la catégorie
    nom = request.form.get("nom")
    description = request.form.get("description", "")
    couleur = request.form.get("couleur", "#8b5cf6")
    limite_budget_raw = request.form.get("limite_budget", "0")
    
    try:
        limite_budget = float(limite_budget_raw) if limite_budget_raw else 0
    except ValueError:
        limite_budget = 0
    
    if nom:
        # Vérifier si le nom n'existe pas déjà (sauf pour la catégorie actuelle)
        existante = Categorie.query.filter(Categorie.nom == nom, Categorie.idCategorie != id).first()
        if not existante:
            categorie.nom = nom
            categorie.description = description
            categorie.couleur = couleur
            categorie.limite_budget = limite_budget
            
            db.session.commit()
            flash("Catégorie modifiée avec succès", "success")
        else:
            flash("Une catégorie avec ce nom existe déjà", "error")
    
    return redirect(url_for("categories"))


@app.route("/categories/delete/<int:id>", methods=["POST"])
def delete_category(id):
    categorie = Categorie.query.get_or_404(id)

    if categorie.transactions:
        return redirect(url_for("categories"))

    db.session.delete(categorie)
    db.session.commit()
    return redirect(url_for("categories"))


@app.route("/depenses-categorie/<int:id>")
def depenses_categorie(id):
    from datetime import timedelta
    from collections import defaultdict

    categorie = Categorie.query.get_or_404(id)

    transactions = Transaction.query.filter(
        Transaction.idCategorie == id,
        Transaction.montant < 0
    ).order_by(Transaction.dateTransaction.desc()).all()

    now = datetime.utcnow()

    depenses_par_mois = defaultdict(float)
    for t in transactions:
        mois_key = t.dateTransaction.strftime('%Y-%m')
        depenses_par_mois[mois_key] += float(-t.montant)

    mois_labels = []
    mois_data = []
    for i in range(11, -1, -1):
        date = now - timedelta(days=i * 30)
        mois_key = date.strftime('%Y-%m')
        mois_label = date.strftime('%b %Y')
        mois_labels.append(mois_label)
        mois_data.append(depenses_par_mois.get(mois_key, 0))

    depenses_par_trimestre = defaultdict(float)
    for t in transactions:
        annee = t.dateTransaction.year
        trimestre = (t.dateTransaction.month - 1) // 3 + 1
        trim_key = f"{annee}-T{trimestre}"
        depenses_par_trimestre[trim_key] += float(-t.montant)

    trimestre_labels = []
    trimestre_data = []
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
        annee_key = str(t.dateTransaction.year)
        depenses_par_annee[annee_key] += float(-t.montant)

    annee_labels = []
    annee_data = []
    for i in range(2, -1, -1):
        a = now.year - i
        annee_labels.append(str(a))
        annee_data.append(depenses_par_annee.get(str(a), 0))

    total_depenses = sum(float(-t.montant) for t in transactions)

    return render_template(
        "detail-depense.html",
        categorie=categorie,
        transactions=transactions[:10],
        total_depenses=total_depenses,
        mois_labels=mois_labels,
        mois_data=mois_data,
        trimestre_labels=trimestre_labels,
        trimestre_data=trimestre_data,
        annee_labels=annee_labels,
        annee_data=annee_data,
    )


@app.route("/archiver-mois", methods=["POST"])
def archiver_mois():
    import json
    from collections import defaultdict
    
    # Récupérer le mois et l'année à archiver (par défaut le mois dernier)
    mois_str = request.form.get("mois")
    annee_str = request.form.get("annee")
    
    now = datetime.utcnow()
    if mois_str and annee_str:
        mois = int(mois_str)
        annee = int(annee_str)
    else:
        # Par défaut, archiver le mois dernier
        if now.month == 1:
            mois = 12
            annee = now.year - 1
        else:
            mois = now.month - 1
            annee = now.year
    
    # Vérifier si une archive existe déjà
    archive_existante = ArchiveMensuelle.query.filter_by(annee=annee, mois=mois).first()
    if archive_existante:
        flash(f"Une archive pour {mois}/{annee} existe déjà", "warning")
        return redirect(url_for("archives"))
    
    # Calculer les dates de début et fin du mois
    debut_mois = datetime(annee, mois, 1)
    if mois == 12:
        fin_mois = datetime(annee + 1, 1, 1)
    else:
        fin_mois = datetime(annee, mois + 1, 1)
    
    # Récupérer les transactions du mois
    transactions_mois = Transaction.query.filter(
        Transaction.dateTransaction >= debut_mois,
        Transaction.dateTransaction < fin_mois
    ).order_by(Transaction.dateTransaction.desc()).all()
    
    # Calculer les statistiques
    total_revenus = sum(float(t.montant) for t in transactions_mois if t.montant > 0)
    total_depenses = sum(float(-t.montant) for t in transactions_mois if t.montant < 0)
    
    # Statistiques par catégorie
    stats_categories = defaultdict(lambda: {'nom': '', 'couleur': '#8b5cf6', 'depenses': 0, 'revenus': 0, 'nb_transactions': 0})
    transactions_data = []
    
    for t in transactions_mois:
        cat_id = t.idCategorie
        stats_categories[cat_id]['nom'] = t.categorie.nom
        stats_categories[cat_id]['couleur'] = t.categorie.couleur or '#8b5cf6'
        stats_categories[cat_id]['nb_transactions'] += 1
        
        if t.montant < 0:
            stats_categories[cat_id]['depenses'] += float(-t.montant)
        else:
            stats_categories[cat_id]['revenus'] += float(t.montant)
        
        transactions_data.append({
            'titre': t.titre,
            'montant': float(t.montant),
            'date': t.dateTransaction.strftime('%Y-%m-%d %H:%M:%S'),
            'categorie': t.categorie.nom,
            'commentaire': t.commentaire or ''
        })
    
    # Récupérer l'épargne totale à ce moment
    total_epargne = db.session.query(
        db.func.coalesce(db.func.sum(Objectif.epargne_actuelle), 0)
    ).scalar()
    
    # Calculer le solde
    solde_final = total_revenus - total_depenses
    
    # Préparer les données JSON
    donnees = {
        'transactions': transactions_data,
        'categories': {k: v for k, v in stats_categories.items()},
        'stats': {
            'nb_transactions': len(transactions_mois),
            'nb_depenses': sum(1 for t in transactions_mois if t.montant < 0),
            'nb_revenus': sum(1 for t in transactions_mois if t.montant > 0)
        }
    }
    
    # Créer l'archive
    archive = ArchiveMensuelle(
        annee=annee,
        mois=mois,
        total_revenus=total_revenus,
        total_depenses=total_depenses,
        total_epargne=float(total_epargne),
        solde_final=solde_final,
        donnees_json=json.dumps(donnees)
    )
    
    db.session.add(archive)
    db.session.commit()
    
    flash(f"Archive créée pour {mois}/{annee} avec {len(transactions_mois)} transactions", "success")
    return redirect(url_for("archives"))


@app.route("/archives")
def archives():
    archives = ArchiveMensuelle.query.order_by(
        ArchiveMensuelle.annee.desc(),
        ArchiveMensuelle.mois.desc()
    ).all()
    
    # Liste des mois disponibles pour archivage
    now = datetime.utcnow()
    mois_disponibles = []
    
    # Obtenir tous les mois qui ont des transactions
    transactions = Transaction.query.all()
    mois_avec_transactions = set()
    for t in transactions:
        mois_avec_transactions.add((t.dateTransaction.year, t.dateTransaction.month))
    
    # Filtrer ceux qui ne sont pas déjà archivés
    archives_existantes = {(a.annee, a.mois) for a in archives}
    
    for annee, mois in sorted(mois_avec_transactions, reverse=True):
        if (annee, mois) not in archives_existantes and (annee < now.year or mois < now.month):
            mois_disponibles.append({'annee': annee, 'mois': mois})
    
    return render_template("archives.html", archives=archives, mois_disponibles=mois_disponibles)


@app.route("/archives/<int:id>")
def voir_archive(id):
    import json
    
    archive = ArchiveMensuelle.query.get_or_404(id)
    donnees = json.loads(archive.donnees_json) if archive.donnees_json else {}
    
    # Nom du mois en français
    mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
    nom_mois = mois_noms[archive.mois]
    
    return render_template("archive-detail.html", 
                         archive=archive, 
                         donnees=donnees,
                         nom_mois=nom_mois)


@app.route("/archives/<int:id>/toggle-masquer", methods=["POST"])
def toggle_masquer_archive(id):
    archive = ArchiveMensuelle.query.get_or_404(id)
    archive.masquee = not archive.masquee
    db.session.commit()
    if archive.masquee:
        flash("Archive masquée", "success")
    else:
        flash("Archive affichée", "success")
    return redirect(url_for("archives"))


@app.route("/archives/<int:id>/supprimer", methods=["POST"])
def supprimer_archive(id):
    archive = ArchiveMensuelle.query.get_or_404(id)
    mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
    nom_complet = f"{mois_noms[archive.mois]} {archive.annee}"
    
    db.session.delete(archive)
    db.session.commit()
    flash(f"Archive {nom_complet} supprimée définitivement", "success")
    return redirect(url_for("archives"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)