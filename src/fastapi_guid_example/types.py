import uuid
import datetime

from dataclasses import dataclass


@dataclass
class Entry:
    id_: uuid.UUID
    user: str
    expires: datetime.datetime
