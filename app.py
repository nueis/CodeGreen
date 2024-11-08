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

@app.route("/index")
def index():
    return render_template("index.html", logged_in=('user_id' in session), user=session.get('nickname'))

@app.route("/")
def home():
    return render_template("homeBuyer.html", logged_in=('user_id' in session), user=session.get('nickname'))

@app.route("/home/buyer")
def home_buyer():
    return render_template("homeBuyer.html", logged_in=('user_id' in session), user=session.get('nickname'))

@app.route("/home/seller")
def home_seller():
    return render_template("homeSeller.html", logged_in=('user_id' in session), user=session.get('nickname'))

@app.route("/productDetail")
def view_product_detail():
    product = {
        'seller_nickname': '이화인',
        'category': '생활 용품',
        'name': '물병',
        'price': 15000,
        'image': 'product_detail_image.png',
        'location': '서울특별시',
        'status': '새상품',
        'rating': 4.5,
        'stock': 10,
        'description': '이 물병은 매우 튼튼하고 가벼워요!',
        'reviews': ['좋아요!', '배송 빠르고 상품 좋아요.', '생각보다 크네요.']
    }
    return render_template("productDetail.html", product=product, logged_in=('user_id' in session), user=session.get('nickname'))

@app.route("/mypage")
def view_mypage():
    if 'user_id' in session:
        return render_template("mypageBuyer.html", logged_in=True, user=session.get('nickname'))
    return redirect(url_for("login"))

@app.route("/productList")
def product_list():
    return render_template("productList.html", logged_in=('user_id' in session), user=session.get('nickname'))

@app.route("/register", methods=["GET", "POST"])
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
            "image": image_filename,
            "reviews": [],
            "rating": 0,
        }

        return redirect(url_for("product_detail", product_id=product_id))

    return render_template("register.html", logged_in=('user_id' in session), user=session.get('nickname'))

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = products.get(product_id)
    if product:
        return render_template("productDetail.html", product=product, logged_in=('user_id' in session), user=session.get('nickname'))
    return "상품을 찾을 수 없습니다.", 404

@app.route("/signUp", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        user_id = request.form.get("user-id")
        password = request.form.get("password")
        nickname = request.form.get("nickname")

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

        # 여기서는 예시로 간단하게 아이디와 비밀번호를 체크합니다.
        if user_id == "testuser" and password == "password":  # 실제 서비스에서는 데이터베이스와 비교해야 함
            session['user_id'] = user_id
            session['nickname'] = "test_nickname"  # 이 값은 실제 DB에서 가져와야 함
            return redirect(url_for("home"))

        return render_template("login.html", error="아이디 또는 비밀번호가 잘못되었습니다.", logged_in=False)
    return render_template("login.html", logged_in=False)

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('nickname', None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)