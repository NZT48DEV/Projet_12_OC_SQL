"""Tests unitaires pour l'autorisation (require_role)."""

import pytest

from app.core.authorization import AuthorizationError, require_role
from app.models.employee import Role


def test_require_role_allows_when_in_allowed():
    """Autorise quand le rôle courant est dans la liste des rôles autorisés."""
    require_role(Role.MANAGEMENT, {Role.MANAGEMENT})


def test_require_role_denies_when_not_in_allowed():
    """Refuse quand le rôle courant n'est pas autorisé."""
    with pytest.raises(AuthorizationError) as exc:
        require_role(Role.SALES, {Role.MANAGEMENT})

    assert "MANAGEMENT" in str(exc.value)
