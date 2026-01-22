from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    abort,
    session,
    jsonify,
)
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_bcrypt import Bcrypt, generate_password_hash
from flask_mail import Mail
from flask_migrate import Migrate
from dotenv import load_dotenv
import datetime
from werkzeug.utils import secure_filename
import os
import uuid

from models import db, User, Task
from forms import RegisterForm, LoginForm, UpdateProfileForm, OTPForm


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

app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER")
app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT"))
app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS") == "True"
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_DEFAULT_SENDER")

mail = Mail(app)


import random
#from datetime import datetime
from flask_mail import Message
from app import mail, db

def otp(user):
    # ساخت OTP 6 رقمی
    otp_code = str(random.randint(100000, 999999))
    user.otp_code = otp_code

    db.session.commit()

    msg = Message("Your OTP Code", recipients=[user.email])
    msg.body = f"Your OTP code is: {otp_code}."
    mail.send(msg)

# --------------------
db.init_app(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

app.permanent_session_lifetime = datetime.timedelta(minutes=3)
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
            username=form.username.data, email=form.email.data, password=hashed_pw
        )
        db.session.add(user)
        db.session.commit()
        flash("Account created. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

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
    task = Task.query.filter_by(uuid=uuid, owner=current_user).first_or_404()

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


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = UpdateProfileForm(obj=current_user)
    otp_form = OTPForm()
    if form.validate_on_submit():

        upload_folder = os.path.join(app.root_path, "static/profile_img")
        os.makedirs(upload_folder, exist_ok=True)

        if form.profile_image.data:
            file = form.profile_image.data

            upload_folder = os.path.join(app.root_path, "static/profile_img")
            os.makedirs(upload_folder, exist_ok=True)

            old_image = current_user.profile_image

            if old_image and old_image != "default.png":
                old_path = os.path.join(upload_folder, old_image)

                if os.path.exists(old_path) and os.path.isfile(old_path):
                    os.remove(old_path)

            ext = os.path.splitext(secure_filename(file.filename))[1]
            filename = f"{uuid.uuid4()}{ext}"

            file.save(os.path.join(upload_folder, filename))
            current_user.profile_image = filename
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", form=form, otp_form=otp_form)


@app.route("/profile/delete-image", methods=["POST"])
@login_required
def delete_profile_image():
    upload_folder = os.path.join(app.root_path, "static/profile_img")

    if current_user.profile_image != "default.png":
        old_path = os.path.join(upload_folder, current_user.profile_image)

        if os.path.exists(old_path):
            os.remove(old_path)

        current_user.profile_image = "default.png"
        db.session.commit()

    return jsonify({"success": True})

@app.route("/profile/change-password", methods=["POST"])
@login_required
def change_password():
    form = OTPForm()

    # اگر request از AJAX است
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if form.validate_on_submit():
        otp = form.otp_code.data
        new_pass = form.new_password.data
        confirm_pass = form.confirm_password.data

        if otp != current_user.otp_code:
            msg = "Invalid OTP code"
            if is_ajax:
                return jsonify(success=False, message=msg)
            flash(msg, "danger")
            return redirect(url_for("profile"))

        if new_pass != confirm_pass:
            msg = "Passwords do not match"
            if is_ajax:
                return jsonify(success=False, message=msg)
            flash(msg, "danger")
            return redirect(url_for("profile"))

        # تغییر پسورد
        hashed_password = generate_password_hash(new_pass)
        current_user.password = hashed_password
        current_user.otp_code = None
        current_user.otp_expiration = None
        db.session.commit()

        msg = "Password updated successfully!"
        if is_ajax:
            return jsonify(success=True, message=msg)

        flash(msg, "success")
        return redirect(url_for("profile"))

    # اگر فرم اعتبارسنجی نشد
    msg = "Invalid input"
    if is_ajax:
        return jsonify(success=False, message=msg)

    flash(msg, "danger")
    return redirect(url_for("profile"))


@app.route("/profile/request-otp", methods=["POST"])
@login_required
def request_new_otp():
    otp(current_user)
    flash("OTP sent to your email!", "info")
    return redirect(url_for("change_password"))


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
