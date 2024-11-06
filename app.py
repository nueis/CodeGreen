from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# 업로드할 파일의 저장 경로 설정
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 업로드 폴더 생성
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 화면 배치를 테스트 하기 위한 샘플 데이터
products = {}
reviews = {}

user_purchases = {
    "user1": [1,2], # user1 purchased products with ID 1,2 
}

products[1] = {
    "product_id": 1,
    "name": "Product A",
    "price": 20000,
    "image": "productA.jpg",
    "reviews": [],
    "rating": 0,
}

products[2] = {
    "product_id": 2,
    "name": "Product B",
    "price": 10000,
    "image": "productB.jpg",
    "reviews": [],
    "rating": 0,
}


@app.route("/index")
def index():
    return render_template("index.html")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/mypage")
def view_review():
    return render_template("mypage.html")

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
        review_id = len(reviews) + 1
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
        reviews[review_id] = new_review

        # 상품 딕셔너리에 추가 
        products[product_id]["reviews"].append(review_id)

        product_reviews = [review["rating"] for review in reviews.values() if review["product_id"] == product_id]
        valid_ratings = [r for r in product_reviews if r is not None]
        products[product_id]["rating"] = sum(valid_ratings) / len(valid_ratings) if valid_ratings else 0

        return redirect(url_for("review_detail", review_id=review_id))

    # Get list of purchased products for the user
    purchased_product_ids = user_purchases.get(user_id, [])
    purchased_products = [products[pid] for pid in purchased_product_ids]

    return render_template("reviewRegister.html", products=purchased_products)

@app.route('/reviews/<int:review_id>')
def review_detail(review_id):
    review = reviews[review_id]
    if review:
        product = products.get(review["product_id"])
        if product:
            return render_template("reviewDetail.html", review=review, product=product)
        return "제품을 찾을 수 없습니다.", 404
    return "리뷰를 찾을 수 없습니다.", 404

if __name__ == "__main__":
    app.run(debug=True)
