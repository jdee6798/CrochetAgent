"""Main CLI agent for crochet pattern creation."""

from __future__ import annotations

import argparse
import sys
import textwrap

from .pattern_generator import parse_request, generate_pattern, can_generate, SUPPORTED_ITEMS
from .terminology import stitch_glossary
from .web_search import format_web_resources


WELCOME = textwrap.dedent("""\
    ============================================================
    Welcome to the Crochet Pattern Creation Agent!
    ============================================================
    This agent can design crochet patterns for you.
    Patterns are written in UK terminology by default.

    Supported items: {items}

    Type your request (e.g. "Make me a beginner beanie hat")
    or type 'quit' to exit. Use --us flag for US terminology.
    ============================================================
""")

HELP_TEXT = textwrap.dedent("""\
    Usage:
      python -m crochet_agent [OPTIONS] [REQUEST]

    Options:
      --us           Output pattern in US crochet terminology
                     (default is UK terminology)
      --glossary     Print a UK/US stitch glossary and exit
      --interactive  Start an interactive session (default when
                     no REQUEST is provided)
      --web          Start the browser-based web app
      --host HOST    Host interface for the web app (default: 127.0.0.1)
      --port PORT    Port for the web app (default: 5000)
      -h, --help     Show this help message and exit

    Examples:
      python -m crochet_agent "make me a beanie hat"
      python -m crochet_agent "granny square" --us
      python -m crochet_agent --interactive
      python -m crochet_agent --glossary
      python -m crochet_agent --web
""")


def process_request(user_input: str, use_us: bool) -> str:
    """Process a user request and return the response text."""
    user_input = user_input.strip()
    if not user_input:
        return "Please describe what you'd like to make."

    req = parse_request(user_input)

    if can_generate(req):
        pattern = generate_pattern(req)
        if pattern is not None:
            return pattern.render(use_us=use_us)
        # Shouldn't happen, but handle gracefully
        return format_web_resources(user_input)
    else:
        # We couldn't generate a pattern – suggest web resources
        msg_parts = [
            f"I'm unable to automatically generate a pattern for: '{user_input}'."
        ]
        if req.item_type == "":
            msg_parts.append(
                f"\nI didn't recognise the item type. Supported items are: "
                + ", ".join(sorted(SUPPORTED_ITEMS)).replace("_", " ")
                + "."
            )
        msg_parts.append("\n")
        msg_parts.append(format_web_resources(user_input))
        return "\n".join(msg_parts)


def interactive_session(use_us: bool) -> None:
    """Run an interactive session with the agent."""
    items_str = ", ".join(s.replace("_", " ") for s in sorted(SUPPORTED_ITEMS))
    print(WELCOME.format(items=items_str))

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye! Happy crocheting!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "bye", "q"):
            print("Goodbye! Happy crocheting!")
            break

        if user_input.lower() in ("glossary", "stitch glossary", "help glossary"):
            print(stitch_glossary(use_us))
            continue

        if user_input.lower() in ("help", "?"):
            print(HELP_TEXT)
            continue

        response = process_request(user_input, use_us)
        print("\nAgent:\n")
        print(response)
        print()


def main(argv: list[str] | None = None) -> int:
    """Entry point for the crochet pattern agent."""
    parser = argparse.ArgumentParser(
        prog="crochet_agent",
        description="Crochet Pattern Creation Agent – generates patterns in UK terminology.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=HELP_TEXT,
    )
    parser.add_argument(
        "request",
        nargs="*",
        help="Describe the item you want a crochet pattern for.",
    )
    parser.add_argument(
        "--us",
        action="store_true",
        default=False,
        help="Output pattern using US crochet terminology (default is UK).",
    )
    parser.add_argument(
        "--glossary",
        action="store_true",
        default=False,
        help="Print a UK/US stitch glossary and exit.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        default=False,
        help="Start an interactive session.",
    )
    parser.add_argument(
        "--web",
        action="store_true",
        default=False,
        help="Start the browser-based web app.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host interface to use for the web app.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to use for the web app.",
    )

    args = parser.parse_args(argv)

    if args.glossary:
        print(stitch_glossary(args.us))
        return 0

    if args.web:
        from .webapp import app as web_app

        web_app.run(host=args.host, port=args.port, debug=False)
        return 0

    request_text = " ".join(args.request).strip()

    if args.interactive or not request_text:
        interactive_session(args.us)
        return 0

    result = process_request(request_text, args.us)
    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
