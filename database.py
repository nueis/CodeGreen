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

