from app.models import Incident, IncidentAudio


def build_mock_transcription(incident: Incident, audio: IncidentAudio) -> str:
    audio_format = audio.format or "desconocido"
    duration = f"{audio.duration_seconds} segundos" if audio.duration_seconds is not None else "duracion no especificada"
    return (
        f"Transcripcion simulada del incidente {incident.id_incident}. "
        f"Audio {audio.id_audio} en formato {audio_format}, {duration}. "
        f"Fuente registrada: {audio.file_url}."
    )
