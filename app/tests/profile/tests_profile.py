import pytest
from unittest.mock import Mock, patch

from flask import Response

from app.blueprints.profile import profile as profile_route
@pytest.mark.parametrize("has_file", [True, False])
def test_profile_route_post(app, client, mocker, has_file):
    mock_user = mocker.Mock()
    mock_user.profile_image = "old.png"
    mocker.patch("app.blueprints.profile.current_user", new=mock_user)

    mocker.patch("app.blueprints.profile.db.session.commit")

    if has_file:
        mock_file_storage = mocker.Mock()
        mock_file_storage.filename = "avatar.png"
        mock_file_storage.save = mocker.Mock()
        type(mock_file_storage).filename = mocker.PropertyMock(return_value="avatar.png")
    else:
        mock_file_storage = None

    mock_form = mocker.Mock()
    mock_form.validate_on_submit.return_value = True
    mock_form.profile_image.data = mock_file_storage
    # mock_form.profile_image = mocker.Mock(data=mock_file_storage)

    mocker.patch("app.blueprints.profile.UpdateProfileForm", return_value=mock_form)
    mocker.patch("app.blueprints.profile.OTPForm", return_value=mocker.Mock())

    mocker.patch("app.blueprints.profile.os.path.exists", return_value=True)
    mocker.patch("app.blueprints.profile.os.path.isfile", return_value=True)
    mocker.patch("app.blueprints.profile.os.remove")
    mocker.patch("app.blueprints.profile.os.makedirs")
    mocker.patch("app.blueprints.profile.uuid.uuid4", return_value="1234")

    mocker.patch("werkzeug.utils.secure_filename", return_value="safe_avatar.png")

    with app.test_request_context("/profile", method="POST"):
        response = profile_route()

    assert isinstance(response, Response)
    assert response.status_code == 302