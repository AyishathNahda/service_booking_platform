import pytest
import uuid

def create_user(client, role: str):
    unique_email = f"{uuid.uuid4()}@example.com"
    response = client.post("/auth/register", json={
        "name": f"Test {role}",
        "email": unique_email,
        "password": "password123",
        "role": role
    })
    return response.json()

def login(client, email: str):
    response = client.post("/auth/login", data={
        "username": email,
        "password": "password123"
    })
    return response.json()["access_token"]

def test_rbac_rules(client):
    # 1. Create Users
    admin = create_user(client, "admin")
    prov_a = create_user(client, "provider")
    prov_b = create_user(client, "provider")
    cust_a = create_user(client, "customer")
    cust_b = create_user(client, "customer")

    # 2. Login to get tokens
    admin_token = login(client, admin["email"])
    prov_a_token = login(client, prov_a["email"])
    prov_b_token = login(client, prov_b["email"])
    cust_a_token = login(client, cust_a["email"])
    cust_b_token = login(client, cust_b["email"])

    def auth_header(token):
        return {"Authorization": f"Bearer {token}"}

    # 3. Create Bookings
    # Customer A books Provider A
    b1_res = client.post("/bookings", json={
        "provider_id": prov_a["id"],
        "start_time": "2026-10-01T10:00:00Z",
        "end_time": "2026-10-01T11:00:00Z"
    }, headers=auth_header(cust_a_token))
    b1_id = b1_res.json()["id"]

    # Customer B books Provider B
    b2_res = client.post("/bookings", json={
        "provider_id": prov_b["id"],
        "start_time": "2026-10-02T10:00:00Z",
        "end_time": "2026-10-02T11:00:00Z"
    }, headers=auth_header(cust_b_token))
    b2_id = b2_res.json()["id"]

    # 4. Test RBAC: Admin sees all bookings
    res_admin = client.get("/bookings", headers=auth_header(admin_token))
    assert len(res_admin.json()) == 2

    # 5. Test RBAC: Provider A sees only own bookings
    res_prov_a = client.get("/bookings", headers=auth_header(prov_a_token))
    assert len(res_prov_a.json()) == 1
    assert res_prov_a.json()[0]["id"] == b1_id

    # 6. Test RBAC: Customer A sees only own bookings
    res_cust_a = client.get("/bookings", headers=auth_header(cust_a_token))
    assert len(res_cust_a.json()) == 1
    assert res_cust_a.json()[0]["id"] == b1_id

    # 7. Test RBAC: Provider A cannot access Provider B's booking
    res_prov_unauth = client.get(f"/bookings/{b2_id}", headers=auth_header(prov_a_token))
    assert res_prov_unauth.status_code == 403

    # 8. Test RBAC: Customer A cannot access Customer B's booking
    res_cust_unauth = client.get(f"/bookings/{b2_id}", headers=auth_header(cust_a_token))
    assert res_cust_unauth.status_code == 403

    # 9. Test RBAC: Admin can access any booking
    res_admin_single = client.get(f"/bookings/{b2_id}", headers=auth_header(admin_token))
    assert res_admin_single.status_code == 200
    assert res_admin_single.json()["id"] == b2_id
