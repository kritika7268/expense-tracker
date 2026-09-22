def test_financial_dashboard_calculations(client, auth_headers):
    # Fetch categories
    cats = client.get("/api/categories", headers=auth_headers).json()["data"]
    salary_cat = next(c for c in cats if c["name"] == "Salary")
    food_cat = next(c for c in cats if c["name"] == "Food")

    # Add Income: 100,000
    client.post("/api/transactions", headers=auth_headers, json={
        "title": "Corporate Salary",
        "amount": 100000.0,
        "type": "income",
        "category_id": salary_cat["id"],
        "transaction_date": "2026-06-01",
        "payment_method": "Bank Transfer"
    })

    # Add Expense: 40,000
    client.post("/api/transactions", headers=auth_headers, json={
        "title": "Living Expenses",
        "amount": 40000.0,
        "type": "expense",
        "category_id": food_cat["id"],
        "transaction_date": "2026-06-05",
        "payment_method": "UPI"
    })

    # Add second Expense: 15,000
    client.post("/api/transactions", headers=auth_headers, json={
        "title": "Catering",
        "amount": 15000.0,
        "type": "expense",
        "category_id": food_cat["id"],
        "transaction_date": "2026-06-10",
        "payment_method": "Credit Card"
    })

    # Get analytics report for 2026-06
    report_res = client.get("/api/analytics/report?month=6&year=2026", headers=auth_headers)
    assert report_res.status_code == 200
    report = report_res.json()["data"]

    assert report["total_income"] == 100000.0
    assert report["total_expense"] == 55000.0
    assert report["total_savings"] == 45000.0
    # Savings rate: (45000 / 100000) * 100 = 45.0%
    assert report["savings_rate"] == 45.0
    assert report["transaction_count"] == 3
    assert report["highest_spending_category"]["category_name"] == "Food"
    assert report["highest_spending_category"]["amount"] == 55000.0
