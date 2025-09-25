from flask import Flask
from flask_cors import CORS
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    # Register blueprints here
    # from api.routes import api_bp
    # app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/')
    def index():
        return {'message': 'PAM-TALK API Server', 'status': 'running'}

    @app.route('/health')
    def health():
        return {'status': 'healthy'}

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )