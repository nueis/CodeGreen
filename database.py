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

    def user_duplicate_check(self, email):
        users = self.db.child("users").get()
        print("users###", users.val())
        if str(users.val()) == "None": # first registration
            return True
        else:
            for res in users.each():
                value = res.val()

                if value['email'] == email:
                    return False
            return True

    def insert_user(self, user_id, email, password, nickname, phone, role):
        user_data = {
            "email": email,
            "password": password,
            "nickname": nickname,
            "phone": phone,
            "role": role
        }
        if self.user_duplicate_check(email):
            self.db.child("users").push(user_data)
            print(user_data)
            return True
        else:
            return False

