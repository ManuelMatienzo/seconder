from math import asin, ceil, cos, radians, sin, sqrt

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import AiAnalysis, Incident, Workshop

AVERAGE_SPEED_KMH = 30


class AssignmentEngineConflictError(Exception):
    pass


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_km = 6371.0
    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)

    haversine_term = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
    return 2 * radius_km * asin(sqrt(haversine_term))


def classification_matches_specialties(classification: str | None, specialties: str | None) -> bool:
    if not classification or not specialties:
        return False

    classification_map = {
        "falla mecanica": ("mecan", "motor", "radiador", "aceite"),
        "problema electrico": ("electr", "bateria", "alternador", "cable"),
        "neumatico": ("llanta", "neumatic", "tire", "rueda"),
        "danio exterior": ("carroceria", "pintura", "paracho", "exterior", "puerta"),
    }

    normalized_specialties = specialties.lower()
    for keyword in classification_map.get(classification.lower(), ()):
        if keyword in normalized_specialties:
            return True

    return False


def build_recommendation_reason(
    distance_km: float,
    specialty_match: bool,
    priority_level: str | None,
) -> str:
    reasons = ["Taller disponible"]
    if distance_km <= 5:
        reasons.append("muy cercano")
    elif distance_km <= 15:
        reasons.append("cercano")

    if specialty_match:
        reasons.append("especialidad alineada")

    if priority_level:
        reasons.append(f"prioridad {priority_level}")

    return ", ".join(reasons)


def calculate_recommendation_score(
    distance_km: float,
    specialty_match: bool,
    rating: float | None,
    priority_level: str | None,
) -> float:
    distance_component = max(0.0, 1.0 - min(distance_km, 50.0) / 50.0)
    specialty_bonus = 0.15 if specialty_match else 0.0
    rating_bonus = min(max((rating or 0.0) / 5.0, 0.0), 1.0) * 0.10
    priority_bonus = 0.05 if (priority_level or "").lower() in {"alta", "urgente"} else 0.0
    return round(min(1.0, distance_component * 0.75 + specialty_bonus + rating_bonus + priority_bonus), 2)


def estimate_time_minutes(distance_km: float) -> int:
    return max(1, ceil((distance_km / AVERAGE_SPEED_KMH) * 60))


def run_assignment_engine(db: Session, incident_id: int) -> dict:
    incident = db.scalar(
        select(Incident)
        .options(joinedload(Incident.ai_analysis))
        .where(Incident.id_incident == incident_id)
    )
    if not incident:
        raise LookupError("Incidente no encontrado")

    if incident.status != "pendiente":
        raise AssignmentEngineConflictError("El incidente no esta en estado pendiente para ser procesado")

    ai_analysis = incident.ai_analysis
    classification = ai_analysis.classification if ai_analysis else None
    priority_level = ai_analysis.priority_level if ai_analysis else None
    structured_summary = ai_analysis.structured_summary if ai_analysis else None

    workshops = db.scalars(
        select(Workshop)
        .where(Workshop.is_available.is_(True))
        .order_by(Workshop.rating.desc().nullslast(), Workshop.id_user.asc())
    ).all()

    incident_lat = float(incident.latitude)
    incident_lon = float(incident.longitude)
    recommendations: list[dict] = []

    for workshop in workshops:
        distance_km = haversine_distance_km(
            incident_lat,
            incident_lon,
            float(workshop.latitude),
            float(workshop.longitude),
        )
        specialty_match = classification_matches_specialties(classification, workshop.specialties)
        score = calculate_recommendation_score(distance_km, specialty_match, workshop.rating, priority_level)
        recommendations.append(
            {
                "id_workshop": workshop.id_user,
                "workshop_name": workshop.workshop_name,
                "is_available": workshop.is_available,
                "distance_km": round(distance_km, 2),
                "estimated_time_min": estimate_time_minutes(distance_km),
                "rating": workshop.rating,
                "specialties": workshop.specialties,
                "score": score,
                "reason": build_recommendation_reason(distance_km, specialty_match, priority_level),
            }
        )

    recommendations.sort(
        key=lambda item: (
            -item["score"],
            item["distance_km"],
            -(item["rating"] or 0.0),
            item["id_workshop"],
        )
    )

    return {
        "id_incident": incident.id_incident,
        "incident_status": incident.status,
        "classification": classification,
        "priority_level": priority_level,
        "structured_summary": structured_summary,
        "incident": {
            "id_incident": incident.id_incident,
            "id_client": incident.id_client,
            "id_vehicle": incident.id_vehicle,
            "incident_status": incident.status,
            "latitude": incident_lat,
            "longitude": incident_lon,
            "description_text": incident.description_text,
        },
        "recommended_workshops": recommendations,
    }
