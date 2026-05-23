def build_prompt_all(testcases, url):

    content = ""
    for tc in testcases:
        content += f"""
ID: {tc['id']}
STEPS:{tc.get('steps', '')}
EXPECTED:{tc.get('expected', '')}
"""

    return f"""
Please generate automation test scripts for the following test cases.

URL: {url}

TEST CASES:
{content}

Generate test scripts based on the test steps and expected results.
Do not include explanations.
"""