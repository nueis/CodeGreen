from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # 세션 관리를 위한 키 설정
HTML_FOLDER = os.path.join(os.getcwd(), 'templates')  # templates 폴더 내에 HTML 파일을 저장

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

# 화면 배치를 테스트 하기 위한 샘플 데이터
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
reviews_data = {}

user_purchases = {
    "user1": [1,2], # user1 purchased products with ID 1,2 
}

products[0] = {
    "product_id": 1,
    "name": "Product A",
    "price": 20000,
    "image_url": "/static/images/bunny.png",
    "reviews": [],
    "rating": 0,
    "seller_nickname": "Ewha",
    "status":"new",
    "description":"a new bunny keyring"
}

products[1] = {
    "product_id": 2,
    "name": "Product B",
    "price": 10000,
    "image_url": "/static/images/badge.png",
    "reviews": [],
    "rating": 0,
    "seller_nickname": "Choi",
    "status":"new",
    "description":"a new badge",
}
products[2] = {
    "product_id": 3,
    "name": "Product C",
    "price": 20000,
    "image_url": "/static/images/bunny.png",
    "reviews": [],
    "rating": 0,
    "seller_nickname": "Ewha",
    "status":"new",
    "description":"a new bunny keyring"
}

products[3] = {
    "product_id": 4,
    "name": "Product D",
    "price": 10000,
    "image_url": "/static/images/badge.png",
    "reviews": [],
    "rating": 0,
    "seller_nickname": "Choi",
    "status":"new",
    "description":"a new badge",
}

products[4] = {
    "product_id": 5,
    "name": "Product name",
    "price": 10000,
    "image_url": "/static/images/badge.png",
    "reviews": [],
    "rating": 0,
    "seller_nickname": "seller nickname",
    "status":"status: new",
    "description":"description:a new badge",
}

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
        nickname = request.form.get("nickname")
        email = request.form.get("email")
        phone = request.form.get("phone")
        role = request.form.get("role")

        # 사용자 정보를 딕셔너리에 저장
        users[email] = {
            "id": id,
            "password": password,
            "nickname": nickname,
            "email": email,
            "phone": phone,
            "role": role
        }

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

@app.route("/products")
def product_list():
    if session['role'] == 'seller':
        return render_template("productListSeller.html", logged_in=('id' in session), user=session.get('nickname'))
    return render_template("productListBuyer.html", logged_in=('id' in session), user=session.get('nickname'))

@app.route("/register", methods = ['GET', 'POST'])
def product_list_new():
    products_per_page = 4
    page = request.args.get('page', 1, type=int)

    product_list = list(products.values())
    start = (page - 1) * products_per_page
    end = start + products_per_page
    paginated_products = product_list[start:end]

    total_pages = (len(product_list) + products_per_page - 1) // products_per_page 

    return render_template("productList.html", products=paginated_products, page=page, total_pages=total_pages)

@app.route("/products/register", methods = ["GET", "POST"])
def register_item():
    if request.method == "POST":

        if session['role'] == 'buyer':
            return redirect(url_for("home"))

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

@app.route("/products/<int:product_id>")
def product_detail(product_id):
    product = products.get(product_id)
    if product:
        if session['role'] == 'seller':
            return render_template("productDetailSeller.html", product = product, logged_in=('id' in session), user=session.get('nickname'))
        else:
            return render_template("productDetailBuyer.html", product=product, logged_in=('id' in session), user=session.get('nickname'))
    return "상품을 찾을 수 없습니다.", 404

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
    session.pop('id', None)
    session.pop('nickname', None)
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

@app.route('/reviews')
def review_list():

    # Sample data for testing layout
    reviews = [
        {"image_url": "../static/images/product.png", "title": "Great Product!", "nickname": "User1", "rating": 4.5},
        {"image_url": "../static/images/product.png", "title": "Very useful", "nickname": "User2", "rating": 4.0},
        {"image_url": "../static/images/product.png", "title": "Highly recommend", "nickname": "User3", "rating": 5.0},
        {"image_url": "../static/images/product.png", "title": "Decent quality", "nickname": "User4", "rating": 3.5},
        {"image_url": "../static/images/product.png", "title": "Worth the price", "nickname": "User5", "rating": 4.2},
        {"image_url": "../static/images/product.png", "title": "Love it!", "nickname": "User6", "rating": 4.8},
        {"image_url": "../static/images/product.png", "title": "Met expectations", "nickname": "User7", "rating": 4.0},
        {"image_url": "../static/images/product.png", "title": "Good value", "nickname": "User8", "rating": 4.3},
        {"image_url": "../static/images/product.png", "title": "Love it!", "nickname": "User6", "rating": 4.8},
        {"image_url": "../static/images/product.png", "title": "Met expectations", "nickname": "User7", "rating": 4.0},
        {"image_url": "../static/images/product.png", "title": "Good value", "nickname": "User8", "rating": 4.3},
    ]
     # Pagination settings
    reviews_per_page = 8
    page = request.args.get('page', 1, type=int)

    start = (page - 1) * reviews_per_page
    end = start + reviews_per_page

    paginated_reviews = reviews[start:end]

    total_pages = (len(reviews) + reviews_per_page - 1) // reviews_per_page 

    return render_template("reviewList.html", reviews=paginated_reviews, page=page, total_pages=total_pages)

@app.route('/myreviews')
def myreview_list():
     # Sample data for testing layout
    reviews = [
        {"image_url": "../static/images/product.png", "title": "Great Product!", "nickname": "User1", "rating": 4.5},
        {"image_url": "../static/images/product.png", "title": "Very useful", "nickname": "User1", "rating": 4.0},
        {"image_url": "../static/images/product.png", "title": "Highly recommend", "nickname": "User1", "rating": 5.0},
    ]
     # Pagination settings
    reviews_per_page = 8
    page = request.args.get('page', 1, type=int)

    start = (page - 1) * reviews_per_page
    end = start + reviews_per_page

    paginated_reviews = reviews[start:end]

    total_pages = (len(reviews) + reviews_per_page - 1) // reviews_per_page 

    return render_template("myreviewList.html", reviews=paginated_reviews, page=page, total_pages=total_pages)

@app.route('/reviews/register', methods = ['GET', 'POST'])
def register_review():

    user_id="user1"

    if request.method == "POST":

        user_nickname = request.form.get("user_nickname")
        product_id = request.form.get("product_id", type=int)
        review_title = request.form.get("review_title")
        review_content = request.form.get("review_content")
        rating = request.form.get("rating", type=int) 

        # 이미지 파일 처리
        image = request.files['image']
        image_filename = f"{len(products) + 1}_{image.filename}"
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        # 리뷰 딕셔너리에 추가
        review_id = len(reviews_data) + 1
        new_review = {
            "review_id": review_id,
            "product_id": product_id,
            "user_id": user_id,
            "user_nickname": user_nickname ,
            "review_title": review_title,
            "review_content": review_content, 
            "rating": rating,
            "image": image_filename        
        }
        reviews_data[review_id] = new_review

        # 상품 딕셔너리에 추가 
        products[product_id]["reviews"].append(review_id)

        product_reviews = [review["rating"] for review in reviews_data.values() if review["product_id"] == product_id]
        valid_ratings = [r for r in product_reviews if r is not None]
        products[product_id]["rating"] = sum(valid_ratings) / len(valid_ratings) if valid_ratings else 0

        return redirect(url_for("review_detail", review_id=review_id))

    # Get list of purchased products for the user
    purchased_product_ids = user_purchases.get(user_id, [])
    purchased_products = [products[pid] for pid in purchased_product_ids]

    return render_template("reviewRegister.html", products=purchased_products)

@app.route('/reviews/<int:review_id>')
def review_detail(review_id):
    review = reviews_data[review_id]
    if review:
        product = products.get(review["product_id"])
        if product:
            return render_template("reviewDetail.html", review=review, product=product)
        return "제품을 찾을 수 없습니다.", 404
    return "리뷰를 찾을 수 없습니다.", 404

@app.route('/html/<filename>')
def open_html_file(filename):
    # 주어진 HTML 파일을 templates 폴더에서 찾음
    try:
        return send_from_directory(HTML_FOLDER, filename)
    except FileNotFoundError:
        return "파일을 찾을 수 없습니다.", 404

if __name__ == "__main__":
    app.run(debug=True)