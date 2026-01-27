from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user

from app.blueprints.profile import send_otp, profile_bp
from app.extensions import db, bcrypt
from app.forms import LoginForm, RegisterForm, RequestOTPForm, OTPForm
from app.models import User

auth_bp = Blueprint("auth", __name__, template_folder="../templates")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            session.permanent = True
            return redirect(url_for("dashboard.dashboard"))
        flash("Login failed", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed)
        db.session.add(user)
        db.session.commit()
        flash("Account created", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = RequestOTPForm()
    if form.validate_on_submit():
        email_or_username = form.email_or_username.data

        user = User.query.filter(
            (User.email == email_or_username) | (User.username == email_or_username)
        ).first()

        if user:
            expires_at = send_otp(user)
            flash("OTP has been sent to your email!", "success")
            session["otp_expires_at"] = expires_at.isoformat()
            return redirect(url_for("profile.change_password_page"))
        else:
            flash("User not found!", "danger")

    return render_template("auth/forgot_password.html", form=form)


@profile_bp.route("/change-password-page", methods=["GET"])
def change_password_page():
    otp_form = OTPForm()

    # اگر OTP از قبل ساخته شده، زمان انقضا را بفرست
    otp_expiration = None
    if current_user.is_authenticated:
        otp_expiration = current_user.otp_expiration
    else:
        # در فراموشی رمز، می‌توانیم از session یا کاربر موقتی استفاده کنیم
        # مثلا از یک متغیر session برای نگهداری expires_at بعد از ارسال OTP
        otp_expiration = session.get("otp_expires_at")

    return render_template(
        "base/change_password.html", otp_form=otp_form, otp_expiration=otp_expiration
    )


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("Logged out", "info")
    return redirect(url_for("auth.login"))
