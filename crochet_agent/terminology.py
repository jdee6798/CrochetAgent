"""UK and US crochet terminology mappings."""

# UK stitch name -> (UK abbreviation, US name, US abbreviation)
UK_TO_US = {
    "double crochet": ("dc", "single crochet", "sc"),
    "half treble crochet": ("htr", "half double crochet", "hdc"),
    "treble crochet": ("tr", "double crochet", "dc"),
    "double treble crochet": ("dtr", "treble crochet", "tr"),
    "triple treble crochet": ("trtr", "double treble crochet", "dtr"),
    "slip stitch": ("sl st", "slip stitch", "sl st"),
    "chain": ("ch", "chain", "ch"),
    "magic ring": ("MR", "magic ring", "MR"),
    "yarn over": ("yrh", "yarn over", "yo"),
    "foundation chain": ("ch", "foundation chain", "ch"),
    "turning chain": ("tch", "turning chain", "tch"),
    "stitch": ("st", "stitch", "st"),
    "round": ("rd", "round", "rnd"),
    "repeat": ("rep", "repeat", "rep"),
    "together": ("tog", "together", "tog"),
    "increase": ("inc", "increase", "inc"),
    "decrease": ("dec", "decrease", "dec"),
    "double crochet two together": ("dc2tog", "single crochet two together", "sc2tog"),
    "treble crochet two together": ("tr2tog", "double crochet two together", "dc2tog"),
}

# Build reverse lookup: US name -> (US abbreviation, UK name, UK abbreviation)
US_TO_UK = {
    us_name: (us_abbr, uk_name, uk_abbr)
    for uk_name, (uk_abbr, us_name, us_abbr) in UK_TO_US.items()
}

# Abbreviation mapping UK abbr -> US abbr
UK_ABBR_TO_US_ABBR = {uk_abbr: us_abbr for _, (uk_abbr, _, us_abbr) in UK_TO_US.items()}

# Abbreviation mapping US abbr -> UK abbr
US_ABBR_TO_UK_ABBR = {us_abbr: uk_abbr for _, (uk_abbr, _, us_abbr) in UK_TO_US.items()}


def convert_pattern_to_us(pattern_text: str) -> str:
    """Convert a pattern written in UK terminology to US terminology."""
    result = pattern_text
    # Replace full names (longest first to avoid partial replacements)
    for uk_name, (uk_abbr, us_name, us_abbr) in sorted(
        UK_TO_US.items(), key=lambda x: len(x[0]), reverse=True
    ):
        result = result.replace(uk_name, us_name)

    # Replace abbreviations (in brackets or standalone, case-sensitive)
    # Work through the known abbreviation pairs
    for uk_abbr, us_abbr in sorted(
        UK_ABBR_TO_US_ABBR.items(), key=lambda x: len(x[0]), reverse=True
    ):
        if uk_abbr != us_abbr:
            # Only replace when surrounded by non-alphanumeric chars or at string boundaries
            import re
            result = re.sub(
                r'(?<![A-Za-z0-9])' + re.escape(uk_abbr) + r'(?![A-Za-z0-9])',
                us_abbr,
                result,
            )

    return result


def terminology_note(use_us: bool) -> str:
    """Return a note about which terminology is being used."""
    if use_us:
        return (
            "Note: This pattern uses US crochet terminology.\n"
            "Key: sc=single crochet, hdc=half double crochet, "
            "dc=double crochet, tr=treble crochet."
        )
    return (
        "Note: This pattern uses UK crochet terminology.\n"
        "Key: dc=double crochet, htr=half treble crochet, "
        "tr=treble crochet, dtr=double treble crochet."
    )


def stitch_glossary(use_us: bool) -> str:
    """Return a stitch glossary showing UK and US equivalents."""
    lines = ["Stitch Glossary (UK = US):"]
    for uk_name, (uk_abbr, us_name, us_abbr) in UK_TO_US.items():
        if uk_name in ("slip stitch", "chain", "magic ring", "stitch", "round",
                       "repeat", "together", "increase", "decrease"):
            continue
        lines.append(f"  {uk_name} ({uk_abbr}) = {us_name} ({us_abbr})")
    if use_us:
        lines.append("\nThis pattern is written in US terminology.")
    else:
        lines.append("\nThis pattern is written in UK terminology.")
    return "\n".join(lines)
