from pydantic import BaseModel


class ListQueryParams(BaseModel):
    skip: int = 0
    limit: int = 100

