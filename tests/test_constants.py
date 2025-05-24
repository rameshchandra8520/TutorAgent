from tools.constants import get_constant

def test_constants():
    result = get_constant("speed of light")
    assert result["value"] == 299792458
    assert result["unit"] == "m/s"
    result = get_constant("gravitational constant")
    assert result["value"] == 6.67430e-11
    assert "Error" in get_constant("unknown constant")
    print("Constants tests passed!")

if __name__ == "__main__":
    test_constants()