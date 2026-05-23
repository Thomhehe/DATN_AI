# pyrefly: ignore [missing-import]
import threading
import time

import streamlit as st
import re
import io
import zipfile
from utils.data_loader import load_excel
import utils.generator_p4 as gen_p4
import utils.generator_p5 as gen_p5
import utils.generator_p1 as gen_p1
import utils.generator_p2 as gen_p2
import utils.generator_p3 as gen_p3
from utils.ai_client import generate_code

st.set_page_config(page_title="AI Test Generator", layout="wide")

st.title("🤖 AI Sinh Kịch Bản Kiểm Thử Tự Động")

col1, col2 = st.columns(2)
with col1:
    framework = st.selectbox(
      "⚙️ Chọn framework",
        ["selenium", "playwright"]
    )
with col2:
    prompt_strategy = st.selectbox(
        "🧠 Chọn chiến lược Prompt",
        ["P1 (Basic Prompt)", "P2 (Framework - Specific Prompt)", "P3 (Structured Test Case Prompt)", "P4 (Locator-aware Prompt)", "P5 (Full Automation Prompt)"]
    )
uploaded_file = st.file_uploader("📂 Upload file Excel test case", type=["xlsx"])

testcases_by_function = {}
urls = {}

if uploaded_file:
    testcases_by_function = load_excel(uploaded_file)
    
    # Lọc bỏ các chức năng không có test case (do thiếu cột ID/Step hoặc sheet rỗng)
    testcases_by_function = {
        k: v for k, v in testcases_by_function.items() 
        if v and len(v.get("prompt_testcases", [])) > 0
    }

    if not testcases_by_function:
        st.error("❌ Không đọc được test case hợp lệ từ file Excel (Thiếu cột ID, Step hoặc không có dữ liệu)")
        st.stop()
        
    st.success(f"✅ Đã load {len(testcases_by_function)} chức năng từ file Excel")

    st.write("### Nhập URL cho từng chức năng:")
    for func_name in testcases_by_function.keys():
        urls[func_name] = st.text_input(f"🌐 URL cho '{func_name}'", key=f"url_{func_name}")

if uploaded_file and testcases_by_function:
    if st.button("🚀 Sinh Test Script"):
        
        if prompt_strategy.startswith("P1"):
            strategies = [("P1", gen_p1.build_prompt_all, None)]
        elif prompt_strategy.startswith("P2"):
            strategies = [("P2", gen_p2.build_prompt_all, gen_p2.save_test)]
        elif prompt_strategy.startswith("P3"):
            strategies = [("P3", gen_p3.build_prompt_all, gen_p3.save_test)]
        elif prompt_strategy.startswith("P4"):
            strategies = [("P4", gen_p4.build_prompt_all, gen_p4.save_test)]
        elif prompt_strategy.startswith("P5"):
            strategies = [("P5", gen_p5.build_prompt_all, gen_p5.save_test)]

        project_files = {}

        grand_total_tokens = 0
        grand_total_time = 0
        
        # Hàm phụ để tìm test case đăng nhập thành công và gom toàn bộ locator
        def find_login_testcase(all_data):
            for f_name, tcs in all_data.items():
                if "đăng nhập" in f_name.lower() or "login" in f_name.lower():
                    # Gom tất cả locator của chức năng đăng nhập
                    locs = {
                        line.strip() for tc in tcs["prompt_testcases"] if tc.get("locator")
                        for line in str(tc["locator"]).split('\n')
                        if line.strip()
                    }
                    # Trả về testcase thành công đã được đắp đầy đủ locator
                    for tc in tcs["prompt_testcases"]:
                        exp = str(tc.get("expected", "")).lower()
                        if any(x in exp for x in ("thành công", "success")):
                            return {**tc, "locator": "\n".join(locs)}
            return None

        # Duyệt qua từng chức năng để sinh code
        for func_name, testcases in testcases_by_function.items():
            url = urls.get(func_name, "").strip()
            if not url:
                st.warning(f"⚠️ Bỏ qua chức năng '{func_name}' vì không có URL.")
                continue

            st.write("---")
            st.subheader(f"⚙️ Đang xử lý: {func_name}")

            prompt_cases = testcases["prompt_testcases"].copy()
            
            # Ký thuật chèn Test Case Đăng Nhập nếu Precondition yêu cầu
            requires_login = any(
                "đăng nhập" in str(tc.get("precondition", "")).lower() or 
                "login" in str(tc.get("precondition", "")).lower()
                for tc in prompt_cases
            )

            if len(strategies) > 1:
                tabs = st.tabs([s[0] for s in strategies])
            else:
                tabs = [st.container()]

            for idx, (s_name, build_prompt_func, save_test_func) in enumerate(strategies):
                with tabs[idx]:
                    current_prompt_cases = prompt_cases.copy()
                    
                    if s_name == "P5" and requires_login:
                        login_tc = find_login_testcase(testcases_by_function)
                        if login_tc and login_tc not in current_prompt_cases:
                            # Chèn test case đăng nhập lên đầu để AI có data map sang
                            current_prompt_cases.insert(0, login_tc)

                    if len(strategies) > 1:
                        st.markdown(f"## Kết quả từ {s_name}")

                    if s_name == "P1":
                        prompt = build_prompt_func(current_prompt_cases, url)
                    else:
                        prompt = build_prompt_func(current_prompt_cases, url, framework, func_name)
                    # Debug prompt
                    with st.expander(f"📜 Xem Prompt ({func_name}) - {s_name}"):
                        st.code(prompt)

                    expected_files = 0 if save_test_func is None else 3

                    progress_placeholder = st.empty()
                    info_placeholder = st.empty()

                    start_time = time.perf_counter()
                    api_result = {}


                    def render_cat_progress(percent, elapsed_time):
                        html = f"""
                        <style>
                        .cat-title {{
                            text-align: center;
                            font-size: 20px;
                            font-weight: 700;
                            margin-bottom: 18px;
                        }}

                        .cat-track {{
                            position: relative;
                            width: 100%;
                            height: 24px;
                            background: #eef1f5;
                            border-radius: 999px;
                            overflow: visible;
                        }}

                        .cat-fill {{
                            width: {percent}%;
                            height: 100%;
                            background: linear-gradient(90deg, #4facfe, #00f2fe);
                            border-radius: 999px;
                            transition: width 0.4s linear;
                        }}

                        .cat-runner {{
                            position: absolute;
                            top: -34px;
                            left: calc({percent}% - 18px);
                            font-size: 34px;
                            transition: left 0.4s linear;
                            transform: scaleX(-1);
                        }}

                        .cat-percent {{
                            text-align: center;
                            margin-top: 10px;
                            font-weight: 600;
                        }}
                        </style>

                        <div class="cat-title">🐾 Đang sinh code cho {func_name} ({s_name})</div>

                        <div class="cat-track">
                            <div class="cat-fill"></div>
                            <div class="cat-runner">🐈</div>
                        </div>

                        <div class="cat-percent">
                            {percent}% · ⏱️ {elapsed_time:.2f}s
                        </div>
                        """

                        progress_placeholder.markdown(html, unsafe_allow_html=True)


                    def call_ai():
                        api_result["result"] = generate_code(
                            prompt,
                            expected_files=expected_files
                        )


                    thread = threading.Thread(target=call_ai)
                    thread.start()
                    progress = 0

                    while thread.is_alive():
                        elapsed_loading = time.perf_counter() - start_time

                        progress = min(95, int(elapsed_loading * 4))

                        render_cat_progress(progress, elapsed_loading)
                        time.sleep(0.05)

                    thread.join()

                    elapsed = time.perf_counter() - start_time

                    render_cat_progress(100, elapsed)

                    result = api_result.get("result", {})
                    usage = result.get("usage")
                    code = result.get("content", "")


                    if usage:
                        prompt_tokens = usage.prompt_tokens
                        completion_tokens = usage.completion_tokens
                        total_tokens = usage.total_tokens

                    else:
                        prompt_tokens = completion_tokens = total_tokens = 0

                    grand_total_tokens += total_tokens
                    grand_total_time += elapsed

                    info_placeholder.success(
                        f"""
                    ⏱️ Time: {elapsed:.2f}s  
                    🔹 Prompt Tokens: {prompt_tokens}  
                    🔹 Completion Tokens: {completion_tokens}  
                    🔹 Total Tokens: {total_tokens}
                    """
                    )

                    if not code or "ERROR" in code:
                        st.error(f"❌ Lỗi khi gọi API cho '{func_name}' ({s_name})")
                        st.code(code)
                        continue

                    if save_test_func is not None and code.count("###FILE:") < expected_files:
                        st.error(
                            f"❌ AI trả về sai format cho '{func_name}' ({s_name}) "
                            f"(không đủ {expected_files} ###FILE)"
                        )
                        st.code(code)
                        continue

                    st.success(f"✅ AI sinh code thành công cho '{func_name}' ({s_name})!")

                    matches = re.findall(r"###FILE:(.+?)\n(.*?)(?=###FILE:|$)", code, re.S)

                    if save_test_func is None:
                        st.markdown("### 📄 Kết quả sinh từ P1")
                        st.code(code, language="python")

                        st.download_button(
                            label=f"⬇️ Tải kết quả P1 ({func_name})",
                            data=code,
                            file_name=f"P1_{func_name}.txt",
                            mime="text/plain",
                            key=f"dl_{func_name}_{s_name}_raw"
                        )
                    else:
                        for name, content in matches:
                            file_name = name.strip()
                            file_content = content.strip()

                            if len(strategies) == 1:
                                zip_path = file_name
                            else:
                                zip_path = f"{s_name.lower()}/{file_name}"

                            project_files[zip_path] = file_content

                            st.markdown(f"### 📁 {file_name}")
                            st.code(file_content, language="python")

                            st.download_button(
                                label=f"⬇️ Tải {file_name.split('/')[-1]} ({s_name})",
                                data=file_content,
                                file_name=f"{s_name}_{file_name.split('/')[-1]}",
                                mime="text/plain",
                                key=f"dl_{func_name}_{file_name}_{s_name}"
                            )

                    if len(strategies) == 1 and save_test_func is not None:
                        try:
                            save_test_func(code)
                            st.success(f"💾 Đã lưu file của '{func_name}' vào project")
                        except Exception as e:
                            st.error(f"❌ Lỗi khi lưu file cho '{func_name}': {e}")
                    elif save_test_func is None:
                        st.info("💡 P1 là Basic Prompt nên không tự động lưu file vào project.")
                    else:
                        st.info(f"💡 Đang ở chế độ so sánh, bỏ qua việc tự động lưu đè file vào project. Bạn có thể xem kết quả trực tiếp hoặc tải file ZIP.")

        if project_files:
            # Tạo requirements.txt
            reqs = """pytest
allure-pytest
openpyxl
pandas
streamlit
"""
            if framework == "selenium":
                reqs += """selenium
webdriver-manager
            """
            else:
                reqs += """playwright
pytest-playwright
            """
            pytest_ini = """[pytest]
pythonpath = .
addopts = --alluredir=allure-results
            """
            for s in strategies:
                if len(strategies) == 1:
                    project_files["requirements.txt"] = reqs
                    project_files["pytest.ini"] = pytest_ini
                else:
                    project_files[f"{s[0].lower()}/requirements.txt"] = reqs
                    project_files[f"{s[0].lower()}/pytest.ini"] = pytest_ini
            
            # Đóng gói thành file ZIP
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for file_path, file_data in project_files.items():
                    zip_file.writestr(file_path, file_data)

            strategies_str = "_".join([s[0].lower() for s in strategies])
            zip_name = f"{re.sub(r'[^a-zA-Z0-9_-]+', '_', uploaded_file.name.rsplit('.', 1)[0])}_{framework}_Prompt_{strategies_str}.zip"

            st.markdown("---")
            st.success(
                f"""
            📊 Tổng kết toàn bộ quá trình sinh code

            ⏱️ Tổng thời gian: {grand_total_time:.2f}s

            🔹 Tổng Tokens: {grand_total_tokens:,}
            """
            )

            st.markdown("---")
            st.subheader("📦 Tải Toàn Bộ Project")
            st.info("💡 Bạn có thể giải nén file ZIP này và mở trực tiếp bằng PyCharm để chạy test.")
            st.download_button(
                label="⬇️ Tải Project (ZIP)",
                data=zip_buffer.getvalue(),
                file_name=zip_name,
                mime="application/zip",
                use_container_width=True
            )

else:
    st.info("👉 Upload file Excel để bắt đầu")