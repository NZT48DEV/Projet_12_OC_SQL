from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash Argon2 (sel inclus) pour stockage en DB."""
    if not password or password.strip() == "":
        raise ValueError("Le mot de passe ne peut pas être vide.")
    return _ph.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Vérifie un mot de passe en clair contre un hash Argon2 stocké."""
    if not password_hash:
        return False
    try:
        return _ph.verify(password_hash, password)
    except VerifyMismatchError:
        return False
