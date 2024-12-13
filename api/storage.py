import firebase_admin, json, os
from firebase_admin import credentials, storage
from werkzeug.utils import secure_filename

# 업로드할 파일의 저장 경로 설정
UPLOAD_FOLDER = os.path.join('../static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

class SThandler:

    def __init__(self):
        # Firebase Admin SDK 초기화
        with open('../configuration/codegreen-1211-firebase-adminsdk-mytx5-d061b9d4ce.json') as f:
            config = json.load(f)

        if not firebase_admin._apps:  # 이미 초기화된 경우 다시 초기화하지 않음
            cred = credentials.Certificate(config)  # Firebase 인증 파일 경로
            firebase_admin.initialize_app(cred, {
                'storageBucket': 'codegreen-1211.firebasestorage.app'  # Firebase Storage 버킷 URL
            })

    # 확장자 체크 함수
    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


    def upload_file_to_firebase(self, file):
        """Firebase Storage에 파일 업로드"""
        if file and self.allowed_file(file.filename):  # 파일이 유효한지 체크
            filename = secure_filename(file.filename)  # 안전한 파일 이름 생성
            bucket = storage.bucket()  # Firebase Storage 버킷 가져오기
            blob = bucket.blob(f'profile_pics/{filename}')  # 업로드할 경로 설정

            # 파일 업로드
            blob.upload_from_file(file)
            blob.make_public()  # 파일을 공개적으로 접근할 수 있도록 설정
            return blob.public_url  # 파일의 공개 URL 반환
        return None
