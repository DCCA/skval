import conversation as C

CONVO = [
    {"role": "user", "content": "I want to order groceries for the week"},
    {
        "role": "assistant",
        "content": "Happy to help! Any dietary restrictions I should know about?",
    },
    {"role": "user", "content": "Vegetarian"},
    {"role": "assistant", "content": "Got it. And what's your budget for this order?"},
    {"role": "user", "content": "About $50"},
    {
        "role": "assistant",
        "content": "Here is your order summary: spinach, tofu, rice... Total $48.",
    },
]


def test_count_questions():
    assert C.count_questions(CONVO) == 2  # two assistant turns ask a question


def test_questions_before_delivery_defaults_to_last_assistant():
    assert C.questions_before_delivery(CONVO) == 2  # both asked before the summary turn


def test_questions_before_explicit_delivery_index():
    # If delivery is the 2nd assistant turn (index 3), only one question preceded it.
    assert C.questions_before_delivery(CONVO, delivered_at=3) == 1


def test_meets_min_questions():
    assert C.meets_min_questions(CONVO, 2) is True
    assert C.meets_min_questions(CONVO, 3) is False


def test_asked_about_keywords():
    res = C.asked_about(CONVO, ["dietary", "budget", "payment"])
    assert res["dietary"] is True and res["budget"] is True and res["payment"] is False


def test_single_turn_has_no_questions():
    st = [
        {"role": "user", "content": "sum 2+2"},
        {"role": "assistant", "content": "Done. Result: 4."},
    ]
    assert C.count_questions(st) == 0
    assert C.meets_min_questions(st, 1) is False


def test_tolerates_empty_and_missing_fields():
    assert C.count_questions([]) == 0
    assert C.questions_before_delivery([]) == 0
    assert C.count_questions([{"role": "assistant"}]) == 0  # no content key
