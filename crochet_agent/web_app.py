"""Web application interface for the crochet pattern agent."""

from __future__ import annotations

from flask import Flask, request, render_template_string

from .agent import process_request
from .terminology import stitch_glossary


HTML_TEMPLATE = """\
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Crochet Pattern Creation Agent</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 960px; margin: 2rem auto; padding: 0 1rem; }
    h1 { margin-bottom: 0.25rem; }
    .subtitle { color: #555; margin-top: 0; }
    form { display: grid; gap: 0.75rem; margin: 1.25rem 0; }
    textarea { width: 100%; min-height: 90px; font-size: 1rem; padding: 0.5rem; }
    .controls { display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; }
    button { padding: 0.5rem 0.8rem; font-size: 0.95rem; cursor: pointer; }
    pre { white-space: pre-wrap; background: #f7f7f7; padding: 1rem; border-radius: 6px; }
  </style>
</head>
<body>
  <h1>🧶 Crochet Pattern Creation Agent</h1>
  <p class="subtitle">Generate crochet patterns with UK terminology by default, or switch to US terms.</p>

  <form method="post">
    <label for="request_text">What would you like to make?</label>
    <textarea id="request_text" name="request_text" placeholder="e.g. Make me a beginner beanie hat">{{ request_text }}</textarea>

    <div class="controls">
      <label><input type="checkbox" name="use_us" {% if use_us %}checked{% endif %}> Use US terminology</label>
      <button type="submit" name="action" value="generate">Generate pattern</button>
      <button type="submit" name="action" value="glossary">Show glossary</button>
    </div>
  </form>

  {% if output %}
    <h2>{{ output_title }}</h2>
    <pre>{{ output }}</pre>
  {% endif %}
</body>
</html>
"""


def create_app() -> Flask:
    """Create and configure the Flask web application."""
    app = Flask(__name__)

    @app.route("/", methods=["GET", "POST"])
    def index() -> str:
        output = ""
        output_title = ""
        request_text = ""
        use_us = False

        if request.method == "POST":
            request_text = request.form.get("request_text", "").strip()
            use_us = request.form.get("use_us") == "on"
            action = request.form.get("action", "generate")

            if action == "glossary":
                output_title = "Stitch Glossary"
                output = stitch_glossary(use_us)
            else:
                output_title = "Generated Pattern"
                output = process_request(request_text, use_us)

        return render_template_string(
            HTML_TEMPLATE,
            output=output,
            output_title=output_title,
            request_text=request_text,
            use_us=use_us,
        )

    return app


def main() -> None:
    """Run the development web server."""
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()
