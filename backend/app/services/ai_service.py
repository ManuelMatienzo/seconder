from __future__ import annotations

from decimal import Decimal
import logging
import os
import tempfile
import unicodedata
from urllib.request import urlopen

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AiAnalysis, Incident, IncidentAudio, IncidentPhoto
from app.services.groq_client import get_groq_client


DEFAULT_PRIORITY_LEVEL = "media"
AI_MODEL_VERSION = "groq-llama3-v1"
DEFAULT_GROQ_TEXT_MODEL = "llama-3.1-8b-instant"
logger = logging.getLogger(__name__)


class AIService:
    def process_incident(self, db: Session, incident: Incident) -> AiAnalysis:
        try:
            with db.begin_nested():
                ai_analysis = db.scalar(select(AiAnalysis).where(AiAnalysis.id_incident == incident.id_incident))
                if not ai_analysis:
                    ai_analysis = AiAnalysis(
                        id_incident=incident.id_incident,
                        priority_level=DEFAULT_PRIORITY_LEVEL,
                    )
                    db.add(ai_analysis)
                    db.flush()

                latest_audio = db.scalar(
                    select(IncidentAudio)
                    .where(IncidentAudio.id_incident == incident.id_incident)
                    .order_by(IncidentAudio.created_at.desc(), IncidentAudio.id_audio.desc())
                )
                latest_photo = db.scalar(
                    select(IncidentPhoto)
                    .where(IncidentPhoto.id_incident == incident.id_incident)
                    .order_by(IncidentPhoto.created_at.desc(), IncidentPhoto.id_photo.desc())
                )

                ai_analysis.audio_transcription = self.transcribe_audio(latest_audio.file_url if latest_audio else None)
                ai_analysis.classification = self.classify_image(
                    latest_photo.file_url if latest_photo else None,
                    incident.description_text,
                )

                priority_level, severity_score = self.calculate_priority(
                    incident.description_text,
                    ai_analysis.audio_transcription,
                    ai_analysis.classification,
                )
                ai_analysis.priority_level = priority_level
                ai_analysis.severity_score = Decimal(severity_score)
                ai_analysis.structured_summary = self.generate_summary(incident, ai_analysis)
                ai_analysis.model_version = AI_MODEL_VERSION
                db.flush()
                return ai_analysis
        except Exception as exc:
            logger.error("Error procesando IA para incidente %s: %s", incident.id_incident, str(exc))
            return db.scalar(select(AiAnalysis).where(AiAnalysis.id_incident == incident.id_incident))

    def transcribe_audio(self, audio_url: str | None) -> str | None:
        if not audio_url:
            return None
        temp_path = None
        try:
            client = get_groq_client()
            with urlopen(audio_url, timeout=20) as response:
                audio_bytes = response.read()
            if not audio_bytes:
                return f"Transcripcion automatica generada desde el audio asociado: {audio_url}"

            suffix = os.path.splitext(audio_url.split("?")[0])[1] or ".wav"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name

            with open(temp_path, "rb") as audio_file:
                response = client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3-turbo",
                )

            transcription = getattr(response, "text", None)
            if transcription:
                return transcription.strip()
        except Exception:
            pass
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

        return f"Transcripcion automatica generada desde el audio asociado: {audio_url}"

    def classify_image(self, image_url: str | None, description: str | None) -> str:
        try:
            client = get_groq_client()
            prompt = f"""
Clasifica el tipo de problema vehicular basandote en esta descripcion:

"{description or ''}"

Responde solo con una categoria corta:
- bateria
- motor
- electrico
- llanta
- combustible
- otro
"""

            print("USANDO GROQ PARA CLASIFICACION")
            model = os.getenv("GROQ_VISION_MODEL") or DEFAULT_GROQ_TEXT_MODEL

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )

            classification = response.choices[0].message.content.strip()
            normalized = self._normalize_text(classification)
            if "bateria" in normalized:
                return "bateria"
            if "motor" in normalized:
                return "motor"
            if "electric" in normalized:
                return "electrico"
            if "llanta" in normalized or "neumatic" in normalized:
                return "llanta"
            if "combust" in normalized:
                return "combustible"
            if classification:
                return classification
        except Exception as exc:
            print("ERROR GROQ CLASIFICACION:", str(exc))

        normalized_text = self._normalize_text(description or image_url)
        if any(keyword in normalized_text for keyword in ("llanta", "neumatic", "tire", "wheel")):
            return "llanta"
        if any(keyword in normalized_text for keyword in ("bateria", "electr", "battery", "spark")):
            return "electrico"
        if any(keyword in normalized_text for keyword in ("motor", "engine", "mecan", "oil")):
            return "motor"
        if any(keyword in normalized_text for keyword in ("combust", "fuel", "gas")):
            return "combustible"
        return "incidente no clasificado"

    def calculate_priority(
        self,
        description: str | None,
        transcription: str | None,
        classification: str | None,
    ) -> tuple[str, int]:
        try:
            client = get_groq_client()
            prompt = f"""
Evalua la gravedad del incidente.

Responde SOLO con:
baja, media o alta

Descripcion: {description or ""}
Transcripcion: {transcription or ""}
Clasificacion: {classification or ""}

Respuesta:
"""

            print("USANDO GROQ PARA PRIORIDAD")
            model = os.getenv("GROQ_VISION_MODEL") or DEFAULT_GROQ_TEXT_MODEL

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )

            priority = response.choices[0].message.content.strip().lower()
            if priority.startswith("alta"):
                return "alta", 80
            if priority.startswith("baja"):
                return "baja", 20
            return "media", 50
        except Exception:
            return "media", 50

    def generate_summary(self, incident: Incident, analysis: AiAnalysis) -> str:
        try:
            client = get_groq_client()
            prompt = f"""
Genera un resumen tecnico breve del incidente.

Incluye:
- tipo de problema
- prioridad
- ubicacion
- descripcion

Datos:
Incidente: {incident.description_text or ""}
Clasificacion: {analysis.classification or ""}
Prioridad: {analysis.priority_level or DEFAULT_PRIORITY_LEVEL}
Ubicacion: lat {incident.latitude}, lon {incident.longitude}

Resumen:
"""

            print("USANDO GROQ PARA RESUMEN")
            model = os.getenv("GROQ_VISION_MODEL") or DEFAULT_GROQ_TEXT_MODEL

            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
            )

            summary = response.choices[0].message.content.strip()
            if summary:
                return summary
        except Exception:
            pass

        return f"Incidente reportado: {incident.description_text or 'Sin descripcion disponible'}"

    def _normalize_text(self, value: str | None) -> str:
        if not value:
            return ""
        normalized = unicodedata.normalize("NFKD", value)
        return normalized.encode("ascii", "ignore").decode("ascii").lower()

    def _has_any_keyword(self, text: str, keywords: tuple[str, ...]) -> bool:
        return any(keyword in text for keyword in keywords)

    def _truncate_text(self, value: str, max_length: int = 180) -> str:
        normalized = " ".join(value.split())
        if len(normalized) <= max_length:
            return normalized
        return normalized[: max_length - 3].rstrip() + "..."
