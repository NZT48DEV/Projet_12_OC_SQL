from __future__ import annotations

from rich.console import Console

console = Console()


def success(message: str) -> None:
    console.print(f"✅ {message}", style="green")


def info(message: str) -> None:
    console.print(f"ℹ️  {message}", style="cyan")


def warning(message: str) -> None:
    console.print(f"⚠️  {message}", style="yellow")


def error(message: str) -> None:
    console.print(f"❌ {message}", style="red")


def forbidden(message: str) -> None:
    console.print(f"⛔ {message}", style="red")
