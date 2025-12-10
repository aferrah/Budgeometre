from flask import Blueprint, render_template
from datetime import datetime, timedelta
from sqlalchemy import func
from extensions import db
from models import Categorie, Transaction

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route("/dashboard")
def budget_dashboard():
    now = datetime.utcnow()

    def get_stats(start_date, end_date=None):
        q_dep = db.session.query(func.coalesce(func.sum(Transaction.montant), 0)).filter(Transaction.montant < 0, Transaction.dateTransaction >= start_date)
        q_rev = db.session.query(func.coalesce(func.sum(Transaction.montant), 0)).filter(Transaction.montant > 0, Transaction.dateTransaction >= start_date)
        if end_date:
            q_dep = q_dep.filter(Transaction.dateTransaction < end_date)
            q_rev = q_rev.filter(Transaction.dateTransaction < end_date)
        return float(-q_dep.scalar()), float(q_rev.scalar())

    def get_depenses_par_cat(start_date):
        result = db.session.query(Categorie.nom, func.coalesce(func.sum(Transaction.montant), 0)).join(Transaction).filter(
            Transaction.montant < 0, Transaction.dateTransaction >= start_date).group_by(Categorie.idCategorie).all()
        return {nom: float(-m) for nom, m in result}

    start_month = datetime(now.year, now.month, 1)
    start_quarter = datetime(now.year, ((now.month - 1) // 3) * 3 + 1, 1)
    start_year = datetime(now.year, 1, 1)

    dep_mois, rev_mois = get_stats(start_month)
    dep_trim, rev_trim = get_stats(start_quarter)
    dep_annee, rev_annee = get_stats(start_year)

    all_categories = Categorie.query.all()
    categories_ids = {c.nom: c.idCategorie for c in all_categories}
    categories_colors = {c.nom: c.couleur or '#8b5cf6' for c in all_categories}

    nb_budgets, budgets_respectes = 0, 0
    budget_alerts = []
    for cat in all_categories:
        if cat.limite_budget and cat.limite_budget > 0:
            nb_budgets += 1
            dep_cat = float(-db.session.query(func.coalesce(func.sum(Transaction.montant), 0)).filter(
                Transaction.idCategorie == cat.idCategorie, Transaction.montant < 0, Transaction.dateTransaction >= start_month).scalar())
            if dep_cat <= float(cat.limite_budget):
                budgets_respectes += 1
            pct = (dep_cat / float(cat.limite_budget)) * 100
            if pct >= 100:
                budget_alerts.append({'type': 'danger', 'category': cat.nom, 'message': f'Budget dépassé ! ({pct:.0f}%)'})
            elif pct >= 80:
                budget_alerts.append({'type': 'warning', 'category': cat.nom, 'message': f'{pct:.0f}% utilisé'})

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
        t, a = (now.month - 1) // 3 + 1 - i, now.year
        while t <= 0: t += 4; a -= 1
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

    return render_template("budget-dashboard.html",
        dep_mois=dep_mois, rev_mois=rev_mois, solde_mois=rev_mois - dep_mois, cat_mois=get_depenses_par_cat(start_month),
        dep_trim=dep_trim, rev_trim=rev_trim, solde_trim=rev_trim - dep_trim, cat_trim=get_depenses_par_cat(start_quarter),
        dep_annee=dep_annee, rev_annee=rev_annee, solde_annee=rev_annee - dep_annee, cat_annee=get_depenses_par_cat(start_year),
        objectifs_respectes=budgets_respectes, nb_objectifs=nb_budgets,
        ratio_objectifs=int(round(100 * budgets_respectes / nb_budgets)) if nb_budgets else 0,
        evol_mois_labels=evol_mois_labels, evol_mois_dep=evol_mois_dep, evol_mois_rev=evol_mois_rev,
        evol_trim_labels=evol_trim_labels, evol_trim_dep=evol_trim_dep, evol_trim_rev=evol_trim_rev,
        evol_annee_labels=evol_annee_labels, evol_annee_dep=evol_annee_dep, evol_annee_rev=evol_annee_rev,
        categories_ids=categories_ids, categories_colors=categories_colors, budget_alerts=budget_alerts)
