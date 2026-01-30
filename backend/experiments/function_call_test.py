import os, sys
import json
from openai import OpenAI

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.print import to_serializable
from tools.weather import WeatherTool


def main():
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    print("Welcome to the Weather Assistant! Type 'exit' to quit.")

    weather_tool = WeatherTool()
    tool_dispatch = {
        "get_weather": weather_tool.get_weather,
    }

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            break

        completion = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": user_input}],
            tools=weather_tool.get_tools(),
        )

        choice_dict = to_serializable(completion.choices[0])
        tool_calls = choice_dict.get("message", {}).get("tool_calls", [])
        if tool_calls:
            for call in tool_calls:
                func_name = call["function"]["name"]
                args = json.loads(call["function"]["arguments"])
                print(func_name, args)
                if func_name in tool_dispatch:
                    result = tool_dispatch[func_name](**args)
                    print(f"[Tool: {func_name}] Result: {result}")
                else:
                    print(f"Unknown tool: {func_name}")
        else:
            # If no tool call, print the model's message content
            content = choice_dict.get("message", {}).get("content")
            if content:
                print(f"Assistant: {content}")
            else:
                print("Assistant: (No response)")


if __name__ == "__main__":
    main()
