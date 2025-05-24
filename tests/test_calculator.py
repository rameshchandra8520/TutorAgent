from tools.calculator import calculate

def test_calculator():
    assert calculate("2 + 3") == 5.0
    assert calculate("6 * 4") == 24.0
    assert calculate("10 / 2") == 5.0
    assert calculate("5 - 3") == 2.0
    assert "Error" in calculate("10 / 0")
    print("Calculator tests passed!")

if __name__ == "__main__":
    test_calculator()