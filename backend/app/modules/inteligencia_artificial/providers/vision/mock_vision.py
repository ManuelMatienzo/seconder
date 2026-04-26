from app.models import IncidentPhoto

ALLOWED_CLASSIFICATIONS = {
    "falla mecanica",
    "problema electrico",
    "neumatico",
    "danio exterior",
    "incidente no clasificado",
}


def build_mock_classification(photo: IncidentPhoto) -> str:
    photo_context = f"{photo.file_url} {photo.format or ''}".lower()

    if any(keyword in photo_context for keyword in ("llanta", "neumatic", "tire", "rueda", "pinch")):
        return "neumatico"
    if any(keyword in photo_context for keyword in ("bateria", "electr", "cable", "luz", "alternador")):
        return "problema electrico"
    if any(keyword in photo_context for keyword in ("golpe", "choque", "aboll", "paracho", "puerta", "exterior")):
        return "danio exterior"
    if any(keyword in photo_context for keyword in ("motor", "mecan", "aceite", "humo", "radiador")):
        return "falla mecanica"

    return "incidente no clasificado"


def normalize_classification(value: str | None) -> str:
    if not value:
        return "incidente no clasificado"

    normalized = value.strip().lower()
    if normalized in ALLOWED_CLASSIFICATIONS:
        return normalized

    aliases = {
        "llanta": "neumatico",
        "llantas": "neumatico",
        "neumatico": "neumatico",
        "neumaticos": "neumatico",
        "electrico": "problema electrico",
        "mecanico": "falla mecanica",
    }
    if normalized in aliases:
        return aliases[normalized]

    if "electr" in normalized or "bateria" in normalized:
        return "problema electrico"
    if "mecan" in normalized or "motor" in normalized or "radiador" in normalized:
        return "falla mecanica"
    if "llanta" in normalized or "neumatic" in normalized or "rueda" in normalized:
        return "neumatico"
    if "golpe" in normalized or "choque" in normalized or "exterior" in normalized:
        return "danio exterior"

    return "incidente no clasificado"
