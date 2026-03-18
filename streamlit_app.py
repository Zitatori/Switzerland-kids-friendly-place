# streamlit_app.py
import streamlit as st
import pandas as pd
from data import load_places

st.set_page_config(page_title="Switzerland Kids-friendly Places", layout="wide")
st.title("🇨🇭 Kids-friendly Places（スイス）")
st.caption("DBと画像を1対1で突合（地図なし・カード表示）")

@st.cache_data
def load_df():
    return load_places()

df = load_df()
if df.empty:
    st.error("DBが空、またはテーブルが読み取れませんでした。kid_friendly_places.db / kid_friendly_places を確認してください。")
    st.stop()

# ------------ フィルタ ------------
with st.sidebar:
    st.header("フィルタ")
    cities = sorted([c for c in df["city"].dropna().unique().tolist() if c])
    city = st.selectbox("場所/エリア（location）", ["全部"] + cities, index=0)

    cats = sorted([c for c in df["category"].dropna().unique().tolist() if c])
    cat = st.selectbox("カテゴリ（category）", ["全部"] + cats, index=0)

    q = st.text_input("キーワード（name / comments / URLを含む場合はnoteに入れて）", "")

mask = pd.Series([True] * len(df))
if city != "全部":
    mask &= (df["city"] == city)
if cat != "全部":
    mask &= (df["category"] == cat)
if q.strip():
    ql = q.strip().lower()
    hay = (
        df["name"].astype(str).str.lower().fillna("")
        + " " + df["note"].astype(str).str.lower().fillna("")
        + " " + df["city"].astype(str).str.lower().fillna("")
        + " " + df["category"].astype(str).str.lower().fillna("")
    )
    mask &= hay.str.contains(ql)

view = df[mask].copy()
st.subheader(f"検索結果：{len(view)}件")

# ------------ カード描画（画像は DBのimage列ベースで厳密一致） ------------
def render_card(rec: dict):
    # 画像
    if rec.get("image_path"):
        st.image(rec["image_path"], use_container_width=True)
    else:
        st.write("🖼️ 画像なし（image列のファイルが見つかりません）")

    # タイトル
    st.markdown(f"**{rec.get('name') or 'No name'}**")

    # メタ
    meta = []
    if rec.get("city"): meta.append(f"📍 {rec['city']}")
    if rec.get("category"): meta.append(f"🏷️ {rec['category']}")
    if meta:
        st.caption(" ・ ".join(meta))

    # コメント
    if rec.get("note"):
        st.write(str(rec["note"])[:240])

cols_per_row = 2  # モバイルでも見やすい2列
records = view.to_dict(orient="records")

if not records:
    st.info("該当データがありません。フィルタを緩めてください。")
else:
    for i in range(0, len(records), cols_per_row):
        row = records[i:i+cols_per_row]
        cols = st.columns(len(row), gap="small")
        for c, r in zip(cols, row):
            with c:
                render_card(r)

st.caption("画像は DBの image 列をそのまま使います。`static/uploads/<image>` に置いてください。")
