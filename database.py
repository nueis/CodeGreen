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

    # def check_email_exists(self, email):
    #     """이메일 중복 여부 확인"""
    #     result = self.db.child("users").order_by_child("email").equal_to(email).get()
    #     return result.val() is not None

    def check_email_exists(self, email):
        """이메일 중복 확인 (전체 데이터를 가져와서 필터링)"""
        try:
            users = self.db.child("users").get()  # 전체 데이터를 가져옴
            if users.each():  # 데이터가 존재하면
                for user in users.each():
                    if user.val().get("email") == email:
                        return True
            return False  # 이메일이 없으면 False 반환
        except Exception as e:
            print(f"Error checking email existence: {e}")
            return False

    # def check_nickname_exists(self, nickname):
    #     """닉네임 중복 여부 확인"""
    #     result = self.db.child("users").order_by_child("nickname").equal_to(nickname).get()
    #     return result.val() is not None

    def check_nickname_exists(self, nickname):
        """닉네임 중복 확인 (전체 데이터를 가져와서 필터링)"""
        try:
            users = self.db.child("users").get()  # 전체 데이터를 가져옴
            if users.each():  # 데이터가 존재하면
                for user in users.each():
                    if user.val().get("nickname") == nickname:  # 닉네임 일치 여부 확인
                        return True
            return False  # 닉네임이 없으면 False 반환
        except Exception as e:
            print(f"Error checking nickname existence: {e}")
            return False

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
            review = self.db.child("reviews").child(review_id).get()
            if review.val():
                print(f"Review {review_id} successfully retrieved from Firebase.")
                return review.val()
            return None
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
## develop/se------------------------------------------------------------------------------
    
    def insert_order(self, order_id, order_data):
        try:
        # Firebase Database의 'orders' 디렉토리에 데이터를 저장
            self.db.child("orders").child(order_id).set(order_data)
            return True
        except Exception as e:
            print(f"Failed to insert order {order_id}: {e}")
            return False  
         
    def get_orders_by_user(self, user_id, role):
        try:
            orders = self.db.child("orders").get().val()  # Firebase에서 모든 주문 데이터 가져오기
            if not orders:
                return []

             # 구매자(buyer) 또는 판매자(seller) 기준으로 주문 필터링
            if role == "buyer":
                return [order for order in orders.values() if order.get("buyer_id") == user_id]
            elif role == "seller":
                return [order for order in orders.values() if order.get("seller_id") == user_id]
        except Exception as e:
            print(f"Failed to fetch orders for {role} {user_id}: {e}")
            return []
    
    def get_reviews_by_buyer_id(self, buyer_id):
        try:
            reviews = self.db.child("reviews").get().val()
            if not reviews:
                return []
            return [review for review in reviews.values() if review.get("buyer_id") == buyer_id]
        except Exception as e:
            print(f"Error retrieving reviews for buyer {buyer_id}: {e}")
            return []

    def get_reviews_by_seller_id(self, seller_id):
        try:
            reviews = self.db.child("reviews").get().val()
            if not reviews:
                return []
            return [review for review in reviews.values() if review.get("seller_id") == seller_id]
        except Exception as e:
            print(f"Error retrieving reviews for seller {seller_id}: {e}")
            return []
##-----------------------------------------------------------------------------------------------------------------------------------------
                
    # home 화면 recent sales 부분 추가
    def get_recent_items(self, count=5):
        try:
            items = self.db.child("items").get()

            if not items.val():
                return []

            # 데이터를 리스트로 변환 및 None 값 필터링
            items_list = [
                {**item.val(), 'id': int(item.key())}
                for item in items.each()
                if item and item.val() and isinstance(item.val(), dict)
            ]

            # ID 기준 내림차순 정렬
            sorted_items = sorted(items_list, key=lambda x: x['id'], reverse=True)
            return sorted_items[:count]
        except Exception as e:
            print(f"Error retrieving recent items from Firebase: {e}")
            return []
    def get_heart_byname(self, uid, name):
        hearts = self.db.child("heart").child(uid).get()
        target_value = ""

        if hearts.val() is None:
            return target_value

        for res in hearts.each():
            key_value = res.key()
            if key_value == name:
                target_value = res.val()  # 해당 상품의 좋아요 상태
                return target_value

        return target_value

    def update_heart(self, user_id, isHeart, item):
        heart_info = {
            "interested": isHeart  # 좋아요 상태
        }


        self.db.child("heart").child(user_id).child(item).set(heart_info)
        return True