import pytest


def auth_headers(client, username="taskuser", password="password123"):
    response = client.post(
        "/auth/register",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200

    response = client.post(
        "/auth/login",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def create_task(client, headers, title="Write tests", description="Cover CRUD"):
    response = client.post(
        "/tasks/",
        headers=headers,
        json={"title": title, "description": description},
    )
    assert response.status_code == 200
    return response.json()


def test_create_task_returns_created_task(client):
    headers = auth_headers(client)

    response = client.post(
        "/tasks/",
        headers=headers,
        json={"title": "Plan sprint", "description": "Pick the next tasks"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"]
    assert data["title"] == "Plan sprint"
    assert data["description"] == "Pick the next tasks"
    assert data["is_completed"] is False


def test_get_tasks_returns_only_current_user_tasks(client):
    first_user_headers = auth_headers(client, username="firstuser")
    second_user_headers = auth_headers(client, username="seconduser")
    first_task = create_task(client, first_user_headers, title="First user's task")
    create_task(client, second_user_headers, title="Second user's task")

    response = client.get("/tasks/", headers=first_user_headers)

    assert response.status_code == 200
    assert response.json() == [first_task]


def test_get_task_returns_task_by_id_for_owner(client):
    headers = auth_headers(client)
    task = create_task(client, headers, title="Read me")

    response = client.get(f"/tasks/{task['id']}", headers=headers)

    assert response.status_code == 200
    assert response.json() == task


def test_update_task_partially_updates_existing_task(client):
    headers = auth_headers(client)
    task = create_task(client, headers, title="Draft", description="Before")

    response = client.patch(
        f"/tasks/{task['id']}",
        headers=headers,
        json={"title": "Done", "is_completed": True},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task["id"]
    assert data["title"] == "Done"
    assert data["description"] == "Before"
    assert data["is_completed"] is True


def test_delete_task_removes_task(client):
    headers = auth_headers(client)
    task = create_task(client, headers)

    response = client.delete(f"/tasks/{task['id']}", headers=headers)

    assert response.status_code == 200
    assert response.json() == {"message": "Task deleted"}

    response = client.get(f"/tasks/{task['id']}", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_other_user_cannot_read_update_or_delete_task(client):
    owner_headers = auth_headers(client, username="owneruser")
    other_headers = auth_headers(client, username="otheruser")
    task = create_task(client, owner_headers)

    response = client.get(f"/tasks/{task['id']}", headers=other_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

    response = client.patch(
        f"/tasks/{task['id']}",
        headers=other_headers,
        json={"title": "Take over"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

    response = client.delete(f"/tasks/{task['id']}", headers=other_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


@pytest.mark.parametrize("method,path", [
    ("post", "/tasks/"),
    ("get", "/tasks/"),
    ("get", "/tasks/1"),
    ("patch", "/tasks/1"),
    ("delete", "/tasks/1"),
])
def test_task_routes_require_authentication(client, method, path):
    request = getattr(client, method)
    kwargs = {}
    if method in {"post", "patch"}:
        kwargs["json"] = {"title": "No token"}

    response = request(path, **kwargs)

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
