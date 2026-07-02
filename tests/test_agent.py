"""Tests for the main agent process_request function."""

import pytest
from crochet_agent.agent import process_request


class TestProcessRequest:
    """Test the main process_request function."""

    def test_beanie_request_returns_pattern(self):
        result = process_request("make me a beanie hat", use_us=False)
        assert "BEANIE" in result.upper() or "HAT" in result.upper()
        assert "UK" in result

    def test_beanie_request_us_terminology(self):
        result = process_request("make me a beanie hat", use_us=True)
        assert "US" in result

    def test_scarf_returns_pattern(self):
        result = process_request("simple scarf", use_us=False)
        assert len(result) > 100
        assert "SCARF" in result.upper()

    def test_granny_square_returns_pattern(self):
        result = process_request("granny square", use_us=False)
        assert "GRANNY" in result.upper()

    def test_dishcloth_returns_pattern(self):
        result = process_request("dishcloth", use_us=False)
        assert "DISHCLOTH" in result.upper() or "FACECLOTH" in result.upper()

    def test_bag_returns_pattern(self):
        result = process_request("market bag", use_us=False)
        assert "BAG" in result.upper()

    def test_blanket_returns_pattern(self):
        result = process_request("blanket", use_us=False)
        assert "BLANKET" in result.upper() or "THROW" in result.upper()

    def test_amigurumi_returns_pattern(self):
        result = process_request("amigurumi toy", use_us=False)
        assert "AMIGURUMI" in result.upper()

    def test_unknown_item_returns_web_resources(self):
        result = process_request("complex cable stitch jumper", use_us=False)
        assert "ravelry.com" in result.lower() or "google.com" in result.lower()

    def test_unknown_item_mentions_input(self):
        result = process_request("lace tablecloth", use_us=False)
        assert "lace tablecloth" in result.lower() or "lace" in result.lower()

    def test_empty_request(self):
        result = process_request("", use_us=False)
        assert len(result) > 0  # graceful response

    def test_uk_pattern_contains_uk_abbreviations(self):
        result = process_request("beanie hat", use_us=False)
        # UK pattern should use 'tr' for treble crochet
        assert "tr" in result

    def test_us_pattern_converts_abbreviations(self):
        result = process_request("beanie hat", use_us=True)
        # US pattern should use 'sc' instead of UK 'dc'
        assert "sc" in result

    def test_whitespace_only_request(self):
        result = process_request("   ", use_us=False)
        assert len(result) > 0
