import re


def format_phone_fr(phone: str | None) -> str:
    """
    Formate un numéro français en format international lisible.
    Ex: 0601020304 -> +33 6 01 02 03 04
    """
    if not phone:
        return ""

    # Supprimer tout sauf les chiffres
    digits = re.sub(r"\D", "", phone)

    # Numéro FR attendu : 10 chiffres commençant par 0
    if len(digits) == 10 and digits.startswith("0"):
        digits = digits[1:]  # enlever le 0 → ex: 612345678

        first = digits[0]  # 6
        rest = digits[1:]  # 12345678
        groups = [rest[i : i + 2] for i in range(0, len(rest), 2)]

        return "+33 " + first + " " + " ".join(groups)

    # Fallback si format inconnu
    return phone
