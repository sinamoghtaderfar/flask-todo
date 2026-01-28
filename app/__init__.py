import os
import datetime
import logging

from flask import Flask, redirect, url_for
from dotenv import load_dotenv
from flask_login import current_user
from flask_migrate import Migrate
from logging.handlers import RotatingFileHandler

from .extensions import db, bcrypt, login_manager, mail
from .models import User
from app.errors import register_error_handlers

def create_app():
    load_dotenv()

    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    app.config["ADMIN_EMAIL"] = os.getenv("ADMIN_EMAIL", "moghtaderfar@gmail.com")
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
    app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
    app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS") == "True"
    app.config["MAIL_USE_SSL"] = os.getenv("MAIL_USE_SSL") == "True"
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER")
    app.config["DEBUG"] = False


    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    Migrate(app, db)

    if not app.debug:

        if not os.path.exists("logs"):
            os.mkdir("logs")

        file_handler = RotatingFileHandler(
            "logs/app.log", maxBytes=10240, backupCount=10
        )
        file_handler.setLevel(logging.ERROR)

        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        file_handler.setFormatter(formatter)

        app.logger.addHandler(file_handler)

    login_manager.login_view = "auth.login"
    app.permanent_session_lifetime = datetime.timedelta(minutes=3)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .blueprints.auth import auth_bp
    from .blueprints.dashboard import dashboard_bp
    from .blueprints.profile import profile_bp
    from .blueprints.action import action_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(action_bp)

    @app.route("/")
    def index():

        if current_user.is_authenticated:
            return redirect(url_for("dashboard.dashboard"))

        return redirect(url_for("auth.login"))

    register_error_handlers(app)

    @app.route("/trigger-error")
    def trigger_error():
        try:
            1 / 0
        except Exception as e:
            app.logger.error("Test error: %s", e, exc_info=True)
        return "Triggered error!"

    return app
