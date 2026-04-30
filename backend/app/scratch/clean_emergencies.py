import sys
from sqlalchemy import delete
from app.core.database import SessionLocal
from app.modules.asignacion_operaciones.models.assignment import Assignment
from app.modules.reporte_emergencias.models.incident import Incident
from app.modules.reporte_emergencias.models.incident_photo import IncidentPhoto
from app.modules.reporte_emergencias.models.incident_audio import IncidentAudio
from app.modules.inteligencia_artificial.models.ai_analysis import AiAnalysis
from app.modules.gestion_usuarios.models.notification import Notification
from app.modules.transacciones.models.payment import Payment

def clean_data():
    db = SessionLocal()
    try:
        print("Iniciando limpieza de datos de emergencia...")
        # Borrar en orden para respetar FKs
        db.execute(delete(Payment))
        db.execute(delete(Assignment))
        db.execute(delete(IncidentPhoto))
        db.execute(delete(IncidentAudio))
        db.execute(delete(AiAnalysis))
        db.execute(delete(Notification))
        db.execute(delete(Incident))
        db.commit()
        print("Limpieza completada con exito.")
    except Exception as e:
        db.rollback()
        # Evitar caracteres no ASCII en el print por si acaso
        try:
            print(f"Error: {str(e)}")
        except:
            print("Error en la limpieza (detalles no imprimibles)")
    finally:
        db.close()

if __name__ == "__main__":
    clean_data()
