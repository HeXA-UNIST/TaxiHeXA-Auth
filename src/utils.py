import secrets
from datetime import timedelta, datetime
from flask_mail import Mail, Message

from src.database.models import Auth, Users

def create_safe_random_otp_code(digits:int = 6) -> str:
    otp_code = ''.join(secrets.choice('0123456789') for _ in range(digits))
    return otp_code

def verified_otp(otp_code:str, email:str, auth:Auth):
    # check otp

    if not email == auth.email:
        return False, "email failed"
    if not otp_code == auth.otp:
        return False, "otp code is not same"
    if auth.created_at + timedelta(minutes=5) < datetime.utcnow():
        return False, "Expired"

    return True, None


def enroll_session(session, user: Users):
    session['nickname'] = user.nickname
    session['is_authenticated'] = "True"
    session['email'] = user.email
    session['user_id'] = user.id


def send_email(mail:Mail, to:str, title:str, content:str):
    msg = Message(
        subject=title,
        recipients=[to],
        body=content
    )
    mail.send(msg)
