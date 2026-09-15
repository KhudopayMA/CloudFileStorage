from enum import StrEnum, unique


@unique
class ResourceTypes(StrEnum):
    FILE = "FILE"
    DIRECTORY = "DIRECTORY"
