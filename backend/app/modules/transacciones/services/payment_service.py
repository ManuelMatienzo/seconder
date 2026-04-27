from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Assignment, Incident, Payment
from app.modules.gestion_usuarios.services import create_notification
from app.modules.transacciones.schemas import PaymentCreateRequest


COMMISSION_RATE = Decimal("0.10")
MONEY_QUANTIZER = Decimal("0.01")


def create_incident_payment(
    db: Session,
    incident: Incident,
    data: PaymentCreateRequest,
) -> Payment:
    assignment = db.scalar(
        select(Assignment)
        .where(Assignment.id_incident == incident.id_incident)
        .order_by(Assignment.id_assignment.desc())
    )
    if not assignment:
        raise LookupError("No existe una atencion registrada para ese incidente")

    if assignment.status != "completado":
        raise PermissionError("El servicio aun no esta completado y no puede pagarse")

    existing_payment = db.scalar(select(Payment).where(Payment.id_assignment == assignment.id_assignment))
    if existing_payment:
        raise FileExistsError("El servicio ya fue pagado")

    platform_commission = (data.total_amount * COMMISSION_RATE).quantize(
        MONEY_QUANTIZER,
        rounding=ROUND_HALF_UP,
    )
    workshop_amount = (data.total_amount - platform_commission).quantize(
        MONEY_QUANTIZER,
        rounding=ROUND_HALF_UP,
    )

    payment = Payment(
        id_assignment=assignment.id_assignment,
        id_client=incident.id_client,
        total_amount=data.total_amount,
        platform_commission=platform_commission,
        workshop_amount=workshop_amount,
        payment_method=data.payment_method,
        payment_status="completado",
    )
    db.add(payment)
    create_notification(
        db,
        incident.id_client,
        "Pago realizado",
        "Tu pago del servicio fue registrado correctamente.",
        "payment",
    )
    create_notification(
        db,
        assignment.id_workshop,
        "Pago registrado",
        "Se registro el pago de un servicio completado para tu taller.",
        "payment",
    )

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("No se pudo registrar el pago") from exc

    db.refresh(payment)
    return payment
