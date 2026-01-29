import uuid
import logging
from flask import render_template, request
from flask_login import current_user
from flask_mail import Message
from app.extensions import mail

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    def send_error_email(error_id, error, user):
        try:
            admin_email = app.config.get("ADMIN_EMAIL")
            if not admin_email:
                return
            admin_email = app.config.get("ADMIN_EMAIL")
            if not admin_email:
                return
            msg = Message(
                subject=f"Server Error: {error_id}",
                recipients=[admin_email],
                body=f"ErrorID: {error_id}\n"
                     f"Path: {request.path}\n"
                     f"User: {user}\n"
                     f"Error: {error}",
            )
            mail.send(msg)

        except Exception as e:
            logger.exception("Failed to send error email: %s", e)

    @app.errorhandler(404)
    def not_found_error(error):
        error_id = uuid.uuid4().hex[:8]
        user = getattr(current_user, "id", "Anonymous")
        logger.warning("[404] ErrorID=%s | Path=%s | User=%s", error_id, request.path, user)
        return render_template("errors/404.html", error_id=error_id), 404

    @app.errorhandler(500)
    def internal_error(error):
        error_id = uuid.uuid4().hex[:8]
        user = getattr(current_user, "id", "Anonymous")
        logger.exception("[500] ErrorID=%s | Path=%s | User=%s", error_id, request.path, user)
        send_error_email(error_id, error, user)
        return render_template("errors/500.html", error_id=error_id), 500

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403
