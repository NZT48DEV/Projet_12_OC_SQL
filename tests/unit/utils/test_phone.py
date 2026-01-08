from __future__ import annotations

from app.utils.phone import format_phone_fr


def test_format_phone_fr_none_returns_empty():
    assert format_phone_fr(None) == ""


def test_format_phone_fr_empty_returns_empty():
    assert format_phone_fr("") == ""


def test_format_phone_fr_plain_mobile():
    # 06 12 34 56 78 -> +33 6 12 34 56 78
    assert format_phone_fr("0612345678") == "+33 6 12 34 56 78"


def test_format_phone_fr_with_spaces():
    assert format_phone_fr("06 12 34 56 78") == "+33 6 12 34 56 78"


def test_format_phone_fr_with_dashes():
    assert format_phone_fr("06-12-34-56-78") == "+33 6 12 34 56 78"


def test_format_phone_fr_unknown_format_fallback():
    # si format inattendu -> renvoyé tel quel
    assert format_phone_fr("123") == "123"
