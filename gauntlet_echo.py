"""Minimal local Gauntlet echo tool, independent of ArmorIQ."""


def gauntlet__echo(message: str) -> str:
    """Return a string unchanged; reject values that are not strings."""
    if not isinstance(message, str):
        raise TypeError("message must be a string")
    return message
