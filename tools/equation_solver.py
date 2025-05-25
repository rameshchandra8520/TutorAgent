import sympy as sp
from sympy import symbols, solve, Eq, sympify
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def solve_equation(equation_str: str) -> str:
    """
    Solve mathematical equations using SymPy.
    
    Args:
        equation_str (str): The equation to solve. Can be in various formats:
            - "x^2 + 3*x + 2 = 0" (standard equation)
            - "x^2 + 3*x + 2" (assumes equals 0)
            - "2*x + 5 = 3*x - 1" (equation with both sides)
            - "solve for x: x^2 - 4 = 0" (with solve instruction)
    
    Returns:
        str: The solution(s) or an error message
    """
    try:
        logger.info(f"Solving equation: {equation_str}")
        
        # Clean up the equation string
        equation_str = equation_str.strip()
        
        # Remove "solve for" instructions and extract variable if specified
        solve_pattern = r"solve for (\w+):\s*(.+)"
        match = re.search(solve_pattern, equation_str.lower())
        if match:
            var_name = match.group(1)
            equation_str = match.group(2)
        else:
            # Try to detect the main variable (most common letter)
            variables = re.findall(r'[a-zA-Z]', equation_str)
            if variables:
                var_name = max(set(variables), key=variables.count)
            else:
                var_name = 'x'  # default variable
        
        # Define the variable
        var = symbols(var_name)
        
        # Parse the equation
        if '=' in equation_str:
            # Split equation into left and right sides
            left_side, right_side = equation_str.split('=', 1)
            left_expr = sympify(left_side.strip())
            right_expr = sympify(right_side.strip())
            equation = Eq(left_expr, right_expr)
        else:
            # Assume the expression equals 0
            expr = sympify(equation_str)
            equation = Eq(expr, 0)
        
        # Solve the equation
        solutions = solve(equation, var)
        
        if not solutions:
            return "No real solutions found"
        elif len(solutions) == 1:
            solution = solutions[0]
            if solution.is_real:
                # Try to simplify and get numerical value
                numerical_value = float(solution.evalf())
                if solution.is_rational and solution.denominator != 1:
                    return f"{var_name} = {solution} ≈ {numerical_value:.6f}"
                else:
                    return f"{var_name} = {solution}"
            else:
                return f"{var_name} = {solution}"
        else:
            # Multiple solutions
            result_parts = []
            for i, sol in enumerate(solutions, 1):
                if sol.is_real:
                    numerical_value = float(sol.evalf())
                    if sol.is_rational and sol.denominator != 1:
                        result_parts.append(f"{var_name}_{i} = {sol} ≈ {numerical_value:.6f}")
                    else:
                        result_parts.append(f"{var_name}_{i} = {sol}")
                else:
                    result_parts.append(f"{var_name}_{i} = {sol}")
            return "Solutions:\n" + "\n".join(result_parts)
            
    except Exception as e:
        logger.error(f"Error solving equation: {str(e)}")
        return f"Error: Could not solve equation '{equation_str}'. {str(e)}"
