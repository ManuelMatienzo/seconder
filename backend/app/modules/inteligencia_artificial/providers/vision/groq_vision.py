import json

from app.core.config import settings
from app.modules.inteligencia_artificial.providers.vision.mock_vision import normalize_classification


class GroqVisionError(RuntimeError):
    pass


def classify_image_with_groq_vision(image_url: str) -> tuple[str, str]:
    try:
        from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI
    except ImportError as exc:
        raise GroqVisionError("La dependencia 'openai' no esta instalada para usar Groq Vision") from exc

    if not settings.GROQ_API_KEY:
        raise GroqVisionError("GROQ_API_KEY no esta configurado")

    client = OpenAI(
        api_key=settings.GROQ_API_KEY,
        base_url=settings.GROQ_BASE_URL,
        timeout=60.0,
    )

    system_prompt = (
        "Eres un clasificador de incidentes vehiculares. "
        "Debes responder solo con un JSON valido con la clave 'classification'. "
        "El valor debe ser exactamente una de estas opciones: "
        "falla mecanica, problema electrico, neumatico, danio exterior, incidente no clasificado."
    )

    user_text = (
        "Clasifica esta imagen de evidencia vehicular en una sola categoria del catalogo fijo. "
        "Si no es posible determinarlo con claridad, usa 'incidente no clasificado'."
    )

    try:
        completion = client.chat.completions.create(
            model=settings.GROQ_VISION_MODEL,
            response_format={"type": "json_object"},
            temperature=0.00000001,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_text},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                },
            ],
        )
    except (APIConnectionError, APITimeoutError) as exc:
        raise GroqVisionError("No se pudo conectar con Groq Vision") from exc
    except APIStatusError as exc:
        raise GroqVisionError(f"Groq Vision respondio con error HTTP {exc.status_code}") from exc
    except Exception as exc:
        raise GroqVisionError("Ocurrio un error inesperado al clasificar con Groq Vision") from exc

    content = completion.choices[0].message.content if completion.choices else None
    if not content:
        raise GroqVisionError("Groq Vision no devolvio contenido de clasificacion")

    try:
        payload = json.loads(content)
    except json.JSONDecodeError:
        return normalize_classification(content), f"groq-{settings.GROQ_VISION_MODEL}"

    classification = normalize_classification(payload.get("classification"))
    return classification, f"groq-{settings.GROQ_VISION_MODEL}"
