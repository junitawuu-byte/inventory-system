"""
庫存管理系統 - 使用 Streamlit
資料來源：inventory.xlsx（請放在與 app.py 同一資料夾）
"""

import streamlit as st
import pandas as pd
from pathlib import Path

# 頁面設定
st.set_page_config(
    page_title="庫存管理系統",
    page_icon="📦",
    layout="centered",
    initial_sidebar_state="expanded",
)

# 資料檔路徑（與 app.py 同目錄）
DATA_FILE = Path(__file__).parent / "inventory.xlsx"

# 只顯示 Excel A～D 欄（工作表上由左而右前四欄）
DISPLAY_COL_COUNT = 4


@st.cache_data(ttl=60)
def load_inventory():
    """讀取 inventory.xlsx，若不存在則回傳空 DataFrame。"""
    if not DATA_FILE.exists():
        return None
    try:
        df = pd.read_excel(DATA_FILE, engine="openpyxl")
        df.columns = df.columns.str.strip()  # 去除欄位名稱前後空白
        return df
    except Exception as e:
        st.error(f"讀取 Excel 時發生錯誤：{e}")
        return None


def main():
    st.title("📦 庫存管理系統")
    st.markdown("---")

    df = load_inventory()

    if df is None:
        st.warning(
            f"找不到 **inventory.xlsx**，請將檔案放在此目錄：\n\n`{DATA_FILE.parent}`"
        )
        st.info("請確認檔名為 `inventory.xlsx`（小寫），且與 app.py 在同一資料夾。")
        return

    if df.empty:
        st.info("目前庫存清單為空。")
        return

    if df.shape[1] == 0:
        st.info("工作表沒有任何欄位。")
        return

    # 僅保留 A～D 欄（欄數不足四則顯示現有欄位）
    n = min(DISPLAY_COL_COUNT, df.shape[1])
    df = df.iloc[:, :n]

    # 側邊欄：查詢條件
    st.sidebar.header("🔍 查詢條件")

    # 取得所有欄位名稱供篩選
    columns = df.columns.tolist()
    text_columns = [
        c for c in columns
        if df[c].dtype == "object" or pd.api.types.is_string_dtype(df[c])
    ]
    if not text_columns:
        text_columns = columns[:1]  # 至少用第一欄

    search_col = st.sidebar.selectbox(
        "依欄位搜尋",
        options=columns,
        index=0,
    )
    search_term = st.sidebar.text_input(
        "關鍵字（留空則顯示全部）",
        placeholder="輸入關鍵字...",
    )

    # 篩選邏輯
    if search_term and search_term.strip():
        mask = df[search_col].astype(str).str.contains(
            search_term.strip(), case=False, na=False
        )
        display_df = df[mask]
    else:
        display_df = df.copy()

    # 主畫面：庫存清單
    st.subheader("庫存清單")

    if display_df.empty:
        st.info("沒有符合條件的資料。")
    else:
        st.caption(f"共 **{len(display_df)}** 筆（總筆數：{len(df)}）")
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("---")
    st.caption("資料來源：inventory.xlsx｜重新整理頁面以更新資料")


if __name__ == "__main__":
    main()
