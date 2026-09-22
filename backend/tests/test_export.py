def test_csv_export_endpoint(client, auth_headers):
    # Fetch categories
    cats = client.get("/api/categories", headers=auth_headers).json()["data"]
    salary_cat = next(c for c in cats if c["name"] == "Salary")
    
    # Add transaction
    client.post("/api/transactions", headers=auth_headers, json={
        "title": "Quarterly Bonus",
        "amount": 15000.0,
        "type": "income",
        "category_id": salary_cat["id"],
        "transaction_date": "2026-04-15",
        "payment_method": "Bank Transfer",
        "description": "High performance bonus"
    })

    # Call CSV Export
    export_res = client.get("/api/transactions/export?type=income", headers=auth_headers)
    assert export_res.status_code == 200
    assert "text/csv" in export_res.headers.get("content-type", "")
    assert "attachment; filename=" in export_res.headers.get("content-disposition", "")
    
    csv_text = export_res.text
    lines = csv_text.strip().split("\r\n") if "\r\n" in csv_text else csv_text.strip().split("\n")
    assert len(lines) >= 2
    assert "Date,Title,Type,Category,Amount,Payment Method,Description" in lines[0]
    assert "Quarterly Bonus" in lines[1]
    assert "15000.00" in lines[1]
    assert "Salary" in lines[1]
