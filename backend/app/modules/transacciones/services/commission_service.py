from datetime import datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Payment
from app.modules.transacciones.schemas import CommissionFilterParams


ZERO = Decimal("0.00")


def _base_commission_query():
    return select(Payment)


def _apply_commission_filters(stmt, filters: CommissionFilterParams):
    if filters.payment_status:
        stmt = stmt.where(Payment.payment_status == filters.payment_status)

    if filters.date_from is not None:
        stmt = stmt.where(Payment.created_at >= datetime.combine(filters.date_from, time.min))

    if filters.date_to is not None:
        stmt = stmt.where(Payment.created_at < datetime.combine(filters.date_to + timedelta(days=1), time.min))

    return stmt


def list_commissions(db: Session, filters: CommissionFilterParams) -> list[dict]:
    stmt = _apply_commission_filters(_base_commission_query(), filters)
    stmt = stmt.order_by(Payment.created_at.desc(), Payment.id_payment.desc())

    payments = list(db.scalars(stmt))
    return [
        {
            "id_payment": payment.id_payment,
            "id_assignment": payment.id_assignment,
            "total_amount": payment.total_amount,
            "platform_commission": payment.platform_commission,
            "workshop_amount": payment.workshop_amount,
            "payment_method": payment.payment_method,
            "payment_status": payment.payment_status,
            "created_at": payment.created_at,
        }
        for payment in payments
    ]


def get_commissions_summary(db: Session, filters: CommissionFilterParams) -> dict:
    stmt = select(
        func.count(Payment.id_payment),
        func.sum(Payment.total_amount),
        func.sum(Payment.platform_commission),
        func.sum(Payment.workshop_amount),
    )
    stmt = _apply_commission_filters(stmt, filters)

    total_transactions, total_amount, total_commission, total_workshop_earnings = db.execute(stmt).one()

    return {
        "total_transactions": total_transactions or 0,
        "total_amount": total_amount or ZERO,
        "total_commission": total_commission or ZERO,
        "total_workshop_earnings": total_workshop_earnings or ZERO,
    }
