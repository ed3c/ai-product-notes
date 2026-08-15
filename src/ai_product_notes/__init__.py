"""AI Product Notes deterministic opportunity compiler."""

from .compiler import ValidationError, canonical_json, compile_opportunity, validate_packet

__all__ = [
    "ValidationError",
    "canonical_json",
    "compile_opportunity",
    "validate_packet",
]
