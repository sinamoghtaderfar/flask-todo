import pytest
from unittest.mock import Mock
from app import create_app
from app.blueprints.profile import send_otp


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app


def test_send_otp(app, mocker):
    user = Mock()
    user.email = "test@test.com"

    # mock random.randint
    mocker.patch("app.blueprints.profile.random.randint", return_value=1)

    # mock mail.send
    mock_mail = mocker.patch("app.blueprints.profile.mail.send")

    # application context
    with app.app_context():
        expiration = send_otp(user)

    assert user.otp_code == "1"
    assert expiration is not None
    mock_mail.assert_called_once()
