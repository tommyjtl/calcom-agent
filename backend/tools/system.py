import datetime
import tzlocal
import os


def get_system_message():
    now = datetime.datetime.now(tzlocal.get_localzone())
    now_str = now.strftime("%Y-%m-%d %H:%M:%S %Z%z")

    # Read the system prompt from the text file
    prompt_file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "system_prompt.txt"
    )
    try:
        # Read the system prompt from the file
        with open(prompt_file_path, "r", encoding="utf-8") as f:
            system_prompt = f.read().strip()
    except FileNotFoundError:
        # Fallback prompt if file is not found
        system_prompt = """
        You are a specialized scheduling assistant that helps with calendar management and booking appointments.
        """

    content = f"{system_prompt}\n\nThe current date and time is {now_str}."

    return {
        "role": "system",
        "content": content,
    }
