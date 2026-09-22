def test_register_success(client):
    res = client.post("/api/auth/register", json={
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "SecurePassword123",
        "confirm_password": "SecurePassword123",
        "currency": "USD"
    })
    assert res.status_code == 201
    body = res.json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert body["data"]["user"]["email"] == "jane@example.com"
    assert body["data"]["user"]["currency"] == "USD"

def test_register_duplicate_email(client):
    payload = {
        "name": "Jane Doe",
        "email": "duplicate@example.com",
        "password": "SecurePassword123",
        "confirm_password": "SecurePassword123"
    }
    res1 = client.post("/api/auth/register", json=payload)
    assert res1.status_code == 201
    
    res2 = client.post("/api/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["message"]

def test_register_password_mismatch(client):
    res = client.post("/api/auth/register", json={
        "name": "Jane Doe",
        "email": "mismatch@example.com",
        "password": "PasswordOne1",
        "confirm_password": "PasswordTwo2"
    })
    assert res.status_code == 422
    assert "Passwords do not match" in res.json()["message"]

def test_login_success(client):
    reg = client.post("/api/auth/register", json={
        "name": "Login Tester",
        "email": "login@example.com",
        "password": "MySecretPassword123",
        "confirm_password": "MySecretPassword123"
    })
    assert reg.status_code == 201
    
    res = client.post("/api/auth/login", json={
        "email": "login@example.com",
        "password": "MySecretPassword123"
    })
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert "access_token" in body["data"]

def test_login_invalid_password(client):
    reg = client.post("/api/auth/register", json={
        "name": "Login Tester",
        "email": "wrongpwd@example.com",
        "password": "MySecretPassword123",
        "confirm_password": "MySecretPassword123"
    })
    assert reg.status_code == 201

    res = client.post("/api/auth/login", json={
        "email": "wrongpwd@example.com",
        "password": "WrongPassword456"
    })
    assert res.status_code == 401
    assert "Invalid email or password" in res.json()["message"]

def test_get_current_user_me(client, auth_headers):
    res = client.get("/api/auth/me", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert body["data"]["email"] == "tester@expensely.com"

def test_unauthorized_access(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401
