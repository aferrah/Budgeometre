from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///budget.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Categorie(db.Model):
    __tablename__ = "CATEGORIE"
    idCategorie = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    couleur = db.Column(db.String(7), default="#8b5cf6")
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
    frequence = db.Column(db.String(20))
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


@app.route("/")
def home():
    transactions = (
        Transaction.query.order_by(Transaction.dateTransaction.desc()).limit(10).all()
    )

    # Total des revenus (montants positifs)
    total_revenus = db.session.query(
        db.func.coalesce(db.func.sum(Transaction.montant), 0)
    ).filter(Transaction.montant > 0).scalar()

    # Total des dépenses (montants négatifs, on prend la valeur absolue)
    total_depenses_raw = db.session.query(
        db.func.coalesce(db.func.sum(Transaction.montant), 0)
    ).filter(Transaction.montant < 0).scalar()

    total_revenus = float(total_revenus)
    total_depenses = float(-total_depenses_raw)  # Valeur positive pour l'affichage
    argentActuel = total_revenus - total_depenses

    return render_template(
        "index.html",
        transactions=transactions,
        argentActuel=argentActuel,
        total_revenus=total_revenus,
        total_depenses=total_depenses,
    )


@app.route("/add-expense", methods=["GET", "POST"])
def add_expense():
    if request.method == "GET":
        # fournir la liste des catégories pour le select
        categories = Categorie.query.order_by(Categorie.nom).all()
        return render_template("add-expense.html", categories=categories)

    # POST : créer une transaction depuis le formulaire
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

    # Si aucune catégorie sélectionnée ou trouvée, créer/attribuer une catégorie 'Autre'
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

    return redirect(url_for("home"))


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


@app.route("/transactions")
def list_transactions():
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


@app.route("/dashboard")
def budget_dashboard():
    from datetime import timedelta
    from collections import defaultdict

    now = datetime.utcnow()

    # Fonction helper pour calculer les stats d'une période
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

    # Stats par mois
    start_month = datetime(now.year, now.month, 1)
    dep_mois, rev_mois = get_stats(start_month)

    # Stats par trimestre
    trimestre = (now.month - 1) // 3
    start_quarter = datetime(now.year, trimestre * 3 + 1, 1)
    dep_trim, rev_trim = get_stats(start_quarter)

    # Stats par année
    start_year = datetime(now.year, 1, 1)
    dep_annee, rev_annee = get_stats(start_year)

    # Dépenses par catégorie (pour chaque période)
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

    # Mapping nom -> id et couleur
    all_categories = Categorie.query.all()
    categories_ids = {cat.nom: cat.idCategorie for cat in all_categories}
    categories_colors = {cat.nom: cat.couleur or '#8b5cf6' for cat in all_categories}

    # Objectifs (basé sur le mois)
    objectifs = Objectif.query.all()
    nb_objectifs = len(objectifs)
    objectifs_respectes = 0
    for obj in objectifs:
        dep_cat = db.session.query(func.coalesce(func.sum(Transaction.montant), 0)).filter(
            Transaction.idCategorie == obj.idCategorie,
            Transaction.montant < 0,
            Transaction.dateTransaction >= start_month
        ).scalar()
        if float(-dep_cat) <= float(obj.montant):
            objectifs_respectes += 1
    ratio_objectifs = int(round(100 * objectifs_respectes / nb_objectifs)) if nb_objectifs > 0 else 0

    # Évolution 6 mois
    evol_mois_labels, evol_mois_dep, evol_mois_rev = [], [], []
    for i in range(5, -1, -1):
        d = now - timedelta(days=i * 30)
        m_start = datetime(d.year, d.month, 1)
        m_end = datetime(d.year + (1 if d.month == 12 else 0), (d.month % 12) + 1, 1)
        dep, rev = get_stats(m_start, m_end)
        evol_mois_labels.append(d.strftime('%b'))
        evol_mois_dep.append(dep)
        evol_mois_rev.append(rev)

    # Évolution 4 trimestres
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

    # Évolution 3 années
    evol_annee_labels, evol_annee_dep, evol_annee_rev = [], [], []
    for i in range(2, -1, -1):
        a = now.year - i
        dep, rev = get_stats(datetime(a, 1, 1), datetime(a + 1, 1, 1))
        evol_annee_labels.append(str(a))
        evol_annee_dep.append(dep)
        evol_annee_rev.append(rev)

    return render_template(
        "budget-dashboard.html",
        # Stats mois
        dep_mois=dep_mois, rev_mois=rev_mois, solde_mois=rev_mois - dep_mois, cat_mois=cat_mois,
        # Stats trimestre
        dep_trim=dep_trim, rev_trim=rev_trim, solde_trim=rev_trim - dep_trim, cat_trim=cat_trim,
        # Stats année
        dep_annee=dep_annee, rev_annee=rev_annee, solde_annee=rev_annee - dep_annee, cat_annee=cat_annee,
        # Objectifs
        objectifs_respectes=objectifs_respectes, nb_objectifs=nb_objectifs, ratio_objectifs=ratio_objectifs,
        # Évolution
        evol_mois_labels=evol_mois_labels, evol_mois_dep=evol_mois_dep, evol_mois_rev=evol_mois_rev,
        evol_trim_labels=evol_trim_labels, evol_trim_dep=evol_trim_dep, evol_trim_rev=evol_trim_rev,
        evol_annee_labels=evol_annee_labels, evol_annee_dep=evol_annee_dep, evol_annee_rev=evol_annee_rev,
        # Catégories IDs et couleurs
        categories_ids=categories_ids,
        categories_colors=categories_colors,
    )


@app.route("/categories", methods=["GET", "POST"])
def categories():
    if request.method == "POST":
        nom = request.form.get("nom")
        description = request.form.get("description", "")
        couleur = request.form.get("couleur", "#8b5cf6")

        if nom:
            # Vérifier si la catégorie existe déjà
            existante = Categorie.query.filter_by(nom=nom).first()
            if not existante:
                nouvelle_cat = Categorie(nom=nom, description=description, couleur=couleur)
                db.session.add(nouvelle_cat)
                db.session.commit()

        return redirect(url_for("categories"))

    # GET : afficher toutes les catégories
    toutes_categories = Categorie.query.order_by(Categorie.nom).all()
    return render_template("categories.html", categories=toutes_categories)


@app.route("/categories/delete/<int:id>", methods=["POST"])
def delete_category(id):
    categorie = Categorie.query.get_or_404(id)

    # Vérifier si des transactions utilisent cette catégorie
    if categorie.transactions:
        # Option : ne pas supprimer si utilisée
        return redirect(url_for("categories"))

    db.session.delete(categorie)
    db.session.commit()
    return redirect(url_for("categories"))


@app.route("/depenses-categorie/<int:id>")
def depenses_categorie(id):
    from datetime import timedelta
    from collections import defaultdict

    categorie = Categorie.query.get_or_404(id)

    # Récupérer toutes les transactions de cette catégorie (dépenses uniquement)
    transactions = Transaction.query.filter(
        Transaction.idCategorie == id,
        Transaction.montant < 0
    ).order_by(Transaction.dateTransaction.desc()).all()

    now = datetime.utcnow()

    # Calculer les dépenses par mois
    depenses_par_mois = defaultdict(float)
    for t in transactions:
        mois_key = t.dateTransaction.strftime('%Y-%m')
        depenses_par_mois[mois_key] += float(-t.montant)

    # Générer les 12 derniers mois
    mois_labels = []
    mois_data = []
    for i in range(11, -1, -1):
        date = now - timedelta(days=i * 30)
        mois_key = date.strftime('%Y-%m')
        mois_label = date.strftime('%b %Y')
        mois_labels.append(mois_label)
        mois_data.append(depenses_par_mois.get(mois_key, 0))

    # Calculer les dépenses par trimestre
    depenses_par_trimestre = defaultdict(float)
    for t in transactions:
        annee = t.dateTransaction.year
        trimestre = (t.dateTransaction.month - 1) // 3 + 1
        trim_key = f"{annee}-T{trimestre}"
        depenses_par_trimestre[trim_key] += float(-t.montant)

    # Générer les 4 derniers trimestres
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

    # Calculer les dépenses par année
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

    # Total dépenses
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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)