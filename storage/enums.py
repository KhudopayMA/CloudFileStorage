from enum import StrEnum, unique, auto

@unique
class ResourceTypes(StrEnum):
    FILE = auto()
    DIRECTORY = auto()
