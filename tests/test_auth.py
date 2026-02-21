import pytest

@pytest.mark.asyncio
async def test_register(client):
    response = await client.post("/api/v1/auth/register", json={
        "username": "newuser",
        "email": "new@test.com",
        "password": "password123"
    })
    assert response.status_code == 201
    assert response.json()["username"] == "newuser"

@pytest.mark.asyncio
async def test_register_duplicate(client):
    await client.post("/api/v1/auth/register", json={
        "username": "dupuser",
        "email": "dup@test.com",
        "password": "password123"
    })
    response = await client.post("/api/v1/auth/register", json={
        "username": "dupuser",
        "email": "dup@test.com",
        "password": "password123"
    })
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_login(client):
    await client.post("/api/v1/auth/register", json={
        "username": "loginuser",
        "email": "login@test.com",
        "password": "password123"
    })
    response = await client.post("/api/v1/auth/login", json={
        "email": "login@test.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_get_me(client, auth_headers):
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    assert "username" in response.json()