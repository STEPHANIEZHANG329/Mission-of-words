from mission_of_words.layout import (
    INNER_SAFETY_INCHES,
    OUTER_SAFETY_INCHES,
    SAFE_MARGIN_INCHES,
    page_margins_inches,
)


def test_facing_page_parity_puts_gutter_on_the_inside():
    odd = page_margins_inches(1)
    even = page_margins_inches(2)
    assert odd["left"] == INNER_SAFETY_INCHES
    assert odd["right"] == OUTER_SAFETY_INCHES
    assert even["right"] == INNER_SAFETY_INCHES
    assert even["left"] == OUTER_SAFETY_INCHES
    assert INNER_SAFETY_INCHES > OUTER_SAFETY_INCHES
    assert min(INNER_SAFETY_INCHES, OUTER_SAFETY_INCHES) >= SAFE_MARGIN_INCHES
