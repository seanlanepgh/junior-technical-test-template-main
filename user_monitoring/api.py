from flask import Blueprint, current_app


api = Blueprint("api", __name__)


@api.post("/event")
def handle_user_event() -> dict:
    current_app.logger.info("Handling user event")
    return {}