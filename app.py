import streamlit as st
import re
from utils.data_loader import load_excel
from utils.generator import build_prompt_all, save_test
from utils.ai_client import generate_code

st.set_page_config(page_title="AI Test Generator", layout="wide")

st.title("🤖 AI Sinh Kịch Bản Kiểm Thử Tự Động")

# ======================
# INPUT
# ======================
framework = st.selectbox(
  "⚙️ Chọn framework",
    ["selenium", "playwright"]
)
uploaded_file = st.file_uploader("📂 Upload file Excel test case", type=["xlsx"])
url = st.text_input("🌐 Nhập URL cần test")
# ======================
# ACTION
# ======================
if uploaded_file and url:
    if st.button("🚀 Sinh Test Script"):
        testcases = load_excel(uploaded_file)

        if not testcases:
            st.error("❌ Không đọc được test case từ file Excel")
            st.stop()

        st.success(f"✅ Đã load {len(testcases)} test case")

        # ======================
        # BUILD PROMPT
        # ======================
        prompt = build_prompt_all(testcases, url, framework)

        # Debug prompt
        with st.expander("📜 Xem Prompt"):
            st.code(prompt)

        # ======================
        # CALL AI
        # ======================
        with st.spinner("🤖 AI đang sinh code..."):
            code = generate_code(prompt)

        # ======================
        # VALIDATE OUTPUT
        # ======================
        if not code or "ERROR" in code:
            st.error("❌ Lỗi khi gọi API")
            st.code(code)
            st.stop()

        if code.count("###FILE:") != 2:
            st.error("❌ AI trả về sai format (không đủ 2 file)")
            st.code(code)
            st.stop()

        st.success("✅ AI sinh code thành công!")

        # ======================
        # PREVIEW + DOWNLOAD
        # ======================
        matches = re.findall(r"###FILE:(.+?)\n(.*?)(?=###FILE:|$)", code, re.S)

        st.subheader("📄 Code sinh ra")

        for name, content in matches:
            file_name = name.strip()
            file_content = content.strip()

            st.markdown(f"### 📁 {file_name}")
            st.code(file_content, language="python")

            st.download_button(
                label=f"⬇️ Tải {file_name}",
                data=file_content,
                file_name=file_name.split("/")[-1],
                mime="text/plain"
            )

        # ======================
        # SAVE FILE
        # ======================
        try:
            save_test(code)
            st.success("💾 Đã lưu file vào project")
        except Exception as e:
            st.error(f"❌ Lỗi khi lưu file: {e}")

else:
    st.info("👉 Upload file Excel + nhập URL để bắt đầu")