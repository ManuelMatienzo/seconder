from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Client, Vehicle
from app.modules.gestion_usuarios.schemas import VehicleCreateRequest


def create_vehicle(db: Session, client_id: int, data: VehicleCreateRequest) -> Vehicle:
    client = db.get(Client, client_id)
    if not client:
        raise LookupError("Cliente no encontrado")

    plate = data.plate.upper()
    existing_vehicle = db.scalar(select(Vehicle).where(Vehicle.plate == plate))
    if existing_vehicle:
        raise ValueError("La placa del vehiculo ya esta registrada")

    vehicle = Vehicle(
        id_client=client_id,
        plate=plate,
        brand=data.brand,
        model=data.model,
        year=data.year,
        color=data.color,
        type=data.type,
    )
    db.add(vehicle)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("No se pudo registrar el vehiculo con los datos enviados") from exc

    db.refresh(vehicle)
    return vehicle


def list_client_vehicles(db: Session, client_id: int) -> list[Vehicle]:
    client = db.get(Client, client_id)
    if not client:
        raise LookupError("Cliente no encontrado")

    return list(
        db.scalars(
            select(Vehicle)
            .where(Vehicle.id_client == client_id, Vehicle.is_active.is_(True))
            .order_by(Vehicle.created_at.desc())
        )
    )
