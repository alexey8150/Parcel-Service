from httpx import Cookies


async def test_get_packages(client):
    response = await client.get("/package")
    assert response.status_code == 404


async def test_post_package(client):
    package_data = {
        "name": "посылка",
        "weight": 101,
        "content_price": 100,
        "type": "clothes"
    }
    response = await client.post("/package", json=package_data)

    assert response.status_code == 201
    assert response.json() == {'package_id': 1}


async def test_get_one_package(client):
    response = await client.get("/package/1")
    assert response.status_code == 200
    assert response.json()["name"] == "посылка"


async def test_get_one_not_exist_package(client):
    response = await client.get("/package/888")
    assert response.status_code == 404


async def test_post_validate_package(client):
    package_data = {
        "name": "посылка",
        "weight": 0,
        "content_price": 100,
        "type": "clothes"
    }
    response = await client.post("/package", json=package_data)

    assert response.status_code == 422


async def test_create_and_get_user_package_with_cookies(client):
    package_data = {
        "name": "посылка",
        "weight": 101,
        "content_price": 100,
        "type": "clothes"
    }

    cookies = Cookies()
    sent_user_uuid = "test-user-uuid-123"
    cookies.set("user_uuid", sent_user_uuid)

    post_response = await client.post("/package", json=package_data, cookies=cookies)
    assert post_response.status_code == 201

    get_response = await client.get("/package/my-packages", cookies=cookies)
    assert get_response.status_code == 200


async def test_create_and_get_user_package_without_cookies(client):
    get_response = await client.get("/package/my-packages")
    assert get_response.status_code == 404
