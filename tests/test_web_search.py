"""Tests for the web search helper."""

import pytest
from crochet_agent.web_search import (
    ravelry_search_url,
    google_search_url,
    lovecrafts_search_url,
    youtube_search_url,
    get_web_resources,
    format_web_resources,
)


class TestSearchUrls:
    """Test that search URLs are well-formed."""

    def test_ravelry_url_contains_query(self):
        url = ravelry_search_url("beanie hat")
        assert "beanie" in url or "beanie+hat" in url or "beanie%20hat" in url

    def test_ravelry_url_is_ravelry(self):
        url = ravelry_search_url("scarf")
        assert "ravelry.com" in url

    def test_google_url_contains_query(self):
        url = google_search_url("granny square")
        assert "google.com" in url
        assert "granny" in url or "granny+square" in url or "granny%20square" in url

    def test_lovecrafts_url_contains_query(self):
        url = lovecrafts_search_url("dishcloth")
        assert "lovecrafts.com" in url

    def test_youtube_url_is_youtube(self):
        url = youtube_search_url("amigurumi bunny")
        assert "youtube.com" in url

    def test_urls_are_strings(self):
        for fn in [ravelry_search_url, google_search_url,
                   lovecrafts_search_url, youtube_search_url]:
            result = fn("test query")
            assert isinstance(result, str)
            assert result.startswith("http")


class TestGetWebResources:
    """Test the get_web_resources helper."""

    def test_returns_list(self):
        resources = get_web_resources("blanket")
        assert isinstance(resources, list)

    def test_returns_multiple_resources(self):
        resources = get_web_resources("blanket")
        assert len(resources) >= 3

    def test_each_resource_has_required_keys(self):
        resources = get_web_resources("blanket")
        for resource in resources:
            assert "name" in resource
            assert "description" in resource
            assert "url" in resource

    def test_resource_urls_are_valid(self):
        resources = get_web_resources("scarf")
        for resource in resources:
            assert resource["url"].startswith("http")

    def test_ravelry_in_resources(self):
        resources = get_web_resources("hat")
        names = [r["name"] for r in resources]
        assert "Ravelry" in names


class TestFormatWebResources:
    """Test the formatted web resources output."""

    def test_format_mentions_query(self):
        text = format_web_resources("cable stitch jumper")
        assert "cable stitch jumper" in text

    def test_format_contains_urls(self):
        text = format_web_resources("jumper")
        assert "http" in text

    def test_format_is_string(self):
        text = format_web_resources("socks")
        assert isinstance(text, str)

    def test_format_contains_ravelry(self):
        text = format_web_resources("hat")
        assert "Ravelry" in text
