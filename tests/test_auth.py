import uuid


def test_register(client):
    email = f"{uuid.uuid4()}@example.com"
    response = client.post("/auth/register", json={
        "name": "Auth Test User",
        "email": email,
        "password": "password123",
        "role": "customer"
    })
    assert response.status_code == 201
    assert response.json()["email"] == email
    assert "password" not in response.json()

def test_register_duplicate_email(client):
    email = f"{uuid.uuid4()}@example.com"
    payload = {
        "name": "Auth Test User",
        "email": email,
        "password": "password123",
        "role": "customer"
    }
    res1 = client.post("/auth/register", json=payload)
    assert res1.status_code == 201
    
    res2 = client.post("/auth/register", json=payload)
    assert res2.status_code == 400
    assert res2.json()["detail"] == "Email already registered"

def test_login_and_me(client):
    email = f"{uuid.uuid4()}@example.com"
    client.post("/auth/register", json={
        "name": "Auth Test User",
        "email": email,
        "password": "password123",
        "role": "customer"
    })
    
    login_res = client.post("/auth/login", data={
        "username": email,
        "password": "password123"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    
    me_res = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email
