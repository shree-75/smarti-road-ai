import os
import urllib.parse
from typing import Dict, Any

DEFAULT_ACCOUNT_SID = ""
DEFAULT_AUTH_TOKEN = ""
DEFAULT_FROM_PHONE = ""
DEFAULT_RECIPIENT_PHONE = "+919704638232"

def get_twilio_credentials():
    account_sid = os.getenv("TWILIO_ACCOUNT_SID") or DEFAULT_ACCOUNT_SID
    auth_token = os.getenv("TWILIO_AUTH_TOKEN") or DEFAULT_AUTH_TOKEN
    from_phone = os.getenv("TWILIO_PHONE_NUMBER", "").strip() or DEFAULT_FROM_PHONE
    to_phone = os.getenv("EMERGENCY_PHONE_NUMBER", "").strip() or DEFAULT_RECIPIENT_PHONE

    return account_sid, auth_token, from_phone, to_phone

def get_twilio_status() -> Dict[str, Any]:
    account_sid, auth_token, from_phone, to_phone = get_twilio_credentials()
    return {
        "account_sid_configured": bool(account_sid),
        "auth_token_configured": bool(auth_token),
        "account_sid_masked": f"{account_sid[:6]}...{account_sid[-4:]}" if account_sid else None,
        "from_phone": from_phone or DEFAULT_FROM_PHONE,
        "to_phone": to_phone or DEFAULT_RECIPIENT_PHONE,
        "ready_for_calls": bool(account_sid and auth_token and from_phone and to_phone)
    }

def update_twilio_credentials(from_phone: str = None, to_phone: str = None, account_sid: str = None, auth_token: str = None):
    if account_sid:
        os.environ["TWILIO_ACCOUNT_SID"] = account_sid.strip()
    if auth_token:
        os.environ["TWILIO_AUTH_TOKEN"] = auth_token.strip()
    if from_phone is not None:
        os.environ["TWILIO_PHONE_NUMBER"] = from_phone.strip()
    if to_phone is not None:
        os.environ["EMERGENCY_PHONE_NUMBER"] = to_phone.strip()

    return get_twilio_status()

def send_emergency_sms(message_body: str, recipient_phone: str = None) -> Dict[str, Any]:
    """
    Dispatches emergency SMS notification using Twilio API.
    """
    account_sid, auth_token, from_phone, default_to = get_twilio_credentials()
    to_phone = (recipient_phone or default_to or DEFAULT_RECIPIENT_PHONE).strip()

    if not account_sid or not auth_token:
        return {"status": "NOT_CONFIGURED", "message": "Twilio Account SID or Auth Token missing"}
    if not from_phone:
        return {"status": "NOT_CONFIGURED", "message": "Twilio Phone Number missing"}
    if not to_phone:
        return {"status": "NOT_CONFIGURED", "message": "Emergency Phone Number missing"}

    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=message_body,
            from_=from_phone,
            to=to_phone
        )
        print(f"[Twilio SMS] Message sent to {to_phone}. SID: {message.sid}")
        return {
            "status": "SENT",
            "sid": message.sid,
            "message": f"Emergency SMS dispatched successfully to {to_phone}"
        }
    except Exception as err:
        print(f"[Twilio SMS Error] {err}")
        return {
            "status": "FAILED",
            "message": f"Twilio SMS Error: {str(err)}"
        }

def make_emergency_call(to_phone: str = None, reason: str = "Critical driver distraction detected") -> Dict[str, Any]:
    """
    Initiates an emergency phone call alert to driver/recipient (+919704638232 default).
    Speaks an urgent, professional alert message via Twilio Voice.
    """
    account_sid, auth_token, from_phone, default_to = get_twilio_credentials()
    target_phone = (to_phone or default_to or DEFAULT_RECIPIENT_PHONE).strip()

    if not account_sid or not auth_token:
        return {"status": "NOT_CONFIGURED", "message": "Twilio Account SID or Auth Token missing"}
    if not from_phone:
        return {"status": "NOT_CONFIGURED", "message": "Twilio Phone Number missing"}
    if not target_phone:
        return {"status": "NOT_CONFIGURED", "message": "Recipient phone number not specified"}

    spoken_message = (
        f"Attention! This is an urgent safety alert from Smart Road AI. "
        f"{reason}. "
        f"Please take immediate control of the steering wheel and drive safely! "
        f"Repeating: {reason}. Immediate action required!"
    )

    try:
        from twilio.rest import Client
        from twilio.twiml.voice_response import VoiceResponse

        vr = VoiceResponse()
        vr.say(spoken_message, voice="alice", language="en-IN")
        twiml_payload = str(vr)

        client = Client(account_sid, auth_token)
        call = client.calls.create(
            twiml=twiml_payload,
            to=target_phone,
            from_=from_phone
        )
        print(f"[Twilio Voice] Voice call successfully placed to {target_phone}! SID: {call.sid} | Reason: {reason}")
        return {
            "status": "CALL_INITIATED",
            "sid": call.sid,
            "to": target_phone,
            "message": f"Emergency voice call dispatched to {target_phone} ({reason})"
        }
    except Exception as err:
        print(f"[Twilio Voice Error] Call to {target_phone} failed: {err}")
        return {
            "status": "FAILED",
            "to": target_phone,
            "message": f"Twilio Voice Error: {str(err)}"
        }
