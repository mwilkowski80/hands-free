import pytest
from handsfree.transcriber import clean_transcription

@pytest.mark.parametrize("input_text,expected", [
    # Podstawowe przypadki
    ("Normalny tekst", "Normalny tekst"),
    ("  Tekst ze spacjami  ", "Tekst ze spacjami"),
    
    # Przypadki z minusem z przodu
    ("-Tekst z minusem", "Tekst z minusem"),
    ("- Tekst z minusem i spacją", "Tekst z minusem i spacją"),
    ("--Tekst z dwoma minusami", "Tekst z dwoma minusami"),
    ("-- Tekst z dwoma minusami i spacją", "Tekst z dwoma minusami i spacją"),
    
    # Kombinacje minusów i spacji
    ("-  Tekst z minusem i wieloma spacjami", "Tekst z minusem i wieloma spacjami"),
    ("--  Tekst z dwoma minusami i wieloma spacjami", "Tekst z dwoma minusami i wieloma spacjami"),
    
    # Przypadki brzegowe
    ("", ""),
    (" ", ""),
    ("-", ""),
    ("--", ""),
    ("- ", ""),
    ("-- ", ""),
    (" - ", ""),
    (" -- ", ""),
    ("-  Czat, ja chcę", "Czat, ja chcę"),
    ("--   Czat, ja chcę", "Czat, ja chcę"),
    
    # Przypadki z minusem w środku tekstu (nie powinny być zmienione)
    ("Tekst z - w środku", "Tekst z - w środku"),
    ("Tekst z -- w środku", "Tekst z -- w środku"),
])
def test_clean_transcription(input_text, expected):
    assert clean_transcription(input_text) == expected 