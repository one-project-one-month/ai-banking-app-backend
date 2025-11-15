from pydantic import BaseModel


class textRequest(BaseModel):
    """Text Request Model"""

    SQL_QUERY: str
