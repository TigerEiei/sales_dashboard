
# นำเข้าไลบรารีที่จำเป็น
import streamlit as st
import pandas as pd
import plotly.express as px

# ตั้งค่าหน้าเว็บไซต์
st.set_page_config(
    page_title="แดชบอร์ดวิเคราะห์ยอดขาย",
    page_icon="📊",
    layout="wide"
)

# ชื่อเว็บไซต์และคำอธิบาย
st.title("แดชบอร์ดวิเคราะห์ยอดขายร้านค้า")
st.write(
    "เว็บไซต์สำหรับวิเคราะห์ยอดขายจากข้อมูลธุรกรรม "
    "เพื่อช่วยให้เข้าใจแนวโน้มและพฤติกรรมการซื้อ"
)


# ==============================
# 1. อ่านข้อมูลจากไฟล์ CSV
# ==============================

import os

FILE_PATH = "ข้อมูลยอดขาย_คัดกรองแล้ว.csv"

if not os.path.exists(FILE_PATH):
    st.error("ไม่พบไฟล์ CSV กรุณาตรวจสอบว่าไฟล์อยู่ในโฟลเดอร์เดียวกับ app.py")
    st.stop()

try:
    df = pd.read_csv(FILE_PATH, encoding="utf-8-sig")
except Exception as e:
    st.error(f"ไม่สามารถอ่านไฟล์ CSV ได้: {e}")
    st.stop()

# ==============================
# 2. ตรวจสอบคอลัมน์ที่จำเป็น
# ==============================

required_columns = [
    "Transaction_ID",
    "Customer_ID",
    "Purchase_Date",
    "Branch",
    "Gender",
    "Age",
    "Category",
    "Amount_THB",
    "Payment_Method",
    "Rating"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    st.error(f"ไม่พบคอลัมน์ที่จำเป็น: {missing_columns}")
    st.stop()

# ==============================
# 3. แปลงชนิดข้อมูล
# ==============================

df["Purchase_Date"] = pd.to_datetime(
    df["Purchase_Date"], errors="coerce"
)

df["Amount_THB"] = pd.to_numeric(
    df["Amount_THB"], errors="coerce"
)

df["Age"] = pd.to_numeric(
    df["Age"], errors="coerce"
)

df["Rating"] = pd.to_numeric(
    df["Rating"], errors="coerce"
)

# ==============================
# 4. แสดงผลการตรวจสอบข้อมูล
# ==============================

st.subheader("ผลการตรวจสอบข้อมูล")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("จำนวนรายการ", f"{len(df):,}")

with col2:
    st.metric("จำนวนคอลัมน์", f"{len(df.columns):,}")

with col3:
    st.metric(
        "รายการซ้ำทั้งแถว",
        f"{df.duplicated().sum():,}"
    )

st.write("**จำนวนค่าว่างในแต่ละคอลัมน์**")

missing_summary = (
    df.isna()
    .sum()
    .reset_index()
)

missing_summary.columns = [
    "ชื่อคอลัมน์",
    "จำนวนค่าว่าง"
]

st.dataframe(
    missing_summary,
    use_container_width=True,
    hide_index=True
)

st.write("**ตัวอย่างข้อมูล 5 รายการแรก**")

st.dataframe(
    df.head(),
    use_container_width=True,
    hide_index=True
)


# ==============================
# 5. สรุปตัวเลขสำคัญ (KPI)
# ==============================

st.divider()
st.header("สรุปภาพรวมยอดขาย")

# ใช้เฉพาะยอดเงินที่แปลงเป็นตัวเลขได้
valid_amounts = df["Amount_THB"].dropna()

total_sales = valid_amounts.sum()
average_sales = valid_amounts.mean()
median_sales = valid_amounts.median()
transaction_count = len(df)

# แสดง KPI 4 ช่อง
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric(
    "จำนวนรายการ",
    f"{transaction_count:,}"
)

kpi2.metric(
    "ยอดซื้อรวม",
    f"฿{total_sales:,.2f}"
)

kpi3.metric(
    "ยอดซื้อเฉลี่ยต่อรายการ",
    f"฿{average_sales:,.2f}"
)

kpi4.metric(
    "ยอดซื้อมัธยฐาน",
    f"฿{median_sales:,.2f}"
)

# แจ้งเตือนหากมีค่ายอดเงินที่ไม่ใช่ตัวเลข
invalid_amount_count = df["Amount_THB"].isna().sum()

if invalid_amount_count > 0:
    st.warning(
        f"พบรายการที่ไม่สามารถอ่านยอดเงินได้ "
        f"{invalid_amount_count} รายการ "
        "จึงไม่นำมาคำนวณยอดซื้อรวมและค่าเฉลี่ย"
    )


# ==============================
# 6. ตัวกรองข้อมูล
# ==============================

st.divider()
st.header("ตัวกรองข้อมูล")

# เตรียมข้อมูลสำหรับกรอง โดยไม่แก้ไข df ต้นฉบับ
df_filtered = df.copy()

# แปลงวันที่ที่ใช้เลือกช่วงเวลา
valid_dates = df_filtered["Purchase_Date"].dropna()

if not valid_dates.empty:
    min_date = valid_dates.min().date()
    max_date = valid_dates.max().date()

    selected_dates = st.date_input(
        "เลือกช่วงวันที่ซื้อ",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
        start_date, end_date = selected_dates

        df_filtered = df_filtered[
            df_filtered["Purchase_Date"].notna()
            & (df_filtered["Purchase_Date"].dt.date >= start_date)
            & (df_filtered["Purchase_Date"].dt.date <= end_date)
        ]
else:
    st.warning("ไม่พบวันที่ที่ถูกต้องสำหรับใช้กรองข้อมูล")

# ตัวกรองสาขา
branches = sorted(df_filtered["Branch"].dropna().unique().tolist())

selected_branches = st.multiselect(
    "เลือกสาขา",
    options=branches,
    default=branches
)

df_filtered = df_filtered[
    df_filtered["Branch"].isin(selected_branches)
]

# ตัวกรองหมวดหมู่สินค้า
categories = sorted(df_filtered["Category"].dropna().unique().tolist())

selected_categories = st.multiselect(
    "เลือกหมวดหมู่สินค้า",
    options=categories,
    default=categories
)

df_filtered = df_filtered[
    df_filtered["Category"].isin(selected_categories)
]

# ตัวกรองวิธีชำระเงิน
payment_methods = sorted(
    df_filtered["Payment_Method"].dropna().unique().tolist()
)

selected_payments = st.multiselect(
    "เลือกวิธีชำระเงิน",
    options=payment_methods,
    default=payment_methods
)

df_filtered = df_filtered[
    df_filtered["Payment_Method"].isin(selected_payments)
]

# แจ้งผลหลังกรอง
st.write(f"**จำนวนรายการหลังกรอง: {len(df_filtered):,} รายการ**")

if df_filtered.empty:
    st.warning("ไม่พบข้อมูลตามเงื่อนไขที่เลือก กรุณาปรับตัวกรอง")
else:
    st.success("พบข้อมูลตามเงื่อนไขที่เลือก")
    st.dataframe(
        df_filtered,
        use_container_width=True,
        hide_index=True
    )


# ==============================
# 7. กราฟวิเคราะห์ยอดขาย
# ==============================

st.divider()
st.header("กราฟวิเคราะห์ยอดขาย")

if df_filtered.empty:
    st.warning("ไม่มีข้อมูลสำหรับสร้างกราฟ กรุณาปรับตัวกรอง")
else:
    # เตรียมยอดขายที่เป็นตัวเลขได้
    chart_df = df_filtered.dropna(
        subset=["Amount_THB"]
    ).copy()

    if chart_df.empty:
        st.warning("ไม่มีข้อมูลยอดขายที่ถูกต้องสำหรับสร้างกราฟ")
    else:
        # ------------------------------
        # กราฟที่ 1: ยอดขายตามหมวดสินค้า
        # ------------------------------
        st.subheader("1. ยอดขายรวมตามหมวดหมู่สินค้า")

        category_sales = (
            chart_df.groupby("Category", as_index=False)
            ["Amount_THB"]
            .sum()
            .sort_values("Amount_THB", ascending=False)
        )

        fig_bar = px.bar(
            category_sales,
            x="Category",
            y="Amount_THB",
            title="เปรียบเทียบยอดขายตามหมวดสินค้า",
            labels={
                "Category": "หมวดหมู่สินค้า",
                "Amount_THB": "ยอดขาย (บาท)"
            },
            text_auto=".2f"
        )

        fig_bar.update_layout(
            xaxis_title="หมวดหมู่สินค้า",
            yaxis_title="ยอดขาย (บาท)"
        )

        st.plotly_chart(
            fig_bar,
            use_container_width=True
        )

        # ------------------------------
        # กราฟที่ 2: แนวโน้มยอดขายรายเดือน
        # ------------------------------
        st.subheader("2. แนวโน้มยอดขายรายเดือน")

        trend_df = chart_df.dropna(
            subset=["Purchase_Date"]
        ).copy()

        if trend_df.empty:
            st.warning("ไม่มีวันที่ที่ถูกต้องสำหรับสร้างกราฟแนวโน้ม")
        else:
            trend_df["เดือน"] = (
                trend_df["Purchase_Date"]
                .dt.to_period("M")
                .astype(str)
            )

            monthly_sales = (
                trend_df.groupby("เดือน", as_index=False)
                ["Amount_THB"]
                .sum()
                .sort_values("เดือน")
            )

            fig_line = px.line(
                monthly_sales,
                x="เดือน",
                y="Amount_THB",
                markers=True,
                title="ยอดขายรวมในแต่ละเดือน",
                labels={
                    "เดือน": "เดือน",
                    "Amount_THB": "ยอดขาย (บาท)"
                }
            )

            fig_line.update_layout(
                xaxis_title="เดือน",
                yaxis_title="ยอดขาย (บาท)"
            )

            st.plotly_chart(
                fig_line,
                use_container_width=True
            )


# ==============================
# 12. วิเคราะห์ยอดขายตามสาขาและวิธีชำระเงิน
# ==============================

st.divider()
st.header("วิเคราะห์ยอดขายตามสาขาและวิธีชำระเงิน")

if df_filtered.empty:
    st.warning("ไม่มีข้อมูลสำหรับสร้างกราฟ")
else:
    branch_payment_df = df_filtered.dropna(
        subset=["Amount_THB"]
    ).copy()

    if branch_payment_df.empty:
        st.warning("ไม่มีข้อมูลยอดขายที่ถูกต้องสำหรับสร้างกราฟ")
    else:
        # --------------------------------
        # กราฟที่ 1: ยอดขายรวมแยกตามสาขา
        # --------------------------------
        st.subheader("1. เปรียบเทียบยอดขายรวมแต่ละสาขา")

        branch_sales = (
            branch_payment_df
            .groupby("Branch", as_index=False)
            .agg(
                Total_Sales=("Amount_THB", "sum"),
                Transaction_Count=("Transaction_ID", "count")
            )
            .sort_values("Total_Sales", ascending=False)
        )

        fig_branch = px.bar(
            branch_sales,
            x="Branch",
            y="Total_Sales",
            text="Total_Sales",
            hover_data=["Transaction_Count"],
            title="ยอดขายรวมแยกตามสาขา",
            labels={
                "Branch": "สาขา",
                "Total_Sales": "ยอดขายรวม (บาท)",
                "Transaction_Count": "จำนวนรายการ"
            }
        )

        fig_branch.update_traces(
            texttemplate="%{text:,.2f}",
            textposition="outside"
        )

        fig_branch.update_layout(
            xaxis_title="สาขา",
            yaxis_title="ยอดขายรวม (บาท)"
        )

        st.plotly_chart(
            fig_branch,
            use_container_width=True
        )

        # --------------------------------
        # กราฟที่ 2: วิธีชำระเงินในแต่ละสาขา
        # --------------------------------
        st.subheader("2. เปรียบเทียบยอดขายตามวิธีชำระเงินในแต่ละสาขา")

        payment_sales = (
            branch_payment_df
            .groupby(
                ["Branch", "Payment_Method"],
                as_index=False
            )
            .agg(
                Total_Sales=("Amount_THB", "sum"),
                Transaction_Count=("Transaction_ID", "count")
            )
        )

        fig_payment = px.bar(
            payment_sales,
            x="Branch",
            y="Total_Sales",
            color="Payment_Method",
            barmode="group",
            hover_data=["Transaction_Count"],
            title="ยอดขายตามวิธีชำระเงิน แยกตามสาขา",
            labels={
                "Branch": "สาขา",
                "Total_Sales": "ยอดขายรวม (บาท)",
                "Payment_Method": "วิธีชำระเงิน",
                "Transaction_Count": "จำนวนรายการ"
            }
        )

        fig_payment.update_layout(
            xaxis_title="สาขา",
            yaxis_title="ยอดขายรวม (บาท)",
            legend_title="วิธีชำระเงิน"
        )

        st.plotly_chart(
            fig_payment,
            use_container_width=True
        )

        # --------------------------------
        # ตารางสรุปประกอบกราฟ
        # --------------------------------
        st.subheader("ตารางสรุปยอดขายแยกตามสาขาและวิธีชำระเงิน")

        payment_table = payment_sales.sort_values(
            ["Branch", "Total_Sales"],
            ascending=[True, False]
        )

        st.dataframe(
            payment_table,
            use_container_width=True,
            hide_index=True
        )


# ==============================
# 8. สรุปผลตามตัวกรอง
# ==============================

st.divider()
st.header("สรุปผลตามตัวกรอง")

if df_filtered.empty:
    st.warning("ไม่มีข้อมูลสำหรับสรุปผล")
else:
    filtered_amounts = df_filtered["Amount_THB"].dropna()

    if filtered_amounts.empty:
        st.warning("ไม่มีข้อมูลยอดเงินที่ถูกต้องสำหรับคำนวณ")
    else:
        filtered_total = filtered_amounts.sum()
        filtered_average = filtered_amounts.mean()
        filtered_median = filtered_amounts.median()

        kpi1, kpi2, kpi3 = st.columns(3)

        kpi1.metric(
            "จำนวนรายการที่กรองได้",
            f"{len(df_filtered):,}"
        )

        kpi2.metric(
            "ยอดซื้อรวมหลังกรอง",
            f"฿{filtered_total:,.2f}"
        )

        kpi3.metric(
            "ยอดซื้อเฉลี่ยหลังกรอง",
            f"฿{filtered_average:,.2f}"
        )

        # หาหมวดสินค้าที่มียอดขายรวมสูงสุด
        category_totals = (
            df_filtered.dropna(subset=["Amount_THB"])
            .groupby("Category")["Amount_THB"]
            .sum()
        )

        if not category_totals.empty:
            top_category = category_totals.idxmax()
            top_category_sales = category_totals.max()

            st.info(
                f"หมวดสินค้าที่มียอดขายรวมสูงสุดในข้อมูลที่เลือกคือ "
                f"**{top_category}** "
                f"ยอดขายรวม {top_category_sales:,.2f} บาท"
            )


# ==============================
# 9. ข้อจำกัดและคุณภาพของข้อมูล
# ==============================

st.divider()
st.header("คุณภาพข้อมูลและข้อจำกัด")

st.write(
    "ส่วนนี้แสดงข้อควรระวังในการตีความผลวิเคราะห์ "
    "โดยไม่แก้ไขข้อมูลต้นฉบับ"
)

# ตรวจสอบยอดเงินติดลบและยอดเงินเป็นศูนย์
negative_count = (df["Amount_THB"] < 0).sum()
zero_count = (df["Amount_THB"] == 0).sum()

# ตรวจสอบวันที่ที่แปลงไม่ได้
invalid_date_count = df["Purchase_Date"].isna().sum()

# ตรวจสอบค่าว่าง
missing_gender = df["Gender"].isna().sum()
missing_age = df["Age"].isna().sum()
missing_rating = df["Rating"].isna().sum()

col1, col2, col3 = st.columns(3)

col1.metric("ยอดเงินติดลบ", f"{negative_count:,} รายการ")
col2.metric("ยอดเงินเป็นศูนย์", f"{zero_count:,} รายการ")
col3.metric("วันที่ไม่ถูกต้อง/ว่าง", f"{invalid_date_count:,} รายการ")

st.write("**ค่าว่างในข้อมูลที่สำคัญ**")

st.write(f"- เพศ: {missing_gender:,} รายการ")
st.write(f"- อายุ: {missing_age:,} รายการ")
st.write(f"- คะแนนรีวิว: {missing_rating:,} รายการ")

st.warning(
    "ข้อจำกัด: ข้อมูลบางรายการไม่มีเพศ อายุ หรือคะแนนรีวิว "
    "การวิเคราะห์แต่ละด้านจึงอาจใช้จำนวนรายการไม่เท่ากัน "
    "ยอดเงินติดลบหรือยอดเงินเป็นศูนย์ควรตรวจสอบกับแหล่งข้อมูล "
    "ก่อนตัดสินใจว่าเป็นข้อผิดพลาด"
)

st.caption(
    "แหล่งข้อมูล: ข้อมูลยอดขาย_คัดกรองแล้ว.csv "
    "| ตัวเลขคำนวณจากข้อมูลที่อ่านได้ในเว็บไซต์"
)


# ==============================
# 10. ตรวจสอบความถูกต้องของผลวิเคราะห์
# ==============================

st.divider()
st.header("ตรวจสอบความถูกต้องของผลวิเคราะห์")

# คำนวณค่าตรวจสอบจากข้อมูลต้นฉบับที่อ่านเข้ามา
check_amounts = df["Amount_THB"].dropna()

check_total_sales = check_amounts.sum()
check_average_sales = check_amounts.mean()
check_median_sales = check_amounts.median()

check_transaction_count = len(df)
check_valid_amount_count = check_amounts.count()

# ตรวจสอบยอดรวมจากตารางสรุปหมวดสินค้า
check_category_total = (
    df.dropna(subset=["Amount_THB"])
    .groupby("Category")["Amount_THB"]
    .sum()
    .sum()
)

# แสดงผลการตรวจสอบ
st.write("**ผลการตรวจสอบข้อมูลทั้งชุด**")

check_result = pd.DataFrame({
    "รายการตรวจสอบ": [
        "จำนวนแถวข้อมูล",
        "จำนวนรายการที่มียอดเงินเป็นตัวเลข",
        "ยอดซื้อรวมจากข้อมูล",
        "ยอดรวมจากตารางหมวดสินค้า",
        "ยอดซื้อเฉลี่ยต่อรายการ",
        "ยอดซื้อมัธยฐาน"
    ],
    "ผลลัพธ์": [
        f"{check_transaction_count:,}",
        f"{check_valid_amount_count:,}",
        f"{check_total_sales:,.2f} บาท",
        f"{check_category_total:,.2f} บาท",
        f"{check_average_sales:,.2f} บาท",
        f"{check_median_sales:,.2f} บาท"
    ]
})

st.dataframe(
    check_result,
    use_container_width=True,
    hide_index=True
)

if abs(check_total_sales - check_category_total) < 0.01:
    st.success("ผ่าน: ยอดรวมจากข้อมูลตรงกับยอดรวมจากตารางหมวดสินค้า")
else:
    st.error("ไม่ผ่าน: ยอดรวมไม่ตรงกัน กรุณาตรวจสอบข้อมูลและการคำนวณ")

st.caption(
    "หมายเหตุ: การตรวจสอบนี้ใช้ข้อมูลทั้งชุด ไม่ได้ใช้เฉพาะข้อมูลที่ผ่านตัวกรอง"
)


# ==============================
# 11. ดาวน์โหลดข้อมูลหลังกรอง
# ==============================

st.divider()
st.header("ส่งออกข้อมูล")

if df_filtered.empty:
    st.info("ไม่มีข้อมูลให้ดาวน์โหลด กรุณาปรับตัวกรอง")
else:
    csv_data = df_filtered.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        label="ดาวน์โหลดข้อมูลที่กรองแล้ว (CSV)",
        data=csv_data,
        file_name="ข้อมูลยอดขาย_หลังกรอง.csv",
        mime="text/csv"
    )

    st.caption(
        "ไฟล์ที่ดาวน์โหลดจะมีเฉพาะรายการที่ตรงกับตัวกรองปัจจุบัน "
        "โดยไม่แก้ไขไฟล์ CSV ต้นฉบับ"
    )

