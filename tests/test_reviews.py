from tests.test_rbac import create_user, login


def test_reviews_flow(client):
    prov = create_user(client, "provider")
    cust = create_user(client, "customer")
    
    prov_token = login(client, prov["email"])
    cust_token = login(client, cust["email"])
    
    def auth_header(token):
        return {"Authorization": f"Bearer {token}"}
        
    # 1. Create booking
    b_res = client.post("/bookings", json={
        "provider_id": prov["id"],
        "start_time": "2026-10-01T10:00:00Z",
        "end_time": "2026-10-01T11:00:00Z"
    }, headers=auth_header(cust_token))
    b_id = b_res.json()["id"]
    
    # 2. Try to review pending booking (should fail)
    r1 = client.post("/reviews", json={
        "booking_id": b_id,
        "rating": 5,
        "comment": "Good"
    }, headers=auth_header(cust_token))
    assert r1.status_code == 400
    
    # 3. Update booking to completed
    client.put(f"/bookings/{b_id}", json={
        "status": "completed"
    }, headers=auth_header(cust_token))
    
    # 4. Review completed booking
    r2 = client.post("/reviews", json={
        "booking_id": b_id,
        "rating": 5,
        "comment": "Good"
    }, headers=auth_header(cust_token))
    assert r2.status_code == 201
    
    # 5. Try to review again (should fail)
    r3 = client.post("/reviews", json={
        "booking_id": b_id,
        "rating": 4,
        "comment": "Good again"
    }, headers=auth_header(cust_token))
    assert r3.status_code == 400
    
    # 6. Fetch provider reviews
    r4 = client.get(f"/reviews/provider/{prov['id']}")
    assert r4.status_code == 200
    assert len(r4.json()) == 1
    assert r4.json()[0]["rating"] == 5
