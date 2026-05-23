from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def is_valid_output(content: str, expected_files: int = 3) -> bool:
    """
    Kiểm tra output AI có đúng số lượng ###FILE hay không.
    """

    if not content:
        return False

    # P1 không yêu cầu ###FILE
    if expected_files == 0:
        return True

    if "###FILE:" not in content:
        return False

    return content.count("###FILE:") >= expected_files


def generate_code(prompt, expected_files: int = 3, max_retries: int = 3):
    """
    Sinh code từ prompt.
    Luôn trả về dict để app.py không bị lỗi result.get().
    """

    last_error = ""
    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_tokens = 0

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

            # Cộng token của mọi lần gọi API
            usage = response.usage

            if usage:
                total_prompt_tokens += usage.prompt_tokens
                total_completion_tokens += usage.completion_tokens
                total_tokens += usage.total_tokens

            if is_valid_output(content, expected_files=expected_files):
                # Tạo usage giả để app.py dùng như cũ
                class Usage:
                    def __init__(self, p, c, t):
                        self.prompt_tokens = p
                        self.completion_tokens = c
                        self.total_tokens = t

                final_usage = Usage(
                    total_prompt_tokens,
                    total_completion_tokens,
                    total_tokens
                )

                return {
                    "content": content,
                    "usage": final_usage
                }

            last_error = f"Sai format (không đủ {expected_files} ###FILE)"

        except Exception as e:
            last_error = str(e)

        print(f"Retry {attempt + 1} failed: {last_error}")

        # Nếu fail toàn bộ retry
        class Usage:
            def __init__(self, p, c, t):
                self.prompt_tokens = p
                self.completion_tokens = c
                self.total_tokens = t

        final_usage = Usage(
            total_prompt_tokens,
            total_completion_tokens,
            total_tokens
        )

    return {
        "content": f"# ERROR: {last_error}",
        "usage": final_usage
    }