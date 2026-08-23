import re

TRANSLATOR_PATTERNS = [
    re.compile(
        r"(?:tradu[cç][aã]o|traduzido|traduzida|translator|translation)"
        r"\s*(?:por|by|:)?\s*([A-ZÀ-Ý][^.!?\n]{1,80})",
        re.I
    ),
]

INTERVIEW_TITLE_MARKERS = (
    "diz",
    "afirma",
    "fala",
    "conta",
    "revela",
    "comenta",
    "explica",
    "avalia",
    "detalha",
    "admite",
    "destaca",
)
