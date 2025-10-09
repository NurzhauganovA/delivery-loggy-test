import pytest

from api.domain.pan import Pan


@pytest.mark.parametrize(
    "pan, masks, expected",
    [
        ("1111222233334444", ["11113333", "11112222"], True),
        ("1234567890123456", ["11113333", "11112222"], False),
        ("1111222233334444", ["12341234"], False),
        ("1111222233334444", ["11112222"], True),
        ("1111222233334444", [], False),
    ]
)
def test_validate_by_masks(pan, masks, expected):
    pan = Pan(value=pan)
    result = pan.is_matched_by_any_mask(masks=masks)
    assert result is expected
