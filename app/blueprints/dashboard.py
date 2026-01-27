from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from app.extensions import db
from app.models import Task

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard", methods=["GET", "POST"])
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
    return render_template("dashboard/dashboard.html", tasks=tasks)


@dashboard_bp.route("/task/<uuid>/edit", methods=["GET", "POST"])
@login_required
def edit_task(uuid):
    task = Task.query.filter_by(uuid=uuid, owner=current_user).first_or_404()

    if request.method == "POST":
        task.title = request.form.get("title")
        task.description = request.form.get("description")
        db.session.commit()
        return redirect(url_for("dashboard"))

    return render_template("dashboard.edit_task.html", task=task)
