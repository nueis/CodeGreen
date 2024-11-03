from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# 업로드할 파일의 저장 경로 설정
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 업로드 폴더 생성
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

products = {}

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

    return render_template("reviews.html", reviews=paginated_reviews, page=page, total_pages=total_pages)

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

    return render_template("reviews.html", reviews=paginated_reviews, page=page, total_pages=total_pages)



if __name__ == "__main__":
    app.run(debug=True)
