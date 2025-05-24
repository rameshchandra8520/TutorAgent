import json

def get_constant(constant_name):
    try:
        with open("tools/constants.json", "r") as file:
            constants = json.load(file)
        constant_name = constant_name.lower()
        for key in constants:
            if constant_name in key.lower():
                return constants[key]
        return f"Error: Constant '{constant_name}' not found"
    except Exception as e:
        return f"Error: {str(e)}"