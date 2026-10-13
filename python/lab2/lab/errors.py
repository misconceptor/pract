"""Custom exception hierarchy for the students manager.

All application errors inherit from :class:`LabError`, so callers can
catch every expected problem with one `except LabError`.
"""

from __future__ import annotations


class LabError(Exception):
    """Base class for every application error."""


class ValidationError(LabError):
    """Invalid data: out-of-range grade, empty name, negative id, etc."""


class DuplicateIdError(LabError):
    """A student with the given ID already exists."""


class StudentNotFoundError(LabError):
    """No student with the given ID was found."""


class CsvFormatError(LabError):
    """CSV file has invalid structure or unparsable values."""