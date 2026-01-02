from twilio.rest import Client
from app.core.config import settings

def send_sms_code(to_phone: str, code: str):
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"CHATBOX : Votre code de réinitialisation est {code}.",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_phone
        )
        return message.sid
    except Exception as e:
        print(f"Erreur Twilio : {e}")
        return None