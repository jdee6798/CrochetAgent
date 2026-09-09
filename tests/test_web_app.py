"""Tests for the Flask web application interface."""

from crochet_agent.web_app import create_app


class TestWebApp:
    def setup_method(self):
        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_index_get_renders_form(self):
        response = self.client.get("/")
        text = response.get_data(as_text=True)
        assert response.status_code == 200
        assert "Crochet Pattern Creation Agent" in text
        assert "Generate pattern" in text

    def test_generate_pattern_post(self):
        response = self.client.post(
            "/",
            data={"request_text": "make me a beanie hat", "action": "generate"},
        )
        text = response.get_data(as_text=True)
        assert response.status_code == 200
        assert "Generated Pattern" in text
        assert "BEANIE" in text.upper() or "HAT" in text.upper()

    def test_generate_pattern_in_us_terms(self):
        response = self.client.post(
            "/",
            data={
                "request_text": "make me a beanie hat",
                "action": "generate",
                "use_us": "on",
            },
        )
        text = response.get_data(as_text=True)
        assert response.status_code == 200
        assert "US" in text

    def test_glossary_post(self):
        response = self.client.post("/", data={"action": "glossary"})
        text = response.get_data(as_text=True)
        assert response.status_code == 200
        assert "Stitch Glossary" in text
        assert "UK" in text and "US" in text
