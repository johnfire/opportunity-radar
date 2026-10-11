from radar.plain_text_extraction import extract_plain_text, shorten_text


def test_strips_tags_and_collapses_whitespace() -> None:
    html = "<p>Als <strong>Landesamt</strong></p>\n\n<p>sind   wir da.</p>"
    assert extract_plain_text(html) == "Als Landesamt sind wir da."


def test_unescapes_html_entities() -> None:
    assert extract_plain_text("<p>Kosten &amp; Nutzen&nbsp;heute</p>") == "Kosten & Nutzen heute"


def test_handles_none_and_empty_input() -> None:
    assert extract_plain_text(None) == ""
    assert extract_plain_text("") == ""


def test_shorten_text_keeps_short_text_unchanged() -> None:
    assert shorten_text("kurz", 10) == "kurz"


def test_shorten_text_cuts_at_word_boundary_with_ellipsis() -> None:
    assert shorten_text("ein sehr langer Satz hier", 14) == "ein sehr…"
