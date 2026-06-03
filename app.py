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
import utils.ui_templates as ui
import importlib
importlib.reload(ui)


st.set_page_config(page_title="AI Test Generator", layout="wide")

ui.render_css()

# ==========================================================
# KHỞI TẠO CÁC BIẾN TRẠNG THÁI HỆ THỐNG (SESSION STATE)
# ==========================================================
# st.session_state giúp lưu giữ dữ liệu xuyên suốt các lượt tải lại trang (rerun) của Streamlit.
if "has_generated" not in st.session_state:
    st.session_state.has_generated = False  # Trạng thái xác nhận đã sinh mã xong hay chưa

if "generation_results" not in st.session_state:
    st.session_state.generation_results = {}  # Lưu trữ kết quả sinh mã bao gồm mã nguồn và các số liệu đo lường

if "last_uploaded_file_name" not in st.session_state:
    st.session_state.last_uploaded_file_name = None  # Lưu tên file Excel cuối cùng được tải lên để nhận diện đổi file


# ==============
# SIDEBAR
# ==============
with st.sidebar:

    ui.render_sidebar_header()
    st.markdown("---")

    prompt_strategy = st.selectbox(
        "🧠 Chọn chiến lược Prompt",
        ["P5 (Full Automation Prompt)", "P4 (Locator-aware Prompt)", "P3 (Structured Test Case Prompt)", "P2 (Framework - Specific Prompt)", "P1 (Basic Prompt)"]
    )

    framework = st.selectbox(
        "⚙️ Chọn framework",
        ["selenium", "playwright"]
    )

    # Reserved for future language support
    language = st.selectbox(
        "💻 Ngôn ngữ",
        ["Python"]
    )

    uploaded_file = st.file_uploader("📂 Tải lên file Excel test case", type=["xlsx"])
    
    st.markdown("---")
    ui.render_sidebar_footer()

# Khởi tạo các biến cục bộ
testcases_by_function = {}
urls = {}

# =========================================
# XỬ LÝ KHI FILE EXCEL ĐƯỢC TẢI LÊN
# =========================================
if uploaded_file:
    # Nếu phát hiện người dùng tải lên một file Excel mới hoàn toàn so với file trước đó
    if st.session_state.last_uploaded_file_name != uploaded_file.name:
        st.session_state.last_uploaded_file_name = uploaded_file.name
        st.session_state.has_generated = False
        st.session_state.generation_results = {}

    testcases_by_function = load_excel(uploaded_file)

    testcases_by_function = {
        k: v for k, v in testcases_by_function.items() 
        if v and len(v.get("prompt_testcases", [])) > 0
    }

    if not testcases_by_function:
        st.sidebar.error("❌ Không đọc được test case hợp lệ từ file Excel (Thiếu cột ID, Step hoặc không có dữ liệu)")
        st.stop()


# ================================
# KHU VỰC HIỂN THỊ CHÍNH
# ================================

# TRƯỜNG HỢP 1: Chưa có file Excel nào được tải lên hệ thống
if not uploaded_file:

    ui.render_header(
        title="🤖 AI Sinh Kịch Bản Kiểm Thử Tự Động",
        subtitle="Sinh code kiểm thử tự động cực nhanh và chuẩn xác từ file Excel test case của bạn!"
    )
    
    # Hộp thông tin hướng dẫn người dùng bắt đầu
    st.info("👉 Hãy bắt đầu bằng cách tải lên file Excel test case của bạn ở thanh cấu hình bên trái! 🐾")

# TRƯỜNG HỢP 2: File Excel đã được tải lên thành công nhưng chưa thực hiện sinh code
elif uploaded_file and not st.session_state.has_generated:
    ui.render_header(
        title="🤖 AI Sinh Kịch Bản Kiểm Thử Tự Động",
        subtitle="Đã tải cấu trúc test case thành công. Hãy thiết lập URL để bắt đầu sinh script!"
    )
    
    st.success(f"✅ Đã tải thành công {len(testcases_by_function)} chức năng từ file Excel '{uploaded_file.name}'!")
    
    # Hiển thị thẻ chỉ dẫn thiết lập URL
    ui.render_url_card()
    
    # Tạo các ô nhập liệu URL kiểm thử động cho từng chức năng phát hiện được từ Excel
    for func_name in testcases_by_function.keys():
        urls[func_name] = st.text_input(f"🌐 URL kiểm thử cho '{func_name}'", key=f"url_{func_name}")
        
    st.markdown("<br><div class='generate-btn-wrapper'></div>", unsafe_allow_html=True)
    
    # NÚT BẮT ĐẦU CHẠY SINH CODE
    if st.button("🚀 Bắt đầu Sinh Test Script ✨", use_container_width=True):
        # Áp dụng chiến lược sinh Prompt dựa trên lựa chọn của người dùng ở Sidebar
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
        
        # Hàm phụ trợ tìm kiếm test case đăng nhập thành công để gom toàn bộ bộ locator của nó
        # Hỗ trợ đắc lực cho chiến lược P5 (Tự động hóa luồng phụ thuộc)
        def find_login_testcase(all_data):
            for f_name, tcs in all_data.items():
                if "đăng nhập" in f_name.lower() or "login" in f_name.lower():
                    # Trích xuất và gom tất cả locator của chức năng đăng nhập
                    locs = {
                        line.strip() for tc in tcs["prompt_testcases"] if tc.get("locator")
                        for line in str(tc["locator"]).split('\n')
                        if line.strip()
                    }
                    # Tìm testcase đăng nhập thành công để đắp đầy đủ locator vào phục vụ tiền điều kiện
                    for tc in tcs["prompt_testcases"]:
                        exp = str(tc.get("expected", "")).lower()
                        if any(x in exp for x in ("thành công", "success")):
                            return {**tc, "locator": "\n".join(locs)}
            return None

        func_results = {}

        # VÒNG LẶP DUYỆT QUA TỪNG CHỨC NĂNG ĐỂ GỌI AI SINH CODE
        for func_name, testcases in testcases_by_function.items():
            url = urls.get(func_name, "").strip()
            # Bỏ qua chức năng nếu người dùng không điền URL kiểm thử
            if not url:
                st.warning(f"⚠️ Bỏ qua chức năng '{func_name}' vì không có URL.")
                continue

            prompt_cases = testcases["prompt_testcases"].copy()
            
            # Kiểm tra xem chức năng hiện tại có yêu cầu tiền điều kiện đăng nhập không
            requires_login = any(
                "đăng nhập" in str(tc.get("precondition", "")).lower() or 
                "login" in str(tc.get("precondition", "")).lower()
                for tc in prompt_cases
            )

            func_results[func_name] = {}

            # Sinh Prompt và gọi mô hình AI sinh mã cho từng chiến lược
            for idx, (s_name, build_prompt_func, save_test_func) in enumerate(strategies):
                current_prompt_cases = prompt_cases.copy()
                
                # Nếu chạy chiến lược P5 và chức năng cần đăng nhập trước, tự động tìm và chèn kịch bản đăng nhập vào đầu prompt
                if s_name == "P5" and requires_login:
                    login_tc = find_login_testcase(testcases_by_function)
                    if login_tc and login_tc not in current_prompt_cases:
                        current_prompt_cases.insert(0, login_tc)

                # Dựng cấu trúc Prompt dựa vào chiến lược lựa chọn
                if s_name == "P1":
                    prompt = build_prompt_func(current_prompt_cases, url)
                else:
                    prompt = build_prompt_func(current_prompt_cases, url, framework, func_name)

                expected_files = 0 if save_test_func is None else 3

                # Khởi tạo các vùng trống (Streamlit Placeholders) để hiển thị hoạt cảnh và tiến trình
                progress_placeholder = st.empty()
                info_placeholder = st.empty()

                start_time = time.perf_counter()
                api_result = {}

                # Hàm cục bộ hỗ trợ cập nhật tiến trình chạy chú mèo
                def render_cat_progress(percent, elapsed_time):
                    ui.render_cat_progress(progress_placeholder, func_name, s_name, percent, elapsed_time)

                # Sử dụng đa luồng (Multithreading) để gọi API của mô hình AI, giúp giữ trang Streamlit không bị đơ
                def call_ai():
                    api_result["result"] = generate_code(
                        prompt,
                        expected_files=expected_files
                    )

                thread = threading.Thread(target=call_ai)
                thread.start()
                progress = 0

                # Chạy hoạt cảnh chú mèo di chuyển tiến độ giả lập khi luồng gọi AI đang chạy
                while thread.is_alive():
                    elapsed_loading = time.perf_counter() - start_time
                    progress = min(95, int(elapsed_loading * 4)) # Tăng dần và dừng lại tối đa ở 95% cho đến khi xong hẳn
                    render_cat_progress(progress, elapsed_loading)
                    time.sleep(0.05)

                thread.join()  # Chờ luồng gọi API hoàn thành hoàn toàn

                elapsed = time.perf_counter() - start_time
                render_cat_progress(100, elapsed)  # Đẩy tiến trình lên 100% khi nhận được kết quả

                # Trích xuất dữ liệu từ kết quả trả về của API AI
                result = api_result.get("result", {})
                usage = result.get("usage")
                code = result.get("content", "")

                # Thống kê lượng token đã tiêu hao
                if usage:
                    prompt_tokens = usage.prompt_tokens
                    completion_tokens = usage.completion_tokens
                    total_tokens = usage.total_tokens
                else:
                    prompt_tokens = completion_tokens = total_tokens = 0

                grand_total_tokens += total_tokens
                grand_total_time += elapsed

                progress_placeholder.empty()

                # Sử dụng biểu thức chính quy (Regex) để bóc tách các tệp tin trong code trả về của AI dựa trên thẻ ###FILE:
                matches = re.findall(r"###FILE:(.+?)\n(.*?)(?=###FILE:|$)", code, re.S)
                parsed_files = []

                if save_test_func is None:
                    # Nếu là P1, lưu trực tiếp mã nguồn thô vào tệp .txt
                    parsed_files.append((f"P1_{func_name}.txt", code))
                else:
                    # Nếu là P2-P5, phân tích tách tệp và nạp vào từ điển project_files để đóng gói ZIP
                    for name, content in matches:
                        file_name = name.strip()
                        file_content = content.strip()
                        if len(strategies) == 1:
                            zip_path = file_name
                        else:
                            zip_path = f"{s_name.lower()}/{file_name}"
                        project_files[zip_path] = file_content
                        parsed_files.append((file_name, file_content))

                # Thực hiện ghi đè hoặc ghi lưu các file code sinh ra vào thư mục vật lý của project
                save_msg = ""
                if len(strategies) == 1 and save_test_func is not None:
                    try:
                        save_test_func(code)
                        save_msg = f"💾 Đã lưu file chức năng '{func_name}' vào project"
                    except Exception as e:
                        save_msg = f"❌ Lỗi khi lưu file cho '{func_name}': {e}"
                elif save_test_func is None:
                    save_msg = "💡 P1 là Basic Prompt nên không tự động lưu file vào project."
                else:
                    save_msg = "💡 Đang ở chế độ so sánh, bỏ qua việc tự động lưu đè file."

                # Lưu trữ kết quả xử lý của chức năng hiện tại
                func_results[func_name] = {
                    "elapsed": elapsed,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                    "code": code,
                    "parsed_files": parsed_files,
                    "save_msg": save_msg,
                    "prompt": prompt
                }

        # ĐÓNG GÓI TOÀN BỘ PROJECT THÀNH FILE ZIP
        zip_data = None
        zip_name = ""
        if project_files:
            # Tạo sẵn các file bổ trợ cần thiết để chạy kiểm thử bao gồm requirements.txt và pytest.ini
            reqs = """pytest
allure-pytest
openpyxl
pandas
streamlit
"""
            if framework == "selenium":
                reqs += "selenium\nwebdriver-manager\n"
                readme_content = """# Automated Test Project

## Framework
Selenium WebDriver

## Environment
- Python 3.10+
- PyCharm

## Setup
### Create virtual environment
```bash
python -m venv .venv
```

### Activate Windows
```bash
.venv\\Scripts\\activate
```

### Install packages
```bash
pip install -r requirements.txt
```

### Run tests
```bash
pytest
```

### Generate Allure Report
```bash
allure serve allure-results
```
"""
            else:
                reqs += "playwright\npytest-playwright\n"
                readme_content = """# Automated Test Project

## Framework
Playwright

## Environment
- Python 3.10+
- PyCharm

## Setup
### Create virtual environment
```bash
python -m venv .venv
```

### Activate Windows
```bash
.venv\\Scripts\\activate
```

### Install packages
```bash
pip install -r requirements.txt
```

### Install Browser
```bash
playwright install
```

### Run tests
```bash
pytest
```

### Generate Allure Report
```bash
allure serve allure-results
```
"""
                
            pytest_ini = """[pytest]
pythonpath = .
addopts = --alluredir=allure-results
"""
            for s in strategies:
                if len(strategies) == 1:
                    project_files["requirements.txt"] = reqs
                    project_files["pytest.ini"] = pytest_ini
                    project_files["README.md"] = readme_content
                else:
                    project_files[f"{s[0].lower()}/requirements.txt"] = reqs
                    project_files[f"{s[0].lower()}/pytest.ini"] = pytest_ini
                    project_files[f"{s[0].lower()}/README.md"] = readme_content

            # Tạo file ZIP trong bộ nhớ đệm BytesIO
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for file_path, file_data in project_files.items():
                    zip_file.writestr(file_path, file_data)
            
            zip_data = zip_buffer.getvalue()
            strategies_str = "_".join([s[0].lower() for s in strategies])
            zip_name = f"{re.sub(r'[^a-zA-Z0-9_-]+', '_', uploaded_file.name.rsplit('.', 1)[0])}_{framework}_Prompt_{strategies_str}.zip"

        # Nạp toàn bộ kết quả tổng hợp vào session_state của Streamlit
        st.session_state.generation_results = {
            "grand_total_time": grand_total_time,
            "grand_total_tokens": grand_total_tokens,
            "zip_data": zip_data,
            "zip_name": zip_name,
            "func_results": func_results,
            "prompt_strategy": s_name
        }
        st.session_state.has_generated = True
        st.rerun()  # Kích hoạt tải lại trang để chuyển sang Case 3 hiển thị workspace kết quả


# TRƯỜNG HỢP 3: Quá trình sinh kịch bản kiểm thử đã hoàn tất! Hiển thị Giao diện Workspace Song Song
elif uploaded_file and st.session_state.has_generated:
    results = st.session_state.generation_results
    func_results = results.get("func_results", {})
    
    # Hiển thị banner tiêu đề thông báo hoàn thành
    ui.render_header(
        title="✨ Kết Quả Sinh Test Script Tự Động ✨",
        subtitle="Hệ thống AI đã hoàn thành việc sinh kịch bản kiểm thử cho dự án của bạn!"
    )
    
    # HIỂN THỊ CÁC Ô SỐ LIỆU ĐO LƯỜNG TỔNG QUAN
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        ui.render_stat_box("⏱️ TỔNG THỜI GIAN CHẠY", f"{results.get('grand_total_time', 0.0):.2f}s")
    with m_col2:
        ui.render_stat_box("🔮 TỔNG SỐ TOKEN SỬ DỤNG", f"{results.get('grand_total_tokens', 0):,}")
    with m_col3:
        st.markdown('<div class="refresh-button-trigger"></div>', unsafe_allow_html=True)
        # Nút hỗ trợ người dùng quay lại giao diện thiết lập ban đầu để sinh lại hoặc chọn cấu hình khác
        if st.button("🔄 Sinh Lại Script Mới 🐾", use_container_width=True):
            st.session_state.has_generated = False
            st.session_state.generation_results = {}
            st.rerun()

    st.markdown("---")

    # LỰA CHỌN CHỨC NĂNG ĐỂ XEM CHI TIẾT
    func_names = list(func_results.keys())
    if func_names:

        prompt_expander_container = st.container()

        selected_func = st.selectbox(
            "📂 Chọn chức năng để hiển thị kết quả:",
            func_names,
            key="active_view_func"
        )
        
        active_tc_data = testcases_by_function[selected_func]
        active_result = func_results.get(selected_func, {})

        if active_result:
            with prompt_expander_container:
                with st.expander("📜 Xem Prompt Gửi Cho AI"):
                    st.code(active_result.get("prompt", ""))
        
        if active_tc_data and active_result:

            col_left, col_right = st.columns([1, 1])
            
            # =========================
            # DỮ LIỆU ĐẦU VÀO
            # =========================
            with col_left:
                st.markdown("<h4 style='color:#1e3c72; text-align:center;'>📝 TEST CASE INPUT</h4>", unsafe_allow_html=True)

                tc_list = active_tc_data.get("prompt_testcases", [])
                tc_ids = [tc.get("id", f"TC_{i+1}") for i, tc in enumerate(tc_list)]
                
                selected_tc_id = st.selectbox(
                    "🔍 Chọn Test Case để xem chi tiết:",
                    tc_ids,
                    key=f"select_tc_{selected_func}"
                )
                
                selected_tc = next((tc for tc in tc_list if tc.get("id") == selected_tc_id), tc_list[0])
                # Hiển thị thẻ Sổ ghi chép chi tiết của Test Case
                ui.render_notebook_card(selected_tc)

            # =======================
            # CỘT BÊN PHẢI
            # =======================
            with col_right:
                used_prompt_strategy = active_result.get("prompt_strategy", "")

                st.markdown(
                    f"<h4 style='color:#1e3c72; text-align:center; margin-bottom:26px;'>GENERATED SCRIPT ({used_prompt_strategy})</h4>",
                    unsafe_allow_html=True
                )
                parsed_files = active_result.get("parsed_files", [])
                
                if parsed_files:
                    file_names = [f[0].split('/')[-1] for f in parsed_files]

                    ui.render_mac_header("Script Workspace")

                    tabs = st.tabs([f"📁 {name}" for name in file_names])
                    
                    for idx, tab in enumerate(tabs):
                        with tab:
                            file_name, file_content = parsed_files[idx]
                            # Render code block bằng iframe HTML mượt mà tránh lỗi mất thanh cuộn
                            ui.render_code_block(file_content, height=330)

                            short_name = file_name.split('/')[-1]
                            st.download_button(
                                label=f"⬇️ Tải {short_name}",
                                data=file_content,
                                file_name=short_name,
                                mime="text/plain",
                                key=f"dl_{selected_func}_{short_name}_{idx}",
                                use_container_width=True
                            )

                    st.markdown("<div style='height: 68px;'></div>", unsafe_allow_html=True)

                    save_msg = active_result.get("save_msg", "")
                    if save_msg:
                        if "❌" in save_msg:
                            st.error(save_msg)
                        elif "💾" in save_msg or "✅" in save_msg:
                            st.success(save_msg)
                        else:
                            st.info(save_msg)

    st.markdown("---")

    # =================================================
    # KHU VỰC TẢI XUỐNG TOÀN BỘ PROJECT (.ZIP)
    # =================================================
    if results.get("zip_data"):
        st.markdown("<h3 style='text-align: center; color: #1e3c72;'>📦 Tải Toàn Bộ Project</h3>", unsafe_allow_html=True)
        # Hiển thị hướng dẫn giải nén
        ui.render_zip_instructions()
        
        st.markdown("<div class='project-dl-wrapper'></div>", unsafe_allow_html=True)

        st.download_button(
            label="⬇️ Tải File ZIP Toàn Bộ Project (.zip) 🐾",
            data=results.get("zip_data"),
            file_name=results.get("zip_name"),
            mime="application/zip",
            use_container_width=True
        )