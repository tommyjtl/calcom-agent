# System imports
import os, sys, json
import traceback

# Flask imports
from flask import Flask, request, jsonify
from flask_cors import CORS

# Cal.com wrapper, utils imports
from cal import CalComTool
from tools.system import get_system_message
from utils.datetime import get_current_server_time, get_current_server_time_in_iso
from utils.print import to_serializable

# Environment variable imports
from openai import OpenAI
from dotenv import load_dotenv

# Load the project-wise .env variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # @TODO: Add CORS constraints in the future

# Initialize OpenAI client and tools at start
# client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY_LIVEXAI"))
cal_tool = CalComTool(api_key=os.getenv("CALCOM_API_KEY"))
tool_dispatch = {
    "cancel_user_booking": cal_tool.cancel_user_booking,
    "create_a_cal_booking": cal_tool.create_a_cal_booking,
    "list_all_cal_bookings": cal_tool.list_all_cal_bookings,
}
tool_specs = cal_tool.get_function_call_specs()

# Store conversation sessions
# @TODO: Change from in-program store to DB store (SQLite or Posgres)
sessions = {}


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Main chat endpoint that processes user messages and returns AI responses
    Expected JSON body:
    {
        "message": "user message",
        "session_id": "optional session identifier"
    }
    """
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Message is required"}), 400

        # Extract user message and session ID
        user_message = data["message"].strip()
        session_id = data.get(
            "session_id", "default"
        )  # Use "default" if no session ID provided

        # Initialize session if it doesn't exist
        if session_id not in sessions:
            sessions[session_id] = [get_system_message()]

        # Create a new message list for the session
        messages = sessions[session_id]

        # Always remind the assistant of the current date and time
        now_str = get_current_server_time()
        messages.append(
            {
                "role": "system",
                "content": f"Reminder: The current date and time is {now_str}.",
            }
        )
        # Add user message to the session
        messages.append({"role": "user", "content": user_message})

        # Create the OpenAI chat completion request
        completion = client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
            tools=tool_specs,
        )

        # Process the response
        choice_dict = to_serializable(completion.choices[0])
        tool_calls = choice_dict.get("message", {}).get("tool_calls", [])

        # Prepare the response data
        response_data = {"message": "", "tool_results": [], "session_id": session_id}

        if tool_calls:
            # If there are tool calls, execute them
            for call in tool_calls:
                func_name = call["function"]["name"]
                args = json.loads(call["function"]["arguments"])

                if func_name in tool_dispatch:
                    result = tool_dispatch[func_name](**args)
                    response_data["tool_results"].append(
                        {"tool": func_name, "args": args, "result": result}
                    )
                else:
                    response_data["tool_results"].append(
                        {
                            "tool": func_name,
                            "args": args,
                            "error": f"Unknown tool: {func_name}",
                        }
                    )

            # Add tool call response to messages
            messages.append(
                {
                    "role": "assistant",
                    "content": f"I've executed the requested tools. Results: {response_data['tool_results']}",
                }
            )
        else:
            # If no tool call, return the model's message content
            content = choice_dict.get("message", {}).get("content")
            if content:
                response_data["message"] = content
                messages.append({"role": "assistant", "content": content})
            else:
                response_data["message"] = "No response generated"

        # Update session
        sessions[session_id] = messages

        return jsonify(response_data)

    except Exception as e:
        # @TODO: Return nice error response to the client

        # Get detailed traceback information
        tb = traceback.format_exc()
        exc_type, _, exc_traceback = sys.exc_info()

        # Get the line number where the error occurred
        line_number = exc_traceback.tb_lineno if exc_traceback else "Unknown"

        error_details = {
            "error": str(e),
            "error_type": exc_type.__name__ if exc_type else "Unknown",
            "line_number": line_number,
            "traceback": (
                tb.split("\n") if app.debug else None
            ),  # Only show traceback in debug mode
            "endpoint": "/api/chat",
        }

        return jsonify(error_details), 500


@app.route("/api/sessions/<session_id>", methods=["DELETE"])
def clear_session(session_id):
    """Clear a specific conversation session"""
    if session_id in sessions:
        del sessions[session_id]
        return jsonify({"message": f"Session {session_id} cleared"})
    return jsonify({"message": "Session not found"}), 404


@app.route("/api/sessions", methods=["GET"])
def list_sessions():
    """List all active sessions"""
    return jsonify({"sessions": list(sessions.keys())})


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": get_current_server_time_in_iso()})


if __name__ == "__main__":
    print("Starting Flask server for personal schedule booking system...")
    app.run(debug=True, host="0.0.0.0", port=3020)
