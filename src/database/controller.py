from sqlalchemy.orm import Session
from src.database.models import Auth, Users

# 1. save_otp(): OTP 저장
def create_otp(db: Session, email: str, otp: str, is_verified:bool=False):
    new_otp = Auth(
        email=email,
        otp=otp,
        is_verified=is_verified
    )
    db.add(new_otp)
    db.commit()
    return otp

def update_otp_is_veritied(db: Session, auth:Auth, is_verified:bool):
    auth.is_verified = is_verified
    db.commit()
    return auth

def select_otp_by_email(db: Session, email: str) -> Auth:
    auth_record = db.query(Auth).filter(Auth.email == email).order_by(Auth.created_at.desc()).first()
    return auth_record

# 3. save_nickname(): 닉네임 저장
def select_user_by_nickname(db: Session, nickname:str) -> Users:
    return db.query(Users).filter(Users.nickname == nickname).first()

def create_user(db: Session, email:str, nickname:str):
    user = Users(
        nickname=nickname,
        email=email
    )
    db.add(user)
    db.commit()
    return user

# 4. check_register(): 회원가입 여부 확인
def select_user_by_email(db: Session, email: str) -> Users:
    user = db.query(Users).filter(Users.email == email).first()
    return user
