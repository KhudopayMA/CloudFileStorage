from enum import StrEnum, auto, unique


@unique
class ResourceTypes(StrEnum):
    FILE = auto()
    DIRECTORY = auto()
