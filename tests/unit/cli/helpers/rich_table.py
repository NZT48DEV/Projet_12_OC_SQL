from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.table import Table


def capture_table(monkeypatch, module_with_console: Any) -> dict:
    """Capture le dernier objet imprimé via console.print()."""
    printed: dict = {}

    def fake_print(obj):
        printed["obj"] = obj

    monkeypatch.setattr(module_with_console.console, "print", fake_print)
    return printed


def get_table(printed: dict) -> Table:
    """Retourne l'objet Table capturé (ou lève une AssertionError)."""
    obj = printed.get("obj")
    assert obj is not None, "Aucune Table Rich n'a été imprimée."
    assert isinstance(obj, Table), f"Objet imprimé inattendu: {type(obj)}"
    return obj


def table_headers(table: Table) -> list[str]:
    """Retourne les en-têtes de colonnes (texte)."""
    return [c.header for c in table.columns]


def table_text(table: Table, *, width: int = 5000) -> str:
    """
    Rend la table via un Console(record=True) pour obtenir un texte complet,
    sans dépendre du terminal ni des ellipsis/troncatures.
    """
    console = Console(
        record=True,
        width=width,
        force_terminal=True,
        color_system=None,
    )
    console.print(table)
    return console.export_text(clear=False)


def table_all_text(table: Table) -> str:
    """Alias pratique pour faire des asserts 'contains' robustes."""
    return table_text(table)
