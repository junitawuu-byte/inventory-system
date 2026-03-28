"""
庫存管理系統 - 使用 Streamlit（雲端即時版）
資料來源：公開 Google 試算表（網址見 SPREADSHEET_URL）
"""

import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 頁面設定
st.set_page_config(
    page_title="庫存管理系統 (雲端即時版)",
    page_icon="📦",
    layout="centered",
    initial_sidebar_state="expanded",
)

# 公開試算表連結（需設為「知道連結的使用者」可檢視）
SPREADSHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1LXz9pXppiDleyQhjiVBg6RUmFfqarM-R2LW9HUIWgtM/edit?usp=sharing"
)

# 只顯示試算表 A～D 欄（由左而右前四欄）
DISPLAY_COL_COUNT = 4
# 每幾秒重新抓取一次最新資料（連線快取）
CACHE_TTL_SECONDS = 60

# 查詢用的欄位名稱（需存在於上述四欄之一；表頭請與試算表一致）
PART_NUMBER_COLUMN = "零件編號"


def load_inventory():
    """從 Google 試算表讀取資料；失敗時回傳 None。"""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=SPREADSHEET_URL, ttl=CACHE_TTL_SECONDS)
    except Exception as e:
        st.error(f"讀取 Google 試算表時發生錯誤：{e}")
        return None

    if df is None or df.empty:
        return df

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()
    if df.shape[1] == 0:
        return df

    n = min(DISPLAY_COL_COUNT, df.shape[1])
    df = df.iloc[:, :n]
    return df


def main():
    st.title("📦 庫存管理系統 (雲端即時版)")
    st.markdown("---")

    df = load_inventory()

    if df is None:
        st.warning("無法載入庫存資料。")
        st.info(
            "請確認試算表已設為**知道連結的使用者可檢視**，且網路正常。"
            "若改為私人試算表，請改用 `.streamlit/secrets.toml` 的服務帳戶設定。"
        )
        return

    if df.empty:
        st.info("目前庫存清單為空。")
        return

    if df.shape[1] == 0:
        st.info("工作表沒有任何欄位。")
        return

    search_query = st.text_input("🔍 輸入零件編號查詢：", placeholder="留空則顯示全部")

    if PART_NUMBER_COLUMN in df.columns:
        search_col = PART_NUMBER_COLUMN
    else:
        search_col = df.columns[0]
        st.caption(
            f"試算表前四欄中找不到「{PART_NUMBER_COLUMN}」欄位，改以「{search_col}」查詢。"
        )

    if search_query and search_query.strip():
        mask = df[search_col].astype(str).str.contains(
            search_query.strip(), case=False, na=False
        )
        display_df = df[mask]
    else:
        display_df = df.copy()

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
    st.caption(
        "資料來源：Google 試算表（公開連結）｜"
        f"約每 {CACHE_TTL_SECONDS} 秒更新快取，或重新整理頁面"
    )


if __name__ == "__main__":
    main()
