import re


def format_phone_fr(phone: str | None) -> str:
    """
    Formate un numéro français en format international lisible.
    Ex: 0601020304 -> +33 6 01 02 03 04
    """
    if not phone:
        return ""

    # Supprime tout sauf les chiffres
    digits = re.sub(r"\D", "", phone)

    # Format FR: 10 chiffres commençant par 0
    if len(digits) == 10 and digits.startswith("0"):
        digits = digits[1:]  # enlever le 0
        groups = [digits[i : i + 2] for i in range(0, len(digits), 2)]
        return "+33 " + " ".join(groups)

    # Fallback : inchangé si format inattendu
    return phone
