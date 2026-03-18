# data.py
import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional

DB_PATH = "kid_friendly_places.db"
TABLE = "kid_friendly_places"
IMG_DIR = Path("static/uploads")

def _conn():
    return sqlite3.connect(DB_PATH)

def _resolve_image_path(name_in_db: Optional[str]) -> Optional[str]:
    """DBのimage列（例: 'banner-monstrofun.jpg'）を static/uploads 配下の実ファイルに解決"""
    if not name_in_db:
        return None
    name_in_db = str(name_in_db).strip()
    p = Path(name_in_db)
    # 絶対/相対の両対応（相対なら uploads 配下を見る）
    if not p.is_absolute():
        p = IMG_DIR / name_in_db
    if p.exists():
        return str(p)
    # サブディレクトリを含めてラフに探索（拡張子違い事故の回避はしない＝厳密一致）
    candidates = list(IMG_DIR.rglob(Path(name_in_db).name))
    if candidates:
        return str(candidates[0])
    return None

def load_places() -> pd.DataFrame:
    with _conn() as con:
        df = pd.read_sql_query(f"SELECT * FROM {TABLE};", con)

    # 列名をあなたのスキーマに合わせて正規化
    # id, name, category, location, ... , comments, image
    df_out = pd.DataFrame()
    df_out["id"] = df.get("id")
    df_out["name"] = df.get("name")
    df_out["city"] = df.get("location")  # 都市/場所名はlocation列
    df_out["category"] = df.get("category")
    df_out["note"] = df.get("comments")

    # 画像の完全一致（DBのimage列をそのまま使う）
    df_out["image_path"] = df.get("image").apply(_resolve_image_path) if "image" in df.columns else None

    # 参考: レーティング等（必要になったらUIで使えるよう保持）
    keep_cols = [
        "has_kids_area", "has_diaper_facility", "indoor", "travel_time_minutes",
        "crowd_rating", "rain_friendly", "friendly_rating", "safety_rating", "cleanliness_rating"
    ]
    for c in keep_cols:
        if c in df.columns:
            df_out[c] = df[c]

    # 欠損の最低限ケア
    df_out["category"] = df_out["category"].fillna("未分類")
    df_out["city"] = df_out["city"].fillna("不明")

    return df_out
