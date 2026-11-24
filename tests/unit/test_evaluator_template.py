"""Contract for the blank review record supplied by the bundled evaluator template."""

from pathlib import Path


def test_handoff_requests_a_grade_and_evidence_for_every_rubric_criterion() -> None:
    template = Path(__file__).resolve().parents[2] / "core" / "docs" / "EVALUATOR.md"
    rubric, heading, handoff = template.read_text().partition("## Review handoff")
    assert heading, "The evaluator has no review handoff"
    criteria = [line.split(". ", 1)[1] for line in rubric.splitlines() if line.startswith("### ")]
    assert len(criteria) == 4
    assert "| Criterion | Grade | Evidence |" in handoff
    for criterion in criteria:
        assert f"| {criterion} |" in handoff


def test_separate_evaluator_assignment_can_be_copied_into_a_fresh_session() -> None:
    template = Path(__file__).resolve().parents[2] / "core" / "docs" / "EVALUATOR.md"
    _, heading, section = template.read_text().partition("## Assign a separate evaluator")
    assert heading, "Missing separate evaluator procedure"
    prompt = section.split("```text\n", 1)[1].split("```", 1)[0]
    for reference in ("<revision>", "<handoff>", "AGENTS.md", "docs/EVALUATOR.md"):
        assert reference in prompt
