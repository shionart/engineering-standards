"""Pure rule: every reply ends with Updated, Created, Removed, Not done and the skills line."""

import re

LABELS = ["Updated", "Created", "Removed", "Not done"]
SKILLS_LABEL = "Relevant skill(s) not used"

# A label starts a line (after list marks, bold or quote marks) and is followed by a colon.
_PATTERNS = {label: re.compile(rf"(?im)^[\s>*_-]*{label}\b[\s*_]*:") for label in LABELS}
_SKILLS = re.compile(r"(?im)^[\s>*_-]*relevant skills?(?:\(s\))?\b[^\n]*\bnot used")


def missing_sections(text: str) -> list[str]:
    """The parts of the required closing block that the reply lacks, in the order they belong."""
    missing = [label for label in LABELS if not _PATTERNS[label].search(text)]
    if not _SKILLS.search(text):
        missing.append(SKILLS_LABEL)
    return missing
