import pytest

from app.core.security import hash_password, verify_password


def test_hash_and_verify_password_ok():
    """Hash puis vérifie un mot de passe valide."""
    password = "S3cret!!"
    pwd_hash = hash_password(password)

    assert isinstance(pwd_hash, str)
    assert pwd_hash != password
    assert verify_password(password, pwd_hash) is True


def test_verify_password_wrong_password():
    """Retourne False si le mot de passe ne correspond pas au hash."""
    pwd_hash = hash_password("S3cret!!")
    assert verify_password("wrong", pwd_hash) is False


def test_hash_password_raises_when_empty():
    """Lève ValueError si le mot de passe est vide ou blanc."""
    with pytest.raises(ValueError):
        hash_password("")

    with pytest.raises(ValueError):
        hash_password("   ")


def test_verify_password_returns_false_when_hash_missing():
    """Retourne False si le hash est vide (ou absent)."""
    assert verify_password("whatever", "") is False
    assert verify_password("whatever", None) is False
