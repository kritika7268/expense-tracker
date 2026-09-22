def test_budget_creation_and_threshold_alerts(client, auth_headers):
    # 1. Get Food category
    cat_res = client.get("/api/categories?type=expense", headers=auth_headers)
    cats = cat_res.json()["data"]
    food_cat = next(c for c in cats if c["name"] == "Food")

    # 2. Create budget: 1,000 for current month
    month = 5
    year = 2026
    b_res = client.post("/api/budgets", headers=auth_headers, json={
        "category_id": food_cat["id"],
        "amount": 1000.0,
        "month": month,
        "year": year
    })
    assert b_res.status_code == 201
    b_data = b_res.json()["data"]
    assert b_data["amount"] == 1000.0
    assert b_data["status"] == "Under Budget"
    assert b_data["percentage"] == 0.0

    # 3. Add expense of 500 (50% -> Under Budget)
    client.post("/api/transactions", headers=auth_headers, json={
        "title": "Groceries 1",
        "amount": 500.0,
        "type": "expense",
        "category_id": food_cat["id"],
        "transaction_date": f"{year}-0{month}-05",
        "payment_method": "UPI"
    })
    budgets_res = client.get(f"/api/budgets?month={month}&year={year}", headers=auth_headers)
    budget = budgets_res.json()["data"]["budgets"][0]
    assert budget["spent"] == 500.0
    assert budget["remaining"] == 500.0
    assert budget["percentage"] == 50.0
    assert budget["status"] == "Under Budget"
    assert budget["warning_message"] is None

    # 4. Add another expense of 350 (Total 850 / 85% -> Near Limit)
    client.post("/api/transactions", headers=auth_headers, json={
        "title": "Groceries 2",
        "amount": 350.0,
        "type": "expense",
        "category_id": food_cat["id"],
        "transaction_date": f"{year}-0{month}-15",
        "payment_method": "Debit Card"
    })
    budgets_res2 = client.get(f"/api/budgets?month={month}&year={year}", headers=auth_headers)
    budget2 = budgets_res2.json()["data"]["budgets"][0]
    assert budget2["spent"] == 850.0
    assert budget2["remaining"] == 150.0
    assert budget2["percentage"] == 85.0
    assert budget2["status"] == "Near Limit"
    assert "85% of your Food budget has been used." in budget2["warning_message"]

    # 5. Add expense of 200 (Total 1050 / 105% -> Over Budget)
    client.post("/api/transactions", headers=auth_headers, json={
        "title": "Groceries 3",
        "amount": 200.0,
        "type": "expense",
        "category_id": food_cat["id"],
        "transaction_date": f"{year}-0{month}-20",
        "payment_method": "Cash"
    })
    budgets_res3 = client.get(f"/api/budgets?month={month}&year={year}", headers=auth_headers)
    budget3 = budgets_res3.json()["data"]["budgets"][0]
    assert budget3["spent"] == 1050.0
    assert budget3["remaining"] == 0.0
    assert budget3["status"] == "Over Budget"
    assert "Your Food budget has been exceeded." in budget3["warning_message"]
