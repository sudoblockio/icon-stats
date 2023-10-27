import pytest
from sqlmodel import SQLModel
from sqlalchemy.orm.exc import UnmappedInstanceError

from icon_stats.db import upsert_model


@pytest.mark.asyncio
async def test_upsert_model_table_not_exists():
    class DoesNotExist(SQLModel):
        foo: str = "bar"

    test_model = DoesNotExist()

    with pytest.raises(UnmappedInstanceError):
        await upsert_model(db_name='stats', model=test_model)
