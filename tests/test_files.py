import csv
from io import BytesIO

from fastapi import status

from app.core.security import get_current_user as app_get_current_user


def auth_override(user):
    def _dep():
        return user

    return _dep


def test_upload_txt_valid(client, create_user):
    user = create_user("u1@example.com", "pass")
    from app.main import app

    app.dependency_overrides[app_get_current_user] = auth_override(user)

    content = "hello " + " " + "Quantori" + " world"
    fileobj = BytesIO(content.encode("utf-8"))

    resp = client.post(
        "/files/upload",
        files={"file": ("note.txt", fileobj, "text/plain")},
    )
    assert resp.status_code == status.HTTP_201_CREATED, resp.text
    data = resp.json()
    assert data["valid"] is True
    assert data["file_type"] == ".txt"
    assert data["uploader"]["email"] == user.email

    resp = client.get("/files")
    assert resp.status_code == status.HTTP_200_OK
    items = resp.json()
    assert len(items) >= 1
    assert any(i["filename"] == "note.txt" for i in items)


def test_upload_csv_valid_only_in_company(client, create_user, tmp_path):
    user = create_user("u2@example.com", "pass")
    from app.main import app

    app.dependency_overrides[app_get_current_user] = auth_override(user)

    p = tmp_path / "test.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["User", "Company Name", "Age"])
        writer.writeheader()
        writer.writerow({"User": "john", "Company Name": "Quantori LLC", "Age": "30"})
        writer.writerow({"User": "kate", "Company Name": "Other", "Age": "31"})

    with p.open("rb") as f:
        resp = client.post("/files/upload", files={"file": (p.name, f, "text/csv")})
    assert resp.status_code == status.HTTP_201_CREATED, resp.text
    data = resp.json()
    assert data["valid"] is True
    assert data["file_type"] == ".csv"


def test_upload_csv_invalid_outside_company(client, create_user, tmp_path):
    user = create_user("u3@example.com", "pass")
    from app.main import app

    app.dependency_overrides[app_get_current_user] = auth_override(user)

    p = tmp_path / "bad.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["User", "Company Name", "Age"])
        writer.writeheader()
        writer.writerow({"User": "Quantori", "Company Name": "Acme", "Age": "30"})

    with p.open("rb") as f:
        resp = client.post("/files/upload", files={"file": (p.name, f, "text/csv")})
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert data["valid"] is False
