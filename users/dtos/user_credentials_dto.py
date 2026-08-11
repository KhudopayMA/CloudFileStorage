from dataclasses import dataclass

@dataclass(slots=True, kw_only=True, frozen=True)
class UserCredentialsDto:
    username: str
    password: str