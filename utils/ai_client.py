from openai import OpenAI
import os
from dotenv import load_dotenv


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def is_valid_output(content: str, expected_files: int = 3) -> bool:
    """
    Kiểm tra output AI có đúng số lượng ###FILE hay không.
    expected_files: mặc định là 3 (pages, tests, data)
    """
    if not content:
        return False

    if "###FILE:" not in content:
        return False

    return content.count("###FILE:") >= expected_files


def generate_code(prompt, expected_files: int = 3, max_retries: int = 3):
    """
    expected_files: mặc định là 3 (pages, tests, data)
    """
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

            if is_valid_output(content, expected_files=expected_files):
                return content

            last_error = (
                f"Sai format (không đủ {expected_files} ###FILE)"
            )

        except Exception as e:
            last_error = str(e)

        print(f"Retry {attempt + 1} failed: {last_error}")

    return f"# ERROR: {last_error}"