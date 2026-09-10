"""Flask web application for the Crochet Pattern Creation Agent."""

from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template_string, request

from .agent import process_request
from .pattern_generator import parse_request

app = Flask(__name__)

_PATTERN_STORE = Path(__file__).resolve().parent / "pattern_library.json"


def _load_patterns() -> list[dict[str, Any]]:
    """Load saved patterns from disk, returning an empty list when missing."""
    if not _PATTERN_STORE.exists():
        return []
    try:
        import json

        with _PATTERN_STORE.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _save_patterns(patterns: list[dict[str, Any]]) -> None:
    """Persist saved patterns to disk."""
    import json

    with _PATTERN_STORE.open("w", encoding="utf-8") as fh:
        json.dump(patterns, fh, indent=2)


def _record_pattern(prompt: str, pattern: str, use_us: bool) -> list[dict[str, Any]]:
    """Store a generated pattern in the local library."""
    patterns = _load_patterns()
    entry = {
        "id": f"pattern-{len(patterns) + 1}-{int(datetime.now(timezone.utc).timestamp())}",
        "prompt": prompt,
        "use_us": use_us,
        "pattern": pattern,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    patterns.insert(0, entry)
    _save_patterns(patterns)
    return patterns


def _generate_image_svg(prompt: str, item_type: str | None = None) -> str:
    """Return a simple SVG illustration representing the finished item."""
    safe_prompt = escape((prompt or "crochet item").strip()[:24])
    normalized = (item_type or "pattern").replace("_", " ").strip().lower()
    label = "Finished item" if not normalized else normalized.title()

    if "top" in normalized or "crop" in normalized:
        shape = """
        <path d="M62 42 L104 22 L146 42 L168 72 L162 176 L78 176 L72 72 Z" fill="#f6d3dd" stroke="#8a5f7b" stroke-width="4"/>
        <path d="M88 66 L86 120 L107 140 L128 120 L126 66 Z" fill="#fff7fb" opacity="0.75"/>
        <path d="M82 46 L96 72 L80 100 M158 46 L144 72 L160 100" stroke="#8a5f7b" stroke-width="4" fill="none"/>
        """
        accent = "#d9b7c7"
        detail = "Simple Top"
    elif "jumper" in normalized or "sweater" in normalized:
        shape = """
        <path d="M70 50 L96 30 L144 30 L170 50 L180 186 L60 186 Z" fill="#bfd8c8" stroke="#3d7465" stroke-width="4"/>
        <rect x="92" y="42" width="56" height="82" rx="18" fill="#eaf7f0" opacity="0.7"/>
        <path d="M92 66 L70 96 M148 66 L170 96 M84 110 L96 180 M156 110 L144 180" stroke="#3d7465" stroke-width="4" fill="none"/>
        """
        accent = "#b7d7c4"
        detail = "Boxy Jumper"
    elif "granny" in normalized:
        shape = """
        <g transform="translate(40,18)">
          <path d="M18 68 L68 18 L118 68 L68 118 Z" fill="#f7d29b" stroke="#a56b42" stroke-width="4"/>
          <path d="M18 68 L68 118 L118 68 L68 18 Z" fill="#f6e7c9" stroke="#a56b42" stroke-width="4"/>
          <path d="M68 18 L118 68 L68 118 L18 68 Z" fill="#f0c47d" stroke="#a56b42" stroke-width="4"/>
          <path d="M68 18 L68 118 M18 68 L118 68" stroke="#a56b42" stroke-width="4" fill="none" opacity="0.7"/>
        </g>
        """
        accent = "#f5d293"
        detail = "Granny Square Top"
    elif "cardigan" in normalized or "shrug" in normalized:
        shape = """
        <path d="M58 48 L96 28 L130 54 L164 28 L202 48 L180 92 L168 186 L92 186 L80 92 Z" fill="#d5c9e8" stroke="#78638f" stroke-width="4"/>
        <path d="M130 54 L130 186 M96 28 L130 54 L164 28" stroke="#78638f" stroke-width="4" fill="none"/>
        <path d="M82 94 L96 116 M178 94 L164 116" stroke="#78638f" stroke-width="4" fill="none"/>
        """
        accent = "#c9b8df"
        detail = "Open Cardigan"
    elif "skirt" in normalized:
        shape = """
        <path d="M96 32 L164 32 L174 72 L210 190 L50 190 L86 72 Z" fill="#f4c8a8" stroke="#a96d61" stroke-width="4"/>
        <path d="M86 72 L174 72 M76 112 L184 112 M64 152 L196 152" stroke="#a96d61" stroke-width="4" fill="none" opacity="0.7"/>
        <path d="M96 32 L96 72 M164 32 L164 72" stroke="#a96d61" stroke-width="4" fill="none"/>
        """
        accent = "#f0b996"
        detail = "A-Line Skirt"
    else:
        shape = """
        <path d="M60 54 L96 28 L144 54 L164 96 L156 188 L84 188 L76 96 Z" fill="#dfe8d9" stroke="#758c6d" stroke-width="4"/>
        <circle cx="78" cy="60" r="12" fill="#f3f8f2"/>
        <circle cx="162" cy="60" r="12" fill="#f3f8f2"/>
        """
        accent = "#dfe8d9"
        detail = "Crochet Project"

    return f"""
    <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 260 230' role='img' aria-label='{label}' width='100%' height='100%'>
      <defs>
        <linearGradient id='bgGrad' x1='0%' x2='100%' y1='0%' y2='100%'>
          <stop offset='0%' stop-color='#fefaf6' />
          <stop offset='100%' stop-color='#f3ebf0' />
        </linearGradient>
      </defs>
      <rect width='260' height='230' rx='22' fill='url(#bgGrad)'/>
      <g transform='translate(10,8)'>
        {shape}
      </g>
      <circle cx='54' cy='52' r='20' fill='{accent}' opacity='0.75'/>
      <circle cx='206' cy='52' r='20' fill='{accent}' opacity='0.75'/>
      <text x='130' y='208' text-anchor='middle' font-family='Segoe UI, sans-serif' font-size='16' font-weight='700' fill='#4d3344'>{detail}</text>
      <text x='130' y='224' text-anchor='middle' font-family='Segoe UI, sans-serif' font-size='10' fill='#675a63'>{safe_prompt}</text>
    </svg>
    """


HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Crochet Pattern Studio</title>
    <style>
      :root {
        --bg: #f8f4f1;
        --bg-strong: #f3eaf2;
        --surface: #fffdfd;
        --card: #fdf7f6;
        --primary: #b48ca6;
        --primary-strong: #825c7d;
        --accent: #d9c9d7;
        --text: #2e2230;
        --muted: #675a63;
        --shadow: rgba(98, 74, 90, 0.10);
        --border: rgba(180, 140, 166, 0.18);
      }

      body[data-theme="dark"] {
        --bg: #1a1719;
        --bg-strong: #221d20;
        --surface: #272124;
        --card: #2c2528;
        --primary: #d9b4c8;
        --primary-strong: #f2d9e6;
        --accent: #8d6a82;
        --text: #f9f0f5;
        --muted: #d4c3cf;
        --shadow: rgba(0, 0, 0, 0.30);
        --border: rgba(217, 180, 200, 0.18);
      }

      * { box-sizing: border-box; }

      body {
        margin: 0;
        min-height: 100vh;
        font-family: "Segoe UI", Tahoma, sans-serif;
        background: linear-gradient(180deg, var(--bg) 0%, var(--bg-strong) 100%);
        color: var(--text);
        transition: background 0.25s ease, color 0.25s ease;
      }

      .shell {
        max-width: 1260px;
        margin: 0 auto;
        padding: 28px 20px 40px;
      }

      .topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        margin-bottom: 22px;
      }

      .brand-wrap {
        display: flex;
        align-items: center;
        gap: 12px;
      }

      .theme-button {
        appearance: none;
        border: 1px solid var(--border);
        background: rgba(255,255,255,0.35);
        color: var(--text);
        border-radius: 999px;
        padding: 8px 12px;
        cursor: pointer;
        font-weight: 600;
      }

      .brand {
        font-size: clamp(1.7rem, 2vw, 2.5rem);
        font-weight: 700;
        color: var(--primary-strong);
        letter-spacing: -0.04em;
      }

      .pill {
        background: rgba(143, 106, 79, 0.06);
        border: 1px solid var(--border);
        border-radius: 999px;
        padding: 8px 14px;
        color: var(--muted);
        font-size: 0.82rem;
        font-weight: 600;
      }

      .layout {
        display: grid;
        grid-template-columns: minmax(320px, 420px) minmax(0, 1fr);
        gap: 22px;
      }

      .panel {
        background: rgba(255, 253, 251, 0.92);
        border: 1px solid var(--border);
        border-radius: 24px;
        box-shadow: 0 18px 40px var(--shadow);
      }

      .form-panel {
        padding: 24px;
      }

      h1 {
        margin: 0 0 8px;
        font-size: 2rem;
        color: var(--primary-strong);
      }

      .subtitle {
        margin: 0 0 20px;
        color: var(--muted);
        line-height: 1.6;
      }

      label {
        display: block;
        font-weight: 700;
        margin-bottom: 10px;
        color: var(--primary-strong);
      }

      textarea {
        width: 100%;
        min-height: 150px;
        resize: vertical;
        border: 1px solid rgba(143, 106, 79, 0.2);
        border-radius: 16px;
        background: var(--surface);
        padding: 14px 16px;
        font: inherit;
        color: var(--text);
      }

      textarea:focus {
        outline: 3px solid rgba(143, 106, 79, 0.14);
        border-color: var(--primary);
      }

      .toggle-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 18px 0 20px;
        gap: 12px;
        background: rgba(217, 192, 165, 0.12);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 12px 14px;
      }

      .toggle-row span {
        font-weight: 700;
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
        background: #d7c4ae;
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
        box-shadow: 0 10px 20px rgba(98, 66, 47, 0.18);
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
        font-size: 1.25rem;
      }

      .toolbar {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-left: auto;
      }

      .mini-button {
        border: 1px solid rgba(180, 140, 166, 0.22);
        background: rgba(180, 140, 166, 0.08);
        color: var(--primary-strong);
        padding: 9px 12px;
        font-size: 0.9rem;
        box-shadow: none;
        transition: transform 0.15s ease, background 0.2s ease;
      }

      .mini-button:hover {
        background: rgba(180, 140, 166, 0.14);
        transform: translateY(-1px);
      }

      .content-grid {
        display: grid;
        grid-template-columns: 280px minmax(0, 1fr);
        gap: 20px;
      }

      .pattern-preview {
        background: linear-gradient(180deg, #fdf7f9 0%, #f4eaf1 100%);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 420px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
      }

      body[data-theme="dark"] .pattern-preview {
        background: linear-gradient(180deg, #2a2226 0%, #201c1d 100%);
      }

      .pattern-preview svg {
        width: 100%;
        max-height: 380px;
        display: block;
        border-radius: 16px;
      }

      .result-box {
        background: linear-gradient(180deg, #fffdfd 0%, #f9f2f6 100%);
        border: 1px solid var(--border);
        border-radius: 16px;
        min-height: 420px;
        padding: 18px 18px 12px;
        white-space: pre-wrap;
        font-family: "Consolas", "Courier New", monospace;
        line-height: 1.6;
        color: var(--text);
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

        .content-grid {
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

        .content-grid {
          grid-template-columns: 1fr;
        }

        .pattern-preview {
          display: none;
        }

        .result-box {
          min-height: auto;
          border: none;
          background: white;
          white-space: pre-wrap;
          padding: 0;
        }
      }

      .library-panel {
        padding: 24px;
      }

      .library-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
        margin-bottom: 18px;
      }

      .library-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 16px;
      }

      .pattern-card {
        background: linear-gradient(180deg, #fffefc, #f8efe8);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 8px 18px rgba(109, 67, 38, 0.08);
      }

      .pattern-card h3 {
        margin: 0 0 8px;
        font-size: 1.05rem;
        color: var(--primary-strong);
      }

      .pattern-card p {
        margin: 0 0 10px;
        color: var(--muted);
        font-size: 0.9rem;
      }

      .pattern-card pre {
        max-height: 180px;
        overflow: auto;
        margin: 0;
        white-space: pre-wrap;
        font-family: "Consolas", "Courier New", monospace;
        font-size: 0.82rem;
        line-height: 1.45;
        background: rgba(255,255,255,0.4);
        border-radius: 10px;
        padding: 10px;
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
        <div class="brand-wrap">
          <div class="brand">Crochet Pattern Studio</div>
          <button type="button" class="theme-button" id="theme-toggle" aria-label="Toggle theme">Dark mode</button>
        </div>
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

          <div class="content-grid">
            <div class="pattern-preview" id="pattern-preview" aria-label="Generated crochet pattern preview">
              <svg viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Crochet square pattern illustration">
                <rect x="0" y="0" width="240" height="240" rx="22" fill="#f7f1ea"/>
                <g fill="none" stroke="#8f6a4f" stroke-linecap="round" stroke-width="7">
                  <path d="M35 110 C55 75, 80 56, 110 60 C130 63, 150 78, 160 100 C172 126, 172 150, 152 176 C130 205, 89 210, 60 184 C38 162, 28 130, 35 110 Z" fill="#e1c5aa" opacity="0.7"/>
                  <path d="M60 90 C82 76, 104 82, 118 102 C129 118, 128 135, 116 149 C102 165, 82 171, 62 162 C45 153, 40 125, 60 90 Z" fill="#f5e7d9"/>
                  <path d="M78 80 L78 160 M102 70 L102 170 M126 76 L126 172 M91 92 L150 92 M88 122 L152 122 M86 154 L146 154"/>
                  <circle cx="78" cy="77" r="12" fill="#b98962"/>
                  <circle cx="102" cy="77" r="12" fill="#d7b89a"/>
                  <circle cx="126" cy="77" r="12" fill="#b98962"/>
                  <circle cx="78" cy="122" r="12" fill="#d7b89a"/>
                  <circle cx="102" cy="122" r="12" fill="#b98962"/>
                  <circle cx="126" cy="122" r="12" fill="#d7b89a"/>
                  <circle cx="78" cy="167" r="12" fill="#b98962"/>
                  <circle cx="102" cy="167" r="12" fill="#d7b89a"/>
                  <circle cx="126" cy="167" r="12" fill="#b98962"/>
                </g>
              </svg>
            </div>
            <div id="result" class="result-box">Type a request and click “Generate pattern” to see a crochet pattern here.</div>
          </div>
        </section>
      </div>
    </div>

    <script>
      const form = document.getElementById('pattern-form');
      const result = document.getElementById('result');
      const copyButton = document.getElementById('copy-pattern');
      const downloadButton = document.getElementById('download-pattern');
      const printButton = document.getElementById('print-pattern');
      const preview = document.getElementById('pattern-preview');
      const themeToggle = document.getElementById('theme-toggle');
      let currentPattern = '';

      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (prefersDark) {
        document.body.setAttribute('data-theme', 'dark');
        themeToggle.textContent = 'Light mode';
      }

      themeToggle.addEventListener('click', () => {
        const isDark = document.body.getAttribute('data-theme') === 'dark';
        document.body.setAttribute('data-theme', isDark ? 'light' : 'dark');
        themeToggle.textContent = isDark ? 'Dark mode' : 'Light mode';
      });

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
            body: JSON.stringify({ prompt, use_us: useUs, save: true }),
          });

          const data = await response.json();
          if (!response.ok) {
            throw new Error(data.error || 'Unable to generate a pattern right now.');
          }

          currentPattern = data.pattern;
          if (data.image_svg) {
            preview.innerHTML = data.image_svg;
          }
          result.classList.remove('loading');
          result.textContent = currentPattern;
        } catch (error) {
          currentPattern = '';
          preview.innerHTML = '<svg ... />';
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


@app.get("/library")
def library_page():
    """Render the saved pattern library page."""
    patterns = _load_patterns()
    library_html = """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Pattern Library</title>
        <style>
          :root {
            --bg: #f5efe8; --surface: #fffdfb; --primary: #8a5e3b; --primary-strong: #6d4326; --muted: #6e5b4e; --border: rgba(138, 94, 59, 0.16);
          }
          body { margin: 0; font-family: "Segoe UI", Tahoma, sans-serif; background: linear-gradient(135deg, #f9f1ea 0%, #efe4d6 100%); color: #2d2018; }
          .shell { max-width: 1100px; margin: 0 auto; padding: 32px 20px 48px; }
          .topbar { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 22px; }
          .brand { font-size: clamp(1.5rem, 2vw, 2.3rem); font-weight: 700; color: var(--primary-strong); }
          .panel { background: rgba(255,253,251,0.92); border: 1px solid var(--border); border-radius: 22px; box-shadow: 0 18px 40px rgba(108,72,53,0.12); }
          .library-panel { padding: 24px; }
          .library-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 20px; }
          .library-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }
          .pattern-card { background: linear-gradient(180deg, #fffefc, #f8efe8); border: 1px solid var(--border); border-radius: 16px; padding: 16px; }
          .pattern-card h3 { margin: 0 0 8px; font-size: 1.05rem; color: var(--primary-strong); }
          .pattern-card p { margin: 0 0 10px; color: var(--muted); font-size: 0.9rem; }
          .pattern-card pre { max-height: 180px; overflow: auto; margin: 0; white-space: pre-wrap; font-family: Consolas, monospace; font-size: 0.8rem; line-height: 1.45; background: rgba(255,255,255,0.4); border-radius: 10px; padding: 10px; }
          a.button { display: inline-block; text-decoration: none; background: linear-gradient(135deg, var(--primary) 0%, var(--primary-strong) 100%); color: white; padding: 11px 16px; border-radius: 12px; font-weight: 700; }
          .empty { padding: 24px; color: var(--muted); }
        </style>
      </head>
      <body>
        <div class="shell">
          <div class="topbar">
            <div class="brand">Pattern library</div>
            <a class="button" href="/">Back to generator</a>
          </div>
          <div class="panel library-panel">
            <div class="library-header">
              <h2>Saved crochet patterns</h2>
            </div>
            <div class="library-grid">
              {% if patterns %}
                {% for entry in patterns %}
                  <article class="pattern-card">
                    <h3>{{ entry.prompt }}</h3>
                    <p>{{ entry.created_at[:10] }} · {% if entry.use_us %}US terminology{% else %}UK terminology{% endif %}</p>
                    <pre>{{ entry.pattern }}</pre>
                  </article>
                {% endfor %}
              {% else %}
                <div class="empty">No saved patterns yet. Generate a pattern from the home page to populate your library.</div>
              {% endif %}
            </div>
          </div>
        </div>
      </body>
    </html>
    """
    return render_template_string(library_html, patterns=patterns)


@app.get("/api/patterns")
def list_patterns():
    """Return all saved patterns."""
    return jsonify({"patterns": _load_patterns()})


@app.post("/api/pattern")
def create_pattern():
    """API endpoint that generates a crochet pattern from a prompt."""
    payload = request.get_json(silent=True) or {}
    prompt = str(payload.get("prompt", "")).strip()
    use_us = bool(payload.get("use_us", False))
    save = bool(payload.get("save", False))

    if not prompt:
        return jsonify({"error": "Please provide a prompt describing the pattern you want."}), 400

    pattern = process_request(prompt, use_us=use_us)
    item_type = parse_request(prompt).item_type
    image_svg = _generate_image_svg(prompt, item_type)
    if save:
        _record_pattern(prompt, pattern, use_us)
    return jsonify({"pattern": pattern, "image_svg": image_svg})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
