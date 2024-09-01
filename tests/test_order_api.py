# Садовников Игорь, 20ая когорта — Финальный проект. Инженер по тестированию плюс
import configparser

import pytest
import requests


@pytest.fixture(scope="module")
def base_url():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['default']['base_url']


@pytest.fixture(scope="module", autouse=True)
def ping_server(base_url):
    response = requests.get(f"{base_url}/ping")
    assert response.status_code == 200, f"Сервер недоступен. Код ответа: {response.status_code}"


@pytest.fixture
def create_order(base_url):
    order_data = {
        "firstName": "Naruto",
        "lastName": "Uchiha",
        "address": "Konoha, 142 apt.",
        "metroStation": 4,
        "phone": "+7 800 355 35 35",
        "rentTime": 5,
        "deliveryDate": "2020-06-06",
        "comment": "Saske, come back to Konoha",
        "color": ["BLACK"]
    }
    response = requests.post(f"{base_url}/orders", json=order_data)
    assert response.status_code == 201, f"Неожиданный статус код: {response.status_code}"
    track = response.json()["track"]
    return track, order_data


def test_create_and_get_order(base_url, create_order):
    track, expected_order_data = create_order
    response = requests.get(f"{base_url}/orders/track?t={track}")
    assert response.status_code == 200, f"Неожиданный статус код: {response.status_code}"

    order_info = response.json()["order"]

    # Проверяем, что все поля совпадают с тем, что было отправлено при создании
    assert order_info["firstName"] == expected_order_data["firstName"], "Имя не совпадает"
    assert order_info["lastName"] == expected_order_data["lastName"], "Фамилия не совпадает"
    assert order_info["address"] == expected_order_data["address"], "Адрес не совпадает"
    assert order_info["metroStation"] == str(expected_order_data["metroStation"]), "Станция метро не совпадает"
    assert order_info["phone"] == expected_order_data["phone"], "Телефон не совпадает"
    assert order_info["rentTime"] == expected_order_data["rentTime"], "Время аренды не совпадает"
    assert order_info["deliveryDate"].startswith(expected_order_data["deliveryDate"]), "Дата доставки не совпадает"
    assert order_info["comment"] == expected_order_data["comment"], "Комментарий не совпадает"
    assert order_info["color"] == expected_order_data["color"], "Цвет не совпадает"


def test_order_status(base_url, create_order):
    track, _ = create_order
    response = requests.get(f"{base_url}/orders/track?t={track}")
    assert response.status_code == 200, f"Неожиданный статус код: {response.status_code}"

    order_info = response.json()["order"]
    status = order_info.get("status", 0)

    if order_info["finished"]:
        assert status == 2, "Ожидаемый статус 2 (завершен), но получен другой статус"
    elif order_info["cancelled"]:
        assert status == -1, "Ожидаемый статус -1 (отменен), но получен другой статус"
    elif order_info["inDelivery"]:
        assert status == 1, "Ожидаемый статус 1 (в доставке), но получен другой статус"
    else:
        assert status == 0, "Ожидаемый статус 0 (по умолчанию), но получен другой статус"
