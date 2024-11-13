import os
import pyrebase
import json

class DBhandler:
    def __init__(self ):
        with open('./Authentication/firebase_auth.json') as f:
            config=json.load(f )
        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()

    def insert_item(self, name, data, img_path):
        # Storage를 사용하지 않고 경로만 저장
        img_url = f"/static/uploads/{os.path.basename(img_path)}"  # 이미지는 로컬 경로로 가정

        # Firebase Realtime Database에 상품 정보 저장
        item_info = {
            "seller": data['seller'],
            "addr": data['addr'],
            "email": data.get('email', ''),  # 이메일이 없다면 빈 문자열
            "category": data['category'],
            "card": data.get('card', ''),  # 카드 필드도 선택적
            "status": data['status'],
            "phone": data.get('phone', ''),  # 폰 번호도 없으면 빈 문자열
            "price": data['price'],
            "stock": data['stock'],
            "img_path": img_url  # 이미지 URL 대신 경로만 저장
        }

        self.db.child("items").child(name).set(item_info)
        return True