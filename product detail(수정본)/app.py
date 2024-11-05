from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    
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

if __name__ == '__main__':
    app.run(debug=True)