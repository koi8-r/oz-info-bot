from datetime import datetime
from typing import List, Optional, Dict

from pydantic import Field, Extra, BaseConfig, BaseModel


class Model(BaseModel):
    class Config(BaseConfig):
        extra = Extra.allow


class Result(Model):
    free_participants: int = Field(alias='freeParticipantCount')
    free_tickets: int = Field(alias='freeTicketCount')
    name: str = Field(alias='name')
    nearest_date: Optional[datetime] = Field(alias='nearestDate')
    last_date: Optional[datetime] = Field(alias='lastDate')


class Response(Model):
    result: List[Result]


class HttpBinResponse(Model):
    headers: Dict[str, str]
    origin: str
