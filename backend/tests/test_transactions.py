from datetime import date

def test_transaction_crud_and_validation(client, auth_headers):
    # 1. Get categories to find an expense category
    cat_res = client.get("/api/categories", headers=auth_headers)
    assert cat_res.status_code == 200
    categories = cat_res.json()["data"]
    food_cat = next((c for c in categories if c["name"] == "Food"), categories[0])
    
    # 2. Validation error on amount <= 0
    bad_tx = client.post("/api/transactions", headers=auth_headers, json={
        "title": "Zero expense",
        "amount": 0,
        "type": "expense",
        "category_id": food_cat["id"],
        "transaction_date": str(date.today()),
        "payment_method": "UPI"
    })
    assert bad_tx.status_code == 422

    # 3. Create valid expense
    create_res = client.post("/api/transactions", headers=auth_headers, json={
        "title": "Grocery Shopping",
        "amount": 2450.50,
        "type": "expense",
        "category_id": food_cat["id"],
        "transaction_date": str(date.today()),
        "payment_method": "UPI",
        "description": "Weekly essentials"
    })
    assert create_res.status_code == 201
    tx_data = create_res.json()["data"]
    tx_id = tx_data["id"]
    assert tx_data["amount"] == 2450.50
    assert tx_data["title"] == "Grocery Shopping"

    # 4. Get single transaction
    get_res = client.get(f"/api/transactions/{tx_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["data"]["id"] == tx_id

    # 5. Update transaction
    update_res = client.put(f"/api/transactions/{tx_id}", headers=auth_headers, json={
        "title": "Supermarket Shopping Updated",
        "amount": 2600.00
    })
    assert update_res.status_code == 200
    assert update_res.json()["data"]["title"] == "Supermarket Shopping Updated"
    assert update_res.json()["data"]["amount"] == 2600.00

    # 6. Delete transaction
    del_res = client.delete(f"/api/transactions/{tx_id}", headers=auth_headers)
    assert del_res.status_code == 200

    # Verify deleted
    get_again = client.get(f"/api/transactions/{tx_id}", headers=auth_headers)
    assert get_again.status_code == 404

def test_transactions_search_and_filter(client, auth_headers):
    # Retrieve categories
    cat_res = client.get("/api/categories", headers=auth_headers)
    cats = cat_res.json()["data"]
    salary_cat = next(c for c in cats if c["name"] == "Salary")
    food_cat = next(c for c in cats if c["name"] == "Food")

    # Add 1 income and 1 expense
    client.post("/api/transactions", headers=auth_headers, json={
        "title": "Monthly Paycheck",
        "amount": 50000.0,
        "type": "income",
        "category_id": salary_cat["id"],
        "transaction_date": "2026-01-10",
        "payment_method": "Bank Transfer"
    })
    client.post("/api/transactions", headers=auth_headers, json={
        "title": "Dinner with Friends",
        "amount": 1500.0,
        "type": "expense",
        "category_id": food_cat["id"],
        "transaction_date": "2026-01-15",
        "payment_method": "Credit Card"
    })

    # Filter by type=income
    inc_res = client.get("/api/transactions?type=income", headers=auth_headers)
    txs = inc_res.json()["data"]["transactions"]
    assert len(txs) == 1
    assert txs[0]["title"] == "Monthly Paycheck"

    # Search by title
    search_res = client.get("/api/transactions?search=Dinner", headers=auth_headers)
    txs_search = search_res.json()["data"]["transactions"]
    assert len(txs_search) == 1
    assert txs_search[0]["title"] == "Dinner with Friends"

    # Filter by payment method
    pm_res = client.get("/api/transactions?payment_method=Credit Card", headers=auth_headers)
    assert len(pm_res.json()["data"]["transactions"]) == 1
