from app.core.security import hash_password, verify_password


def test_hash_and_verify_password_ok():
    password = "S3cret!!"
    pwd_hash = hash_password(password)

    assert isinstance(pwd_hash, str)
    assert pwd_hash != password
    assert verify_password(password, pwd_hash) is True


def test_verify_password_wrong_password():
    pwd_hash = hash_password("S3cret!!")
    assert verify_password("wrong", pwd_hash) is False
