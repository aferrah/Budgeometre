from routes.home import home_bp
from routes.transactions import transactions_bp
from routes.categories import categories_bp
from routes.objectifs import objectifs_bp
from routes.dashboard import dashboard_bp
from routes.archives import archives_bp
from routes.admin import admin_bp


def register_blueprints(app):
    app.register_blueprint(home_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(objectifs_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(archives_bp)
    app.register_blueprint(admin_bp)
