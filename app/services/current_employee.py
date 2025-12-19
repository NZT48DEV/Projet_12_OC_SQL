from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.jwt_service import TokenError, employee_id_from_access_token
from app.core.token_store import load_access_token
from app.repositories.employee_repository import EmployeeRepository


class NotAuthenticatedError(Exception):
    """Aucun utilisateur authentifié (ou token invalide/expiré)."""


def get_current_employee(session: Session):
    """
    Récupère l'employé courant via l'access token stocké localement.
    """
    token = load_access_token()
    if not token:
        raise NotAuthenticatedError(
            "Non authentifié : aucun token local trouvé. Faites `login`."
        )

    try:
        employee_id = employee_id_from_access_token(token)
    except TokenError as exc:
        raise NotAuthenticatedError(
            f"Non authentifié : {exc} Faites `refresh-token` ou `login`."
        ) from exc

    repo = EmployeeRepository(session)
    employee = repo.get_by_id(employee_id)
    if employee is None:
        raise NotAuthenticatedError("Utilisateur introuvable pour ce token.")
    return employee
