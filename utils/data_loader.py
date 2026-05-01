import re

import pandas as pd


import string


def extract_feature(tc_id, title=""):
    tc_id_str = str(tc_id).lower()
    if "[" in tc_id_str and "-" in tc_id_str:
        return tc_id_str.split("[")[1].split("-")[0].strip()
        
    if title:
        clean_title = title.translate(str.maketrans('', '', string.punctuation)).strip()
        if clean_title:
            words = clean_title.lower().split()
            if words:
                return "_".join(words[:2])
                
    return tc_id_str.split("-")[0].strip() if "-" in tc_id_str else "test"


def normalize_column_name(name):
    if pd.isna(name):
        return ""
    return str(name).strip().lower()


def find_column(columns, candidates):
    for col in columns:
        name = normalize_column_name(col)
        if any(candidate in name for candidate in candidates):
            return col
    return None


def parse_key_value_data(value):
    if pd.isna(value):
        return {}

    raw = str(value).strip()
    if not raw:
        return {}

    data = {}
    for item in re.split(r"[\r\n;]+", raw):
        if ":" in item:
            key, val = item.split(":", 1)
            key = key.strip()
            val = val.strip()
            if key:
                data[key] = val
    return data


def normalize_ref(value):
    if pd.isna(value):
        return ""
    return re.sub(r"[^A-Za-z0-9]", "", str(value)).lower()


def numeric_suffix(value):
    if pd.isna(value):
        return ""
    match = re.search(r"(\d+)$", str(value).strip())
    return match.group(1) if match else ""


def read_excel_sheets(file):
    try:
        file.seek(0)
    except Exception:
        pass
        
    sheets = pd.read_excel(file, sheet_name=None, header=None, engine="openpyxl")
    result = {}
    
    for sheet_name, df in sheets.items():
        if df.empty:
            continue
            
        header_row_idx = 0
        max_score = -1
        keywords = {"id", "tc id", "td id", "steps", "procedure", "test case procedure", "expected", "expected result", "expected output", "title", "description", "data", "test data"}
        
        for i in range(min(15, len(df))):
            row_values = [str(x).lower().strip() for x in df.iloc[i].values if pd.notna(x)]
            score = sum(1 for v in row_values if any(k in v for k in keywords))
            if score > max_score:
                max_score = score
                header_row_idx = i
                
        if max_score > 0:
            df.columns = df.iloc[header_row_idx]
            df = df[header_row_idx + 1:].reset_index(drop=True)
        else:
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)
            
        result[sheet_name] = df
        
    return result


def parse_testdata_sheet(df):
    df.columns = [str(c).strip() for c in df.columns]
    id_col = find_column(df.columns, ["td id", "test data", "data id", "id"])
    data_col = find_column(df.columns, ["data", "test data", "value", "input", "data (key: value)"])
    desc_col = find_column(df.columns, ["description", "desc", "title"])

    if id_col is None:
        return {}

    data_by_key = {}
    for _, row in df.iterrows():
        raw_id = row.get(id_col)
        if pd.isna(raw_id):
            continue

        key = normalize_ref(raw_id)
        if not key:
            continue

        data = {}
        if data_col is not None and not pd.isna(row.get(data_col)):
            data = parse_key_value_data(row.get(data_col))

        extra_cols = [c for c in df.columns if c not in {id_col, data_col, desc_col}]
        for col in extra_cols:
            if col and col not in {id_col, desc_col}:
                val = row.get(col)
                if not pd.isna(val) and str(val).strip():
                    data[col.strip()] = str(val).strip()

        if not data:
            continue

        data_by_key.setdefault(key, []).append(data)

    return data_by_key


def parse_testcase_sheet(df, data_by_key):
    df.columns = [str(c).strip() for c in df.columns]
    id_col = find_column(df.columns, ["id", "tc id"])
    steps_col = find_column(df.columns, ["test case procedure", "steps", "procedure"])
    expected_col = find_column(df.columns, ["expected output", "expected", "expected result"])
    description_col = find_column(df.columns, ["test case description", "description", "desc", "title", "precondition"])
    data_ref_col = find_column(df.columns, ["test data", "data id", "td id", "data reference", "testdata", "test data ref"])

    if id_col is None or steps_col is None:
        return []

    testcases = []
    for _, row in df.iterrows():
        tc_id = row.get(id_col)
        if pd.isna(tc_id):
            continue

        tc_id = str(tc_id).strip()
        steps = str(row.get(steps_col)).strip()
        if not steps or steps.lower() == "nan":
            continue

        data_ref = None
        if data_ref_col is not None and not pd.isna(row.get(data_ref_col)):
            data_ref = str(row.get(data_ref_col)).strip()

        normalized_ref = normalize_ref(data_ref) if data_ref else normalize_ref(tc_id)
        found_data = data_by_key.get(normalized_ref)
        if not found_data:
            num = numeric_suffix(normalized_ref)
            if num:
                for key, value in data_by_key.items():
                    if numeric_suffix(key) == num:
                        found_data = value
                        break

        test_data = found_data or []
        testcases.append({
            "id": tc_id,
            "feature": extract_feature(tc_id, str(row.get(description_col)).strip() if description_col is not None else ""),
            "description": str(row.get(description_col)).strip() if description_col is not None else "",
            "steps": steps,
            "expected": str(row.get(expected_col)).strip() if expected_col is not None else "",
            "test_data": test_data,
        })

    return testcases


def load_excel(file):
    sheets = read_excel_sheets(file)
    if not sheets:
        return []

    if len(sheets) == 1:
        df = next(iter(sheets.values()))
        return parse_testcase_sheet(df, {})

    testcase_df = None
    testdata_df = None
    for _, df in sheets.items():
        cols = [normalize_column_name(c) for c in df.columns]
        is_tc = any("step" in c or "procedure" in c for c in cols)
        is_td = any("td id" in c or "data (key: value)" in c for c in cols)
        
        if is_tc:
            testcase_df = df
        elif is_td:
            testdata_df = df
        elif any("test data" in c for c in cols) and not is_tc:
            testdata_df = df

    if testcase_df is None:
        testcase_df = next(iter(sheets.values()))

    data_by_key = parse_testdata_sheet(testdata_df) if testdata_df is not None else {}
    return parse_testcase_sheet(testcase_df, data_by_key)
