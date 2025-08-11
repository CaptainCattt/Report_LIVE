import streamlit as st
from PIL import Image
import base64

# 🔺 Đặt lệnh set_page_config ở dòng đầu tiên
st.set_page_config(page_title="REPORT LIVESTREAM OF BRAND", layout="wide")


# Chèn logo từ GitHub vào góc trên bên trái
st.markdown(
    """
    <div style='top: 60px; left: 40px; z-index: 1000;'>
        <img src='https://raw.githubusercontent.com/CaptainCattt/Report_of_shopee/main/logo-lamvlog.png' width='150'/>
    </div>
    """,
    unsafe_allow_html=True,
)

# ======= TIÊU ĐỀ CĂN GIỮA =======
st.markdown(
    """
    <div style='text-align: center; display: flex; justify-content: center; align-items: center; gap: 10px;'>
        <img src='https://img.icons8.com/?size=100&id=118638&format=png&color=000000' width='40'/>
        <h1 style='color: red; margin: 0;'>REPORT LIVESTREAM OF BRAND</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br><br><br>", unsafe_allow_html=True)


# Tạo các cột cho upload file
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        "<h3 style='text-align: center;'>📥 Upload File Name Of Brand</h3>",
        unsafe_allow_html=True,
    )
    df_brands = st.file_uploader(
        "Tải lên file về các tên BRAND tham gia phiên LIVE",
        type=["xlsx", "xls"],
        key="tiktok_all",
    )

with col2:
    st.markdown(
        "<h3 style='text-align: center;'>📥 Upload File Report Of LIVE</h3>",
        unsafe_allow_html=True,
    )
    df = st.file_uploader(
        "Tải lên báo cáo chi tiết của phiên LIVE",
        type=["xlsx", "xls"],
        key="tiktok_income",
    )

# Khởi tạo trạng thái nếu chưa có
if "processing" not in st.session_state:
    st.session_state.processing = False

# Nút xử lý
import streamlit as st

# Tùy chỉnh kích thước và căn giữa nút
st.markdown(
    """
    <style>
        .center-button {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .button-style {
            font-size: 20px;
            padding: 15px 10px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .button-style:hover {
            background-color: #45a049;
        }
    </style>

""",
    unsafe_allow_html=True,
)

# Nút Xử lý dữ liệu
with st.container():
    st.markdown('<div class="center-button">', unsafe_allow_html=True)
    process_btn = st.button(
        "🆗 Start 🆗",
        key="process_data",
        disabled=st.session_state.processing,
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

if st.button("🔁 Reset 🔁", use_container_width=True):
    st.session_state.clear()
    st.rerun()


def process_tiktok_daily_report(df_brands, df):

    def detect_brand_from_name(product_name: str, brand_keywords: list):
        name = product_name.lower()
        for kw in brand_keywords:
            if kw in name:
                return kw  # hoặc return tên chuẩn hóa nếu bạn có thêm cột 'Brand chuẩn'
        return "Khác"

    def format_vn_currency(x):
        if pd.isnull(x):
            return ""
        return f"{x:,.0f} ₫".replace(",", ".")

    brand_keywords = df_brands["Brand"].dropna().str.lower().tolist()
    df["SKU Category"] = df["Tên sản phẩm"].apply(
        lambda x: detect_brand_from_name(x, brand_keywords)
    )
    df["SKU Category"] = df["SKU Category"].str.upper()

    def evaluate_collab(row):
        try:
            gmv_moi_don = (
                row["GMV đã ghi nhận"] / row["Đơn hàng chính"]
                if row["Đơn hàng chính"]
                else 0
            )
            ctr = row["Tỷ lệ nhấp"] * 100 if pd.notnull(row["Tỷ lệ nhấp"]) else 0
            ctor = (
                row["CTOR (Đơn hàng chính)"] * 100
                if pd.notnull(row["CTOR (Đơn hàng chính)"])
                else 0
            )
            pay_rate = (
                row["Tỷ lệ thanh toán"] * 100
                if pd.notnull(row["Tỷ lệ thanh toán"])
                else 0
            )
            cart_conversion = (
                row["Số món bán ra "] / row["Số lượt thêm vào giỏ hàng"]
                if row["Số lượt thêm vào giỏ hàng"]
                else 0
            )
            don_per_view = (
                row["Đơn hàng chính"] / row["Lượt hiển thị sản phẩm"]
                if row["Lượt hiển thị sản phẩm"]
                else 0
            )

            score = 0
            score += gmv_moi_don >= 70000
            score += ctr >= 3
            score += ctor >= 5
            score += pay_rate >= 95
            score += cart_conversion >= 0.5
            score += don_per_view >= 0.002

            return pd.Series(
                {
                    "GMV mỗi đơn": round(gmv_moi_don, 0),
                    "CTR (%)": round(ctr, 2),
                    "CTOR (%)": round(ctor, 2),
                    "Tỷ lệ thanh toán (%)": round(pay_rate, 2),
                    "Tỷ lệ chuyển đổi giỏ hàng": round(cart_conversion, 2),
                    "Hiệu quả đơn/view": round(don_per_view, 4),
                    "Điểm đánh giá (0-6)": score,
                    "Nên tiếp tục collab?": "✅ Có" if score >= 3 else "❌ Không",
                }
            )

        except Exception as e:
            # Nếu có lỗi (ví dụ thiếu cột), trả về NaN hoặc default
            return pd.Series(
                {
                    "GMV mỗi đơn": None,
                    "CTR (%)": None,
                    "CTOR (%)": None,
                    "Tỷ lệ thanh toán (%)": None,
                    "Tỷ lệ chuyển đổi giỏ hàng": None,
                    "Hiệu quả đơn/view": None,
                    "Điểm đánh giá (0-6)": 0,
                    "Nên tiếp tục collab?": "❌ Không",
                }
            )

    df_result = df.copy()
    df_result = df_result.join(df_result.apply(evaluate_collab, axis=1))

    df_result_new = df_result[
        [
            "Tên sản phẩm",
            "SKU Category",
            "GMV đã ghi nhận",
            "Đơn hàng chính",
            "GMV mỗi đơn",
            "CTR (%)",
            "CTOR (%)",
            "Tỷ lệ thanh toán (%)",
            "Tỷ lệ chuyển đổi giỏ hàng",
            "Hiệu quả đơn/view",
            "Điểm đánh giá (0-6)",
            "Nên tiếp tục collab?",
        ]
    ].copy()
    df_result_new["GMV đã ghi nhận"] = df_result_new["GMV đã ghi nhận"].apply(
        format_vn_currency
    )

    brand_eval = (
        df_result.groupby("Tên sản phẩm")
        .agg(
            {
                "GMV đã ghi nhận": "sum",
                "Đơn hàng chính": "sum",
                "GMV mỗi đơn": "mean",
                "CTR (%)": "mean",
                "CTOR (%)": "mean",
                "Tỷ lệ thanh toán (%)": "mean",
                "Tỷ lệ chuyển đổi giỏ hàng": "mean",
                "Hiệu quả đơn/view": "mean",
                "Điểm đánh giá (0-6)": "mean",
            }
        )
        .reset_index()
    )

    # Gợi ý đánh giá brand
    brand_eval["Nên tiếp tục collab?"] = brand_eval["Điểm đánh giá (0-6)"].apply(
        lambda x: "✅ Có" if x >= 3 else "❌ Không"
    )

    brand_eval_1 = (
        df_result.groupby("SKU Category")
        .agg(
            {
                "GMV đã ghi nhận": "sum",
                "Đơn hàng chính": "sum",
                "GMV mỗi đơn": "mean",
                "CTR (%)": "mean",
                "CTOR (%)": "mean",
                "Tỷ lệ thanh toán (%)": "mean",
                "Tỷ lệ chuyển đổi giỏ hàng": "mean",
                "Hiệu quả đơn/view": "mean",
                "Điểm đánh giá (0-6)": "mean",
            }
        )
        .reset_index()
    )

    brand_eval_1["Nên tiếp tục collab?"] = brand_eval_1["Điểm đánh giá (0-6)"].apply(
        lambda x: "✅ Có" if x >= 3 else "❌ Không"
    )

    return (df_result_new, brand_eval, brand_eval_1)


import io


def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Report")
    processed_data = output.getvalue()
    return processed_data


import pandas as pd

if process_btn:
    if not df_brands or not df:
        st.warning("Vui lòng upload cả 2 file!")
    else:
        with st.spinner("⏳ Đang xử lý dữ liệu, vui lòng chờ..."):
            # Đọc dữ liệu từ file upload
            df_brands = pd.read_excel(df_brands)
            df = pd.read_excel(df)

            # Xử lý dữ liệu
            df_result_new, brand_eval, brand_eval_1 = process_tiktok_daily_report(
                df_brands, df
            )

            # Lưu vào session
            st.session_state["df_result_new"] = df_result_new
            st.session_state["brand_eval"] = brand_eval
            st.session_state["brand_eval_1"] = brand_eval_1

if "df_result_new" in st.session_state:
    st.dataframe(st.session_state["df_result_new"], use_container_width=True)
    import io

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        st.session_state["df_result_new"].to_excel(
            writer, index=False, sheet_name="Report"
        )
    processed_data = output.getvalue()

    st.download_button(
        label="📥 Tải báo cáo Excel",
        data=processed_data,
        file_name="bao_cao_collab.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

if "brand_eval_1" in st.session_state:
    st.dataframe(st.session_state["brand_eval_1"], use_container_width=True)

    import io

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        st.session_state["brand_eval_1"].to_excel(
            writer, index=False, sheet_name="Report"
        )
    processed_data = output.getvalue()

    st.download_button(
        label="📥 Tải báo cáo Excel",
        data=processed_data,
        file_name="brand_total.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
