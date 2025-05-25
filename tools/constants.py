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

# Chemistry-specific constants
CHEMISTRY_CONSTANTS = {
    "avogadro_number": 6.022e23,
    "gas_constant": 8.314,  # J/(mol·K)
    "planck_constant": 6.626e-34,  # J·s
    "boltzmann_constant": 1.381e-23,  # J/K
    "electron_mass": 9.109e-31,  # kg
    "proton_mass": 1.673e-27,  # kg
    "elementary_charge": 1.602e-19,  # C
    "atomic_mass_unit": 1.661e-27,  # kg
}