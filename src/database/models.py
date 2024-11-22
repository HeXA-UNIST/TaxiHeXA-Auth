from sqlalchemy import Integer, String, DateTime, Boolean
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Auth 테이블 모델
class Auth(Base):
    __tablename__ = "auth"  # 테이블 이름
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)  # 이메일 주소
    otp = Column(String, nullable=False)  # 인증 번호
    created_at = Column(DateTime, server_default=current_timestamp())  # 인증 번호 발급 시간
    is_verified = Column(Boolean, nullable=False, default=False)  # 인증 성공 여부

# User 테이블 모델
class Users(Base):
    __tablename__ = "users"  # 테이블 이름
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)  # 이메일 주소
    nickname = Column(String, nullable=False, unique=True, index=True)  # 닉네임
    is_banned = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, server_default=current_timestamp())  # 계정 생성 시간


# 데이터베이스 생성
# Base.metadata.create_all(engine)