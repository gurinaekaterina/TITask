from io import BytesIO

from fastapi import status

from app.core.security import get_current_user as app_get_current_user


def auth_override(user):
    def _dep():
        return user

    return _dep


def upload_dummy_file(client, user, app):
    app.dependency_overrides[app_get_current_user] = auth_override(user)
    content = BytesIO(b"Abyrvalg inside")
    resp = client.post(
        "/files/upload", files={"file": ("a.txt", content, "text/plain")}
    )
    assert resp.status_code == status.HTTP_201_CREATED
    return resp.json()["id"]


def test_create_and_get_comments(client, create_user):
    from app.main import app

    user = create_user("c1@example.com", "pass")
    file_id = upload_dummy_file(client, user, app)

    app.dependency_overrides[app_get_current_user] = auth_override(user)
    r = client.post(f"/comments/file/{file_id}", json={"text": "first!"})
    assert r.status_code == status.HTTP_201_CREATED
    data = r.json()
    assert data["text"] == "first!"
    assert data["file_id"] == file_id
    assert data["author"]["email"] == user.email

    r = client.get(f"/comments/file/{file_id}")
    assert r.status_code == status.HTTP_200_OK
    lst = r.json()
    assert len(lst) == 1
    assert lst[0]["text"] == "first!"


def test_update_comment_permissions(client, create_user):
    from app.main import app

    owner = create_user("owner@example.com", "pass")
    other = create_user("other@example.com", "pass")
    file_id = upload_dummy_file(client, owner, app)

    app.dependency_overrides[app_get_current_user] = auth_override(owner)
    r = client.post(f"/comments/file/{file_id}", json={"text": "edit me"})
    assert r.status_code == status.HTTP_201_CREATED
    comment_id = r.json()["id"]

    app.dependency_overrides[app_get_current_user] = auth_override(other)
    r = client.patch(f"/comments/{comment_id}", json={"text": "hacked"})
    assert r.status_code == status.HTTP_403_FORBIDDEN

    app.dependency_overrides[app_get_current_user] = auth_override(owner)
    r = client.patch(f"/comments/{comment_id}", json={"text": "updated"})
    assert r.status_code == status.HTTP_200_OK
    assert r.json()["text"] == "updated"
