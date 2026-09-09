"""Flask web application for the Crochet Pattern Creation Agent."""

from __future__ import annotations

from flask import Flask, jsonify, render_template_string, request

from .agent import process_request

app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Crochet Pattern Studio</title>
    <style>
      :root {
        --bg: #f5efe8;
        --surface: #fffdfb;
        --surface-strong: #f2e3d2;
        --primary: #8a5e3b;
        --primary-strong: #6d4326;
        --accent: #d7b89a;
        --text: #2d2018;
        --muted: #6e5b4e;
        --shadow: rgba(108, 72, 53, 0.18);
        --border: rgba(138, 94, 59, 0.16);
      }

      * { box-sizing: border-box; }

      body {
        margin: 0;
        min-height: 100vh;
        font-family: "Segoe UI", Tahoma, sans-serif;
        background: linear-gradient(135deg, #f9f1ea 0%, #efe4d6 100%);
        color: var(--text);
      }

      .shell {
        max-width: 1200px;
        margin: 0 auto;
        padding: 32px 20px 48px;
      }

      .topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 22px;
      }

      .brand {
        font-size: clamp(1.5rem, 2vw, 2.3rem);
        font-weight: 700;
        letter-spacing: 0.04em;
        color: var(--primary-strong);
      }

      .pill {
        background: rgba(138, 94, 59, 0.08);
        border: 1px solid var(--border);
        border-radius: 999px;
        padding: 8px 16px;
        color: var(--muted);
        font-size: 0.9rem;
      }

      .layout {
        display: grid;
        grid-template-columns: minmax(300px, 420px) minmax(0, 1fr);
        gap: 22px;
      }

      .panel {
        background: rgba(255, 253, 251, 0.92);
        border: 1px solid var(--border);
        border-radius: 22px;
        box-shadow: 0 18px 40px var(--shadow);
      }

      .form-panel {
        padding: 24px;
      }

      h1 {
        margin: 0 0 8px;
        font-size: 1.8rem;
        color: var(--primary-strong);
      }

      .subtitle {
        margin: 0 0 20px;
        color: var(--muted);
        line-height: 1.5;
      }

      label {
        display: block;
        font-weight: 600;
        margin-bottom: 10px;
        color: var(--primary-strong);
      }

      textarea {
        width: 100%;
        min-height: 140px;
        resize: vertical;
        border: 1px solid rgba(138, 94, 59, 0.25);
        border-radius: 14px;
        background: var(--surface);
        padding: 14px 16px;
        font: inherit;
        color: var(--text);
      }

      textarea:focus {
        outline: 3px solid rgba(138, 94, 59, 0.15);
        border-color: var(--primary);
      }

      .toggle-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 18px 0 20px;
        gap: 12px;
        background: rgba(215, 184, 154, 0.12);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 12px 14px;
      }

      .toggle-row span {
        font-weight: 600;
      }

      .switch {
        position: relative;
        width: 54px;
        height: 30px;
      }

      .switch input {
        opacity: 0;
        width: 0;
        height: 0;
      }

      .slider {
        position: absolute;
        inset: 0;
        cursor: pointer;
        background: #d6c7b9;
        border-radius: 999px;
        transition: 0.2s ease;
      }

      .slider::before {
        content: "";
        position: absolute;
        width: 22px;
        height: 22px;
        left: 4px;
        top: 4px;
        border-radius: 50%;
        background: white;
        transition: 0.2s ease;
      }

      .switch input:checked + .slider {
        background: var(--primary);
      }

      .switch input:checked + .slider::before {
        transform: translateX(24px);
      }

      button {
        border: none;
        border-radius: 12px;
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-strong) 100%);
        color: white;
        font: inherit;
        font-weight: 700;
        padding: 13px 18px;
        cursor: pointer;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
        box-shadow: 0 10px 20px rgba(109, 67, 38, 0.2);
      }

      button:hover {
        transform: translateY(-1px);
      }

      .result-panel {
        padding: 18px 20px 20px;
      }

      .result-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 14px;
        gap: 12px;
      }

      .result-header h2 {
        margin: 0;
        font-size: 1.3rem;
      }

      .toolbar {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-left: auto;
      }

      .mini-button {
        border: 1px solid rgba(138, 94, 59, 0.18);
        background: rgba(138, 94, 59, 0.06);
        color: var(--primary-strong);
        padding: 9px 12px;
        font-size: 0.9rem;
        box-shadow: none;
      }

      .mini-button:hover {
        background: rgba(138, 94, 59, 0.12);
      }

      .result-box {
        background: linear-gradient(180deg, #fffcfa 0%, #f8efe8 100%);
        border: 1px solid var(--border);
        border-radius: 14px;
        min-height: 420px;
        padding: 18px 18px 12px;
        white-space: pre-wrap;
        font-family: "Consolas", "Courier New", monospace;
        line-height: 1.5;
        color: #2a1e18;
        overflow: auto;
      }

      .loading {
        color: var(--muted);
        font-style: italic;
      }

      @media (max-width: 860px) {
        .layout {
          grid-template-columns: 1fr;
        }
      }

      @media print {
        .topbar,
        .form-panel,
        .toolbar {
          display: none !important;
        }

        .shell {
          max-width: none;
          padding: 0;
        }

        .result-panel {
          box-shadow: none;
          border: none;
          background: white;
          padding: 0;
        }

        .result-box {
          min-height: auto;
          border: none;
          background: white;
          white-space: pre-wrap;
          padding: 0;
        }
      }
    </style>
  </head>
  <body>
    <div class="shell">
      <div class="topbar">
        <div class="brand">Crochet Pattern Studio</div>
        <div class="pill">UK default • US option</div>
      </div>

      <div class="layout">
        <section class="panel form-panel">
          <h1>Design a pattern</h1>
          <p class="subtitle">Describe the item you want to crochet, and the agent will generate a complete pattern in UK terminology by default.</p>

          <form id="pattern-form">
            <label for="prompt">Your request</label>
            <textarea id="prompt" name="prompt" placeholder="Example: make me a beginner beanie hat">make me a beanie hat</textarea>

            <div class="toggle-row">
              <span>Output in US terminology</span>
              <label class="switch" aria-label="Use US terminology">
                <input id="use-us" type="checkbox">
                <span class="slider"></span>
              </label>
            </div>

            <button type="submit">Generate pattern</button>
          </form>
        </section>

        <section class="panel result-panel">
          <div class="result-header">
            <h2>Pattern output</h2>
            <div class="toolbar">
              <button type="button" class="mini-button" id="copy-pattern">Copy pattern</button>
              <button type="button" class="mini-button" id="download-pattern">Download as .txt</button>
              <button type="button" class="mini-button" id="print-pattern">Print / Save PDF</button>
            </div>
          </div>
          <div id="result" class="result-box">Type a request and click “Generate pattern” to see a crochet pattern here.</div>
        </section>
      </div>
    </div>

    <script>
      const form = document.getElementById('pattern-form');
      const result = document.getElementById('result');
      const copyButton = document.getElementById('copy-pattern');
      const downloadButton = document.getElementById('download-pattern');
      const printButton = document.getElementById('print-pattern');
      let currentPattern = '';

      async function copyCurrentPattern() {
        if (!currentPattern.trim()) {
          return;
        }

        try {
          await navigator.clipboard.writeText(currentPattern);
          copyButton.textContent = 'Copied!';
          setTimeout(() => { copyButton.textContent = 'Copy pattern'; }, 1200);
        } catch (error) {
          copyButton.textContent = 'Copy failed';
          setTimeout(() => { copyButton.textContent = 'Copy pattern'; }, 1200);
        }
      }

      function downloadCurrentPattern() {
        if (!currentPattern.trim()) {
          return;
        }

        const blob = new Blob([currentPattern], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'crochet-pattern.txt';
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
      }

      function printCurrentPattern() {
        if (!currentPattern.trim()) {
          return;
        }
        window.print();
      }

      copyButton.addEventListener('click', copyCurrentPattern);
      downloadButton.addEventListener('click', downloadCurrentPattern);
      printButton.addEventListener('click', printCurrentPattern);

      form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const prompt = document.getElementById('prompt').value.trim();
        const useUs = document.getElementById('use-us').checked;

        if (!prompt) {
          currentPattern = '';
          result.textContent = 'Please describe what you would like to make.';
          return;
        }

        result.classList.add('loading');
        result.textContent = 'Generating your crochet pattern...';

        try {
          const response = await fetch('/api/pattern', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, use_us: useUs }),
          });

          const data = await response.json();
          if (!response.ok) {
            throw new Error(data.error || 'Unable to generate a pattern right now.');
          }

          currentPattern = data.pattern;
          result.classList.remove('loading');
          result.textContent = currentPattern;
        } catch (error) {
          currentPattern = '';
          result.classList.remove('loading');
          result.textContent = error.message || 'Something went wrong while generating the pattern.';
        }
      });
    </script>
  </body>
</html>
"""


@app.get("/")
def index():
    """Serve the browser UI."""
    return render_template_string(HTML_TEMPLATE)


@app.post("/api/pattern")
def create_pattern():
    """API endpoint that generates a crochet pattern from a prompt."""
    payload = request.get_json(silent=True) or {}
    prompt = str(payload.get("prompt", "")).strip()
    use_us = bool(payload.get("use_us", False))

    if not prompt:
        return jsonify({"error": "Please provide a prompt describing the pattern you want."}), 400

    pattern = process_request(prompt, use_us=use_us)
    return jsonify({"pattern": pattern})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
