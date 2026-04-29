import pandas as pd

def extract_feature(tc_id):
    if "[" in tc_id and "-" in tc_id:
        return tc_id.split("[")[1].split("-")[0]
    return "Unknown"

def load_excel(file):
    # 🔥 FIX: đọc đúng dòng header
    df = pd.read_excel(file, header=7)

    df.columns = df.columns.str.strip()

    testcases = []

    for _, row in df.iterrows():
        tc_id = row.get("ID")

        if pd.isna(tc_id):
            continue

        tc_id = str(tc_id).strip()

        steps = str(row.get("Test Case Procedure")).strip()
        if not steps or steps.lower() == "nan":
            continue

        testcases.append({
            "id": tc_id,
            "feature": extract_feature(tc_id),
            "description": str(row.get("Test Case Description")).strip(),
            "steps": steps,
            "expected": str(row.get("Expected Output")).strip()
        })

    return testcases