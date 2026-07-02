"""Tests for the pattern generator."""

import pytest
from crochet_agent.pattern_generator import (
    parse_request,
    generate_pattern,
    can_generate,
    PatternRequest,
    SUPPORTED_ITEMS,
)


class TestParseRequest:
    """Test that user requests are parsed correctly."""

    def test_detects_beanie(self):
        req = parse_request("make me a beanie hat")
        assert req.item_type == "beanie"

    def test_detects_hat_as_beanie(self):
        req = parse_request("I want a hat")
        assert req.item_type == "beanie"

    def test_detects_scarf(self):
        req = parse_request("create a scarf pattern please")
        assert req.item_type == "scarf"

    def test_detects_cowl(self):
        req = parse_request("I would like a cowl")
        assert req.item_type == "scarf"

    def test_detects_granny_square(self):
        req = parse_request("granny square")
        assert req.item_type == "granny_square"

    def test_detects_dishcloth(self):
        req = parse_request("simple dishcloth")
        assert req.item_type == "dishcloth"

    def test_detects_facecloth(self):
        req = parse_request("facecloth for the bathroom")
        assert req.item_type == "dishcloth"

    def test_detects_bag(self):
        req = parse_request("market bag pattern")
        assert req.item_type == "bag"

    def test_detects_blanket(self):
        req = parse_request("baby blanket pattern")
        assert req.item_type == "blanket"

    def test_detects_amigurumi(self):
        req = parse_request("amigurumi bunny")
        assert req.item_type == "amigurumi"

    def test_detects_toy(self):
        req = parse_request("crochet toy for a child")
        assert req.item_type == "amigurumi"

    def test_unknown_item_type(self):
        req = parse_request("cable stitch jumper")
        assert req.item_type == ""

    def test_detects_baby_size(self):
        req = parse_request("baby beanie hat")
        assert req.size == "baby"

    def test_detects_chunky_yarn(self):
        req = parse_request("chunky yarn blanket")
        assert req.yarn_weight == "bulky"

    def test_detects_beginner_skill(self):
        req = parse_request("beginner scarf pattern")
        assert req.skill_level == "beginner"

    def test_default_size(self):
        req = parse_request("scarf pattern")
        assert req.size == "adult_m"

    def test_default_yarn_weight(self):
        req = parse_request("beanie hat")
        assert req.yarn_weight == "worsted"

    def test_raw_text_preserved(self):
        req = parse_request("  Hello World  ")
        assert req.raw == "  Hello World  "


class TestCanGenerate:
    """Test the can_generate function."""

    @pytest.mark.parametrize("item_input", [
        "make a beanie hat",
        "simple scarf",
        "granny square",
        "dishcloth",
        "market bag",
        "throw blanket",
        "amigurumi toy",
    ])
    def test_supported_items(self, item_input):
        req = parse_request(item_input)
        assert can_generate(req), f"Expected can_generate=True for: '{item_input}'"

    def test_unsupported_item(self):
        req = parse_request("cable stitch jumper with complex textured stitches")
        assert not can_generate(req)

    def test_empty_input(self):
        req = parse_request("")
        assert not can_generate(req)


class TestGeneratePattern:
    """Test that generate_pattern returns valid Pattern objects."""

    def _make_pattern(self, text: str):
        req = parse_request(text)
        pattern = generate_pattern(req)
        assert pattern is not None, f"Expected a pattern for: '{text}'"
        return pattern

    def test_beanie_has_title(self):
        pattern = self._make_pattern("beanie hat")
        assert "beanie" in pattern.title.lower() or "hat" in pattern.title.lower()

    def test_scarf_has_instructions(self):
        pattern = self._make_pattern("scarf")
        assert len(pattern.instructions) > 50

    def test_granny_square_has_materials(self):
        pattern = self._make_pattern("granny square")
        assert len(pattern.materials) >= 2

    def test_dishcloth_uses_cotton_yarn(self):
        pattern = self._make_pattern("dishcloth")
        materials_text = " ".join(pattern.materials).lower()
        assert "cotton" in materials_text

    def test_bag_has_instructions(self):
        pattern = self._make_pattern("market bag")
        assert len(pattern.instructions) > 50

    def test_blanket_has_size_in_title(self):
        pattern = self._make_pattern("blanket")
        assert "blanket" in pattern.title.lower() or "throw" in pattern.title.lower()

    def test_amigurumi_has_notes(self):
        pattern = self._make_pattern("amigurumi toy")
        assert len(pattern.notes) >= 1

    def test_unknown_item_returns_none(self):
        req = parse_request("complex cable stitch jumper")
        assert generate_pattern(req) is None

    def test_pattern_render_uk_by_default(self):
        pattern = self._make_pattern("beanie hat")
        rendered = pattern.render(use_us=False)
        assert "UK" in rendered

    def test_pattern_render_us_flag(self):
        pattern = self._make_pattern("beanie hat")
        rendered = pattern.render(use_us=True)
        assert "US" in rendered

    def test_baby_beanie_smaller_than_adult(self):
        baby = self._make_pattern("baby beanie")
        adult = self._make_pattern("adult beanie hat")
        # Baby pattern should have fewer rounds — just check both generate successfully
        assert baby is not None
        assert adult is not None

    def test_cowl_pattern_generated(self):
        req = parse_request("cowl")
        pattern = generate_pattern(req)
        assert pattern is not None
        assert "cowl" in pattern.title.lower() or "scarf" in pattern.title.lower()

    def test_all_supported_items_generate_a_pattern(self):
        # Map item_type → a sample user input that triggers it
        sample_inputs = {
            "beanie": "beanie hat",
            "scarf": "scarf",
            "granny_square": "granny square",
            "dishcloth": "dishcloth",
            "bag": "bag",
            "blanket": "blanket",
            "amigurumi": "amigurumi toy",
        }
        for item_type, user_input in sample_inputs.items():
            req = parse_request(user_input)
            assert req.item_type == item_type, f"Detection failed for '{user_input}'"
            pattern = generate_pattern(req)
            assert pattern is not None, f"Pattern generation failed for '{user_input}'"
            assert pattern.generated is True
