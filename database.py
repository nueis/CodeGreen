import os
import pyrebase
import hashlib 
import json

class DBhandler:
    def __init__(self ):
        with open('./Authentication/firebase_auth.json') as f:
            config=json.load(f )
        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()

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

    def insert_user(self, id, password, nickname, email, phone, role):
        user_data = {
            "id": id,
            "password": password,
            "nickname": nickname,
            "email": email,
            "phone": phone,
            "role": role
        }
        if self.user_duplicate_check(email):
            self.db.child("users").push(user_data)
            print(user_data)
            return True
        else:
            return False
        
    def find_user(self, id, password):
        users = self.db.child("users").get()
        target_value=[]

        if not users.val():
            print("No users found")
            return None

        for res in users.each():
            value = res.val()
            print(f"Checking user: {value}") #data 확인

            if 'id' in value and 'password' in value:
                if value['id'] == id and value['password'] == password :
                    return value    # 사용자 정보 반환
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

