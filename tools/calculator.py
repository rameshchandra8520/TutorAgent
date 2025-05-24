def calculate(expression):
    try:
        # Remove whitespace and split by operator
        expression = expression.replace(" ", "")
        if "+" in expression:
            a, b = map(float, expression.split("+"))
            return a + b
        elif "-" in expression:
            a, b = map(float, expression.split("-"))
            return a - b
        elif "*" in expression:
            a, b = map(float, expression.split("*"))
            return a * b
        elif "/" in expression:
            a, b = map(float, expression.split("/"))
            if b == 0:
                raise ValueError("Division by zero")
            return a / b
        else:
            raise ValueError("Invalid expression")
    except Exception as e:
        return f"Error: {str(e)}"