from flask.testing import FlaskClient


def test_handle_user_event_doesnt_do_anything_yet(client: FlaskClient) -> None:
    response = client.post("/event")
    assert response.status_code == 200
    assert response.json == {}
