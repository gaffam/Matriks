from spec_reader import parse_spec

def test_parse_spec(tmp_path):
    spec = tmp_path / "spec.txt"
    spec.write_text("Bu ihalede 5 adet kamera ve 3 personel istenmektedir")
    result = parse_spec(spec)
    assert result["kamera"] == 5
    assert result["personel"] == 3
