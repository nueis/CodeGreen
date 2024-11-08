from flask import Flask, render_template

app = Flask(__name__)

@app.route('/productreviews') 
def reviews():
    reviews_data = [
        {"title": "리뷰 제목", "author": "작성자 닉네임", "date": "작성 날짜"},
        {"title": "리뷰 제목", "author": "작성자 닉네임", "date": "작성 날짜"},
        {"title": "리뷰 제목", "author": "작성자 닉네임", "date": "작성 날짜"},
    ]
    return render_template('productreviews.html', reviews=reviews_data)

if __name__ == '__main__':
    app.run(debug=True)
