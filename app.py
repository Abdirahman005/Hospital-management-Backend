from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import time
from werkzeug.security import generate_password_hash, check_password_hash
import os  # <-- added

# ================= FLASK APP =================
app = Flask(__name__)
CORS(app)

# ================= DATABASE CONFIG =================
# Use environment variable DATABASE_URL (set on Render)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ================= MODELS =================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # hashed password

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100), nullable=False)
    days = db.Column(db.ARRAY(db.String), nullable=False)
    report_time = db.Column(db.Time, nullable=False)
    leave_time = db.Column(db.Time, nullable=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    time = db.Column(db.Time, nullable=False)

# ================= CREATE TABLES =================
with app.app_context():
    db.create_all()

# ================= AUTH ROUTES =================
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "Username already exists"}), 400
    hashed_pw = generate_password_hash(data['password'], method='pbkdf2:sha256')
    user = User(username=data['username'], password=hashed_pw)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        return jsonify({"message": "Login successful"})
    return jsonify({"message": "Invalid credentials"}), 401

# ================= DOCTOR ROUTES =================
@app.route('/doctors', methods=['GET'])
def get_doctors():
    doctors = Doctor.query.all()
    return jsonify([{
        "id": d.id,
        "name": d.name,
        "specialization": d.specialization,
        "qualification": d.qualification,
        "days": d.days,
        "reportTime": d.report_time.strftime("%H:%M"),
        "leaveTime": d.leave_time.strftime("%H:%M")
    } for d in doctors])

@app.route('/doctors', methods=['POST'])
def add_doctor():
    data = request.json
    doctor = Doctor(
        name=data['name'],
        specialization=data['specialization'],
        qualification=data['qualification'],
        days=data['days'],
        report_time=time.fromisoformat(data['reportTime']),
        leave_time=time.fromisoformat(data['leaveTime'])
    )
    db.session.add(doctor)
    db.session.commit()
    return jsonify({"message": "Doctor added successfully", "id": doctor.id})

@app.route('/doctors/<int:id>', methods=['PUT'])
def update_doctor(id):
    data = request.json
    doctor = Doctor.query.get_or_404(id)
    doctor.name = data['name']
    doctor.specialization = data['specialization']
    doctor.qualification = data['qualification']
    doctor.days = data['days']
    doctor.report_time = time.fromisoformat(data['reportTime'])
    doctor.leave_time = time.fromisoformat(data['leaveTime'])
    db.session.commit()
    return jsonify({"message": "Doctor updated successfully"})

@app.route('/doctors/<int:id>', methods=['DELETE'])
def delete_doctor(id):
    doctor = Doctor.query.get_or_404(id)
    db.session.delete(doctor)
    db.session.commit()
    return jsonify({"message": "Doctor deleted successfully"})

# ================= APPOINTMENT ROUTES =================
@app.route('/appointments', methods=['GET'])
def get_appointments():
    appointments = Appointment.query.all()
    return jsonify([{
        "id": a.id,
        "patient_name": a.patient_name,
        "doctor_id": a.doctor_id,
        "time": a.time.strftime("%H:%M")
    } for a in appointments])

@app.route('/appointments', methods=['POST'])
def add_appointment():
    data = request.json
    doctor = Doctor.query.get(data['doctorId'])
    if not doctor:
        return jsonify({"message": "Doctor not found"}), 404
    appointment = Appointment(
        patient_name=data['patientName'],
        doctor_id=data['doctorId'],
        time=time.fromisoformat(data['time'])
    )
    db.session.add(appointment)
    db.session.commit()
    return jsonify({"message": "Appointment booked successfully", "id": appointment.id})

# ================= RUN APP =================
if __name__ == "__main__":
    app.run(debug=True)
