from __future__ import annotations

from csw_bench.textnorm import normalize, tokenize


def test_diacritics_and_case_are_folded() -> None:
    assert normalize("Compré") == normalize("compre")


def test_punctuation_collapses_without_breaking_matches() -> None:
    """A response wrapping the answer in quotes or list markers must still contain the
    normalized item text as a substring.
    """
    assert normalize("Compré los libros ayer.") in normalize('(1) "Compré los libros ayer."')


def test_whitespace_runs_collapse() -> None:
    assert normalize("los  libros,   ayer") == "los libros ayer"


def test_tokenize_splits_normalized_words() -> None:
    assert tokenize("Compré the libros, ayer.") == ["compre", "the", "libros", "ayer"]
