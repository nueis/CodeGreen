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

SECRET_KEY = 'super_secret_key'
app.secret_key = SECRET_KEY



# 업로드할 파일의 저장 경로 설정
UPLOAD_FOLDER = os.path.join('static', 'uploads')

# JWT 검증 제외 경로 리스트
EXCLUDED_ENDPOINTS = [
    'page_signup', 'service_siginup',
    'page_login', 'service_login',
    'page_findid', 'service_findid',
    'default'
]

# @app.before_request
# def set_default_session_values():
#     """애플리케이션 시작 시 기본 세션 값 설정"""
#     session['id'] = 'test_user_id'
#     session['nickname'] = 'TestUser'
#     session['role'] = 'buyer'
#     # session['role'] = 'seller'

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
    #########################################################################################################
    ####### 세션 시연용 code####################################################################################
    #########################################################################################################

    # # 세션에 role이 설정되어 있는지 확인
    # role = session.get('role', None)  # 기본값은 None으로 설정
    #
    # if role == 'buyer':
    #     return render_template("homeBuyer.html", loggedIn=True, user=session.get('nickname', 'GUEST'))
    # elif role == 'seller':
    #     return render_template("homeSeller.html", loggedIn=True, user=session.get('nickname', 'GUEST'))
    # else:
    #     # role 값이 없거나 잘못된 경우 기본값으로 GUEST 처리
    #     return render_template("homeBuyer.html", loggedIn=False, user="GUEST")

    #########################################################################################################
    ####### 프로덕선용 code####################################################################################
    #########################################################################################################

    recent_sales = DB.get_recent_items(5)

    if hasattr(g, 'user') and g.user:

        if g.user['role'] == 'seller':
            return render_template(
                "homeSeller.html",
                logged_in=True,
                user=g.user['nickname'],
                recent_sales=recent_sales
            )

        else:
            return render_template(
                "homeBuyer.html",
                logged_in=True,
                user=g.user['nickname'],
                recent_sales=recent_sales
            )
    return render_template(
        "homeBuyer.html",
        logged_in=False,
        user="GUEST",
        recent_sales=recent_sales
    )


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
    profile_pic_url = None  # 기본값 설정
    if 'profile-pic' in request.files:
        file = request.files['profile-pic']
        if file.filename != '':  # 파일명이 비어 있지 않으면
            profile_pic_url = ST.upload_file_to_firebase(file)  # Firebase Storage에 업로드하고 URL 반환

    # 사용자 데이터 삽입
    success = DB.insert_user(id, password_hash, nickname, email, phone, role, profile_pic_url)
    if success:
        return jsonify({"message": "회원가입이 성공적으로 완료되었습니다."}), 201
        # return render_template("lcogin.html")
    else:
        return jsonify({"message": "회원가입 중 문제가 발생했습니다. 다시 시도해주세요."}), 500
        # return render_template("login.html")

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

        # 최근 항목 가져오기
        try:
            recent_items = DB.get_recent_items(count=5)  # DB에서 최근 5개의 항목 가져오기
        except Exception as e:
            print(f"Error fetching recent items: {e}")
            recent_items = []  # 오류 발생 시 빈 리스트 반환

        if user["role"] == "seller":
            # JWT 토큰을 클라이언트에 반환하고, 사용자 정보를 HTML 템플릿에 전달
            return render_template(
                "homeSeller.html",
                user=user['nickname'],
                recent_sales=recent_items,
                token=token,
                loggedIn=True)
        else:
            # JWT 토큰을 클라이언트에 반환하고, 사용자 정보를 HTML 템플릿에 전달
            return render_template(
                "homeBuyer.html",
                user=user['nickname'],
                recent_sales=recent_items,
                token=token,
                loggedIn=True)

    else:
        flash("잘못된 ID or PW")
        return render_template("login.html")

# 아이디 찾기 페이지
@app.route("/page/findid")
def page_findid():
    return render_template("findId.html")

# 아이디 찾기 처리
@app.route("/service/findid", methods=['GET'])
def service_findid():
    email = request.form.get("email")

    # 이메일로 아이디 찾기
    if email in users:
        id = users[email]["id"]
        return render_template("findId.html", id=id, found=True, logged_in=False)
    else:
        return render_template("findId.html", error="가입되지 않은 회원입니다.", logged_in=False)

    return render_template("findId.html", logged_in=False)

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

@app.route("/", methods=['GET', 'POST'])
def home():
    if 'id' in session:
        recent_sales = DB.get_recent_items(5)

        if session['role'] == 'seller':
            return render_template("homeSeller.html", logged_in=True, user=session.get('nickname'), recent_sales=recent_sales)
        return render_template("homeBuyer.html", logged_in=True, user=session.get('nickname'), recent_sales=recent_sales)
    return redirect(url_for("login_user"))  # 로그인하지 않은 경우 로그인 화면으로 리다이렉트

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
        # 템플릿 렌더링: 역할에 따라 다른 템플릿 선택
        if 'id' in session:
            if session['role'] == 'seller':
                return render_template(
                    "productDetailSeller.html",  # 판매자용 템플릿
                    product=product,
                    name=product['name'],
                    logged_in=True,
                    user=session.get('nickname')
                )
            elif session['role'] == 'buyer':
                return render_template(
                    "productDetailBuyer.html",  # 구매자용 템플릿
                    product=product,
                    name=product['name'],
                    logged_in=True,
                    user=session.get('nickname')
                )
        else:
            # 비로그인 사용자는 기본적으로 구매자용 템플릿 사용
            return render_template(
                "productDetailBuyer.html",
                product=product,
                name=product['name'],
                logged_in=False,
                user=None
            )

    except Exception as e:
        logging.error(f"Error retrieving product details: {e}")
        return f"An unexpected error occurred: {str(e)}", 500

# 구매 (주문 생성)
@app.route("/create_order", methods=["POST"])
def create_order():
    if 'id' not in session:
        return redirect(url_for('login_user'))  # 로그인이 안 되어있다면 로그인 페이지로 이동
    
    # 세션에서 구매자 ID와 이메일 가져오기
    buyer_id = session['id']
    buyer_email = session.get('email', 'unknown@example.com')  # 이메일이 없으면 기본값
    
    # 요청에서 상품 ID 가져오기
    product_id = request.form.get('product_id')
    
    # Firebase에서 상품 정보 가져오기
    product = DB.get_item_by_id(product_id)  # Firebase의 상품 데이터 조회
    if not product:
        return "상품 정보를 찾을 수 없습니다.", 404
    
    # 주문 데이터 구성
    order_data = {
        "buyer_id": buyer_id,
        "buyer_email": buyer_email,
        "seller_id": product.get("seller_id"),
        "product_name": product.get("name"),
        "category": product.get("category"),
        "location": product.get("location"),  # 직거래 주소
        "order_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    # Firebase에 데이터 저장
    order_id = f"order_{datetime.now().timestamp()}"  # 유니크한 주문 ID 생성
    if DB.insert_order(order_id, order_data):
        return redirect(url_for("mypage"))
    else:
        return "주문 생성에 실패했습니다.", 500


# 마이 페이지
@app.route("/mypage")
def view_review():
    if session['role'] == 'seller':
        return redirect(url_for('mypage_seller'))
    elif session['role'] == 'buyer':
        return redirect(url_for('mypage_buyer'))
    else:
        return redirect(url_for("login_user"))

@app.route("/mypage/buyer")
def mypage_buyer():
    if 'id' not in session or session.get('role') != 'buyer':
        return redirect(url_for('login_user'))

    buyer_id = session['id']
    orders = DB.get_orders_by_user(buyer_id, role='buyer')  # 구매자 주문 데이터 가져오기
    total_orders = len(orders)  # 총 주문 수 계산

    reviews = DB.get_reviews_by_buyer_id(buyer_id)
    total_reviews = len(reviews)

    return render_template(
        "mypageBuy.html",
        orders=orders,
        total_orders=total_orders,
        total_reviews=total_reviews,
        logged_in=True,
        user=session.get('nickname')
    )

@app.route("/mypage/seller")
def mypage_seller():
    if 'id' not in session or session.get('role') != 'seller':
        return redirect(url_for('login_user'))

    seller_id = session['id']
    orders = DB.get_orders_by_user(seller_id, role="seller")  # 판매자 주문 데이터 가져오기
    total_orders = len(orders)  # 총 주문 수 계산

    reviews = DB.get_reviews_by_seller_id(seller_id)
    total_reviews = len(reviews)

    return render_template(
        "mypageSell.html",
        orders=orders,
        total_orders=total_orders,
        total_reviews=total_reviews,
        logged_in=True,
        user=session.get('nickname')
    )

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

        # 템플릿 렌더링: 역할에 따라 다른 템플릿 선택
        if 'id' in session:
            if session['role'] == 'seller':
                return render_template(
                    "browseSeller.html",
                    products=products,
                    page=page,
                    total_pages=total_pages,
                    green_view=green_view,
                    logged_in=True,
                    user=session.get('nickname')
                )
            elif session['role'] == 'buyer':
                return render_template(
                    "browseBuyer.html",
                    products=products,
                    page=page,
                    total_pages=total_pages,
                    green_view=green_view,
                    logged_in=True,
                    user=session.get('nickname')
                )
        else:
            # 비로그인 사용자 기본 동작
            return render_template(
                "browseBuyer.html",
                products=products,
                page=page,
                total_pages=total_pages,
                green_view=green_view,
                logged_in=False,
                user=None
            )
    except Exception as e:
        logging.error(f"Error loading products: {e}")
        return f"Error loading products: {e}", 500


@app.route('/your_route')
def your_view_function():
    items = DB.get_items()  # DB에서 아이템 가져오기
    print(items)  # 콘솔에 출력
    return render_template('your_template.html', items=items)



@app.route("/register", methods=["GET", "POST"])
def register():
    # 로그인 여부 확인
    if 'id' not in session:
        flash("상품 등록은 로그인한 사용자만 이용할 수 있습니다.")
        return redirect(url_for("login_user"))
    
    if request.method == "POST":
        # 현재 로그인 한 사용자 ID 가져오기
        seller_id = session.get("id")

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
# <<<<<<< HEAD
#             "img_path": image_filename
# =======
#             "category": category,
#             "ewha_green": ewha_green,
#             "img_path": image_filename,
#             "seller_id": seller_id
# >>>>>>> develop/team
        }

        # Firebase에 데이터 저장
        product_id = str(len(DB.get_items()) + 1)
        if DB.insert_item(product_id, product_data):
            return redirect(url_for("browse"))
        return render_template("error.html", message="상품 등록에 실패했습니다.")

    # GET 요청 시, 로그인 정보와 함께 렌더링
    return render_template(
        "register.html", 
        logged_in=('id' in session), 
        user=session.get('nickname')
    )


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

@app.route('/reviews', methods=['GET'])
def review_list():
    try:
        # Fetch and validate reviews
        reviews = DB.get_reviews()
        if isinstance(reviews, dict):
            reviews = list(reviews.values()) 
        valid_reviews = [review for review in reviews if review is not None]

        # Pagination logic
        page = request.args.get('page', default=1, type=int)
        reviews_per_page = 8
        total_reviews = len(valid_reviews)
        total_pages = (total_reviews + reviews_per_page - 1) // reviews_per_page

        if page < 1:
            page = 1
        elif page > total_pages:
            page = total_pages

        start_idx = (page - 1) * reviews_per_page
        end_idx = start_idx + reviews_per_page
        paginated_reviews = valid_reviews[start_idx:end_idx]

        # Default handling for missing fields
        for review in paginated_reviews:
            review["img_path"] = review.get("img_path", "default.jpg")

        return render_template(
            "reviewList.html",
            reviews=paginated_reviews,
            page=page,
            total_pages=total_pages,
            logged_in=('id' in session),
            user=session.get('nickname')
        )
    except Exception as e:
        logging.error(f"Error loading reviews: {e}")
        return f"Error loading reviews: {str(e)}", 500

@app.route('/myreviews')
def myreview_list():
    try:
        reviews = DB.get_review_by_nickname(session.get('nickname'))
        if reviews is None:
            reviews = []
        elif isinstance(reviews, dict):
            reviews = list(reviews.values()) 
        valid_reviews = [review for review in reviews if review is not None]
        
        # Pagination settings
        page = request.args.get('page', default=1, type=int)
        reviews_per_page = 8
        total_reviews = len(valid_reviews)
        total_pages = (total_reviews + reviews_per_page - 1) // reviews_per_page

        if page < 1:
            page = 1
        elif page > total_pages:
            page = total_pages

        start_idx = (page - 1) * reviews_per_page
        end_idx = start_idx + reviews_per_page
        paginated_reviews = valid_reviews[start_idx:end_idx]

        # Default handling for missing fields
        for review in paginated_reviews:
            review["img_path"] = review.get("img_path", "default.jpg")

        return render_template(
            "myreviewList.html",
            reviews=paginated_reviews,
            page=page,
            total_pages=total_pages,
            logged_in=('id' in session),
            user=session.get('nickname')
        )
    except Exception as e:
        logging.error(f"Error loading reviews: {e}")
        return f"Error loading reviews: {str(e)}", 500

@app.route("/reviews/register/<name>/")
def register_review_init(name):
    user_id = session.get('id')
    user_nickname = session.get('nickname')
    return render_template("reviewRegister.html", 
                           product_name=name, 
                           user_id=user_id, 
                           user_nickname=user_nickname,
                           user=user_nickname,
                           logged_in=('id' in session))

@app.route('/reviews/register', methods = ['GET', 'POST'])
def register_review():
    
    if request.method == "POST":
        review_title = request.form.get("review_title")
        review_content = request.form.get("review_content")
        rating = request.form.get("rating", type=int) 
        purchase_date = request.form.get("purchase_date")
        product_name = request.form.get("product_name")
        seller_id = request.form.get("seller_id")

        # 이미지 파일 처리
        image = request.files['image']
        image_filename = f"{product_name}_{image.filename}"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        image.save(image_path)


        # Firebase에 데이터 구성
        review_id = str(len(DB.get_reviews())+1)
        new_review = {
            "user_nickname": session.get('nickname'),
            "buyer_id": session.get('id'),
            "product_name":product_name,
            "review_title": review_title,
            "review_content": review_content, 
            "rating": rating,
            "img_path": image_filename,      
            "purchase_date": purchase_date,
            "review_date": datetime.today().strftime('%Y-%m-%d'),
            "review_id": review_id,
            "seller_id" : seller_id
        }


        buyer_id = session.get('id')
        reviews = DB.get_reviews_by_buyer_id(buyer_id)  # buyer_id로 리뷰 조회
        review_count = len(reviews)  # 리뷰 개수 세기

        # Firebase에 데이터 추가 
        DB.insert_review(review_id, new_review)
        return redirect(url_for("review_detail", review_id=review_id))
    return render_template("register_review.html")


@app.route('/reviews/<int:review_id>')
def review_detail(review_id):
    review = DB.get_review_by_id(review_id)
    if review:
        return render_template("reviewDetail.html", review=review,
                               logged_in=('id' in session),
                               user=session.get('nickname'))
    return "리뷰를 찾을 수 없습니다.", 404

## develop/se----------------------------------------------------------------------------------------------
def get_reviews_by_user(self, user_id, role):
    try:
        reviews = self.db.child("reviews").get().val()
        if not reviews:
            return []

        # 구매자(buyer) 또는 판매자(seller) 기준으로 리뷰 필터링
        if role == "buyer":
            return [review for review in reviews.values() if review.get("buyer_id") == user_id]
        elif role == "seller":
            return [review for review in reviews.values() if review.get("seller_id") == user_id]
    except Exception as e:
        logging.error(f"Failed to fetch reviews for {role} {user_id}: {e}")
        return []
##------------------------------------------------------------------------------------------------
      
@app.route('/show_heart/<name>/', methods=['GET'])
def show_heart(name):
    my_heart = DB.get_heart_byname(session['id'], name)
    return jsonify({'my_heart': my_heart})


@app.route('/like/<name>/', methods=['POST'])
def like(name):
    print(request.form)
    my_heart = DB.update_heart(session['id'], 'Y', name)
    return jsonify({'msg': '좋아요 완료!'})

@app.route('/unlike/<name>/', methods=['POST'])
def unlike(name):

    my_heart = DB.update_heart(session['id'], 'N', name)
    return jsonify({'msg': '좋아요 취소!'})

if __name__ == "__main__":
    app.run(debug=True)