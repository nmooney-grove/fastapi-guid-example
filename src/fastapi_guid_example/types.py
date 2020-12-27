from datetime import datetime, timedelta
from typing import Any, Dict
import uuid

from dataclasses import dataclass

def _construct_datetime(data: Any) -> datetime:
    out = datetime.now() + timedelta(days=30)
    if isinstance(data, int):
        out = datetime.fromtimestamp(data)
    if isinstance(data, datetime):
        out = data
    return out



@dataclass
class Entry:
    id_: uuid.UUID
    user: str
    expires: datetime

    @staticmethod
    def from_dict(dict_: Dict[str, Any]) -> "Entry":
        id_ = dict_.get("id_", uuid.uuid4()) # Generate new random guid if not provided
        user = dict_.get("user", "") # TODO not the best default for this

        expires_raw = dict_.get("expires")
        expires = _construct_datetime(expires_raw)

        if not all([id_, user, expires]):
            raise ValueError() # TODO expanding this will make it more usable
        return Entry(id_, user, expires)
