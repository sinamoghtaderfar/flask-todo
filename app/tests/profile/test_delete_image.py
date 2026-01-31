import pytest
from unittest.mock import Mock

from app.blueprints.profile import delete_profile_image


@pytest.mark.parametrize("has_custom_image", [True, False])
def test_delete_profile_image(app, mocker, has_custom_image):

    mock_user = Mock()
    mock_user.profile_image = "custom-123.png" if has_custom_image else "default.png"
    mocker.patch("app.blueprints.profile.current_user", mock_user)

    mock_commit = mocker.patch("app.blueprints.profile.db.session.commit")

    mock_exists = mocker.patch("os.path.exists")
    mock_remove = mocker.patch("os.remove")

    mock_exists.return_value = has_custom_image

    with app.test_request_context("/delete-image", method="POST"):
        response = delete_profile_image()

    assert response.status_code == 200
    assert response.is_json is True
    assert response.get_json() == {"success": True}

    if has_custom_image:
        mock_remove.assert_called_once()
        mock_commit.assert_called_once()
        assert mock_user.profile_image == "default.png"
    else:
        mock_remove.assert_not_called()
        mock_commit.assert_not_called()
        assert mock_user.profile_image == "default.png"