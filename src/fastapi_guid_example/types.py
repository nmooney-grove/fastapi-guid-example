"""Definitions for Domain Types.

Mostly that's just Entry.
"""
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Mapping
import uuid

import dataclasses

def _construct_datetime(data: Any) -> datetime:
    out = datetime.now() + timedelta(days=30)
    if isinstance(data, int):
        out = datetime.fromtimestamp(data)
    if isinstance(data, datetime):
        out = data
    return out



@dataclasses.dataclass
class Entry:
    """Core data type. A generic mapping of a GUID to some metadata."""

    guid: uuid.UUID
    user: str
    expires: datetime

    def dict(self, timestamp: bool = False):
        """Return a dictionary representation of the Entry."""
        out = dataclasses.asdict(self)
        if timestamp:
            out["expires"] = datetime.timestamp(out["expires"])
        return out

    @staticmethod
    def from_dict(dict_: Mapping[str, Any]) -> "Entry":
        """Given a dictionary, create an Entry.

        This implementation is VERY permissive:
        - Additional keys are ignored
        - Missing keys are replaced by defaults of varying quality
        """
        guid = dict_.get("guid", uuid.uuid4()) # Generate new random guid if not provided
        user = dict_.get("user", "") # TODO not the best default for this

        expires_raw = dict_.get("expires")
        expires = _construct_datetime(expires_raw)

        if not all([guid, user, expires]):
            raise ValueError() # TODO expanding this will make it more usable
        return Entry(guid, user, expires)