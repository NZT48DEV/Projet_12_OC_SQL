from __future__ import annotations

from app.models.employee import Role


class AuthorizationError(Exception):
    """Erreur levée quand l'utilisateur n'a pas les permissions requises."""


def require_role(current_role: Role, allowed: set[Role]) -> None:
    """
    Vérifie que le rôle courant fait partie des rôles autorisés.

    Args:
        current_role: rôle de l'utilisateur courant.
        allowed: ensemble de rôles autorisés.

    Raises:
        AuthorizationError: si current_role n'est pas autorisé.
    """
    if current_role not in allowed:
        raise AuthorizationError(
            f"Accès refusé. Rôle requis: {', '.join(r.value for r in allowed)}."
        )
