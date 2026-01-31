from datetime import datetime

from app.blueprints.profile import request_otp


def test_request_otp(app, mocker, client):
    mock_user = mocker.Mock()
    mock_user.email = "test@test.com"

    mocker.patch("app.blueprints.profile.current_user", mock_user)
    mock_expiration = datetime(2026, 1, 31, 18, 0, 0)
    mocker.patch("app.blueprints.profile.send_otp", return_value=mock_expiration)

    with app.app_context():
        with app.test_request_context("/request-otp", method="POST"):
            response = request_otp()
            data = response.get_json()

    assert data["success"] is True
    assert "OTP sent" in data["message"]
