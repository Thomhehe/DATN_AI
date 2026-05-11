from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def is_valid_output(content: str) -> bool:
    """Check AI output đúng format chưa"""
    if not content:
        return False

    if "###FILE:" not in content:
        return False

    # phải đúng 2 file
    if content.count("###FILE:") != 4:
        return False

    return True


def generate_code(prompt, max_retries=3):
    last_error = ""

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a Senior QA Automation Engineer.\n"
                            "Always follow output format EXACTLY.\n"
                            "Only return code.\n"
                            "If format is wrong, response is invalid."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            content = response.choices[0].message.content.strip()

            if is_valid_output(content):
                return content

            last_error = "Sai format (không đủ 4 ###FILE)"

        except Exception as e:
            last_error = str(e)

        print(f"Retry {attempt + 1} failed: {last_error}")

    return f"# ERROR: {last_error}"