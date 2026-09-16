"""Unit tests verifying the integrity, schema, and routing assertions of CineFlow Agent Skills."""

import json
import re
from pathlib import Path

import pytest
import yaml

SKILLS_DIR = Path(__file__).resolve().parent.parent.parent / ".agents" / "skills"

EXPECTED_SKILLS = [
    "orchestrating_production_lifecycle",
    "triaging_studio_telemetry",
    "formatting_screenplays",
    "locking_character_continuity",
    "rendering_storyboard_frames",
    "directing_character_dialogue",
    "composing_cinematic_scores",
    "auditing_visual_continuity",
]

REQUIRED_SECTIONS = [
    "## When to use",
    "## When NOT to use",
    "## Workflow",
    "## Examples",
    "## Output format",
    "## Anti-patterns to avoid",
]

VALID_TRAJECTORY_MODES = {"EXACT", "IN_ORDER", "ANY_ORDER"}


def test_all_expected_skills_exist():
    """Verify all 8 domain skill directories and SKILL.md files exist."""
    for skill in EXPECTED_SKILLS:
        skill_dir = SKILLS_DIR / skill
        assert skill_dir.is_dir(), f"Skill directory missing: {skill_dir}"
        skill_md = skill_dir / "SKILL.md"
        assert skill_md.is_file(), f"SKILL.md missing in {skill_dir}"


@pytest.mark.parametrize("skill_name", EXPECTED_SKILLS)
def test_skill_markdown_structure_and_frontmatter(skill_name: str):
    """Validate YAML frontmatter and required markdown sections in each SKILL.md."""
    skill_md = SKILLS_DIR / skill_name / "SKILL.md"
    content = skill_md.read_text(encoding="utf-8")

    # Verify YAML frontmatter delimiters
    assert content.startswith("---\n"), f"Frontmatter missing start in {skill_name}"
    parts = content.split("---\n", 2)
    assert len(parts) >= 3, f"Invalid frontmatter structure in {skill_name}"
    frontmatter_raw = parts[1]
    body = parts[2]

    # Parse YAML frontmatter
    fm = yaml.safe_load(frontmatter_raw)
    assert isinstance(fm, dict), f"Frontmatter is not a mapping in {skill_name}"
    assert "name" in fm, f"Missing 'name' in frontmatter for {skill_name}"
    assert "description" in fm, f"Missing 'description' in frontmatter for {skill_name}"
    assert "version" in fm, f"Missing 'version' in frontmatter for {skill_name}"
    assert "license" in fm, f"Missing 'license' in frontmatter for {skill_name}"
    assert "allowed-tools" in fm, (
        f"Missing 'allowed-tools' in frontmatter for {skill_name}"
    )
    assert "metadata" in fm, f"Missing 'metadata' in frontmatter for {skill_name}"

    # Verify name is kebab-case
    assert re.match(r"^[a-z]+(-[a-z]+)*$", fm["name"]), (
        f"Skill name '{fm['name']}' must be kebab-case"
    )

    # Description length bound: <= 1024 chars
    desc = fm["description"].strip()
    assert len(desc) <= 1024, (
        f"Description in {skill_name} exceeds 1024 chars ({len(desc)} chars)"
    )
    assert "Do NOT use for" in desc, (
        f"Description in {skill_name} must specify explicit anti-triggers"
    )

    # Verify required body sections
    for sec in REQUIRED_SECTIONS:
        assert sec in body, f"Section '{sec}' missing in {skill_name}/SKILL.md"


@pytest.mark.parametrize("skill_name", EXPECTED_SKILLS)
def test_skill_eval_suite_schema_and_coverage(skill_name: str):
    """Validate that every skill has an evals/test_cases.json adhering to the canonical EDD schema."""
    eval_file = SKILLS_DIR / skill_name / "evals" / "test_cases.json"
    assert eval_file.is_file(), f"evals/test_cases.json missing in {skill_name}"

    with open(eval_file, encoding="utf-8") as f:
        cases = json.load(f)

    assert isinstance(cases, list), f"Test cases in {skill_name} must be a JSON array"
    assert len(cases) >= 3, (
        f"Expected at least 3 test cases for {skill_name}, found {len(cases)}"
    )

    has_positive = False
    has_negative = False

    for case in cases:
        # Schema checks
        assert "case_id" in case, f"Missing case_id in {case}"
        assert "description" in case, f"Missing description in {case}"
        assert "input" in case, f"Missing input in {case}"
        assert "expected_skill" in case, f"Missing expected_skill in {case}"
        assert "expected_tool_calls" in case, f"Missing expected_tool_calls in {case}"
        assert "expected_output_format" in case, (
            f"Missing expected_output_format in {case}"
        )
        assert "rubric" in case, f"Missing rubric in {case}"
        assert "trajectory_mode" in case, f"Missing trajectory_mode in {case}"

        assert case["trajectory_mode"] in VALID_TRAJECTORY_MODES, (
            f"Invalid trajectory_mode {case['trajectory_mode']} in {case['case_id']}"
        )
        assert isinstance(case["rubric"], list) and len(case["rubric"]) > 0

        # Check positive vs negative triggers
        if "Negative Trigger" in case["description"]:
            has_negative = True
        else:
            has_positive = True

    assert has_positive, (
        f"Skill {skill_name} must have at least one positive trigger test case"
    )
    assert has_negative, (
        f"Skill {skill_name} must have at least one negative trigger test case"
    )
