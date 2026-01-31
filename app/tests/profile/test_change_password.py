import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from flask import Flask

from app.blueprints.profile import change_password
from app.blueprints.profile import db

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "testsecret"
    return app

@pytest.fixture
def mock_user():
    user = Mock()
    user.otp_code = "123456"
    user.otp_expiration = datetime.utcnow() + timedelta(minutes=5)
    user.password = None
    return user

def test_change_password_success_logged_in(app, mock_user):
    with patch("app.blueprints.profile.current_user", mock_user):
        with patch("app.blueprints.profile.db.session.commit") as mock_commit:
            with patch("app.blueprints.profile.url_for", return_value="/mocked-url"):
                with app.test_request_context("/profile/change-password", method="POST", data={
                    "otp_code": "123456",
                    "new_password": "newstrongpassword"
                }):
                    response = change_password()
                    json_data = response.get_json()
                    assert json_data["success"] is True
                    assert json_data["redirect"] == "/mocked-url"
                    assert mock_user.otp_code is None
                    assert mock_user.otp_expiration is None
                    assert mock_user.password is not None
                    mock_commit.assert_called_once()

def test_change_password_invalid_otp_logged_in(app, mock_user):
    with patch("app.blueprints.profile.current_user", mock_user):
        with app.test_request_context("/profile/change-password", method="POST", data={
            "otp_code": "000000",  # OTP اشتباه
            "new_password": "newstrongpassword"
        }):
            response = change_password()
            json_data = response.get_json()
            assert response.status_code == 400
            assert json_data["message"] == "Invalid OTP code"

def test_change_password_expired_otp_logged_in(app, mock_user):
    mock_user.otp_expiration = datetime.utcnow() - timedelta(minutes=1)
    with patch("app.blueprints.profile.current_user", mock_user):
        with app.test_request_context("/profile/change-password", method="POST", data={
            "otp_code": "123456",
            "new_password": "newstrongpassword"
        }):
            response = change_password()
            json_data = response.get_json()
            assert response.status_code == 400
            assert json_data["message"] == "OTP has expired"

def test_change_password_success_not_logged_in(app, mocker, mock_user):
    mocker.patch("app.blueprints.profile.User.query.filter_by", return_value=Mock(first=lambda: mock_user))
    with patch.object(db.session, "commit") as mock_commit:
        with app.test_request_context("/profile/change-password", method="POST", data={
            "otp_code": "123456",
            "new_password": "newstrongpassword"
        }):
            response = change_password()
            json_data = response.get_json()
            assert json_data["success"] is True
            assert mock_user.otp_code is None
            assert mock_user.otp_expiration is None
            assert mock_user.password is not None
            mock_commit.assert_called_once()

def test_change_password_invalid_otp_not_logged_in(app, mocker):
    mocker.patch("app.blueprints.profile.User.query.filter_by", return_value=Mock(first=lambda: None))
    with app.test_request_context("/profile/change-password", method="POST", data={
        "otp_code": "000000",
        "new_password": "newstrongpassword"
    }):
        response = change_password()
        json_data = response.get_json()
        assert response.status_code == 400
        assert json_data["message"] == "Invalid OTP code"

def test_change_password_expired_otp_not_logged_in(app, mocker, mock_user):
    mock_user.otp_expiration = datetime.utcnow() - timedelta(minutes=1)
    mocker.patch("app.blueprints.profile.User.query.filter_by", return_value=Mock(first=lambda: mock_user))
    with app.test_request_context("/profile/change-password", method="POST", data={
        "otp_code": "123456",
        "new_password": "newstrongpassword"
    }):
        response = change_password()
        json_data = response.get_json()
        assert response.status_code == 400
        assert json_data["message"] == "OTP has expired"
