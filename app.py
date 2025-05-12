from flask import Flask, render_template, request, redirect, session, jsonify
from models import db, MedicalDevice, User, HospitalReview, Cancer
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://obmfactory:masterit1234!@218.209.20.32:3306/medical_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SECURE'] = False

# SQLAlchemy 초기화
db.init_app(app)

# 데이터베이스 테이블 생성
def create_tables():
    with app.app_context():
        db.create_all()

# 홈 페이지
@app.route("/")
def home():
    return render_template("index.html")

@app.route('/hospital')
def hospital():
    return render_template('hospital.html')

@app.route("/device")
def device():
    return render_template("device.html")

@app.route("/disease")
def disease():
    return render_template("disease.html")

@app.route("/insurance")
def insurance():
    return render_template("insurance.html")

@app.route("/reserve")  
def reserve():
    return render_template("reserve.html")

# 로그인
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password, password):
            return jsonify({'error': '로그인 실패! 아이디와 비밀번호를 확인하세요.'}), 401

        session['user_id'] = user.id
        session['username'] = user.username

        return jsonify({'message': '로그인 성공!', 'redirect': '/'})

    return render_template('login.html')

# 현재 로그인된 사용자 정보 반환
@app.route('/get_user', methods=['GET'])
def get_user():
    if 'user_id' in session:
        return jsonify({'user_id': session['user_id'], 'username': session['username']})
    return jsonify({'error': '로그인이 필요합니다.'}), 401

# 회원가입
@app.route('/signup', methods=['POST'])
def signup():
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        diet = request.form.get('diet')
        location = request.form.get('location')
        height = request.form.get('height')
        weight = request.form.get('weight')
        family_history = request.form.get('family_history')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'error': '이미 사용 중인 아이디입니다.'}), 400

        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            password=hashed_password,
            email=email,
            diet=diet,
            location=location,
            height=float(height) if height else None,
            weight=float(weight) if weight else None,
            family_history=family_history
        )

        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': '회원가입이 완료되었습니다!', 'redirect': '/login'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'회원가입 중 오류 발생: {str(e)}'}), 500

# 로그아웃
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect('/')

@app.route('/review', methods=['GET', 'POST'])
def review():
    try:
        if request.method == 'POST':
            if 'user_id' not in session:
                return jsonify({'error': '로그인이 필요합니다.'}), 401

            data = request.get_json()
            if not data or 'hospital_name' not in data or 'review_text' not in data or 'rating' not in data:
                return jsonify({'error': '모든 필드를 입력해야 합니다.'}), 400

            new_review = HospitalReview(
                user_id=session['user_id'],
                hospital_name=data['hospital_name'],
                review_text=data['review_text'],
                rating=int(data['rating']),
                optional_username=data.get('optional_username', None)  # 🔥 추가된 필드 사용
            )
            db.session.add(new_review)
            db.session.commit()

            return jsonify({'message': '리뷰가 성공적으로 등록되었습니다.'}), 200

        # GET 요청 (리뷰 목록 불러오기)
        page = int(request.args.get('page', 1))
        per_page = 5

        reviews_query = HospitalReview.query.order_by(HospitalReview.created_at.desc())
        total_reviews = reviews_query.count()
        reviews = reviews_query.offset((page - 1) * per_page).limit(per_page).all()

        has_more = (page * per_page) < total_reviews

        return jsonify({
            'reviews': [{
                'hospital_name': review.hospital_name,
                'review_text': review.review_text,
                'rating': review.rating,
                'created_at': review.created_at.strftime('%Y-%m-%d') if review.created_at else 'N/A',
                'optional_username': review.optional_username,
                'user': {'username': review.user.username if review.user else '알 수 없음'}
            } for review in reviews],
            'hasMore': has_more
        })
    except Exception as e:
        import traceback
        print("리뷰 API 오류:", traceback.format_exc())  # 콘솔에 상세 오류 출력
        return jsonify({'error': f'리뷰 데이터를 가져오는 중 오류 발생: {str(e)}'}), 500



# 검색 기능
@app.route('/api/search', methods=['GET'])
def search_device():
    disease = request.args.get('disease')
    if not disease:
        return jsonify([])

    results = MedicalDevice.query.filter(MedicalDevice.related_disease.ilike(f"%{disease}%")).all()
    output = [{"device_name": r.category_name, "hospital_name": r.hospital_name} for r in results]
    return jsonify(output)

@app.route('/api/cancer/gender')
def cancer_gender():
    results = db.session.query(Cancer.성별, db.func.sum(Cancer.발생자수)).group_by(Cancer.성별).all()
    data = {
        "labels": [r[0] for r in results],
        "data": [r[1] for r in results]
    }
    return jsonify(data)

@app.route('/api/cancer/age')
def cancer_age():
    results = db.session.query(Cancer.연령군, db.func.sum(Cancer.발생자수)).group_by(Cancer.연령군).all()
    data = {
        "labels": [r[0] for r in results],
        "data": [r[1] for r in results]
    }
    return jsonify(data)

@app.route('/api/cancer/gender-specific')
def cancer_gender_specific():
    results = db.session.query(Cancer.암종, db.func.sum(Cancer.발생자수)).group_by(Cancer.암종).all()
    data = {
        "labels": [r[0] for r in results],
        "data": [r[1] for r in results]
    }
    return jsonify(data)


if __name__ == "__main__":
    create_tables()
    app.run(host="0.0.0.0",debug=True)
