import string

from app.services.encoding import encode, decode


def test_encode_zero():
    assert encode(0) == "0"


def test_encode_small_numbers():
    assert encode(1) == "1"
    assert encode(61) == "Z"
    assert encode(62) == "10"


def test_decode_reverses_encode():
    for n in [0, 1, 61, 62, 12345, 999_999_999]:
        assert decode(encode(n)) == n


def test_encoded_output_is_url_safe():
    safe_chars = set(string.ascii_letters + string.digits)
    for n in [1, 123456, 999_999_999]:
        code = encode(n)
        assert all(char in safe_chars for char in code)


def test_encode_is_deterministic():
    assert encode(42) == encode(42)