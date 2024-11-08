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
    return render_template("productDetail.html", product=product)
    # return render_template("homeSeller.html")

@app.route("/mypage")
def view_review():
    return render_template("mypageBuy.html")

@app.route("/productList")
def product_list():
    return render_template("productList.html")

@app.route("/register", methods = ["GET", "POST"])
def register_item():
    if request.method == "POST":

        name = request.form.get("name")
        seller = request.form.get("seller")
        addr = request.form.get("addr")
        category = request.form.get("category")
        status = request.form.get("status")
        price = request.form.get("price", type=float)
        stock = request.form.get("stock", type=int)

        # 이미지 파일 처리
        image = request.files['image']
        image_filename = f"{len(products) + 1}_{image.filename}"
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        # 상품 딕셔너리에 추가
        product_id = len(products) + 1
        products[product_id] = {
            "name": name,
            "description": "상품 설명을 여기에 입력하세요",
            "price": price,
            "seller_nickname": seller,
            "category": category,
            "location": addr,
            "status": status,
            "stock": stock,
            "image": image_filename,  # 이미지 파일 이름 저장
            "reviews": [],
            "rating": 0,
        }

        return redirect(url_for("product_detail", product_id=product_id))

    return render_template("register.html")

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = products.get(product_id)
    if product:
        return render_template("productDetail.html", product=product)
    return "상품을 찾을 수 없습니다.", 404

@app.route('/productTest/<int:product_id>')
def product_detail_Test(product_id):
    product = {
        'name': '토끼 키링',
        'seller': '이화연',
        'is_green': True,
        'category': '이화 굿즈',
        'price': '5,000원',
        'short_intro': '토끼 키링',
        'region': '서울 서대문구 이화여대길',
        'status': '새 제품 - 최상',
        'stock': 3,
        'description': '수제 토끼 키링입니다',
        'reviews': [
            {'nickname': 'user1', 'rating': 4, 'content': '귀여워요'},
            {'nickname': 'user2', 'rating': 5, 'content': '마음에 들어요!'}
        ]
    }
    return render_template('product_detail.html', product=product)


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

@app.route('/review')
def reviews():
    reviews_data = [
        {"title": "리뷰 제목", "author": "작성자 닉네임", "date": "작성 날짜"},
        {"title": "리뷰 제목", "author": "작성자 닉네임", "date": "작성 날짜"},
        {"title": "리뷰 제목", "author": "작성자 닉네임", "date": "작성 날짜"},
    ]
    return render_template('productreviews.html', reviews=reviews_data)

if __name__ == "__main__":
    app.run(debug=True)