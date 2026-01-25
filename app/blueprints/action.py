from flask import Flask, render_template, request, redirect, url_for, abort, Blueprint
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Task

#app = Flask(__name__)
action_bp = Blueprint("action", __name__, url_prefix="/action")
# ================== EDIT TASK ==================
@action_bp.route("/task/<task_uuid>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_uuid):
    task = Task.query.filter_by(uuid=task_uuid, owner=current_user).first_or_404()

    if request.method == "POST":
        task.title = request.form.get("title")
        task.description = request.form.get("description")
        db.session.commit()
        return redirect(url_for("dashboard.dashboard"))

    return render_template("dashboard/edit_task.html", task=task)

# ================== DELETE TASK ==================
@action_bp.route("/task/<int:task_id>/delete")
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        abort(403)

    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("dashboard.dashboard"))

# ================== COMPLETE TASK ==================
@action_bp.route("/task/<int:task_id>/complete")
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        abort(403)

    task.completed = True
    db.session.commit()
    return redirect(url_for("dashboard.dashboard"))
