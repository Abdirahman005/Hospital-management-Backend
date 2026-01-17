from flask import Blueprint, request, jsonify
from models import db, Appointment

appointment_bp = Blueprint("appointment_bp", __name__)

@appointment_bp.route("/appointments", methods=["GET"])
def get_appointments():
    appointments = Appointment.query.all()
    result = []
    for a in appointments:
        result.append({
            "id": a.id,
            "patientName": a.patient_name,
            "doctorId": a.doctor_id,
            "time": a.time
        })
    return jsonify(result)

@appointment_bp.route("/appointments", methods=["POST"])
def add_appointment():
    data = request.json
    new_appointment = Appointment(
        patient_name=data["patientName"],
        doctor_id=data["doctorId"],
        time=data["time"]
    )
    db.session.add(new_appointment)
    db.session.commit()
    return jsonify({"message": "Appointment added"}), 201
