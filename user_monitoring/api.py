from flask import Blueprint, request, current_app
from user_monitoring.models import User, UserEvent
from datetime import datetime
from user_monitoring.db import db
api = Blueprint("api", __name__)

# This api would need some authentication and authorization
# So not just anyone or any user can use the api

@api.post("/event")
def handle_user_event() -> dict:
    current_app.logger.info("Handling user event")
    event_data = request.get_json()
    
    # Validate the event data
    is_valid, missing_fields = validate_event_data(event_data)
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
        user = get_user(user_id)
        if not user:
            return {"error": "User not found"}, 404

        # Create a new UserEvent instance
        current_app.logger.info("Inserting new user event")
        insert_user_event(event_data)
        alerts = get_Alerts(event_data)
        alertResultStruct = {'user_id': user_id ,'alert': alerts["alert_boolean"], 'alert_codes': alerts["alert_codes"]}
        return alertResultStruct
    
    except Exception as e:
        current_app.logger.error(f"Error handling user event: {e}")
        return {"error": "Internal server error"}, 500

def validate_event_data(event_data):
    """
    Validate the incoming event data.
    
    Args:
        event_data (dict): The event data dictionary.
        
    Returns:
        tuple: A tuple containing a boolean indicating if the data is valid,
               and a list of missing fields (if any).
    """
    required_fields = ["type", "amount", "user_id", "time"]
    missing_fields = [field for field in required_fields if field not in event_data or not event_data[field]]
    return not missing_fields, missing_fields

def get_user(user_id):
    """
    Retrieve a user from the database by ID.
    
    Args:
        user_id (int): The ID of the user.
        
    Returns:
        User: The user object, or None if not found.
    """
    return User.query.get(user_id)
def insert_user_event(event_data):
    """
    Insert a new user event into the database.

    Args:
        event_type (str): The type of the event.
        amount (float): The amount associated with the event.
        user_id (int): The ID of the user associated with the event.
        event_time (datetime): The time of the event.

    Returns:
        UserEvent: The newly created UserEvent object.
    """
    event_type = event_data["type"]
    amount = event_data["amount"]
    user_id = event_data["user_id"]
    event_time = event_data["time"]
    user_event = UserEvent(
        event_type=event_type,
        amount=amount,
        event_time=event_time,
        user_id=user_id,
        created_at= datetime.now()
    )
    db.session.add(user_event)
    db.session.commit()
    return user_event

# Get Alerts 
# Need to return an array of codes and boolean 
# Array of codes could be a enum to improve readable and allow for more codes in the future
def get_Alerts(event_data):
    """
    Get alerts based on the event data and user's event history.

    Args:
        event_data (dict): A dictionary containing the event data.

    Returns:
        dict: A dictionary containing the alert status and alert codes.
    """
    alert_codes =[]
    alert_boolean = False
    events = get_user_events(event_data["user_id"])
    # Check for three consecutive withdrawals
    alertCode = consecutive_withdrawals(events)
    if(alertCode is not None):
        alert_codes.append(alertCode)
    # Check for three consecutive deposits where each one is larger
    alertCode = consecutive_deposits(events) 
    if(alertCode is not None):
        alert_codes.append(alertCode)
    # Check for large withdrawal amount
    # Needed to convert amount string to float
    if event_data["type"] == "withdraw" and float(event_data["amount"]) > 100:
        alert_codes.append(1100)
    if alert_codes:
        alert_boolean = True
        
    
    alertStruct = {'alert_boolean': alert_boolean, 'alert_codes': alert_codes}
    return alertStruct
# This would be a endpoint in a real application
def get_user_events(user_id):
    """
    Retrieve all user events for a given user ID.

    Args:
        user_id (int): The ID of the user.

    Returns:
        list: A list of UserEvent objects.
    """
    try:
        events = UserEvent.query.filter_by(user_id=user_id).all()
        event_list = [
            {
                "id": event.id,
                "event_type": event.event_type,
                "amount": event.amount,
                "event_time": event.event_time,
                "user_id": event.user_id
            }
            for event in events
        ]
        return event_list

    except Exception as e:
        current_app.logger.error(f"Error retrieving user events: {e}")
        return {"error": "Internal server error"}, 500
def consecutive_withdrawals(events):
    """
    Check for consecutive deposits where each one is larger than the previous one.

    Args:
        events (list): A list of dictionaries containing the event details.

    Returns:
        int: The number of consecutive larger deposits.
    """
    # Check for three consecutive withdrawals
    consecutive_withdrawals = 0
    for event in events[::-1]:  # Iterate over events in reverse order
        if event["event_type"] == "withdraw":
            consecutive_withdrawals += 1
            print(event["event_type"])
            print(consecutive_withdrawals)
        else:
            break
    print(consecutive_withdrawals)
    if consecutive_withdrawals >= 3:
        return 30
def consecutive_deposits(events):
    """
    Check for consecutive withdrawals.

    Args:
        events (list): A list of dictionaries containing the event details.

    Returns:
        int: The number of consecutive withdrawals.
    """
    # Check for three consecutive deposits where each one is larger
    consecutive_larger_deposits = 0
    previous_amount = 0
    ignore_withdrawals = False
    for event in events[::-1]:  # Iterate over events in reverse order
        if event["event_type"] == "deposit":
            current_amount = event["amount"]
            print("current:" ,current_amount)
            print("previous:",previous_amount)
            if current_amount > previous_amount:
                consecutive_larger_deposits += 1
                previous_amount = current_amount
                ignore_withdrawals = False
            else:
                consecutive_larger_deposits = 1
                previous_amount = current_amount
                ignore_withdrawals = False
        elif ignore_withdrawals:
            continue
        else:
            consecutive_larger_deposits = 0
            ignore_withdrawals = True
        print(event["id"])
        print(consecutive_larger_deposits)
        if consecutive_larger_deposits >= 3:
            return 300
            break


