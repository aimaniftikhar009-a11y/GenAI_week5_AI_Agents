from google.genai import types


weather_schema = types.FunctionDeclaration(

    name="get_weather",

    description="Get live weather information for a city.",

    parameters_json_schema={

        "type": "object",

        "properties": {

            "location": {

                "type": "string",

                "description": "Name of the city"

            }

        },

        "required": ["location"]

    }

)


calculator_schema = types.FunctionDeclaration(

    name="calculate",

    description="Perform mathematical calculations.",

    parameters_json_schema={

        "type": "object",

        "properties": {

            "expression": {

                "type": "string",

                "description": "Mathematical expression"

            }

        },

        "required": ["expression"]

    }

)


agent_tools = types.Tool(

    function_declarations=[

        weather_schema,

        calculator_schema

    ]

)