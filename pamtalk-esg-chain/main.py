from flask import Flask
from flask_cors import CORS

from app.api.token_routes import token_routes
from app.api.wallet_routes import wallet_routes
from app.api.batch_routes import batch_routes
from app.api.carbon_routes import carbon_routes
from app.api.mall_routes import mall_routes
from app.routes.social import social_bp
from app.routes.blockchain_monitor import blockchain_monitor_bp
from app.routes.blockchain_setup import blockchain_setup_bp


def create_app():
    app = Flask(__name__)

    # CORS 설정
    CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    app.register_blueprint(token_routes, url_prefix="/api/token")
    app.register_blueprint(wallet_routes, url_prefix="/api/wallet")
    app.register_blueprint(batch_routes, url_prefix="/api/batch")
    app.register_blueprint(carbon_routes, url_prefix="/api/carbon")
    app.register_blueprint(mall_routes, url_prefix="/api/mall")
    app.register_blueprint(social_bp, url_prefix="/api/social")
    app.register_blueprint(blockchain_monitor_bp, url_prefix="/api/blockchain")
    app.register_blueprint(blockchain_setup_bp, url_prefix="/api/blockchain-setup")
    app.config['DEBUG'] = True
    app.config['PROPAGATE_EXCEPTIONS'] = True
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
