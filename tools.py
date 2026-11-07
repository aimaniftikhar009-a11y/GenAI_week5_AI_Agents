import requests
import ast
import operator


# TOOL 1: LIVE WEATHER FUNCTION

def get_weather(location: str):
    """Get current weather information for a city."""

    try:
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"

        geo_params = {
            "name": location,
            "count": 1,
            "language": "en",
            "format": "json"
        }

        geo_response = requests.get(
            geo_url,
            params=geo_params,
            timeout=15
        )

        geo_response.raise_for_status()

        geo_data = geo_response.json()

        if not geo_data.get("results"):
            return {"error": "City not found"}

        city = geo_data["results"][0]

        latitude = city["latitude"]
        longitude = city["longitude"]

        weather_url = "https://api.open-meteo.com/v1/forecast"

        weather_params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m"
        }

        weather_response = requests.get(
            weather_url,
            params=weather_params,
            timeout=15
        )

        weather_response.raise_for_status()

        data = weather_response.json()

        current = data["current"]

        return {
            "city": city["name"],
            "temperature": current["temperature_2m"],
            "humidity": current["relative_humidity_2m"],
            "feels_like": current["apparent_temperature"],
            "wind_speed": current["wind_speed_10m"]
        }

    except Exception as e:
        return {"error": str(e)}


# TOOL 2: MATHEMATICAL CALCULATOR

def calculate(expression: str):
    """Perform safe mathematical calculations."""

    operations = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.Mod: operator.mod
    }

    def evaluate(node):

        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        elif isinstance(node, ast.Constant):
            if type(node.value) in (int, float):
                return node.value

            raise ValueError("Only numbers are allowed")

        elif isinstance(node, ast.BinOp):

            op = type(node.op)

            if op not in operations:
                raise ValueError("Operation not allowed")

            left = evaluate(node.left)
            right = evaluate(node.right)

            if op == ast.Pow and abs(right) > 10:
                raise ValueError("Exponent is too large")

            result = operations[op](left, right)

            if abs(result) > 1e100:
                raise ValueError("Result is too large")

            return result

        elif isinstance(node, ast.UnaryOp):

            value = evaluate(node.operand)

            if isinstance(node.op, ast.USub):
                return -value

            if isinstance(node.op, ast.UAdd):
                return value

            raise ValueError("Operation not allowed")

        raise ValueError("Invalid mathematical expression")

    try:

        tree = ast.parse(expression, mode="eval")

        answer = evaluate(tree)

        return {
            "expression": expression,
            "answer": answer
        }

    except Exception as e:

        return {"error": str(e)}