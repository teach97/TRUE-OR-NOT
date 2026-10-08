"""Text length helpers shared by extraction and direct-check flows."""

def _truncate_units(text: str, max_units: int) -> str:
    """Truncate to a UTF-16 unit budget without splitting astral characters."""
    units = 0
    out: list[str] = []
    for char in text:
        units += 2 if ord(char) > 0xFFFF else 1
        if units > max_units:
            break
        out.append(char)
    return "".join(out)
