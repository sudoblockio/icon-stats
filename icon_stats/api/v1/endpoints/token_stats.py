from http import HTTPStatus
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlmodel import func, select

from icon_stats.db import get_session
from icon_stats.models.token_stats import TokenStats

router = APIRouter()


@router.get("/stats/tokens")
async def get_token_stats(
    response: Response,
    address: str,
    skip: int = Query(0),
    limit: int = Query(100, gt=0, lt=101),
    session: AsyncSession = Depends(get_session),
) -> list[TokenStats]:
    """Return list of delegations."""
    query = (
        select(TokenStats)
        .offset(skip)
        .limit(limit)
        .order_by(TokenStats.value.desc())
    )

    result = await session.execute(query)
    delegations = result.scalars().all()

    # Check if exists
    if len(delegations) == 0:
        return Response(status_code=HTTPStatus.NO_CONTENT.value)

    # Return the count in header
    query_count = select([func.count(TokenStats.address)]).where(TokenStats.address == address)
    result_count = await session.execute(query_count)
    total_count = str(result_count.scalars().all()[0])
    response.headers["x-total-count"] = total_count

    return delegations
