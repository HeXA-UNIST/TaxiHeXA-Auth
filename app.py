from flask import Flask, json, request, g, session

from src.middleware.cors import cors
from src.middleware.mail import mail
from src.database.database import init_db
import src.database.controller as controller
import src.utils as utils

from config import config


def init_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'scudeto2@gmail.com'  # 본인의 Gmail 주소
    app.config['MAIL_PASSWORD'] = 'tpdk otmu prkj aemt'     # Gmail 앱 비밀번호
    app.config['MAIL_DEFAULT_SENDER'] = 'scudeto2@gmail.com'

    # app에 뭔가 더 추가하고 싶은게 있으면 여기에 추가
    cors.init_app(app)
    mail.init_app(app)

    return app

app = init_app()
engine, get_db = init_db(config.DATABASE_URI)


# 연결이 끊어질때 db close
@app.teardown_appcontext
def teardown_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/api/taxi_auth/status')
def status():
    return json.jsonify({'status': 'ok'})

# 1. 이메일 인증 번호 요청
@app.route('/api/taxi_auth/request_verify', methods=["POST"])
def request_verify():
    db = get_db()
    data = request.get_json()
    email = data.get("email", "")

    if not email:
        return json.jsonify({"msg": "Invalid email format."}), 400
    if email.endswith("unist@ac.kr"):
        return json.jsonify({"msg": "Invalid email format."}), 400
    
    # Generate OTP
    otp_code = utils.create_safe_random_otp_code()
    controller.create_otp(db, email, otp_code)

    # OTP 디버깅 용도로 출력 (실제 프로덕션에서는 제외)
    print(f"Generated OTP for {email}: {otp_code}")
    utils.send_email(mail, email, "Your OTP Code", f"Your OTP code is: {otp_code}. It is valid for 5 minutes.")
    return json.jsonify({"msg": "OTP sent successfully."}), 200

# 2. 이메일 인증 번호 확인
@app.route('/api/taxi_auth/check_verify', methods=["POST"])
def verify_email():
    db = get_db()
    data = request.get_json()
    email = data.get("email", "")
    otp_code = data.get("otp", "")

    if not email or not otp_code:
        return json.jsonify({"msg": "Email and OTP are required."}), 400

    auth = controller.select_otp_by_email(db, email)
    verified, err = utils.verified_otp(otp_code, email, auth)
    if not verified:
        return json.jsonify({"msg" : err}), 400
    else:
        controller.update_otp_is_veritied(db, auth, True)

    user = controller.select_user_by_email(db, email)
    if user.is_banned:
        return {"msg" : "엄"}, 403
    if user:
        utils.enroll_session(session, user)
        
    return json.jsonify({
        "msg":"엄",
        "registered" : True if user else False,
        "nickname" : user.nickname if user else ""
    }), 200

# 3. 닉네임 설정
@app.route('/api/taxi_auth/register', methods=["POST"])
def register_user():
    db = get_db()
    data = request.get_json()
    email = data.get("email", "")
    nickname = data.get("nickname", "")

    if not email or not nickname:
        return {"msg":"닉네임을 정확히 입력해주세요."}, 401

    duplicated_user_by_nickname = controller.select_user_by_nickname(db, nickname)
    if duplicated_user_by_nickname:
        return {"msg" : "중복된 닉네임입니다."}, 401

    duplicated_user_by_email = controller.select_user_by_email(db, email)
    if duplicated_user_by_email:
        return {"msg" : "중복된 이메일입니다."}, 401
    
    user = controller.create_user(db, email, nickname)
    utils.enroll_session(session, user)

    return json.jsonify({"msg": "User registered successfully."}), 200

@app.route("/api/taxi_hexa/logout")
def logout():
    session.clear()
    return {"msg":"done"}, 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=13242)