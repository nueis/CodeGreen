import pyrebase
import json

class DBhandler:
    def __init__(self):
        with open('./authentication/firebase_auth.json') as f:
            config = json.load(f)

        # Firebase 초기화
        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()

    # 회원가입 함수

    def check_user_exists(self, user_id):
        """사용자 ID로 중복 여부 확인"""
        result = self.db.child("users").child(user_id).get()
        return result.val() is not None  # 존재하면 True, 아니면 False

    def check_email_exists(self, email):
        """이메일 중복 여부 확인"""
        result = self.db.child("users").order_by_child("email").equal_to(email).get()
        return result.val() is not None

    def check_nickname_exists(self, nickname):
        """닉네임 중복 여부 확인"""
        result = self.db.child("users").order_by_child("nickname").equal_to(nickname).get()
        return result.val() is not None

    def insert_user(self, user_id, password_hash, nickname, email, phone, role, profile_pic_url):
        """사용자 추가"""
        try:
            user_data = {
                "id": user_id,
                "password": password_hash,
                "nickname": nickname,
                "email": email,
                "phone": phone,
                "role": role,
                "profile_pic": profile_pic_url
            }
            self.db.child("users").child(user_id).set(user_data)
            return True
        except Exception as e:
            print(f"Error inserting user: {e}")
            return False

    # 로그인 함수
    def find_user(self, user_id, password_hash):
        """Firebase에서 사용자 조회 및 비밀번호 확인"""
        users = self.db.child("users").get()  # 'users' 경로에서 모든 사용자 데이터 조회

        for user in users.each():
            value = user.val()

            # ID와 해시된 비밀번호가 일치하는지 확인
            if value['id'] == user_id and value['password'] == password_hash:
                return {
                    "id": value["id"],
                    "nickname": value["nickname"],
                    "role": value["role"]
                }

        return None  # 일치하는 사용자가 없으면 None 반환

    def insert_item(self, product_id, product_data):
        try:
            self.db.child("items").child(product_id).set(product_data)
            print(f"Item {product_id} successfully inserted into Firebase.")
            return True
        except Exception as e:
            print(f"Error inserting item {product_id} into Firebase: {e}")
            return False
        
    def get_items(self):
        try:
            items = self.db.child("items").get()
            if items.val():
                print("Items successfully retrieved from Firebase.")
                return items.val()
            return {}
        except Exception as e:
            print(f"Error retrieving items from Firebase: {e}")
            return {}

    def get_item_by_id(self, product_id):
        try:
            item = self.db.child("items").child(product_id).get()
            if item.val():
                print(f"Item {product_id} successfully retrieved from Firebase.")
                return item.val()
            return None
        except Exception as e:
            print(f"Error retrieving item {product_id} from Firebase: {e}")
            return None
    
    def insert_review(self, review_id, review_data):
        try:
            self.db.child("reviews").child(review_id).set(review_data)
            print(f"Review {review_id} successfully inserted into Firebase.")
            return True
        except Exception as e:
            print(f"Error inserting item {review_id} into Firebase: {e}")
            return False
    
    def get_reviews(self):
        try:
            result = self.db.child("reviews").get()
            if result.val():
                print("reviews successfully retrieved from Firebase")
                return result.val()
            return {}
        except Exception as e:
            print(f"Error retrieving reviews from Firebase: {e}")
            return {}
        
    def get_review_by_id(self, review_id):
        try:
            reviews = self.db.child("reviews").get()
            target_value=""
            for review in reviews.each():
                key_value = review.key()
                if key_value == review_id:
                    target_value=review.val()
            return target_value
        except Exception as e:
            print(f"Error retrieving review {review_id} from Firebase: {e}")
            return None

    def get_review_by_nickname(self, nickname):
        try:
            reviews = self.db.child("reviews").order_by_child("user_nickname").equal_to(nickname).get()
            if reviews.val():
                print("reviews successfully retrieved from Firebase")
                return reviews.val()
            return {}
        except Exception as e:
            print(f"Error retrieving review {nickname} from Firebase: {e}")
            return None

