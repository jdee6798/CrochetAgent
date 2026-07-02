"""Web search helpers for finding crochet patterns online."""

from urllib.parse import urlencode, quote_plus


RAVELRY_SEARCH_URL = "https://www.ravelry.com/patterns/search"
GOOGLE_SEARCH_URL = "https://www.google.com/search"
LOVECRAFTS_SEARCH_URL = "https://www.lovecrafts.com/en-gb/search"


def ravelry_search_url(query: str, craft: str = "crochet") -> str:
    """Build a Ravelry pattern search URL for the given query."""
    params = {
        "craft": craft,
        "query": query,
        "sort": "best",
    }
    return f"{RAVELRY_SEARCH_URL}#query={quote_plus(query)}&craft={craft}&sort=best"


def google_search_url(query: str) -> str:
    """Build a Google search URL for the given crochet pattern query."""
    full_query = f"free crochet pattern {query}"
    params = {"q": full_query}
    return f"{GOOGLE_SEARCH_URL}?{urlencode(params)}"


def lovecrafts_search_url(query: str) -> str:
    """Build a LoveCrafts search URL for the given crochet pattern query."""
    return f"{LOVECRAFTS_SEARCH_URL}?{urlencode({'q': query + ' crochet pattern'})}"


def youtube_search_url(query: str) -> str:
    """Build a YouTube search URL for crochet pattern tutorials."""
    full_query = f"crochet {query} tutorial for beginners"
    params = {"search_query": full_query}
    return f"https://www.youtube.com/results?{urlencode(params)}"


def get_web_resources(query: str) -> list[dict]:
    """Return a list of web resources for finding the requested crochet pattern."""
    return [
        {
            "name": "Ravelry",
            "description": "The largest crochet and knitting pattern database",
            "url": ravelry_search_url(query),
        },
        {
            "name": "LoveCrafts",
            "description": "Free and paid crochet patterns with UK-friendly content",
            "url": lovecrafts_search_url(query),
        },
        {
            "name": "Google Search",
            "description": "Find free patterns from blogs and crochet communities",
            "url": google_search_url(query),
        },
        {
            "name": "YouTube Tutorials",
            "description": "Video tutorials that walk through the pattern step by step",
            "url": youtube_search_url(query),
        },
    ]


def format_web_resources(query: str) -> str:
    """Format web resources as a human-readable string."""
    resources = get_web_resources(query)
    lines = [
        f"I wasn't able to generate a specific pattern for '{query}', "
        "but here are some great places to find one:\n"
    ]
    for resource in resources:
        lines.append(f"  {resource['name']}: {resource['description']}")
        lines.append(f"    {resource['url']}\n")
    lines.append(
        "Tip: On Ravelry you can filter by yarn weight, difficulty, and language."
    )
    return "\n".join(lines)
