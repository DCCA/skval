import classify


def _md(desc, body=""):
    return f"---\nname: x\ndescription: {desc}\n---\n{body}"


def test_file_transform():
    r = classify.classify_skill(
        _md(
            "Use whenever the user wants to do anything with PDF files: extract text, merge PDFs, fill forms, OCR."
        )
    )
    assert r["type"] == "file_transform"


def test_interactive():
    r = classify.classify_skill(
        _md(
            "Concierge-style flow that asks about budget and dietary needs before placing an order."
        )
    )
    assert r["type"] == "interactive"


def test_discipline():
    r = classify.classify_skill(
        _md(
            "Test-driven development: always write a failing test first (RED), then make it pass (GREEN), then refactor."
        )
    )
    assert r["type"] == "discipline"


def test_reference():
    r = classify.classify_skill(
        _md("Reference knowledge to answer questions about the product's pricing and limits.")
    )
    assert r["type"] == "reference"


def test_default_task():
    r = classify.classify_skill(_md("Produce a haiku from a topic the user provides."))
    assert r["type"] == "task"


def test_recommend_strategy():
    assert classify.recommend_strategy("interactive")["executor"] == "multi_turn"
    assert classify.recommend_strategy("file_transform")["fixtures"] is True
    assert classify.recommend_strategy("task")["executor"] == "single_turn"
    # unknown type falls back to task strategy
    assert classify.recommend_strategy("???")["executor"] == "single_turn"


def test_signals_are_exposed():
    r = classify.classify_skill(_md("Extract tables from .xlsx spreadsheets."))
    assert r["signals"]["file_transform"]  # transparent: which patterns matched
    assert "scores" in r and "also" in r


def test_confidence():
    # clear winner -> high
    strong = classify.classify_skill(
        _md(
            "Use whenever the user wants to do anything with PDF files: extract text, merge PDFs, OCR."
        )
    )
    assert strong["confidence"] == "high"
    # plain task (no signals) -> medium default, not flagged as ambiguous
    plain = classify.classify_skill(_md("Produce a haiku from a topic the user provides."))
    assert plain["type"] == "task" and plain["confidence"] == "medium"
    # genuine tie between two types -> low (agent should confirm)
    tie = classify.classify_skill(
        _md("Update the spreadsheet after you ask the user for the new total.")
    )
    assert tie["confidence"] == "low" and tie["also"]
