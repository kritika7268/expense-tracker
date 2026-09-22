def test_user_data_isolation(client):
    # 1. Register User A
    res_a = client.post("/api/auth/register", json={
        "name": "User Alpha",
        "email": "alpha@example.com",
        "password": "PasswordAlpha123",
        "confirm_password": "PasswordAlpha123",
        "currency": "INR"
    })
    token_a = res_a.json()["data"]["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. Register User B
    res_b = client.post("/api/auth/register", json={
        "name": "User Beta",
        "email": "beta@example.com",
        "password": "PasswordBeta123",
        "confirm_password": "PasswordBeta123",
        "currency": "USD"
    })
    token_b = res_b.json()["data"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Get User A's category
    cats_a = client.get("/api/categories", headers=headers_a).json()["data"]
    cat_a = cats_a[0]

    # User A creates a transaction
    tx_res = client.post("/api/transactions", headers=headers_a, json={
        "title": "Alpha Confidential Expense",
        "amount": 999.99,
        "type": cat_a["type"],
        "category_id": cat_a["id"],
        "transaction_date": "2026-03-01",
        "payment_method": "Cash"
    })
    tx_id = tx_res.json()["data"]["id"]

    # 3. User B tries to view User A's transaction directly -> MUST FAIL (404)
    b_view_res = client.get(f"/api/transactions/{tx_id}", headers=headers_b)
    assert b_view_res.status_code == 404

    # 4. User B tries to edit User A's transaction -> MUST FAIL (404)
    b_edit_res = client.put(f"/api/transactions/{tx_id}", headers=headers_b, json={
        "title": "Hacked Title",
        "amount": 1.0
    })
    assert b_edit_res.status_code == 404

    # 5. User B tries to delete User A's transaction -> MUST FAIL (404)
    b_del_res = client.delete(f"/api/transactions/{tx_id}", headers=headers_b)
    assert b_del_res.status_code == 404

    # 6. User B lists transactions -> User A's transaction must NOT be present
    b_list_res = client.get("/api/transactions", headers=headers_b)
    assert len(b_list_res.json()["data"]["transactions"]) == 0

    # 7. User A creates a budget
    budget_res = client.post("/api/budgets", headers=headers_a, json={
        "category_id": cat_a["id"],
        "amount": 5000.0,
        "month": 3,
        "year": 2026
    })
    budget_id = budget_res.json()["data"]["id"]

    # User B tries to access User A's budget -> MUST FAIL (404)
    b_budget_res = client.get(f"/api/budgets/{budget_id}", headers=headers_b)
    assert b_budget_res.status_code == 404
