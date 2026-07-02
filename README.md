# Crochet Pattern Creation Agent

A command-line agent that designs crochet patterns based on your requirements.
Patterns are written in **UK crochet terminology** by default, with an option to output **US terminology** instead.

## Features

- 🧶 Generates complete crochet patterns for popular items
- 🇬🇧 Uses **UK terminology** by default (dc, tr, htr, dtr…)
- 🇺🇸 Switch to **US terminology** with the `--us` flag
- 🌐 Falls back to curated **web resources** (Ravelry, LoveCrafts, YouTube) for unsupported patterns
- 🔤 Built-in UK ↔ US **stitch glossary**
- 💬 Interactive or single-command mode

## Supported Pattern Types

| Item | Example request |
|---|---|
| Beanie / Hat | `"make me a beanie hat"` |
| Scarf / Cowl | `"simple scarf"`, `"cowl"` |
| Granny Square | `"granny square"` |
| Dishcloth / Facecloth | `"dishcloth"`, `"facecloth"` |
| Bag / Tote | `"market bag"` |
| Blanket / Throw | `"baby blanket"` |
| Amigurumi / Toy | `"amigurumi bunny"`, `"crochet toy"` |

For any unsupported pattern, the agent provides links to **Ravelry**, **LoveCrafts**, **Google**, and **YouTube**.

## Quick Start

```bash
# Single pattern request (UK terminology)
python -m crochet_agent "make me a beanie hat"

# Switch to US terminology
python -m crochet_agent "granny square" --us

# Pattern for a specific size and yarn weight
python -m crochet_agent "baby blanket chunky yarn"

# Show the UK/US stitch glossary
python -m crochet_agent --glossary

# Start an interactive session
python -m crochet_agent --interactive
```

## UK vs US Terminology

| UK | UK abbr | US | US abbr |
|---|---|---|---|
| double crochet | dc | single crochet | sc |
| half treble crochet | htr | half double crochet | hdc |
| treble crochet | tr | double crochet | dc |
| double treble crochet | dtr | treble crochet | tr |
| triple treble crochet | trtr | double treble crochet | dtr |

## Project Structure

```
crochet_agent/
├── __init__.py          # Public API
├── __main__.py          # python -m crochet_agent entry point
├── agent.py             # CLI and request dispatcher
├── pattern_generator.py # Pattern templates and request parsing
├── terminology.py       # UK/US terminology mapping and conversion
└── web_search.py        # Web resource URL builders

tests/
├── test_agent.py
├── test_pattern_generator.py
├── test_terminology.py
└── test_web_search.py
```

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```
