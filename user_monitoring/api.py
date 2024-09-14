from flask import Blueprint, request, current_app
from user_monitoring.models import User, UserEvent
from datetime import datetime, timedelta
from user_monitoring.Class.user_events import UserEvents
from user_monitoring.db import db

api = Blueprint("api", __name__)

# This api would need some authentication and authorization
# So not just anyone or any user can use the api


@api.post("/event")
def handle_user_event() -> dict:
    current_app.logger.info("Handling user event")
    event_data = request.get_json()

    # Validate the event data
    is_valid, missing_fields = UserEvents.validate_event_data(event_data)
    if not is_valid:
        error_message = f"Missing required parameters: {', '.join(missing_fields)}"
        return {"error": error_message}, 400
    # Need to add some more strict type validation for all fields not just type
    event_type = event_data["type"]
    if event_type not in ["deposit", "withdraw"]:
        return {"error": "Invalid event type. Must be 'deposit' or 'withdraw'."}, 400

    user_id = event_data["user_id"]
    try:
        # Check if the user exists
        current_app.logger.info("Checking if user exists")
        user = UserEvents.get_user(user_id)
        if not user:
            return {"error": "User not found"}, 404

        # Create a new UserEvent instance
        current_app.logger.info("Inserting new user event")
        UserEvents.insert_user_event(event_data)
        alerts = UserEvents.get_Alerts(event_data)
        alertResultStruct = {
            "user_id": user_id,
            "alert": alerts["alert_boolean"],
            "alert_codes": alerts["alert_codes"],
        }
        return alertResultStruct

    except Exception as e:
        current_app.logger.error(f"Error handling user event: {e}")
        return {"error": "Internal server error"}, 500
