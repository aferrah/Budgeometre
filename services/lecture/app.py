import sys
sys.path.insert(0, '/app')

from flask import Flask
from shared.config import Config
from shared.extensions import db
from routes import lecture_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    app.register_blueprint(lecture_bp, url_prefix='/api')

    return app


app = create_app()

@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002, debug=True)