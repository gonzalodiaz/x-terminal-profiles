"""Minimal TOML serializer for writing profile configs.

Only supports flat key-value pairs and sections (tables) — no nested tables,
arrays of tables, or inline tables. This is sufficient for profile.toml files.
"""

from __future__ import annotations


def dumps(data: dict) -> str:
    """Serialize a dict to a TOML string.

    Top-level string keys without dict values are written first as bare key-value pairs.
    Dict values become [section] tables.
    """
    lines: list[str] = []

    # Write top-level bare key-value pairs first
    for key, value in data.items():
        if not isinstance(value, dict):
            lines.append(f"{key} = {_format_value(value)}")

    # Write sections
    for key, value in data.items():
        if isinstance(value, dict):
            if lines:
                lines.append("")
            lines.append(f"[{key}]")
            for k, v in value.items():
                lines.append(f"{k} = {_format_value(v)}")

    lines.append("")  # trailing newline
    return "\n".join(lines)


def _format_value(value: object) -> str:
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return str(value)
    raise TypeError(f"Unsupported TOML value type: {type(value)}")
