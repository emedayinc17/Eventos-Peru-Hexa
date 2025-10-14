# created by emeday 2025
from dataclasses import dataclass

@dataclass
class User:
    id: str
    email: str
    password_hash: str
    status: int
    is_deleted: int
