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

    def test_pattern_api_generates_pattern(self):
        client = app.test_client()
        response = client.post(
            "/api/pattern",
            json={"prompt": "make me a beanie hat", "use_us": False},
        )
        assert response.status_code == 200
        payload = response.get_json()
        assert "pattern" in payload
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
