from dataclasses import dataclass


@dataclass(slots=True, frozen=True, kw_only=True)
class ResourceMetaDto:
    path: str
    name: str
    size: int
    type: str
