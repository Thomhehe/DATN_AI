import streamlit as st

CSS_STYLE = """
/* Nhập font chữ tùy chỉnh từ Google Fonts (Quicksand cho văn bản thông dụng và JetBrains Mono cho khối mã nguồn) */
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* Áp dụng font Quicksand cho toàn bộ ứng dụng (ngoại trừ các icon đặc biệt của Streamlit) */
html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], .stMarkdown, p, label, button {
    font-family: 'Quicksand', sans-serif;
}

/* Định dạng tiêu đề (h1-h6)*/
h1, h2, h3, h4, h5, h6 {
    font-family: 'Quicksand', sans-serif;
    font-weight: 700 !important;
    color: #2c3e50 !important;
}

/* Khung tiêu đề trang chính với hiệu ứng chuyển màu Gradient xanh dương pastel */
.custom-header {
    background: linear-gradient(135deg, #345bc4 0%, #5d87ed 100%);
    color: white !important;
    padding: 14px 20px;
    border-radius: 16px;
    text-align: center;
    box-shadow: 0 6px 12px rgba(52, 91, 196, 0.2);
    margin-bottom: 24px;
}
.custom-header h1 {
    color: white !important;
    margin: 0;
    font-size: 1.8rem !important;
}
.custom-header p {
    margin: 4px 0 0 0;
    font-size: 0.95rem;
    opacity: 0.95;
}

/* Khung hiển thị Test Case kiểu Sổ ghi chép (Cute Notebook) ở cột bên trái */
.cute-notebook {
    background-color: #FFFDF9; /* Màu nền giấy ấm cúng */
    border: 2px solid #a5c2f4; /* Viền mỏng xanh nhẹ */
    border-left: 8px solid #345bc4; /* Gáy sổ màu xanh đậm */
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 6px 16px rgba(52, 91, 196, 0.08);
    margin-bottom: 20px;
    position: relative;
    
    /* Thiết lập chiều cao cố định để cân bằng với Khung Code bên phải, hỗ trợ cuộn dọc nếu test case dài */
    height: 400px !important;
    max-height: 400px !important;
    overflow-y: auto !important;
}

/* Tùy chỉnh thanh cuộn tinh tế cho Khung hiển thị Sổ ghi chép */
.cute-notebook::-webkit-scrollbar {
    width: 6px;
}
.cute-notebook::-webkit-scrollbar-track {
    background: #FFFDF9;
    border-radius: 4px;
}
.cute-notebook::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 4px;
}
.cute-notebook::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
}

/* Định dạng tiêu đề và các trường thông tin bên trong Sổ ghi chép */
.notebook-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #345bc4;
    border-bottom: 2px solid #a5c2f4;
    padding-bottom: 8px;
    margin-bottom: 12px;
}
.notebook-field {
    margin-bottom: 12px;
    padding-left: 0px;
}
.notebook-label {
    font-weight: 700;
    color: #345bc4;
    font-size: 0.95rem;
}
.notebook-val {
    color: #1e293b;
    font-size: 0.95rem;
    white-space: pre-wrap;
    background-color: rgba(219, 234, 254, 0.5);
    padding: 8px 12px 8px 17px;
    border-radius: 8px;
    margin-top: 4px;
    line-height: 1.4;
}

/* Thanh tiêu đề của Khung Code mô phỏng thiết bị macOS nhưng dùng tông màu xanh đồng bộ */
.mac-header {
    background: linear-gradient(135deg, #345bc4 0%, #5d87ed 100%);
    padding: 12px 18px;
    display: flex;
    align-items: center;
    border-top: 2px solid #a5c2f4;
    border-left: 2px solid #a5c2f4;
    border-right: 2px solid #a5c2f4;
    border-bottom: 1px solid #a5c2f4;
    
    /* Đảm bảo tiêu đề nằm trên cùng so với lớp overlay trên màn hình nhỏ */
    position: relative !important;
    z-index: 10 !important;
}
.mac-title {
    color: #ffffff !important;
    font-size: 0.95rem;
    margin-left: 0px;
    font-weight: 700;
}

/* Thẻ hiển thị hướng dẫn thiết lập URL kiểm thử */
.url-card {
    background-color: #F0FDF4;
    border: 2px solid #DCFCE7;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 6px 12px rgba(22, 163, 74, 0.05);
    margin-bottom: 24px;
}
.url-card-title {
    color: #16A34A;
    font-weight: 700;
    font-size: 1.25rem;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Ô thông tin hiển thị các chỉ số thống kê tổng quát (Thống kê thời gian, token) */
.stat-box {
    background-color: #F5F3FF; /* Màu tím pastel */
    border: 2px solid #DDD6FE;
    border-radius: 12px;
    padding: 15px;
    text-align: center;
    box-shadow: 0 4px 10px rgba(139, 92, 246, 0.05);
}
.stat-title {
    font-size: 0.9rem;
    color: #7C3AED;
    font-weight: 600;
    margin-bottom: 5px;
}
.stat-value {
    font-size: 1.6rem;
    font-weight: 700;
    color: #6D28D9;
}

/* Định dạng bo góc tròn mềm mại cho toàn bộ các nút bấm của Streamlit */
.stButton>button {
    border-radius: 20px !important;
    font-weight: 700 !important;
    transition: all 0.3s ease !important;
}
.stButton>button:hover {
    transform: scale(1.03) !important; /* Hiệu ứng phóng to nhẹ khi di chuột */
}

/* Tùy chỉnh riêng cho Nút Bắt Đầu Sinh Test Script (Xanh Lá cây nổi bật) */
div[data-testid="stElementContainer"]:has(.generate-btn-wrapper) + div[data-testid="stElementContainer"] .stButton>button {
    background-color: #F0FDF4 !important;
    color: #16A34A !important;
    border: 2px solid #bbf7d0 !important;
    box-shadow: 0 4px 10px rgba(22, 163, 74, 0.08) !important;
}
div[data-testid="stElementContainer"]:has(.generate-btn-wrapper) + div[data-testid="stElementContainer"] .stButton>button:hover {
    background-color: #DCFCE7 !important;
    color: #15803D !important;
    border-color: #86efac !important;
    box-shadow: 0 6px 15px rgba(22, 163, 74, 0.15) !important;
}

/* Tùy chỉnh riêng cho Nút Tải Project ZIP (Màu xanh dương pastel) */
div[data-testid="stElementContainer"]:has(.project-dl-wrapper) + div[data-testid="stElementContainer"] button {
    background-color: #eef5ff !important;
    color: #1d4ed8 !important;
    border: 2px solid #bfdbfe !important;
    box-shadow: 0 4px 10px rgba(29, 78, 216, 0.08) !important;
}
div[data-testid="stElementContainer"]:has(.project-dl-wrapper) + div[data-testid="stElementContainer"] button:hover {
    background-color: #dbeafe !important;
    color: #1e40af !important;
    border-color: #93c5fd !important;
    box-shadow: 0 6px 15px rgba(29, 78, 216, 0.15) !important;
}

/* Đường chạy hoạt cảnh chú mèo dễ thương khi đang chờ AI sinh code */
.cat-title {
    text-align: center;
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 18px;
    color: #1e3c72;
}
.cat-track {
    position: relative;
    width: 100%;
    height: 24px;
    background: #eef1f5;
    border-radius: 999px;
    overflow: visible;
}
.cat-fill {
    height: 100%;
    background: linear-gradient(90deg, #93c5fd 0%, #dbeafe 100%);
    border-radius: 999px;
    transition: width 0.4s linear;
}
.cat-runner {
    position: absolute;
    top: -34px;
    font-size: 34px;
    transition: left 0.4s linear;
    transform: scaleX(-1); /* Quay mặt chú mèo hướng sang bên phải */
}
.cat-percent {
    text-align: center;
    margin-top: 10px;
    font-weight: 600;
    color: #1a365d;
}

/* Tùy chỉnh thanh cuộn cho các khối code chuẩn (dùng cho Prompt view) */
.stCodeBlock pre {
    max-height: 310px !important;
    overflow-y: auto !important;
}

/* Căn chỉnh lại khoảng cách lề trên cho các điều khiển selectbox ở cột bên trái */
div[data-testid="column"]:first-child div[data-testid="stSelectbox"] {
    margin-top: -10px !important;
}

/* Sinh lại script theo chiều dọc trong cột chứa */
div:has(> .refresh-button-trigger) + div {
    margin-top: 15px !important;
}

/* Đồng bộ hóa thiết kế viền khung và cố định kích thước cho Script Workspace (stTabs) */
div[data-testid="stTabs"] {
    border-left: 2px solid #a5c2f4 !important;
    border-right: 2px solid #a5c2f4 !important;
    border-bottom: 2px solid #a5c2f4 !important;
    border-bottom-left-radius: 16px !important;
    border-bottom-right-radius: 16px !important;
    margin-top: -16px !important; /* Đẩy tab lên trên để nối liền mạch hoàn hảo với mac-header */
    padding: 12px !important;
    box-shadow: 0 10px 25px rgba(52, 91, 196, 0.05) !important;
    
    /* Chiều cao tổng cố định 422px giúp khớp chính xác với cột Test Case bên trái */
    height: 422px !important;
    max-height: 422px !important;
    position: relative !important;
    overflow: visible !important; /* Hỗ trợ hiển thị các nút tải được định vị tuyệt đối bên ngoài */
}

/* Ngăn các khối chứa bên trong stTabs tự động thêm scrollbar hoặc cắt xén giao diện */
div[data-testid="stTabs"] > div {
    overflow: visible !important;
}

/* Giới hạn khu vực bảng điều khiển Tab đang mở và ẩn các phần tràn */
div[data-testid="stTabs"] [data-testid="stTabsTabPanel"][aria-hidden="false"] {
    height: 330px !important;
    max-height: 330px !important;
    overflow: hidden !important;
}

/* Ẩn hoàn toàn các Tab không hoạt động để tránh chiếm dụng không gian màn hình */
div[data-testid="stTabs"] [data-testid="stTabsTabPanel"][aria-hidden="true"] {
    height: 0px !important;
    max-height: 0px !important;
    padding: 0px !important;
    margin: 0px !important;
    overflow: hidden !important;
    border: none !important;
    display: none !important;
}

/* Cố định độ cao và ẩn thanh cuộn thô của phần tử chứa iframe HTML tùy chỉnh */
div[data-testid="stTabs"] [data-testid="stTabsTabPanel"][aria-hidden="false"] [data-testid="stHtml"] {
    height: 330px !important;
    min-height: 330px !important;
    max-height: 330px !important;
    overflow: hidden !important;
}

/* Ép iframe HTML hiển thị code lấp đầy hoàn toàn diện tích của tab đang hoạt động */
div[data-testid="stTabs"] [data-testid="stTabsTabPanel"][aria-hidden="false"] [data-testid="stHtml"] iframe {
    height: 330px !important;
    min-height: 330px !important;
    max-height: 330px !important;
    width: 100% !important;
}

/* Ép các container trung gian ở dạng static để mốc định vị tuyệt đối luôn là div[data-testid="stTabs"] */
div[data-testid="stTabs"] [data-testid="stTabsTabPanel"],
div[data-testid="stTabs"] div[data-testid="stElementContainer"] {
    position: static !important;
}

/* Định vị nút tải riêng lẻ cách khung code 15px, chiều rộng bằng chiều rộng thông báo (khung viền ngoài stTabs) */
div[data-testid="stTabs"] div[data-testid="stDownloadButton"] {
    position: absolute !important;
    top: calc(100% + 23px) !important;
    left: -2px !important;
    right: -2px !important;
    width: auto !important; /* Ép trình duyệt tính chiều rộng tự động theo left và right */
    z-index: 99 !important;
}

/* Đồng bộ kích thước nút bấm bên trong để trải rộng hết khung và có độ cao cố định 38px */
div[data-testid="stTabs"] div[data-testid="stDownloadButton"] button,
div[data-testid="stTabs"] div[data-testid="stButton"] button,
div[data-testid="stTabs"] .stDownloadButton button,
div[data-testid="stTabs"] .stButton button {
    width: 100% !important;
    height: 38px !important;
    box-sizing: border-box !important;
    margin: 0 !important;
}

/* Reset khoảng cách của hộp thông báo thành công/lỗi để đảm khoảng cách 15px từ nút tải được hiển thị chuẩn xác */
div[data-testid="stNotification"] {
    margin-top: 0px !important;
    margin-bottom: 0px !important;
}

/* Định dạng thanh cuộn mượt mà cho các khối code và panel hiển thị */
.stCodeBlock::-webkit-scrollbar, .stCodeBlock pre::-webkit-scrollbar, [data-testid="stTabsTabPanel"]::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
.stCodeBlock::-webkit-scrollbar-track, .stCodeBlock pre::-webkit-scrollbar-track, [data-testid="stTabsTabPanel"]::-webkit-scrollbar-track {
    background: #f8fafc;
    border-radius: 4px;
}
.stCodeBlock::-webkit-scrollbar-thumb, .stCodeBlock pre::-webkit-scrollbar-thumb, [data-testid="stTabsTabPanel"]::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 4px;
}
.stCodeBlock::-webkit-scrollbar-thumb:hover, .stCodeBlock pre::-webkit-scrollbar-thumb:hover, [data-testid="stTabsTabPanel"]::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
}
"""

# ==========================================
# CÁC HÀM PYTHON HIỂN THỊ THÀNH PHẦN GIAO DIỆN
# ==========================================

def render_css():
    """Nhúng chuỗi CSS_STYLE tùy chỉnh trực tiếp vào mã HTML của trang Streamlit."""
    import time
    timestamp = int(time.time())
    st.markdown(f"<style>{CSS_STYLE}</style>", unsafe_allow_html=True)

def render_sidebar_header():
    """Hiển thị tiêu đề biểu tượng chú mèo dễ thương ở đỉnh thanh Sidebar bên trái."""
    st.markdown(
        "<div style='text-align: center;'>"
        "<h2 style='color: #FF7B00; margin-bottom: 0px;'>🐾 Cài Đặt</h2>"
        "<p style='color: #666; font-size: 0.85rem; margin-top: 0px;'>AI Test Script Generator</p>"
        "</div>", 
        unsafe_allow_html=True
    )


def render_sidebar_footer():
    """Hiển thị dòng chữ bản quyền dễ thương ở đáy thanh Sidebar bên trái."""
    st.markdown("<div style='text-align: center; font-size: 0.85rem; color: #888;'>🐾 Coded with love 💖</div>", unsafe_allow_html=True)


def render_header(title, subtitle):
    """Hiển thị banner tiêu đề chính ở trung tâm giao diện với Gradient màu xanh dương."""
    st.markdown(f"""
    <div class='custom-header'>
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def render_url_card():
    """Hiển thị thẻ chỉ dẫn nhập URL xanh lá pastel nhằm hướng dẫn người dùng cấu hình URL kiểm thử."""
    st.markdown("""
    <div class='url-card'>
        <div class='url-card-title'>🌐 Thiết lập URL cho các chức năng</div>
        <p style='color: #4b5563; font-size: 0.95rem; margin-top:-5px;'>Nhập địa chỉ URL kiểm thử tương ứng cho từng chức năng. AI sẽ sử dụng URL này để khởi tạo trình duyệt trong mã nguồn.</p>
    </div>
    """, unsafe_allow_html=True)


def render_cat_progress(placeholder, func_name, s_name, percent, elapsed_time):
    """
    Tạo hoạt cảnh đường chạy chú mèo di chuyển theo phần trăm tiến độ sinh code của AI.
    
    Tham số:
        placeholder: Streamlit container rỗng (st.empty) dùng để cập nhật giao diện động liên tục.
        func_name (str): Tên chức năng đang được xử lý sinh mã.
        s_name (str): Tên chiến lược Prompt được áp dụng (P1 - P5).
        percent (int): Phần trăm tiến độ hoàn thành hiện tại.
        elapsed_time (float): Thời gian đã trôi qua tính theo giây.
    """
    html = f"""
    <div class="cat-title">🐾 Đang sinh code cho {func_name} ({s_name})</div>
    <div class="cat-track">
        <div class="cat-fill" style="width: {percent}%;"></div>
        <div class="cat-runner" style="left: calc({percent}% - 18px);">🐈</div>
    </div>
    <div class="cat-percent">
        {percent}% · ⏱️ {elapsed_time:.2f}s
    </div>
    """
    placeholder.markdown(html, unsafe_allow_html=True)


def render_stat_box(title, value):
    """
    Hiển thị hộp số liệu thống kê (ví dụ: Tổng thời gian chạy, Tổng số token sử dụng).
    
    Tham số:
        title (str): Nhãn hoặc tiêu đề của số liệu.
        value (str): Giá trị cần hiển thị nổi bật.
    """
    st.markdown(f"""
    <div class='stat-box'>
        <div class='stat-title'>{title}</div>
        <div class='stat-value'>{value}</div>
    </div>
    """, unsafe_allow_html=True)


def render_notebook_card(selected_tc):
    """
    Hiển thị thông tin chi tiết một Test Case được lựa chọn dưới dạng Sổ Ghi Chép màu giấy ấm cúng.
    Các trường dữ liệu (Precondition, Steps, Expected, Test Data, Locator) được kiểm tra sự tồn tại
    và loại bỏ giá trị trống hoặc "Không có" trước khi render để tối ưu hóa không gian.
    
    Tham số:
        selected_tc (dict): Từ điển chứa các trường dữ liệu của Test Case đang chọn.
    """
    # Thay thế dấu xuống dòng bằng thẻ <br> để xuống hàng chuẩn trong HTML
    precondition = str(selected_tc.get("precondition", "")).strip().replace("\n", "<br>")
    steps_formatted = str(selected_tc.get("steps", "")).strip().replace("\n", "<br>")
    expected = str(selected_tc.get("expected", "")).strip().replace("\n", "<br>")
    
    # Khởi dựng thẻ bao ngoài Sổ Ghi Chép
    notebook_html = f"""
    <div class="cute-notebook">
        <div class="notebook-title">📋 {selected_tc.get("id", "TC_001")}</div>
    """
    
    # Chỉ hiển thị Điều kiện tiên quyết nếu trường này tồn tại và không phải là "không có"
    if precondition and precondition.lower() != "không có":
        notebook_html += f"""
        <div class="notebook-field">
            <div class="notebook-label">🌱 Điều kiện tiên quyết (Precondition):</div>
            <div class="notebook-val">{precondition}</div>
        </div>
        """
    
    # Hiển thị Các bước thực hiện (Trường bắt buộc)
    notebook_html += f"""
        <div class="notebook-field">
            <div class="notebook-label">👣 Các bước thực hiện (Steps):</div>
            <div class="notebook-val">{steps_formatted}</div>
        </div>
    """
    
    # Chỉ hiển thị Kết quả mong đợi nếu tồn tại và không phải là "không có"
    if expected and expected.lower() != "không có":
        notebook_html += f"""
        <div class="notebook-field">
            <div class="notebook-label">🔮 Kết quả mong đợi (Expected):</div>
            <div class="notebook-val">{expected}</div>
        </div>
        """
    
    # Định dạng hiển thị Dữ liệu kiểm thử (Test Data)
    data_formatted = selected_tc.get("data", {})
    data_str = ""
    if isinstance(data_formatted, dict) and data_formatted:
        data_str = "\n".join([f"{k}: {v}" for k, v in data_formatted.items()]).strip()
    elif data_formatted:
        data_str = str(data_formatted).strip()
    
    if data_str and data_str.lower() != "không có":
        data_str = data_str.replace("\n", "<br>")
        notebook_html += f"""
        <div class="notebook-field">
            <div class="notebook-label">💾 Dữ liệu kiểm thử (Test Data):</div>
            <div class="notebook-val">{data_str}</div>
        </div>
        """
    
    # Định dạng hiển thị Bộ định vị (Locator)
    locator = str(selected_tc.get("locator", "")).strip()
    if locator and locator.lower() != "không có":
        locator = locator.replace("\n", "<br>")
        notebook_html += f"""
        <div class="notebook-field">
            <div class="notebook-label">🔍 Bộ định vị (Locator):</div>
            <div class="notebook-val">{locator}</div>
        </div>
        """
    
    notebook_html += "</div>"
    
    # Loại bỏ dấu xuống dòng trong mã HTML để tránh trình biên dịch markdown của Streamlit làm vỡ giao diện
    notebook_html_clean = "".join([line.strip() for line in notebook_html.split("\n")])
    st.markdown(notebook_html_clean, unsafe_allow_html=True)


def render_mac_header(title):
    """
    Hiển thị thanh tiêu đề màu xanh đậm để làm khung trên cho Script Workspace.
    """
    st.markdown(f"""
    <div class="mac-header" style="border-top-left-radius: 16px; border-top-right-radius: 16px; justify-content: flex-start;">
        <div class="mac-title" style="margin-left: 0px; font-size: 0.95rem;">{title}</div>
    </div>
    """, unsafe_allow_html=True)


def render_zip_instructions():
    """Hiển thị hộp thoại gợi ý thông tin hướng dẫn sử dụng file ZIP project sau khi tải về."""
    st.markdown("""
    <div style="
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 20px !important;
        padding: 12px 24px !important;
        margin-bottom: 16px !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.02) !important;
        display: flex;
        align-items: center;
        gap: 8px;
    ">
        <span>💡 Bạn có thể giải nén file ZIP này và mở trực tiếp bằng PyCharm hoặc VSCode để chạy test ngay lập tức.</span>
    </div>
    """, unsafe_allow_html=True)


def render_code_block(file_content, height=330):
    """
    Sử dụng Streamlit Components để nhúng một iframe HTML chứa thư viện Highlight.js.
    Phương pháp này đảm bảo mã nguồn hiển thị cực kỳ đẹp mắt với font chữ JetBrains Mono,
    đồng thời giải quyết triệt để lỗi mất thanh cuộn ngang/dọc và lỗi cuộn trang của Streamlit đối với các file mã nguồn dài.
    
    Tham số:
        file_content (str): Nội dung mã nguồn Python cần hiển thị.
        height (int): Chiều cao hiển thị của iframe (mặc định là 330px để khớp với workspace).
    """
    import html
    import streamlit.components.v1 as components
    
    # Mã hóa các ký tự đặc biệt trong mã nguồn Python sang HTML Entities để tránh xung đột mã lệnh
    safe_code = html.escape(file_content)
    
    # Mã HTML hoàn chỉnh bao gồm thư viện highlight.js và cấu hình font, thanh cuộn chuyên sâu
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/github.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/languages/python.min.js"></script>
        <style>
            html, body {{
                margin: 0;
                padding: 0;
                width: 100%;
                height: 100%;
                background-color: transparent;
                overflow: hidden !important;
            }}
            .code-container {{
                height: 100%;
                overflow: auto;
                border: none;
                border-radius: 12px;
                background: #f8fafc;
                padding: 12px;
                box-sizing: border-box;
            }}
            .code-container::-webkit-scrollbar {{
                width: 8px;
                height: 8px;
            }}
            .code-container::-webkit-scrollbar-track {{
                background: #f8fafc;
                border-radius: 4px;
            }}
            .code-container::-webkit-scrollbar-thumb {{
                background: #cbd5e1;
                border-radius: 4px;
            }}
            .code-container::-webkit-scrollbar-thumb:hover {{
                background: #94a3b8;
            }}
            pre {{
                margin: 0;
                padding: 0;
                background: transparent !important;
            }}
            code {{
                font-family: 'JetBrains Mono', monospace !important;
                font-size: 13px !important;
                line-height: 1.5 !important;
                background: transparent !important;
                padding: 0 !important;
                
                font-variant-ligatures: none !important;
                font-feature-settings: "liga" 0 !important;
            }}
        </style>
    </head>
    <body>
        <div class="code-container">
            <pre><code class="language-python">{safe_code}</code></pre>
        </div>
        <script>
            // Kích hoạt Highlight.js để bôi màu cú pháp mã nguồn
            hljs.highlightAll();

            // Khôi phục cuộn về đỉnh góc trái của khối code sau khi tải hoặc đổi tab nhằm tránh tình trạng bị lệch
            function resetScroll() {{
                const box = document.querySelector('.code-container');
                if (box) {{
                    box.scrollTop = 0;
                    box.scrollLeft = 0;
                }}
                window.scrollTo(0, 0);
            }}

            // Gọi hàm resetScroll ở các mốc thời gian khác nhau để đảm bảo trình duyệt render xong hoàn toàn
            setTimeout(resetScroll, 50);
            setTimeout(resetScroll, 200);
            setTimeout(resetScroll, 500);
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=height, scrolling=False)
