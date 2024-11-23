import pytest
from flask import json
from app import app, get_db  # Flask 앱과 DB 세션 가져오기
from src.database.controller import create_user, create_otp
from src.database.models import Auth, Users

# Pytest Fixture: Flask 테스트 클라이언트
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client

# Test 1: `/api/taxi_auth/status` 상태 확인
def test_status(client):
    response = client.get('/api/taxi_auth/status')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'ok'}

# Test 2: 이메일 인증 번호 요청
def test_request_verify(client):
    db = get_db()
    email = "unknown@unist.ac.kr"

    # 이메일 형식 오류 테스트
    invalid_email_response = client.post('/api/taxi_auth/request_verify', json={"email": "invalid-email"})
    assert invalid_email_response.status_code == 400

    invalid_email_response = client.post('/api/taxi_auth/request_verify', json={"email": ""})
    assert invalid_email_response.status_code == 400

    # 올바른 요청
    valid_email_response = client.post('/api/taxi_auth/request_verify', json={"email": email})
    assert valid_email_response.status_code == 200

    # OTP가 DB에 저장되었는지 확인
    auth = db.query(Auth).filter(Auth.email == email).first()
    assert auth is not None
    assert auth.email == email

# Test 3: 이메일 인증 번호 확인
def test_check_verify(client):
    db = get_db()
    email = "unknown@unist.ac.kr"
    otp_code = "1234"

    # 테스트용 OTP 생성
    create_otp(db, email, otp_code)

    # 성공 케이스

    # 1) 기존에 존재하지 않는 이메일
    valid_response = client.post('/api/taxi_auth/check_verify', json={"email": email, "otp": otp_code})
    assert valid_response.status_code == 200
    assert valid_response.get_json().get('registered') == False

    # 로그인이 안 되는지 확인
    with client.session_transaction() as session:
        assert session.get('is_authenticated') is None
        assert session.get('email') is None

    # 유저 생성
    create_user(db, email, "nickname")

    # 2) 기존에 존재하는 이메일
    valid_response = client.post('/api/taxi_auth/check_verify', json={"email": email, "otp": otp_code})
    assert valid_response.status_code == 200
    assert valid_response.get_json().get('registered') == True

    # 로그인 되는 지 확인
    with client.session_transaction() as session:
        assert session.get('is_authenticated') == 'True'
        assert session.get('email') == email

    # 실패 케이스
    invalid_response = client.post('/api/taxi_auth/check_verify', json={"email": email, "otp": "wrong-otp"})
    assert invalid_response.status_code == 400

    invalid_response = client.post('/api/taxi_auth/check_verify', json={"email": "", "otp": otp_code})
    assert invalid_response.status_code == 400

    invalid_response = client.post('/api/taxi_auth/check_verify', json={"email": email, "otp": ""})
    assert invalid_response.status_code == 400

# Test 4: 닉네임 등록
def test_register_user(client):
    db = get_db()
    email = "unknown@unist.ac.kr"
    nickname = "newuser123"

    # invalid input format
    duplicate_nickname_response = client.post('/api/taxi_auth/register', json={"email": "", "nickname": "nickname"})
    assert duplicate_nickname_response.status_code == 401
    duplicate_nickname_response = client.post('/api/taxi_auth/register', json={"email": "abs@unist.ac.kr", "nickname": ""})
    assert duplicate_nickname_response.status_code == 401

    # 사용자 db에 저장
    create_user(db, email, "existingnickname")

    # 닉네임 중복 테스트
    duplicate_nickname_response = client.post('/api/taxi_auth/register', json={"email": "1", "nickname": "existingnickname"})
    assert duplicate_nickname_response.status_code == 401
    # 이메일 중복 테스트
    duplicate_email_response = client.post('/api/taxi_auth/register', json={"email": email, "nickname": "anothernickname"})
    assert duplicate_email_response.status_code == 401

    # 새로운 사용자 등록
    valid_response = client.post('/api/taxi_auth/register', json={"email": "rzbsys@unist.ac.kr", "nickname": nickname})
    assert valid_response.status_code == 200
    # 로그인 되는 지 확인
    with client.session_transaction() as session:
        assert session.get('is_authenticated') == 'True'
        assert session.get('email') == "rzbsys@unist.ac.kr"

    

# Test 5: 로그아웃
def test_logout(client):
    # 세션을 설정한 후 로그아웃
    with client.session_transaction() as session:
        session['is_authenticated'] = "True"

    logout_response = client.get('/api/taxi_hexa/logout')
    assert logout_response.status_code == 200
    with client.session_transaction() as session:
        assert session.get('is_authenticated') is None
