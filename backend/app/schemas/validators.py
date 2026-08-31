"""
Shared Pydantic field-validator logic, reused across schemas instead of
each one re-implementing the same character-set/blank checks.
"""


def validate_ascii_printable_charset(value: str, field_label: str) -> str:
    """Restricts to printable ASCII (standard keyboard characters) --
    letters, numbers, and symbols, no emoji/accented letters/control
    characters. Originally added for passwords, where it's what lets
    MAX_PASSWORD_LENGTH safely equal bcrypt's 72-byte limit (every
    character is guaranteed exactly 1 byte) -- reused here for anything
    else that wants the same "no exotic characters" guarantee."""
    if not (value.isascii() and value.isprintable()):
        raise ValueError(f"{field_label} may only contain letters, numbers, and symbols.")
    return value


def validate_not_blank(value: str, field_label: str) -> str:
    """Strips surrounding whitespace and rejects the result if that
    leaves nothing -- e.g. a program name of "    " passes a plain
    min_length check (4 characters) but shouldn't be accepted, and
    shouldn't be stored with incidental leading/trailing padding either."""
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{field_label} cannot be blank.")
    return stripped
