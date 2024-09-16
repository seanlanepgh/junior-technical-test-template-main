from datetime import datetime, timedelta
from user_monitoring.models import User, UserEvent
from user_monitoring.db import db
from enum import Enum


class AlertCodes(Enum):
    WITHDRAWAL_GREATER_THAN_HUNDRED = 1100
    THREE_CONSECUTIVE_WITHDRAWALS = 30
    THREE_CONSECUTIVE_LARGER_DEPOSITS = 300
    DEPOSIT_AMOUNT_EXCEEDED_WITHIN_TIME = 123


class UserEvents:
    @staticmethod
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
        missing_fields = [
            field
            for field in required_fields
            if field not in event_data or not event_data[field]
        ]
        return not missing_fields, missing_fields

    @staticmethod
    def get_user(user_id):
        """
        Retrieve a user from the database by ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            User: The user object, or None if not found.
        """
        return User.query.get(user_id)

    @staticmethod
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
            created_at=datetime.now(),
        )
        db.session.add(user_event)
        db.session.commit()
        return user_event

    # Get Alerts
    # Need to return an array of codes and boolean
    @staticmethod
    def get_Alerts(event_data):
        """
        Get alerts based on the event data and user's event history.

        Args:
            event_data (dict): A dictionary containing the event data.

        Returns:
            dict: A dictionary containing the alert status and alert codes.
        """
        alert_codes = []
        alert_boolean = False
        events = UserEvents.get_user_events(event_data["user_id"])

        # Check for large withdrawal amount
        # Needed to convert amount string to float
        if event_data["type"] == "withdraw" and float(event_data["amount"]) > 100:
            alert_codes.append(AlertCodes.WITHDRAWAL_GREATER_THAN_HUNDRED.value)
        # Check for three consecutive withdrawals
        alertCode = UserEvents.consecutive_withdrawals(events)
        if alertCode is not None:
            alert_codes.append(AlertCodes.THREE_CONSECUTIVE_WITHDRAWALS.value)
        # Check for three consecutive deposits where each one is larger
        alertCode = UserEvents.consecutive_deposits(events)
        if alertCode is not None:
            alert_codes.append(AlertCodes.THREE_CONSECUTIVE_LARGER_DEPOSITS.value)

        # Check if total deposit amount exceeds $200 within 30 seconds
        if event_data[
            "type"
        ] == "deposit" and UserEvents.check_deposit_amount_within_time(events):
            alert_codes.append(AlertCodes.DEPOSIT_AMOUNT_EXCEEDED_WITHIN_TIME.value)

        if alert_codes:
            alert_boolean = True

        alertStruct = {"alert_boolean": alert_boolean, "alert_codes": alert_codes}
        return alertStruct

    # This would be a endpoint in a real application
    @staticmethod
    def get_user_events(user_id):
        """
        Retrieve all user events for a given user ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            list: A list of UserEvent objects.
        """

        events = UserEvent.query.filter_by(user_id=user_id).all()
        event_list = [
            {
                "id": event.id,
                "event_type": event.event_type,
                "amount": event.amount,
                "event_time": event.event_time,
                "user_id": event.user_id,
                "created_at": event.created_at,
            }
            for event in events
        ]
        return event_list

    @staticmethod
    def consecutive_withdrawals(events):
        """
        Check for consecutive withdrawals.

        Args:
            events (list): A list of dictionaries containing the event details.

        Returns:
            int: The number of consecutive withdrawals.
        """

        # Check for three consecutive withdrawals
        consecutive_withdrawals = 0
        for event in events[::-1]:  # Iterate over events in reverse order
            if event["event_type"] == "withdraw":
                consecutive_withdrawals += 1
            else:
                break
        if consecutive_withdrawals >= 3:
            return 30

    @staticmethod
    def consecutive_deposits(events):
        """
        Check for consecutive deposits where each one is larger than the previous one.

        Args:
            events (list): A list of dictionaries containing the event details.

        Returns:
            int: The number of consecutive larger deposits.
        """
        # Check for three consecutive deposits where each one is larger
        consecutive_larger_deposits = 0
        previous_amount = 0

        # Remove withdraw events from the events list
        # I originally used a boolean to skip over the withdraw events
        filtered_events = [
            event for event in events if event["event_type"] == "deposit"
        ]
        eventCount = 0
        for event in filtered_events[::-1]:  # Iterate over events in reverse order
            current_amount = event["amount"]
            print("current:", current_amount)
            print("previous:", previous_amount)
            if current_amount < previous_amount and current_amount != previous_amount:
                consecutive_larger_deposits += 1
                previous_amount = current_amount
                print(event["id"])
                print(consecutive_larger_deposits)
            else:
                consecutive_larger_deposits = 1
                previous_amount = current_amount
            print(event["id"])
            print(consecutive_larger_deposits)

            if consecutive_larger_deposits >= 3:
                return 300
                break
            eventCount += 1
            if eventCount > 3:
                break

    @staticmethod
    def check_deposit_amount_within_time(events, amount_threshold=200, time_window=30):
        """
        Check if the total amount deposited in events exceeds a specified threshold within a given time window.

        Args:
            events (list): A list of dictionaries containing the event details.
            amount_threshold (float): The maximum total deposit amount allowed within the time window.
            time_window (int): The time window in seconds.

        Returns:
            bool: True if the total deposit amount exceeds the threshold within the time window, False otherwise.
        """
        total_deposit_amount = 0
        end_time = datetime.now()
        start_time = end_time - timedelta(seconds=time_window)
        for event in events[::-1]:  # Iterate over events in reverse order
            if event["event_type"] == "deposit":
                event_created_at = event["created_at"]
                if start_time <= event_created_at <= end_time:
                    total_deposit_amount += event["amount"]

        return total_deposit_amount > amount_threshold
