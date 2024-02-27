from http import HTTPStatus

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlmodel import select

from icon_stats.db import get_session_api
from icon_stats.models.applications import Application
from icon_stats.models.contracts import Contract
from icon_stats.models.ecosystem import Ecosystem
from icon_stats.models.tokens import Token

router = APIRouter()


@router.get("/ecosystem")
async def get_ecosystem_stats(
    response: Response,
    session: AsyncSession = Depends(get_session_api),
) -> list[Ecosystem]:
    """Return list of ecosystem stats."""
    query = select(Ecosystem)

    result = await session.execute(query)
    output = result.scalars().all()

    if len(output) == 0:
        response.status_code = HTTPStatus.NO_CONTENT.value
        return []

    response.headers["x-total-count"] = str(len(output))
    return output


@router.get("/applications")
async def get_application_stats(
    response: Response,
    session: AsyncSession = Depends(get_session_api),
) -> list[Application]:
    """Return list of application stats."""
    query = select(Application)

    result = await session.execute(query)
    output = result.scalars().all()

    if len(output) == 0:
        response.status_code = HTTPStatus.NO_CONTENT.value
        return []

    response.headers["x-total-count"] = str(len(output))
    return output


@router.get("/contracts")
async def get_contract_stats(
    response: Response,
    session: AsyncSession = Depends(get_session_api),
) -> list[Contract]:
    """Return list of contract stats."""
    query = select(Contract)

    result = await session.execute(query)
    output = result.scalars().all()

    if len(output) == 0:
        response.status_code = HTTPStatus.NO_CONTENT.value
        return []

    response.headers["x-total-count"] = str(len(output))

    return output


@router.get("/tokens")
async def get_token_stats(
    response: Response,
    session: AsyncSession = Depends(get_session_api),
) -> list[Token]:
    """Return list of token stats."""
    query = select(Token)

    result = await session.execute(query)
    output = result.scalars().all()

    if len(output) == 0:
        response.status_code = HTTPStatus.NO_CONTENT.value
        return []

    response.headers["x-total-count"] = str(len(output))

    return output
