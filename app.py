from flask import Flask, render_template, request, flash, redirect, url_for, session
from database import DBhandler
import os
import hashlib
import sys

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # 세션 관리를 위한 키 설정

DB = DBhandler()

@app.before_request
def set_default_session_values():
    # 세션에 'role' 키가 없을 경우 기본값을 'buyer'로 설정
    if 'role' not in session:
        session['role'] = 'buyer'

# 업로드할 파일의 저장 경로 설정
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

@app.route("/index")
def index():
    return render_template("indexBuyer.html", logged_in=('id' in session), user=session.get('nickname'))

@app.route("/", methods=['GET', 'POST'])
def home():
    if session['role'] == 'seller':
        return render_template("homeSeller.html", logged_in=('id' in session), user=session.get('nickname'))

    return render_template("homeBuyer.html", logged_in=('id' in session), user=session.get('nickname'))

@app.route("/signUp", methods=['GET', 'POST'])
def sign_up():
    if request.method == "POST":
        id = request.form.get("id")
        password = request.form.get("password")
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        nickname = request.form.get("nickname")
        email = request.form.get("email")
        phone = request.form.get("phone")
        role = request.form.get("role")

        if DB.insert_user(id, password_hash, nickname, email, phone, role):
            return render_template("login.html")
        else:
            flash("user id already exists!")
            return render_template("signUp.html")

        # 사용자 정보를 딕셔너리에 저장
        # users[email] = {
        #     "id": id,
        #     "password": password,
        #     "nickname": nickname,
        #     "email": email,
        #     "phone": phone,
        #     "role": role
        # }
        #
        # if not DB.check_user_exists(email):
        #     users[email] = {
        #         "id": id,
        #         "password": password,
        #         "nickname": nickname,
        #         "email": email,
        #         "phone": phone,
        #         "role": role
        #     }
        #     DB.insert_user(id, email, password, nickname, phone, role)
        #     session['id'] = id
        #     return redirect(url_for("home"))
        # return render_template("signUp.html", error="이메일이 이미 등록되어 있습니다.")

        # 회원가입 후 세션에 저장하여 자동 로그인 처리
        session['id'] = id
        session['nickname'] = nickname
        session['role'] = role

        return redirect(url_for("home", logged_in=('id' in session), user=session.get('nickname')))

    return render_template('signUp.html', logged_in=False)

@app.route("/productDetail")
def view_produceDetail():
    # 예시로 product 정보를 설정했습니다.
    product = {
        'image': 'product_detail_image.png',
        'seller_nickname': '이화인',
        'category': '생활 용품',
        'name': '물병',
        'price': 15000,
        'location': '서울특별시',
        'status': '새상품',
        'rating': 4.5,
        'stock': 10,
        'description': '이 물병은 매우 튼튼하고 가벼워요!',
        'reviews': ['좋아요!', '배송 빠르고 상품 좋아요.', '생각보다 크네요.']
    }

    if session['role'] == 'seller':
        return render_template("productDetailSeller.html", product = product, logged_in=('id' in session), user=session.get('nickname'))

    return render_template("productDetailBuyer.html", product=product, logged_in=('id' in session), user=session.get('nickname'))

@app.route("/mypage")
def view_review():
    if session['role'] == 'seller':
        return render_template("mypageSell.html")
    elif session['role'] == 'buyer':
        return render_template("mypageBuy.html")
    else:
        return redirect(url_for("login"))

@app.route("/productList")
def product_list():
    if session['role'] == 'seller':
        return render_template("productListSeller.html", logged_in=('id' in session), user=session.get('nickname'))
    return render_template("productListBuyer.html", logged_in=('id' in session), user=session.get('nickname'))

# @app.route("/register", methods = ['GET', 'POST'])
# def register_item():
#     if request.method == "POST":
#
#         if session['role'] == 'buyer':
#             return redirect(url_for("home"))
#
#         name = request.form.get("name")
#         seller = request.form.get("seller")
#         addr = request.form.get("addr")
#         category = request.form.get("category")
#         status = request.form.get("status")
#         price = request.form.get("price", type=float)
#         stock = request.form.get("stock", type=int)
#
#         # 이미지 파일 처리
#         image = request.files['image']
#         image_filename = f"{len(products) + 1}_{image.filename}"
#         image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
#
#         # 상품 딕셔너리에 추가
#         product_id = len(products) + 1
#         products[product_id] = {
#             "name": name,
#             "description": "상품 설명을 여기에 입력하세요",
#             "price": price,
#             "seller_nickname": seller,
#             "category": category,
#             "location": addr,
#             "status": status,
#             "stock": stock,
#             "image": image_filename,  # 이미지 파일 이름 저장
#             "reviews": [],
#             "rating": 0,
#         }
#
#         image_file = request.files['image']
#         image_file.save("static/imag/{}.".format(image_file.filename))
#         data = request.form
#         DB.insert_item(data['name'], data['price'], data['location'], data['status'], data['rating'], data['stock'], data['reviews'])
#
#         # return redirect(url_for("product_detail", product_id=product_id))
#
#     return render_template("register.html")

@app.route("/test")
def testAssignment():
    return render_template("register.html")

# 상품 등록 시 새로운 product_id 생성 (정수)
product_id = len(DB.db.child("items").get().val() or {}) + 1

@app.route("/testtest", methods=['GET', 'POST'])
def register_item():
    if request.method == "POST":
        name = request.form.get("name")
        seller = request.form.get("seller")
        addr = request.form.get("addr")
        category = request.form.get("category")
        status = request.form.get("status")
        price = request.form.get("price", type=float)
        stock = request.form.get("stock", type=int)

        # 이미지 처리
        image = request.files['image']
        image_filename = f"{name}_{image.filename}"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image.save(image_path)

        # Firebase 저장 데이터 준비
        data = {
            "seller": seller,
            "addr": addr,
            "category": category,
            "status": status,
            "price": price,
            "stock": stock,
        }

        # DB에 저장 (product_id 사용)
        DB.insert_item(str(product_id), data, image_path)

        # 정수 product_id로 이동
        return redirect(url_for("product_detail", product_id=product_id))

    return render_template("register.html")

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    return render_template("homeSeller.html")

# @app.route("/product/<int:product_id>")
# def product_detail(product_id):
#     product = products.get(product_id)
#     if product:
#         if session['role'] == 'seller':
#             return render_template("productDetailSeller.html", product = product, logged_in=('id' in session), user=session.get('nickname'))
#         else:
#             return render_template("productDetailBuyer.html", product=product, logged_in=('id' in session), user=session.get('nickname'))
#     return "상품을 찾을 수 없습니다.", 404

@app.route("/login", methods=['Get', 'POST'])
def login():
    if request.method == "POST":
        id = request.form.get("user-id")
        password = request.form.get("password")

        # 로그인 유효성 검사
        for user in users.values():
            if user["id"] == id and user["password"] == password:
                session['id'] = id
                session['nickname'] = user['nickname']
                return redirect(url_for("home"))

        return render_template("login.html", error="아이디 또는 비밀번호가 잘못되었습니다.", logged_in=False)

    return render_template("login.html", logged_in=False)

@app.route("/findId", methods=['GET', 'POST'])
def find_id():
    if request.method == "POST":
        email = request.form.get("email")

        # 이메일로 아이디 찾기
        if email in users:
            user_id = users[email]["id"]
            return render_template("findId.html", user_id=user_id, found=True, logged_in=False)
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