# pyrefly: ignore [missing-import]
import streamlit as st
import re
import io
import zipfile
from utils.data_loader import load_excel
from utils.generator import build_prompt_all, save_test
from utils.ai_client import generate_code

st.set_page_config(page_title="AI Test Generator", layout="wide")

st.title("🤖 AI Sinh Kịch Bản Kiểm Thử Tự Động")

framework = st.selectbox(
  "⚙️ Chọn framework",
    ["selenium", "playwright"]
)
uploaded_file = st.file_uploader("📂 Upload file Excel test case", type=["xlsx"])

testcases_by_function = {}
urls = {}

if uploaded_file:
    testcases_by_function = load_excel(uploaded_file)
    if not testcases_by_function:
        st.error("❌ Không đọc được test case từ file Excel")
        st.stop()
        
    st.success(f"✅ Đã load {len(testcases_by_function)} chức năng từ file Excel")
    
    st.write("### Nhập URL cho từng chức năng:")
    for func_name in testcases_by_function.keys():
        urls[func_name] = st.text_input(f"🌐 URL cho '{func_name}'", key=f"url_{func_name}")

if uploaded_file and testcases_by_function:
    if st.button("🚀 Sinh Test Script"):
        
        project_files = {}

        # Duyệt qua từng chức năng để sinh code
        for func_name, testcases in testcases_by_function.items():
            url = urls.get(func_name, "").strip()
            if not url:
                st.warning(f"⚠️ Bỏ qua chức năng '{func_name}' vì không có URL.")
                continue

            st.write("---")
            st.subheader(f"⚙️ Đang xử lý: {func_name}")

            prompt = build_prompt_all(testcases["prompt_testcases"], url, framework, func_name)
            # Debug prompt
            with st.expander(f"📜 Xem Prompt ({func_name})"):
                st.code(prompt)

            with st.spinner(f"🤖 AI đang sinh code cho '{func_name}'..."):
                code = generate_code(prompt)

            if not code or "ERROR" in code:
                st.error(f"❌ Lỗi khi gọi API cho '{func_name}'")
                st.code(code)
                continue

            if code.count("###FILE:") < 4:
                st.error(f"❌ AI trả về sai format cho '{func_name}' (không đủ file)")
                st.code(code)
                continue

            st.success(f"✅ AI sinh code thành công cho '{func_name}'!")

            matches = re.findall(r"###FILE:(.+?)\n(.*?)(?=###FILE:|$)", code, re.S)

            for name, content in matches:
                file_name = name.strip()
                file_content = content.strip()

                project_files[file_name] = file_content

                st.markdown(f"### 📁 {file_name}")
                st.code(file_content, language="python")

                st.download_button(
                    label=f"⬇️ Tải {file_name.split('/')[-1]}",
                    data=file_content,
                    file_name=file_name.split("/")[-1],
                    mime="text/plain",
                    key=f"dl_{func_name}_{file_name}"
                )

            try:
                save_test(code)
                st.success(f"💾 Đã lưu file của '{func_name}' vào project")
            except Exception as e:
                st.error(f"❌ Lỗi khi lưu file cho '{func_name}': {e}")

        if project_files:
            # Tạo requirements.txt
            reqs = "pytest\nallure-pytest\n"
            if framework == "selenium":
                reqs += "selenium\nwebdriver-manager\n"
            else:
                reqs += "playwright\npytest-playwright\n"
            project_files["requirements.txt"] = reqs
            
            # Đóng gói thành file ZIP
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for file_path, file_data in project_files.items():
                    zip_file.writestr(file_path, file_data)
            
            st.markdown("---")
            st.subheader("📦 Tải Toàn Bộ Project")
            st.info("💡 Bạn có thể giải nén file ZIP này và mở trực tiếp bằng PyCharm để chạy test.")
            st.download_button(
                label="⬇️ Tải Project (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="Automation_Project.zip",
                mime="application/zip",
                use_container_width=True
            )

else:
    st.info("👉 Upload file Excel để bắt đầu")