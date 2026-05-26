from typing import Optional


def build_display_name(
    *,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    username: Optional[str] = None,
    email: Optional[str] = None,
) -> str:
    """Human-readable name for UI (ник / отображаемое имя)."""
    parts = [str(first_name or "").strip(), str(last_name or "").strip()]
    full = " ".join(part for part in parts if part)
    if full:
        return full
    if username and str(username).strip():
        return str(username).strip()
    if email and str(email).strip():
        return str(email).strip()
    return ""
