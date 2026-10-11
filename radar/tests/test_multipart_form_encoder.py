from radar.multipart_form_encoder import FormPart, encode_multipart_form


def test_encodes_each_part_with_name_and_content_type() -> None:
    parts = [
        FormPart(name="query", content='{"a":1}', content_type="application/json"),
        FormPart(name="languages", content='["en"]', content_type="application/json"),
    ]
    content_type_header, body = encode_multipart_form(parts, boundary="XBOUNDARY")
    text = body.decode("utf-8")
    assert content_type_header == "multipart/form-data; boundary=XBOUNDARY"
    assert 'Content-Disposition: form-data; name="query"' in text
    assert "Content-Type: application/json" in text
    assert '{"a":1}' in text
    assert text.endswith("--XBOUNDARY--\r\n")


def test_part_has_no_filename() -> None:
    _, body = encode_multipart_form([FormPart("query", "{}", "application/json")], boundary="B")
    assert b"filename" not in body


def test_boundary_is_generated_when_not_given() -> None:
    content_type_header, _ = encode_multipart_form([FormPart("q", "x", "text/plain")])
    assert content_type_header.startswith("multipart/form-data; boundary=")
