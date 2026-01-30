class WeatherTool:
    ENDPOINT_PREFIX = "https://api.cal.com/v2/"

    def __init__(self):
        pass

    def get_weather(self, location):
        # Dummy implementation for demonstration
        return {"location": location, "temperature": "22°C", "condition": "Sunny"}

    def get_tools(self):
        return [
            # example weathers
            {
                "type": "function",
                "function": {
                    "name": "get_weather",  # name of the function
                    # "description": "Get current temperature for a given location.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City and country e.g. Bogotá, Colombia",
                            }
                        },
                        "required": ["location"],
                        "additionalProperties": False,
                    },
                    "strict": True,
                },
            }
        ]
