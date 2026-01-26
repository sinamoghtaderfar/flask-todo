from datetime import datetime, timedelta
import os
import uuid


from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user, logout_user
from werkzeug.utils import secure_filename

from app.extensions import db, mail
from app.forms import UpdateProfileForm, OTPForm
from flask_mail import Message
from flask_bcrypt import generate_password_hash
import random

from flask import current_app



profile_bp = Blueprint("profile", __name__, url_prefix="/profile")

def send_otp(user):
    code = str(random.randint(100000, 999999))
    user.otp_code = code

    user.otp_expiration = datetime.utcnow() + timedelta(minutes=1)
    db.session.commit()

    msg = Message("OTP Code", recipients=[user.email])
    msg.body = f"Your OTP code is: {code}"
    mail.send(msg)

    return user.otp_expiration

@profile_bp.route("/request-otp", methods=["POST"])
@login_required
def request_otp():
    esexpiration = send_otp(current_user)
    return jsonify({
        "success": True,
        "message": "OTP sent! Check your email.",
        "expires_at": esexpiration.isoformat() + "Z"
    })

@profile_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = UpdateProfileForm(obj=current_user)
    otp_form = OTPForm()
    if form.validate_on_submit():

        upload_folder = os.path.join(current_app.root_path, "static/profile_img")
        os.makedirs(upload_folder, exist_ok=True)

        if form.profile_image.data:
            file = form.profile_image.data

            upload_folder = os.path.join(current_app.root_path, "static/profile_img")
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
        return redirect(url_for("profile.profile"))

    return render_template("profile/profile.html", form=form, otp_form=otp_form)


@profile_bp.route("/delete-image", methods=["POST"])
@login_required
def delete_profile_image():
    print("Delete image called!")
    upload_folder = os.path.join(current_app.root_path, "static/profile_img")

    if current_user.profile_image != "default.png":
        old_path = os.path.join(upload_folder, current_user.profile_image)
        if os.path.exists(old_path):
            os.remove(old_path)
        current_user.profile_image = "default.png"
        db.session.commit()

    return jsonify({"success": True})


@profile_bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    otp_code = request.form.get("otp_code")
    new_password = request.form.get("new_password")

    if current_user.otp_code != otp_code:
        return jsonify({"success": False, "message": "Invalid OTP!"})

    if datetime.utcnow() > current_user.otp_expiration:
        return jsonify({"success": False, "message": "OTP expired!"})

    current_user.password = generate_password_hash(new_password)
    current_user.otp_code = None
    current_user.otp_expiration = None
    db.session.commit()

    logout_user()

    return jsonify(
        {"success": True, "message": "Password updated successfully!", "redirect": url_for('auth.login')})


