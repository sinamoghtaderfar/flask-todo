from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user
from app.extensions import db, bcrypt
from app.forms import LoginForm, RegisterForm
from app.models import User

auth_bp = Blueprint(
    "auth",
    __name__,
    template_folder="../templates"
)

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
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed
        )
        db.session.add(user)
        db.session.commit()
        flash("Account created", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("Logged out", "info")
    return redirect(url_for("auth.login"))
