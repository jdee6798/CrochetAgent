"""Tests for UK/US terminology conversion."""

import pytest
from crochet_agent.terminology import (
    convert_pattern_to_us,
    terminology_note,
    stitch_glossary,
    UK_TO_US,
    UK_ABBR_TO_US_ABBR,
)


class TestUkToUsMapping:
    """Test that the UK_TO_US mapping is complete and consistent."""

    def test_all_entries_have_four_fields(self):
        for uk_name, value in UK_TO_US.items():
            assert len(value) == 3, f"Entry '{uk_name}' should have 3 values"

    def test_key_stitch_mappings(self):
        assert UK_TO_US["double crochet"][0] == "dc"
        assert UK_TO_US["double crochet"][1] == "single crochet"
        assert UK_TO_US["double crochet"][2] == "sc"

        assert UK_TO_US["treble crochet"][0] == "tr"
        assert UK_TO_US["treble crochet"][1] == "double crochet"
        assert UK_TO_US["treble crochet"][2] == "dc"

        assert UK_TO_US["half treble crochet"][0] == "htr"
        assert UK_TO_US["half treble crochet"][1] == "half double crochet"
        assert UK_TO_US["half treble crochet"][2] == "hdc"

    def test_same_stitches_unchanged(self):
        # slip stitch and chain are the same in both systems
        assert UK_TO_US["slip stitch"][1] == "slip stitch"
        assert UK_TO_US["chain"][1] == "chain"


class TestConvertPatternToUs:
    """Test the text conversion from UK to US terminology."""

    def test_converts_double_crochet(self):
        uk = "Work 1 dc in each st."
        us = convert_pattern_to_us(uk)
        assert "sc" in us
        assert "dc" not in us.replace("double crochet", "")  # dc → sc, treble stays

    def test_converts_treble_crochet_name(self):
        uk = "Work 1 treble crochet in next st."
        us = convert_pattern_to_us(uk)
        assert "double crochet" in us

    def test_converts_htr_abbreviation(self):
        uk = "Work 1 htr in next st."
        us = convert_pattern_to_us(uk)
        assert "hdc" in us
        assert "htr" not in us

    def test_chain_unchanged(self):
        uk = "Ch 10, sl st to join."
        us = convert_pattern_to_us(uk)
        assert "ch" in us.lower()
        assert "sl st" in us

    def test_magic_ring_unchanged(self):
        uk = "Start with a magic ring (MR)."
        us = convert_pattern_to_us(uk)
        assert "magic ring" in us
        assert "MR" in us

    def test_empty_string(self):
        assert convert_pattern_to_us("") == ""

    def test_no_crochet_text_unchanged(self):
        text = "Hello, world!"
        assert convert_pattern_to_us(text) == text


class TestTerminologyNote:
    """Test the terminology note helper."""

    def test_uk_note_mentions_uk(self):
        note = terminology_note(use_us=False)
        assert "UK" in note

    def test_us_note_mentions_us(self):
        note = terminology_note(use_us=True)
        assert "US" in note

    def test_uk_note_has_abbreviations(self):
        note = terminology_note(use_us=False)
        assert "dc=" in note or "dc =" in note

    def test_us_note_has_abbreviations(self):
        note = terminology_note(use_us=True)
        assert "sc=" in note or "sc =" in note


class TestStitchGlossary:
    """Test the stitch glossary output."""

    def test_glossary_contains_key_stitches(self):
        glossary = stitch_glossary(use_us=False)
        assert "double crochet" in glossary
        assert "treble crochet" in glossary
        assert "half treble crochet" in glossary

    def test_glossary_uk_label(self):
        glossary = stitch_glossary(use_us=False)
        assert "UK" in glossary

    def test_glossary_us_label(self):
        glossary = stitch_glossary(use_us=True)
        assert "US" in glossary

    def test_glossary_shows_equivalents(self):
        glossary = stitch_glossary(use_us=False)
        assert "=" in glossary  # shows UK = US equivalents
