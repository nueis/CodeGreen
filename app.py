from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # 세션 관리를 위한 키 설정

# 업로드할 파일의 저장 경로 설정
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 업로드 폴더 생성
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

products = {}
users = {
    "testuser@example.com": {
        "user_id": "testuser",
        "password": "password",
        "nickname": "test_nickname"
    }
}

@app.route("/index")
def index():
    return render_template("index.html", logged_in=('user_id' in session), user=session.get('nickname'))

@app.route("/")
def home():
    return render_template("homeBuyer.html", logged_in=('user_id' in session), user=session.get('nickname'))

@app.route("/signUp", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        user_id = request.form.get("user-id")
        password = request.form.get("password")
        nickname = request.form.get("nickname")
        email = request.form.get("email")

        # 사용자 정보를 딕셔너리에 저장
        users[email] = {
            "user_id": user_id,
            "password": password,
            "nickname": nickname
        }

        # 회원가입 후 세션에 저장하여 자동 로그인 처리
        session['user_id'] = user_id
        session['nickname'] = nickname

        return redirect(url_for("home"))

    return render_template('signUp.html', logged_in=False)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form.get("user-id")
        password = request.form.get("password")

        # 로그인 유효성 검사
        for user in users.values():
            if user["user_id"] == user_id and user["password"] == password:
                session['user_id'] = user_id
                session['nickname'] = user['nickname']
                return redirect(url_for("home"))

        return render_template("login.html", error="아이디 또는 비밀번호가 잘못되었습니다.", logged_in=False)
    return render_template("login.html", logged_in=False)

@app.route("/findId", methods=["GET", "POST"])
def find_id():
    if request.method == "POST":
        email = request.form.get("email")

        # 이메일로 아이디 찾기
        if email in users:
            user_id = users[email]["user_id"]
            return render_template("findId.html", user_id=user_id, found=True, logged_in=False)
        else:
            return render_template("findId.html", error="해당 이메일로 가입된 아이디가 없습니다.", logged_in=False)

    return render_template("findId.html", logged_in=False)

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('nickname', None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)