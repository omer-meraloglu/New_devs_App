from decimal import Decimal, ROUND_HALF_UP
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.services.cache import get_revenue_summary
from app.core.auth import authenticate_request as get_current_user

router = APIRouter()

@router.get("/dashboard/summary")
async def get_dashboard_summary(
    property_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:

    tenant_id = getattr(current_user, "tenant_id", "default_tenant") or "default_tenant"

    revenue_data = await get_revenue_summary(property_id, tenant_id)

    # total_amount can carry sub-cent precision (see schema.sql), so round to
    # the nearest cent using Decimal before converting to float. Converting the
    # raw sub-cent value straight to float lets binary floating-point error
    # shift the displayed total by a cent.
    total_revenue_cents = Decimal(revenue_data['total']).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    return {
        "property_id": revenue_data['property_id'],
        "total_revenue": float(total_revenue_cents),
        "currency": revenue_data['currency'],
        "reservations_count": revenue_data['count']
    }
