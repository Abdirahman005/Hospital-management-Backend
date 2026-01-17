from flask import Blueprint, request, jsonify
from models import db, Doctor

doctor_bp = Blueprint("doctor_bp", __name__)

@doctor_bp.route("/doctors", methods=["GET"])
def get_doctors():
    doctors = Doctor.query.all()
    result = []
    for doc in doctors:
        result.append({
            "id": doc.id,
            "name": doc.name,
            "specialization": doc.specialization,
            "qualification": doc.qualification,
            "days": doc.days.split(","),
            "reportTime": doc.report_time,
            "leaveTime": doc.leave_time
        })
    return jsonify(result)

@doctor_bp.route("/doctors", methods=["POST"])
def add_doctor():
    data = request.json
    days = ",".join(data.get("days", []))
    new_doc = Doctor(
        name=data["name"],
        specialization=data["specialization"],
        qualification=data["qualification"],
        days=days,
        report_time=data["reportTime"],
        leave_time=data["leaveTime"]
    )
    db.session.add(new_doc)
    db.session.commit()
    return jsonify({"message": "Doctor added"}), 201

@doctor_bp.route("/doctors/<int:id>", methods=["PUT"])
def edit_doctor(id):
    doc = Doctor.query.get_or_404(id)
    data = request.json
    doc.name = data["name"]
    doc.specialization = data["specialization"]
    doc.qualification = data["qualification"]
    doc.days = ",".join(data.get("days", []))
    doc.report_time = data["reportTime"]
    doc.leave_time = data["leaveTime"]
    db.session.commit()
    return jsonify({"message": "Doctor updated"})

@doctor_bp.route("/doctors/<int:id>", methods=["DELETE"])
def delete_doctor(id):
    doc = Doctor.query.get_or_404(id)
    db.session.delete(doc)
    db.session.commit()
    return jsonify({"message": "Doctor deleted"})
