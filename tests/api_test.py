import pytest
import requests
import json

BASE_URL = "http://127.0.0.1:5000"  # Replace with your actual API endpoint


@pytest.fixture
def invalid_type_event_data():
    return {
        "type": "test",
        "amount": 100.0,
        "user_id": 1,
        "time": 10,
    }


@pytest.fixture
def invalid_amount_event_data():
    return {
        "type": "test",
        "amount": "100.0",
        "user_id": 1,
        "time": 10,
    }


@pytest.fixture
def invalid_user_event_data():
    return {
        "type": "deposit",
        "amount": 100.0,
        "user_id": 999,
        "time": 10,
    }


@pytest.fixture
def deposit_event_data():
    return {
        "type": "deposit",
        "amount": 100.0,
        "user_id": 1,
        "time": 10,
    }


def withdraw_event_data():
    return {
        "type": "withdraw",
        "amount": 100.0,
        "user_id": 1,
        "time": 10,
    }


def test_alert_withdrawal_greater_than_hundred():
    event_data = {
        "type": "withdraw",
        "amount": 150.0,
        "user_id": 1,
        "time": 10,
    }
    url = f"{BASE_URL}/event"
    response = requests.post(url, json=event_data)
    assert response.status_code == 200
    data = response.json()
    assert data["alert"] is True
    assert 1100 in data["alert_codes"]


def test_alert_three_consecutive_withdrawals():
    # Create three consecutive withdrawal events
    event_data = {
        "type": "withdraw",
        "amount": 50.0,
        "user_id": 1,
        "time": 10,
    }
    url = f"{BASE_URL}/event"
    requests.post(url, json=event_data)
    requests.post(url, json=event_data)
    response = requests.post(url, json=event_data)
    assert response.status_code == 200
    data = response.json()
    assert data["alert"] is True
    assert 30 in data["alert_codes"]


def test_alert_three_consecutive_larger_deposits():
    # Create three consecutive larger deposit events
    event_data = {
        "type": "deposit",
        "amount": 50.0,
        "user_id": 1,
        "time": 10,
    }
    url = f"{BASE_URL}/event"
    requests.post(url, json=event_data)

    event_data["amount"] = 100.0
    requests.post(url, json=event_data)

    event_data["amount"] = 150.0
    response = requests.post(url, json=event_data)
    assert response.status_code == 200
    data = response.json()
    assert data["alert"] is True
    assert 300 in data["alert_codes"]


def test_alert_deposit_amount_exceeded_within_time():
    # Create multiple deposit events within a short time window
    event_data = {
        "type": "deposit",
        "amount": 100.0,
        "user_id": 1,
        "time": 10,
    }
    url = f"{BASE_URL}/event"
    requests.post(url, json=event_data)
    requests.post(url, json=event_data)
    response = requests.post(url, json=event_data)

    assert response.status_code == 200
    data = response.json()
    assert data["alert"] is True
    assert 123 in data["alert_codes"]


def test_alert_user_not_found():
    event_data = {
        "type": "deposit",
        "amount": 100.0,
        "user_id": 999,  # Non-existent user ID
        "time": 10,
    }
    url = f"{BASE_URL}/event"
    response = requests.post(url, json=event_data)
    assert response.status_code == 404
    data = response.json()
    assert "User not found" in data["error"]


def test_create_event_with_invalid_type(invalid_type_event_data):
    url = f"{BASE_URL}/event"

    response = requests.post(url, json=invalid_type_event_data)
    assert (
        response.status_code == 400
    )  # Assuming the API returns a 400 Bad Request for invalid event types


def test_create_event_with_invalid_amount(invalid_amount_event_data):
    url = f"{BASE_URL}/event"
    response = requests.post(url, json=invalid_amount_event_data)
    assert (
        response.status_code == 400
    )  # Assuming the API returns a 400 Bad Request for invalid amount types


def test_create_deposit_event(deposit_event_data):
    url = f"{BASE_URL}/event"
    response = requests.post(url, json=deposit_event_data)
    assert (
        response.status_code == 200
    )  # Assuming the API returns a 200 Created for successful event creation


def test_create_withdraw_event():
    url = f"{BASE_URL}/event"
    data = withdraw_event_data()
    response = requests.post(url, json=data)
    assert (
        response.status_code == 200
    )  # Assuming the API returns a 200 Created for successful event creation


def test_alert_three_consecutive_larger_deposits_with_withdraw():
    # Create three consecutive larger deposit events
    event_data = {
        "type": "deposit",
        "amount": 10.0,
        "user_id": 1,
        "time": 10,
    }

    withdraw_event_data = {
        "type": "deposit",
        "amount": 50.0,
        "user_id": 1,
        "time": 10,
    }
    url = f"{BASE_URL}/event"
    requests.post(url, json=event_data)

    event_data["amount"] = 30.0
    requests.post(url, json=event_data)
    event_data["amount"] = 40.0
    requests.post(url, json=withdraw_event_data)
    response = requests.post(url, json=event_data)
    assert response.status_code == 200
    data = response.json()
    assert data["alert"] is True
    assert 300 in data["alert_codes"]


def test_alert_deposit_amount_exceeded_within_time_with_withdraw():
    # Create multiple deposit events within a short time window
    event_data = {
        "type": "deposit",
        "amount": 100.0,
        "user_id": 1,
        "time": 10,
    }
    withdraw_event_data = {
        "type": "deposit",
        "amount": 50.0,
        "user_id": 1,
        "time": 10,
    }
    url = f"{BASE_URL}/event"
    requests.post(url, json=event_data)
    requests.post(url, json=withdraw_event_data)
    requests.post(url, json=event_data)
    response = requests.post(url, json=event_data)

    assert response.status_code == 200
    data = response.json()
    assert data["alert"] is True
    assert 123 in data["alert_codes"]
