import re
import pandas as pd

# =========================
# 1. UTIL SIMPLE
# =========================

def normalize(name):
    if pd.isna(name):
        return ""
    return str(name).strip().lower()

# Đọc test data
def parse_key_value(value):
    if pd.isna(value):
        return {}

    data = {}
    for item in str(value).splitlines():
        if ":" in item:
            k, v = item.split(":", 1)
            data[k.strip()] = v.strip()
    return data


# Đọc sheet
def read_excel(file):
    file.seek(0)
    return pd.read_excel(file, sheet_name=None, engine="openpyxl")

# Đọc sheet test data
def parse_testdata(df):
    df.columns = [str(c).strip() for c in df.columns]

    id_col = next((c for c in df.columns if "td id" in normalize(c)), None)
    data_col = next((c for c in df.columns if "data" in normalize(c)), None)

    if not id_col:
        return {}

    result = {}

    for _, row in df.iterrows():
        td_id = row.get(id_col)
        if pd.isna(td_id):
            continue

        td_id = str(td_id).strip()

        data = {}
        if data_col:
            data = parse_key_value(row.get(data_col))

        result[td_id] = data

    return result


def parse_testcase(df, td_map):
    df.columns = [str(c).strip() for c in df.columns]

    id_col = next((c for c in df.columns if "id" in normalize(c)), None)
    step_col = next((c for c in df.columns if "step" in normalize(c)), None)
    expected_col = next((c for c in df.columns if "expected" in normalize(c)), None)
    td_col = next((c for c in df.columns if "td id" in normalize(c) or "test data" in normalize(c)), None)
    locator_col = next((c for c in df.columns if "locator" in normalize(c)), None)

    if not id_col or not step_col:
        return {
            "prompt_testcases": [],
            "json_testcases": []
        }

    prompt_cases = []
    json_cases = []

    for _, row in df.iterrows():

        tc_id = row.get(id_col)

        if pd.isna(tc_id):
            continue

        tc_id = str(tc_id).strip()

        td_ref = (
            str(row.get(td_col)).strip()
            if td_col and not pd.isna(row.get(td_col))
            else None
        )

        data = td_map.get(td_ref, {}) if td_ref else {}

        expected = (
            str(row.get(expected_col)).strip()
            if expected_col and not pd.isna(row.get(expected_col))
            else ""
        )

        expected_for_json = expected
        if re.search(r'(["\']).*?\1\s+or\s+(["\']).*?\2', expected, re.IGNORECASE):
            matches = re.findall(r'(["\'])(.*?)\1', expected)
            if matches:
                expected_for_json = [m[1] for m in matches]

        # Dữ liệu dùng cho AI sinh code
        prompt_cases.append({
            "id": tc_id,
            "steps": str(row.get(step_col)).strip(),
            "locator": (
                str(row.get(locator_col)).strip()
                if locator_col and not pd.isna(row.get(locator_col))
                else ""
            ),
            "data": data,
            "expected": expected
        })

        # Dữ liệu dùng để sinh file json data-driven
        json_cases.append({
            "id": tc_id,
            **data,
            "expected": expected_for_json
        })

    return {
        "prompt_testcases": prompt_cases,
        "json_testcases": json_cases
    }
# =========================
# 5. MAIN LOADER
# =========================

def load_excel(file):
    sheets = read_excel(file)

    tc_sheets = {}
    td_sheets = {}

    for name, df in sheets.items():
        cols = [normalize(c) for c in df.columns]

        if any("step" in c for c in cols):
            tc_sheets[name] = df
        elif any("td id" in c or "data" in c for c in cols):
            td_sheets[name] = df

    result = {}

    for tc_name, tc_df in tc_sheets.items():

        # match TD sheet đơn giản theo tên
        td_df = None
        for name, df in td_sheets.items():
            if tc_name.lower() in name.lower():
                td_df = df
                break

        td_map = parse_testdata(td_df) if td_df is not None else {}
        testcases = parse_testcase(tc_df, td_map)

        result[tc_name] = testcases

    return result