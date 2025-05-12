from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# 병원 정보 모델
class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)

# 의료기기 정보 모델
class MedicalDevice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(255), nullable=False)
    related_disease = db.Column(db.String(255), nullable=False)
    hospital_name = db.Column(db.String(255), nullable=False)

# 의료 공백(Healthcare Gap) 정보 모델
class MedicalGap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String(200), nullable=False)
    issue = db.Column(db.Text, nullable=False)

# 환자 데이터 모델
class PatientData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(100), nullable=False, unique=True)
    diagnosis = db.Column(db.String(300), nullable=False)

# 만성질환 관리 플랜 모델
class ChronicDiseasePlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_name = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text, nullable=False)

# 질병 관리 모델
class DiseaseManagement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    disease_name = db.Column(db.String(200), nullable=False)
    management_strategy = db.Column(db.Text, nullable=False)

# 보험 정보 모델
class Insurance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    policy_name = db.Column(db.String(200), nullable=False)

# 예약(Reservation) 모델
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(100), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)

# 암 발생 통계 모델 (기존 데이터셋)
class CancerStats(db.Model):
    __tablename__ = '국립암센터_암발생_통계_정보'
    id = db.Column(db.Integer, primary_key=True)
    발생연도 = db.Column(db.String(4), nullable=False)
    성별 = db.Column(db.String(50), nullable=False)
    국제질병분류 = db.Column(db.String(50), nullable=False)
    암종 = db.Column(db.String(50), nullable=False)
    연령군 = db.Column(db.String(20), nullable=False)
    발생자수 = db.Column(db.Integer, nullable=False)

# 암 발생 데이터 테이블 (새로운 cancer 테이블 추가)
class Cancer(db.Model):
    __tablename__ = 'cancer'
    id = db.Column(db.Integer, primary_key=True)
    발생연도 = db.Column(db.String(4), nullable=False)
    성별 = db.Column(db.String(50), nullable=False)
    연령군 = db.Column(db.String(20), nullable=False)
    암종 = db.Column(db.String(100), nullable=False)
    발생자수 = db.Column(db.Integer, nullable=False)

# 사용자(User) 모델
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # 🔥 평문 비밀번호 저장
    email = db.Column(db.String(120), unique=True, nullable=False)
    diet = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    height = db.Column(db.Float, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    family_history = db.Column(db.Text, nullable=True)

class HospitalReview(db.Model):
    __tablename__ = 'hospital_review'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ForeignKey 추가
    hospital_name = db.Column(db.String(200), nullable=False)
    review_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    optional_username = db.Column(db.String(200), nullable=True)

    user = db.relationship('User', backref=db.backref('reviews', lazy=True))

