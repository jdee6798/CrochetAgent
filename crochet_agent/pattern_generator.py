"""Crochet pattern generator using UK terminology by default."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from .terminology import convert_pattern_to_us, terminology_note, stitch_glossary

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class PatternRequest:
    """Parsed user request for a crochet pattern."""

    raw: str
    item_type: str = ""
    size: str = ""
    yarn_weight: str = ""
    hook_size: str = ""
    skill_level: str = ""
    notes: list[str] = field(default_factory=list)


@dataclass
class Pattern:
    """A generated crochet pattern."""

    title: str
    materials: list[str]
    abbreviations: str
    gauge: str
    instructions: str
    notes: list[str] = field(default_factory=list)
    generated: bool = True  # False means we couldn't generate; suggest web instead

    def render(self, use_us: bool = False) -> str:
        """Render the full pattern as a formatted string."""
        text = _render_raw(self)
        if use_us:
            text = convert_pattern_to_us(text)
        # Add terminology note at the top
        note = terminology_note(use_us)
        return f"{note}\n\n{text}"


def _render_raw(pattern: Pattern) -> str:
    """Render pattern in UK terminology (internal format)."""
    lines: list[str] = []

    lines.append("=" * 60)
    lines.append(pattern.title.upper())
    lines.append("=" * 60)

    lines.append("\nMATERIALS")
    lines.append("-" * 20)
    for mat in pattern.materials:
        lines.append(f"  • {mat}")

    lines.append("\nGAUGE")
    lines.append("-" * 20)
    lines.append(f"  {pattern.gauge}")

    lines.append("\nABBREVIATIONS")
    lines.append("-" * 20)
    lines.append(f"  {pattern.abbreviations}")

    lines.append("\nINSTRUCTIONS")
    lines.append("-" * 20)
    lines.append(pattern.instructions)

    if pattern.notes:
        lines.append("\nNOTES")
        lines.append("-" * 20)
        for note in pattern.notes:
            lines.append(f"  * {note}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Item type detection
# ---------------------------------------------------------------------------

ITEM_PATTERNS: dict[str, list[str]] = {
    "beanie": ["beanie", "hat", "cap", "bobble hat", "toque"],
    "scarf": ["scarf", "cowl", "snood", "neck warmer", "infinity scarf"],
    "granny_square": ["granny square", "granny", "square motif", "motif"],
    "dishcloth": ["dishcloth", "dish cloth", "facecloth", "face cloth",
                  "washcloth", "wash cloth", "flannel"],
    "bag": ["bag", "tote", "market bag", "shopping bag", "purse", "handbag"],
    "blanket": ["blanket", "throw", "afghan", "lap blanket"],
    "socks": ["socks", "sock", "slippers", "slipper boots"],
    "gloves": ["gloves", "mittens", "fingerless gloves", "mitts"],
    "amigurumi": ["amigurumi", "stuffed animal", "plushie", "toy", "teddy",
                  "bunny", "bear", "cat", "dog", "animal"],
}

SIZE_PATTERNS: dict[str, list[str]] = {
    "baby": ["baby", "infant", "newborn", "toddler"],
    "child": ["child", "children", "kid", "kids", "girl", "boy"],
    "adult_s": ["small", "size s", "xs"],
    "adult_m": ["medium", "size m", "average"],
    "adult_l": ["large", "size l", "oversized", "big"],
    "one_size": ["one size", "all sizes"],
}

YARN_WEIGHTS: dict[str, list[str]] = {
    "lace": ["lace", "cobweb", "2 ply"],
    "fingering": ["fingering", "sock yarn", "4 ply", "sport"],
    "dk": ["dk", "double knit", "light worsted", "8 ply"],
    "worsted": ["worsted", "aran", "10 ply", "medium weight"],
    "bulky": ["bulky", "chunky", "super chunky", "12 ply", "thick"],
    "super_bulky": ["super bulky", "super chunky", "arm knit", "jumbo"],
}

SKILL_LEVELS: dict[str, list[str]] = {
    "beginner": ["beginner", "easy", "simple", "first", "starter", "basic"],
    "intermediate": ["intermediate", "medium difficulty"],
    "advanced": ["advanced", "complex", "experienced", "expert"],
}


def _detect(text: str, mapping: dict[str, list[str]]) -> str:
    """Return the first matching key from a mapping, or empty string."""
    lower = text.lower()
    for key, keywords in mapping.items():
        for kw in keywords:
            if kw in lower:
                return key
    return ""


def parse_request(user_input: str) -> PatternRequest:
    """Parse a user input string into a PatternRequest."""
    req = PatternRequest(raw=user_input)
    req.item_type = _detect(user_input, ITEM_PATTERNS)
    req.size = _detect(user_input, SIZE_PATTERNS) or "adult_m"
    req.yarn_weight = _detect(user_input, YARN_WEIGHTS) or "worsted"
    req.skill_level = _detect(user_input, SKILL_LEVELS) or "beginner"
    return req


# ---------------------------------------------------------------------------
# Default hook sizes by yarn weight
# ---------------------------------------------------------------------------

HOOK_BY_WEIGHT: dict[str, str] = {
    "lace": "1.5 mm (UK 2½, US 8 Steel)",
    "fingering": "2.5 mm (UK 12, US B-1/C-2)",
    "dk": "4.0 mm (UK 8, US G-6)",
    "worsted": "5.0 mm (UK 6, US H-8)",
    "bulky": "6.5 mm (UK 3, US K-10½)",
    "super_bulky": "10.0 mm (UK 000, US N/P-15)",
}

YARN_BY_WEIGHT: dict[str, str] = {
    "lace": "Approx. 400 m / 100 g lace weight yarn",
    "fingering": "Approx. 200 m / 100 g 4-ply / fingering yarn",
    "dk": "Approx. 200 m / 100 g DK yarn",
    "worsted": "Approx. 100 m / 100 g Aran / worsted yarn",
    "bulky": "Approx. 80 m / 100 g chunky yarn",
    "super_bulky": "Approx. 50 m / 100 g super chunky yarn",
}


# ---------------------------------------------------------------------------
# Pattern templates (in UK terminology)
# ---------------------------------------------------------------------------

def _beanie_pattern(req: PatternRequest) -> Pattern:
    """Generate a basic beanie/hat pattern."""
    hook = HOOK_BY_WEIGHT.get(req.yarn_weight, "5.0 mm (UK 6, US H-8)")
    yarn = YARN_BY_WEIGHT.get(req.yarn_weight, "100 g Aran / worsted yarn")

    sizes = {
        "baby": (30, 15, 9, 45),
        "child": (42, 18, 12, 52),
        "adult_s": (50, 20, 14, 56),
        "adult_m": (54, 22, 16, 58),
        "adult_l": (58, 24, 18, 62),
        "one_size": (54, 22, 16, 58),
    }
    ch_count, body_rows, border_rows, head_circ = sizes.get(req.size, (54, 22, 16, 58))

    instructions = f"""\
Foundation: Using a magic ring (MR), chain (ch) 3 (counts as first treble crochet (tr)).

Round 1 (Rd 1): Work 11 tr into MR. Join with a slip stitch (sl st) to top of ch-3. (12 tr)

Rd 2: Ch 3, tr in same st, 2 tr in each st around. Sl st to top of ch-3. (24 tr)

Rd 3: Ch 3, tr in same st, *tr in next st, 2 tr in next st; rep from * around, tr in last st.
  Sl st to top of ch-3. (36 tr)

Rd 4: Ch 3, tr in same st, *tr in next 2 sts, 2 tr in next st; rep from * around, tr in last 2 sts.
  Sl st to top of ch-3. (48 tr)

Rd 5: Ch 3, tr in same st, *tr in next 3 sts, 2 tr in next st; rep from * around, tr in last 3 sts.
  Sl st to top of ch-3. (60 tr)

Rd 6–{body_rows}: Ch 3, tr in each st around. Sl st to top of ch-3. (60 tr)
  Continue working rounds without increasing until hat measures approx. {head_circ // 2} cm from centre.

Brim (optional ribbed edge):
  Work {border_rows} rows of dc in the back loop only (BLO) around the bottom edge.
  Sl st to join. Fasten off and weave in ends.

Finishing: Weave in all ends. Block lightly if desired."""

    return Pattern(
        title=f"Simple Crochet Beanie Hat ({req.size.replace('_', ' ').title()})",
        materials=[
            yarn,
            hook,
            "Yarn needle",
            "Stitch marker (optional)",
        ],
        abbreviations=(
            "ch=chain, MR=magic ring, tr=treble crochet, sl st=slip stitch, "
            "dc=double crochet, st=stitch, rd=round, rep=repeat, BLO=back loop only"
        ),
        gauge=f"14 tr × 8 rows = 10 cm square using {hook.split(' ')[0]} hook.",
        instructions=instructions,
        notes=[
            "Pattern is worked from the crown down in rounds.",
            "Adjust the number of body rounds for a deeper or shallower hat.",
            "For a pom-pom, attach one to the crown after finishing.",
        ],
    )


def _scarf_pattern(req: PatternRequest) -> Pattern:
    """Generate a basic scarf / cowl pattern."""
    hook = HOOK_BY_WEIGHT.get(req.yarn_weight, "5.0 mm (UK 6, US H-8)")
    yarn = YARN_BY_WEIGHT.get(req.yarn_weight, "100 g Aran / worsted yarn")

    is_cowl = "cowl" in req.raw.lower() or "snood" in req.raw.lower()
    stitch_count = 12 if req.yarn_weight in ("bulky", "super_bulky") else 16
    length_rows = 20 if req.yarn_weight in ("bulky", "super_bulky") else 30

    if is_cowl:
        instructions = f"""\
Foundation: Ch {stitch_count * 4}. Sl st to first ch to form a loop (take care not to twist).

Rd 1: Ch 3 (counts as tr), tr in each ch around. Sl st to top of ch-3. ({stitch_count * 4} tr)

Rd 2–{length_rows}: Ch 3, tr in each st around. Sl st to top of ch-3.

Fasten off. Weave in ends. Block to measurements if desired."""
        title = f"Simple Crochet Cowl ({req.size.replace('_', ' ').title()})"
    else:
        width_ch = stitch_count + 3
        instructions = f"""\
Foundation: Ch {width_ch}.

Row 1: Tr in 4th ch from hook (skipped ch count as tr), tr in each ch across. Turn. ({stitch_count} tr)

Row 2–{length_rows * 6}: Ch 3 (counts as tr), tr in each st across to end. Turn. ({stitch_count} tr)

Fasten off. Weave in ends. Block if desired."""
        title = f"Simple Crochet Scarf ({req.size.replace('_', ' ').title()})"

    return Pattern(
        title=title,
        materials=[
            f"2–3 balls of {yarn}",
            hook,
            "Yarn needle",
        ],
        abbreviations=(
            "ch=chain, tr=treble crochet, sl st=slip stitch, "
            "st=stitch, rd=round, rep=repeat"
        ),
        gauge=f"14 tr × 8 rows = 10 cm square using {hook.split(' ')[0]} hook.",
        instructions=instructions,
        notes=[
            "Adjust the foundation chain length to change the width.",
            "Add a border in double crochet for a neater edge.",
            "Fringe can be added to scarf ends if desired.",
        ],
    )


def _granny_square_pattern(req: PatternRequest) -> Pattern:
    """Generate a classic granny square pattern."""
    hook = HOOK_BY_WEIGHT.get(req.yarn_weight, "4.0 mm (UK 8, US G-6)")
    yarn = YARN_BY_WEIGHT.get(req.yarn_weight, "DK yarn in 3–4 colours")

    instructions = """\
Using Colour A, make a magic ring (MR).

Round 1 (Rd 1): Ch 3 (counts as tr), 2 tr in MR, ch 2, *3 tr in MR, ch 2; rep from * 2 more times.
  Sl st to top of ch-3. Fasten off Colour A. (4 tr clusters, 4 ch-2 corner spaces)

Rd 2: Join Colour B to any ch-2 corner space.
  Ch 3, 2 tr in same space, ch 2, 3 tr in same space (corner made),
  *ch 1, (3 tr, ch 2, 3 tr) in next ch-2 corner space; rep from * 2 more times, ch 1.
  Sl st to top of ch-3. Fasten off Colour B.

Rd 3: Join Colour C to any ch-2 corner space.
  Ch 3, 2 tr in same space, ch 2, 3 tr in same space (corner made),
  *ch 1, 3 tr in next ch-1 space, ch 1, (3 tr, ch 2, 3 tr) in corner space;
  rep from * 2 more times, ch 1, 3 tr in next ch-1 space, ch 1.
  Sl st to top of ch-3. Fasten off Colour C.

Rd 4: Join Colour D (or Colour A) to any ch-2 corner space.
  Ch 3, 2 tr in same space, ch 2, 3 tr in same space (corner made),
  *(ch 1, 3 tr in next ch-1 space) across to next corner, ch 1,
  (3 tr, ch 2, 3 tr) in corner space; rep from * to end, ch 1.
  Sl st to top of ch-3. Fasten off.

Finishing: Weave in all ends. Block square to approx. 15 × 15 cm."""

    return Pattern(
        title="Classic Granny Square",
        materials=[
            f"{yarn} in 3–4 colours (labelled A, B, C, D)",
            hook,
            "Yarn needle",
            "Scissors",
        ],
        abbreviations=(
            "ch=chain, MR=magic ring, tr=treble crochet, sl st=slip stitch, "
            "sp=space, st=stitch, rd=round, rep=repeat"
        ),
        gauge="Finished square approx. 15 × 15 cm blocked.",
        instructions=instructions,
        notes=[
            "This pattern can be repeated to make as many squares as needed.",
            "Join squares using sl st or dc join method.",
            "For a blanket, make 6×8 squares and join for a 90×120 cm throw.",
            "Use a single colour throughout for a modern look.",
        ],
    )


def _dishcloth_pattern(req: PatternRequest) -> Pattern:
    """Generate a simple dishcloth / facecloth pattern."""
    hook = "4.0 mm (UK 8, US G-6)"
    yarn = "50–75 g cotton DK yarn"

    instructions = """\
Foundation: Ch 31.

Row 1: Dc in 2nd ch from hook and each ch across. Turn. (30 dc)

Row 2: Ch 1, dc in each st across. Turn. (30 dc)

Rows 3–30: Repeat Row 2.

Border (optional):
  Round 1: Ch 1, dc evenly around all four edges, working 3 dc in each corner.
  Sl st to first dc to join. Fasten off.

Weave in ends."""

    return Pattern(
        title="Simple Double Crochet Dishcloth / Facecloth",
        materials=[
            yarn,
            hook,
            "Yarn needle",
        ],
        abbreviations=(
            "ch=chain, dc=double crochet, sl st=slip stitch, st=stitch"
        ),
        gauge="18 dc × 20 rows = 10 cm square using 4.0 mm hook and cotton DK.",
        instructions=instructions,
        notes=[
            "Use 100% cotton yarn for best absorbency.",
            "Adjust size by changing foundation chain and number of rows.",
            "Works well as a face cloth or eco-friendly kitchen dishcloth.",
        ],
    )


def _bag_pattern(req: PatternRequest) -> Pattern:
    """Generate a simple market bag pattern."""
    hook = HOOK_BY_WEIGHT.get(req.yarn_weight, "5.0 mm (UK 6, US H-8)")
    yarn = YARN_BY_WEIGHT.get(req.yarn_weight, "100 g Aran yarn")

    instructions = """\
Base:
  Ch 21. Work in rows of dc until piece measures 20 cm.
  Do not fasten off; pivot to work around the base in rounds.

Body:
  Round 1 (Rd 1): Ch 3 (counts as tr), tr evenly around base perimeter.
  Sl st to top of ch-3.

Rd 2–20: Ch 3, tr in each st around. Sl st to top of ch-3.

Mesh section (optional, for a lacy market bag look):
  Rd 21–30: Ch 5, *sk 1 st, tr in next st, ch 2; rep from * around. Sl st to 3rd ch.

Top edging:
  Work 2 rounds of dc around the top opening.

Handles (make 2):
  Ch 60. Sl st to first ch to form a loop.
  Work 2 rounds of dc around loop. Fasten off.
  Attach handles to opposite sides of the bag top.

Fasten off. Weave in all ends."""

    return Pattern(
        title="Simple Crochet Market Bag / Tote",
        materials=[
            f"200 g {yarn}",
            hook,
            "Yarn needle",
            "Stitch marker",
        ],
        abbreviations=(
            "ch=chain, dc=double crochet, tr=treble crochet, sl st=slip stitch, "
            "st=stitch, rd=round, sk=skip, rep=repeat"
        ),
        gauge=f"14 tr × 8 rows = 10 cm square using {hook.split(' ')[0]} hook.",
        instructions=instructions,
        notes=[
            "Use cotton or jute yarn for a sturdy grocery bag.",
            "The mesh section reduces weight and adds stretch.",
            "Block when wet to open up the mesh stitches.",
        ],
    )


def _blanket_pattern(req: PatternRequest) -> Pattern:
    """Generate a simple blanket pattern."""
    hook = HOOK_BY_WEIGHT.get(req.yarn_weight, "6.5 mm (UK 3, US K-10½)")
    yarn = YARN_BY_WEIGHT.get(req.yarn_weight, "chunky yarn")

    sizes = {
        "baby": (60, 80),
        "child": (80, 100),
        "adult_s": (120, 150),
        "adult_m": (130, 170),
        "adult_l": (150, 200),
        "one_size": (130, 170),
    }
    width_cm, length_cm = sizes.get(req.size, (130, 170))

    # Rough stitch count: 1 tr ≈ 0.7 cm in bulky yarn
    stitch_width = max(20, int(width_cm / 0.7))
    ch_count = stitch_width + 3

    instructions = f"""\
Foundation: Ch {ch_count}.

Row 1: Tr in 4th ch from hook and each ch across. Turn. ({stitch_width} tr)

Row 2+: Ch 3 (counts as tr), tr in each st across. Turn. ({stitch_width} tr)

Continue until blanket measures approx. {length_cm} cm from foundation.

Border:
  Round 1: Ch 1, dc evenly around all four edges, working 3 dc in each corner.
  Sl st to join.

  Round 2: Ch 1, dc in each st around, 3 dc in corner sts.
  Sl st to join. Fasten off.

Weave in all ends. Block to measurements."""

    return Pattern(
        title=f"Simple Crochet Blanket / Throw ({width_cm}×{length_cm} cm)",
        materials=[
            f"600–900 g {yarn}",
            hook,
            "Yarn needle",
            "Stitch marker",
        ],
        abbreviations=(
            "ch=chain, tr=treble crochet, dc=double crochet, sl st=slip stitch, "
            "st=stitch"
        ),
        gauge=f"10 tr × 6 rows = 10 cm square using {hook.split(' ')[0]} hook.",
        instructions=instructions,
        notes=[
            "Use a chunky or super chunky yarn for a quicker crochet.",
            "Adjust chain count to change the width.",
            "For a striped blanket, change colour every 2–4 rows.",
        ],
    )


def _amigurumi_pattern(req: PatternRequest) -> Pattern:
    """Generate a basic amigurumi ball / body shape."""
    hook = "3.0 mm (UK 11, US C-2/D-3)"
    yarn = "50 g DK amigurumi yarn"

    # Detect what animal/toy
    lower = req.raw.lower()
    animal = "bunny" if "bunny" in lower or "rabbit" in lower else \
             "bear" if "bear" in lower or "teddy" in lower else \
             "cat" if "cat" in lower else \
             "dog" if "dog" in lower else "animal"

    instructions = f"""\
Body (work in a continuous spiral, do not join rounds):

Round 1 (Rd 1): 6 dc into MR. (6 dc)

Rd 2: 2 dc in each st around. (12 dc)

Rd 3: *Dc in next st, 2 dc in next st; rep from * around. (18 dc)

Rd 4: *Dc in next 2 sts, 2 dc in next st; rep from * around. (24 dc)

Rd 5: *Dc in next 3 sts, 2 dc in next st; rep from * around. (30 dc)

Rd 6–10: Dc in each st around. (30 dc)

Rd 11: *Dc in next 3 sts, dc2tog; rep from * around. (24 dc)

Rd 12: *Dc in next 2 sts, dc2tog; rep from * around. (18 dc)
  Begin stuffing firmly with polyester fiberfill.

Rd 13: *Dc in next st, dc2tog; rep from * around. (12 dc)

Rd 14: *Dc2tog; rep from * around. (6 dc)
  Finish stuffing. Cut yarn leaving a 15 cm tail.
  Thread tail through remaining 6 sts, pull tight to close. Knot securely.

Head: Make another piece following Rd 1–10 above. Sew to body when finished.

Ears (for {animal}, make 2):
  Rd 1: 6 dc into MR.
  Rd 2: 2 dc in each st around. (12 dc)
  Rd 3–5: Dc in each st around.
  Sl st to close. Flatten ear and sew onto head.

Finishing:
  Add safety eyes between Rd 6 and Rd 7 of head, 6–8 sts apart.
  Embroider nose with black yarn.
  Sew head securely to body.
  Weave in all ends."""

    return Pattern(
        title=f"Simple Amigurumi {animal.title()}",
        materials=[
            yarn,
            hook,
            "Polyester fibrefill stuffing",
            "2 × safety eyes (10–12 mm)",
            "Yarn needle",
            "Stitch marker",
        ],
        abbreviations=(
            "MR=magic ring, dc=double crochet, sl st=slip stitch, "
            "dc2tog=double crochet two together (decrease), "
            "st=stitch, rd=round, rep=repeat"
        ),
        gauge="Gauge is not critical for amigurumi. Use a tight tension to hide stuffing.",
        instructions=instructions,
        notes=[
            "Work in continuous spiral rounds – do not join at end of each round.",
            "Use a stitch marker to track the beginning of each round.",
            "Stuff firmly as you go for a neat shape.",
            "Do not use safety eyes for toys intended for children under 3.",
        ],
    )


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

# Items that can be generated
SUPPORTED_ITEMS = frozenset([
    "beanie", "scarf", "granny_square", "dishcloth", "bag", "blanket", "amigurumi",
])

_GENERATORS = {
    "beanie": _beanie_pattern,
    "scarf": _scarf_pattern,
    "granny_square": _granny_square_pattern,
    "dishcloth": _dishcloth_pattern,
    "bag": _bag_pattern,
    "blanket": _blanket_pattern,
    "amigurumi": _amigurumi_pattern,
}


def generate_pattern(request: PatternRequest) -> Optional[Pattern]:
    """
    Generate a crochet pattern for the given request.

    Returns a Pattern if the item type is supported, or None if the request
    is too complex or the item type is not recognised.
    """
    generator = _GENERATORS.get(request.item_type)
    if generator is None:
        return None
    return generator(request)


def can_generate(request: PatternRequest) -> bool:
    """Return True if the agent can generate a pattern for this request."""
    return request.item_type in SUPPORTED_ITEMS
