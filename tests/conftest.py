from typing import Generator

import pytest
from flask.testing import FlaskClient
from flask import Flask

from user_monitoring.app import create_app


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    app = create_app()
    with app.app_context():
        yield app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()
