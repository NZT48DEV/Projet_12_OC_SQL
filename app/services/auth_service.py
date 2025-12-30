from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.repositories.employee_repository import EmployeeRepository


class AuthenticationError(Exception):
    """Identifiants invalides."""


def authenticate_employee(session: Session, email: str, password: str):
    """
    Authentifie un employé via email + mot de passe.

    Retourne l'Employee si OK, sinon lève AuthenticationError.
    Refuse la connexion si le compte est désactivé (soft delete).
    """
    repo = EmployeeRepository(session)
    employee = repo.get_by_email(email)

    # Message générique (ne pas révéler si l'email existe)
    if employee is None or not verify_password(password, employee.password_hash):
        raise AuthenticationError("Email ou mot de passe invalide.")

    # Soft delete : compte désactivé => pas de connexion
    if not employee.is_active:
        raise AuthenticationError("Compte désactivé.")

    return employee
