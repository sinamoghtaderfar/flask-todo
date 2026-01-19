from flask import Flask, render_template, redirect, url_for, flash, request, abort, session
from flask_login import LoginManager, login_user, logout_user,login_required, current_user
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from dotenv import load_dotenv
from datetime import timedelta
import os

from models import db, User, Task
from forms import RegisterForm, LoginForm, AddTaskForm


# --------config------------
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql://{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# --------------------
db.init_app(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

app.permanent_session_lifetime = timedelta(minutes=3)
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# ---------Routes-----------
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        if title:
            task = Task(title=title, description=description, owner=current_user)
            db.session.add(task)
            db.session.commit()
    tasks = Task.query.filter_by(owner=current_user).all()
    return render_template("dashboard.html", tasks=tasks)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email already registered. Please login.", "danger")
            return redirect(url_for("login"))
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_pw
        )
        db.session.add(user)
        db.session.commit()
        flash("Account created. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))  # اگر قبلاً login شده

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            session.permanent = True
            return redirect(url_for("dashboard"))
        else:
            flash("Login failed. Check username and password.", "danger")

    return render_template("login.html", form=form)

@app.route("/delete/<int:task_id>")
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        abort(403)

    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/task/<uuid>/edit", methods=["GET", "POST"])
@login_required
def edit_task(uuid):
    task = Task.query.filter_by(
        uuid=uuid,
        owner=current_user
    ).first_or_404()

    if request.method == "POST":
        task.title = request.form.get("title")
        task.description = request.form.get("description")
        db.session.commit()
        return redirect(url_for("dashboard"))

    return render_template("edit_task.html", task=task)


@app.route("/complete/<int:task_id>")
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        abort(403)
    task.completed = True
    db.session.commit()

    return redirect(url_for("dashboard"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


if __name__ == "__main__":
    app.run(debug=True)
