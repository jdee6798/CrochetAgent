"""Tests for the web app and API."""

from crochet_agent.webapp import app


class TestWebApp:
    """Smoke tests for the browser app and API route."""

    def test_index_page_loads(self):
        client = app.test_client()
        response = client.get("/")
        assert response.status_code == 200
        assert b"Crochet Pattern" in response.data

    def test_index_page_has_export_actions(self):
        client = app.test_client()
        response = client.get("/")
        assert response.status_code == 200
        assert b"Copy pattern" in response.data
        assert b"Download as .txt" in response.data
        assert b"Print / Save PDF" in response.data
        assert b"pattern-preview" in response.data
        assert b"theme-toggle" in response.data

    def test_library_page_loads(self):
        client = app.test_client()
        response = client.get("/library")
        assert response.status_code == 200
        assert b"Pattern library" in response.data

    def test_saved_patterns_api_returns_list(self):
        client = app.test_client()
        response = client.post(
            "/api/pattern",
            json={"prompt": "make me a beanie hat", "use_us": False, "save": True},
        )
        assert response.status_code == 200
        saved = client.get("/api/patterns")
        assert saved.status_code == 200
        payload = saved.get_json()
        assert "patterns" in payload
        assert isinstance(payload["patterns"], list)

    def test_pattern_api_generates_pattern(self):
        client = app.test_client()
        response = client.post(
            "/api/pattern",
            json={"prompt": "make me a beanie hat", "use_us": False},
        )
        assert response.status_code == 200
        payload = response.get_json()
        assert "pattern" in payload
        assert "image_svg" in payload
        assert "BEANIE" in payload["pattern"].upper() or "HAT" in payload["pattern"].upper()

    def test_pattern_api_supports_us_terminology(self):
        client = app.test_client()
        response = client.post(
            "/api/pattern",
            json={"prompt": "make me a beanie hat", "use_us": True},
        )
        assert response.status_code == 200
        payload = response.get_json()
        assert "US" in payload["pattern"]

    def test_top_pattern_preview_is_generated(self):
        client = app.test_client()
        response = client.post(
            "/api/pattern",
            json={"prompt": "simple top", "use_us": False},
        )
        assert response.status_code == 200
        payload = response.get_json()
        assert "<svg" in payload["image_svg"].lower()
        assert "top" in payload["image_svg"].lower() or "shirt" in payload["image_svg"].lower()

    def test_new_garment_previews_are_distinct(self):
        client = app.test_client()
        cardigan = client.post("/api/pattern", json={"prompt": "crochet cardigan"}).get_json()
        skirt = client.post("/api/pattern", json={"prompt": "crochet skirt"}).get_json()
        assert "Open Cardigan" in cardigan["image_svg"]
        assert "A-Line Skirt" in skirt["image_svg"]
