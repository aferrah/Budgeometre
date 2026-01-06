import os
from flask import Flask
from routes import home_bp, transactions_bp, categories_bp, objectifs_bp, archives_bp, dashboard_bp

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev')
app.config['LECTURE_URL'] = os.environ.get('LECTURE_SERVICE_URL', 'http://lecture-service:5002')
app.config['ECRITURE_URL'] = os.environ.get('ECRITURE_SERVICE_URL', 'http://ecriture-service:5001')

app.register_blueprint(home_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(categories_bp)
app.register_blueprint(objectifs_bp)
app.register_blueprint(archives_bp)
app.register_blueprint(dashboard_bp)

# Endpoint de health check pour Kubernetes
@app.route('/health')
def health():
    return {'status': 'healthy'}, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)