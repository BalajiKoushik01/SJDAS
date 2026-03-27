from backend.routers.auth import _create_access_token, _decode_token
from backend.services.contracts import normalize_decode_result


def test_decode_contract_normalization_supports_legacy_keys():
    payload = {
        "styleLabel": "Kanjivaram",
        "styleConfidence": 0.9,
        "svgUrl": "https://example.com/a.svg",
        "floatCheckPassed": True,
    }
    result = normalize_decode_result(payload)
    assert result.style_label == "Kanjivaram"
    assert result.style_confidence == 0.9
    assert result.svg_url == "https://example.com/a.svg"


def test_jwt_create_and_decode_round_trip():
    token = _create_access_token(subject="admin", roles=["admin"])
    user = _decode_token(token)
    assert user.username == "admin"
    assert "admin" in user.roles
