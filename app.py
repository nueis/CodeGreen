import logging
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify, g
from database import DBhandler
from storage import SThandler
from datetime import datetime, timedelta
import os
import hashlib
import jwt

app = Flask(__name__, static_folder='static')
DB = DBhandler()
ST = SThandler()

# 세션 관리를 위한 키 설정
SECRET_KEY = 'super_secret_key'

# 업로드할 파일의 저장 경로 설정
UPLOAD_FOLDER = os.path.join('static', 'uploads')

# JWT 검증 제외 경로 리스트
EXCLUDED_ENDPOINTS = [
    'page_signup', 'service_siginup',
    'page_login', 'service_login',
    'page_findid',
    'default'
]

# 모든 요청 전에 실행되는 로직
@app.before_request
def check_jwt_token():
    # 정적 파일 및 favicon 요청 예외 처리
    if request.path.startswith('/static') or request.path == '/favicon.ico':
        return

    """제외 경로 리스트 외 모든 요청에 대해 JWT 검증"""
    if request.endpoint in EXCLUDED_ENDPOINTS or request.endpoint is None:
        return

    # Authorization 헤더에서 토큰 추출
    bearerToken = request.headers.get('Authorization')
    if bearerToken is None:
        g.user = None
        return jsonify({"message": "Missing Authorization Header"}), 401

    # Bearer 토큰 형식 확인
    if not bearerToken.startswith("Bearer "):
        return jsonify({"message": "Invalid Token Format"}), 401

    # Bearer 뒷 부분의 토큰만 추출
    token = bearerToken.split(" ")[1]

    try: # 토큰 디코딩
        decoded_user = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        # DB에 사용자 존재 여부 확인
        user = DB.find_user(decoded_user.get("id"))
        if not user: # 존재하지 않는 사용자
            return jsonify({"message": "User not found"}), 401

        # g.user에 사용자 정보 저장
        g.user = {
            "id": user["id"],  # 사용자 ID
            "nickname": user["nickname"],  # 사용자 닉네임
            "role": user["role"]  # 사용자 역할
        }

    except jwt.ExpiredSignatureError: # 만료된 토큰
        g.user = None
        return jsonify({"message": "Expired Token"}), 401

    except jwt.InvalidTokenError: # 유효하지 않은 토큰
        g.user = None
        return jsonify({"message": "Invalid Token"}), 401

@app.route('/')
def default():
    return render_template("homeBuyer.html", loggedIn=False)

# 아이디 찾기 페이지
@app.route("/page/findid")
def page_findid():
    return render_template("findId.html")

# 회원가입 페이지
@app.route("/page/signup")
def page_signup():
    return render_template("signUp.html")

# 회원가입 처리
@app.route("/service/signup", methods=['POST'])
def service_signup():
    # 폼 데이터 가져오기
    id = request.form.get("id")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm-password")
    nickname = request.form.get("nickname")
    email = f"{request.form.get('email')}@{request.form.get('domain')}"
    if request.form.get("domain") == "custom":
        email = f"{request.form.get('email')}@{request.form.get('custom-domain')}"
    phone = f"{request.form.get('phone1')}-{request.form.get('phone2')}-{request.form.get('phone3')}" if all(
        [request.form.get('phone1'), request.form.get('phone2'), request.form.get('phone3')]) else None
    role = request.form.get("role")

    # 비밀번호 확인
    if password != confirm_password:
        return jsonify({"message": "비밀번호가 일치하지 않습니다."}), 400

    # 사용자 중복 확인
    if DB.check_user_exists(id):
        return jsonify({"message": "이미 존재하는 아이디입니다."}), 400
    if DB.check_email_exists(email):
        return jsonify({"message": "이미 존재하는 이메일입니다."}), 400
    if DB.check_nickname_exists(nickname):
        return jsonify({"message": "이미 존재하는 닉네임입니다."}), 400

    # 비밀번호 해시 생성
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    # 프로필 사진 처리 (옵션)
    profile_pic_path = None
    if 'profile-pic' in request.files:
        file = request.files['profile-pic']
        if file.filename != '':  # 파일명이 비어 있지 않으면
            profile_pic_url = ST.upload_file_to_firebase(file)  # Firebase Storage에 업로드하고 URL 반환

    # 사용자 데이터 삽입
    success = DB.insert_user(id, password_hash, nickname, email, phone, role, profile_pic_url)
    if success:
        return jsonify({"message": "회원가입이 성공적으로 완료되었습니다."}), 201
    else:
        return jsonify({"message": "회원가입 중 문제가 발생했습니다. 다시 시도해주세요."}), 500

# 로그인 페이지
@app.route("/page/login")
def page_login():
    return render_template("login.html")

# 로그인 처리
@app.route("/service/login", methods=['POST'])
def service_login():
    id = request.form['id']
    pw = request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

    user = DB.find_user(id, pw_hash)

    if user: # 기가입 유저
        # JWT 토큰 생성
        payload = {
            "id": user["id"],  # 사용자 ID
            "role": user["role"],  # 사용자 역할
            "exp": datetime.utcnow() + timedelta(hours=1)  # 만료 시간 설정 (1시간)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        if user["role"] == "seller":
            # JWT 토큰을 클라이언트에 반환하고, 사용자 정보를 HTML 템플릿에 전달
            return render_template("homeSeller.html", user=user['nickname'], token=token, loggedIn=True)
        else:
            # JWT 토큰을 클라이언트에 반환하고, 사용자 정보를 HTML 템플릿에 전달
            return render_template("homeBuyer.html", user=user['nickname'], token=token, loggedIn=True)

    else:
        flash("잘못된 ID or PW")
        return render_template("login.html")

# 업로드 폴더 생성
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

products = {}
users = {}
# users = {
#     "testuser@example.com": {
#         "id": "test",
#         "password": "test",
#         "nickname": "test",
#         "role": "seller",
#         "email": "test@test.com",
#         "phone": "1234567890"
#     }
# }

# @app.route("/index")
# def index():
#     return render_template("indexSeller.html", logged_in=('id' in session), user=session.get('nickname'))

# @app.route("/", methods=['GET', 'POST'])
# def home():
#     if 'id' in session:
#         if session['role'] == 'seller':
#             return render_template("homeSeller.html", logged_in=True, user=session.get('nickname'))
#         return render_template("homeBuyer.html", logged_in=True, user=session.get('nickname'))
#     return redirect(url_for("login_user"))  # 로그인하지 않은 경우 로그인 화면으로 리다이렉트

# 상품 상세 페이지
@app.route("/view_detail/<product_name>/")
def product_detail(product_name):
    try:
        logging.debug(f"Requested product name: {product_name}")
        all_products = DB.get_items()  # 리스트 반환
        logging.debug(f"All products: {all_products}")

        # 리스트에서 이름으로 상품 검색
        product = next((item for item in all_products if item and item.get("name") == product_name), None)

        if not product:
            logging.error(f"Product with name '{product_name}' not found.")
            return f"Product '{product_name}' not found", 404

        return render_template(
            "productDetailBuyer.html",
            product=product,
            logged_in=('id' in session),
            user=session.get('nickname')
        )
    except Exception as e:
        logging.error(f"Error retrieving product details: {e}")
        return f"An unexpected error occurred: {str(e)}", 500


@app.route("/mypage")
def view_review():
    if session['role'] == 'seller':
        return render_template("mypageSell.html")
    elif session['role'] == 'buyer':
        return render_template("mypageBuy.html")
    else:
        return redirect(url_for("login"))

@app.route("/browse", methods=["GET"])
def browse():
    try:
        # Firebase에서 데이터 가져오기
        all_products = DB.get_items()  # Firebase에서 전체 상품 리스트 반환
        logging.debug(f"DEBUG: All Products from Firebase: {all_products}")

        # 유효한 데이터만 필터링
        if isinstance(all_products, list):
            valid_products = [product for product in all_products if product is not None]
        else:
            valid_products = []

        # `green_view` 처리 (URL 파라미터 기반)
        green_view = request.args.get('green_view', default="false").lower() == "true"

        if green_view:
            # green_view=True인 경우, 이화그린 상품만 필터링
            valid_products = [product for product in valid_products if product.get("ewha_green", False)]

        # 페이지네이션 처리
        page = request.args.get('page', default=1, type=int)
        items_per_page = 4
        total_products = len(valid_products)
        total_pages = (total_products + items_per_page - 1) // items_per_page

        if page < 1:
            page = 1
        elif page > total_pages:
            page = total_pages

        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        products = valid_products[start_idx:end_idx]

        # 기본 이미지 경로 설정
        for product in products:
            product["img_path"] = product.get("img_path", "default.jpg")

        # 템플릿 렌더링
        return render_template(
            "browseBuyer.html",
            products=products,
            page=page,
            total_pages=total_pages,
            green_view=green_view,
            logged_in=('id' in session),
            user=session.get('nickname')
        )
    except Exception as e:
        logging.error(f"Error loading products: {e}")
        return f"Error loading products: {e}", 500




# 상품 등록
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # 상품 등록 데이터 수집
        name = request.form.get("name")
        price = float(request.form.get("price").replace('₩', '').replace(',', ''))
        category = request.form.get("category")
        description_short = request.form.get("description_short")
        description_long = request.form.get("description_long")

        # 이미지 처리
        image = request.files['file']
        image_filename = f"{name}_{image.filename}"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image.save(image_path)

        # Firebase에 저장할 데이터 구성
        product_data = {
            "name": name,
            "price": price,
            "category": category,
            "description_short": description_short,
            "description_long": description_long,
            "img_path": image_filename
        }

        # Firebase에 데이터 저장
        product_id = str(len(DB.get_items()) + 1)
        if DB.insert_item(product_id, product_data):
            return redirect(url_for("browse"))
        return render_template("error.html", message="상품 등록에 실패했습니다.")

    return render_template("register.html")

@app.route("/findId", methods=['GET', 'POST'])
def find_id():
    if request.method == "POST":
        email = request.form.get("email")

        # 이메일로 아이디 찾기
        if email in users:
            id = users[email]["id"]
            return render_template("findId.html", id=id, found=True, logged_in=False)
        else:
            return render_template("findId.html", error="가입되지 않은 회원입니다.", logged_in=False)

    return render_template("findId.html", logged_in=False)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route('/review')
def reviews():
    reviews_data = [
        {"title": "리뷰 제목", "author": "작성자 닉네임", "date": "작성 날짜"},
        {"title": "리뷰 제목", "author": "작성자 닉네임", "date": "작성 날짜"},
        {"title": "리뷰 제목", "author": "작성자 닉네임", "date": "작성 날짜"},
    ]

    if session['role'] == 'seller':
        return render_template("productreviewsSeller.html", reviews=reviews_data, logged_in=('id' in session), user=session.get('nickname'))

    return render_template('productreviewsBuyer.html', reviews=reviews_data)

if __name__ == "__main__":
    app.run(debug=True)