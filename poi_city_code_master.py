#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
・日本郵政の郵便番号マスター（utf_ken_all.csv）の 8 列目から
　郡名を含む市区町村名を抜き出す
・poi_city_code_master03.tsv.orig の 3 列目（郡名なし）と
　末尾一致させて郡名を付加する
・結果を poi_city_code_master03.tsv として出力する
"""
import pandas as pd
from pathlib import Path

UTF_PATH = Path("utf_ken_all.csv")
POI_PATH = Path("poi_city_code_master03.tsv.orig")
OUT_PATH = Path("poi_city_code_master03.tsv")      # 上書きしたい場合は .orig を外す

# ------------------------------------------------------------
# 1) 郡名付きマスタを作る
# ------------------------------------------------------------
# utf_ken_all.csv のカラム:
#  0: 団体コード, 1: 旧郵便番号, 2: 郵便番号, 3‑5: カナ,
#  6: 都道府県名, 7: 市区町村名, 8: 町域名, 9‑: 各種フラグ
cols_needed = [6, 7]                   # 6 = 都道府県, 7 = 市区町村 (郡名入り)
utf = pd.read_csv(
    UTF_PATH,
    header=None,
    usecols=cols_needed,
    dtype=str,
    encoding="utf-8",
)
utf.columns = ["pref", "full_name"]
utf = utf.drop_duplicates()

# 「郡XX町(村)」の末尾 (= 郡名を除いた町村名) をキーに辞書化
def strip_gun(name: str) -> str:
    """'石狩郡当別町' -> '当別町' など。'郡' が無ければそのまま返す。"""
    return name.split("郡", 1)[1] if "郡" in name else name

utf["plain_name"] = utf["full_name"].map(strip_gun)
mapping = dict(
    ((row.pref, row.plain_name), row.full_name) for row in utf.itertuples(index=False)
)

# ------------------------------------------------------------
# 2) 元 TSV を読み込み、3 列目を郡名付きで上書き
# ------------------------------------------------------------
poi = pd.read_csv(
    POI_PATH,
    sep="\t",
    header=None,
    names=["code", "pref", "town"],
    dtype={"code": str, "pref": str, "town": str},
)

def add_gun(row):
    return mapping.get((row.pref, row.town), row.town)   # ヒットしなければそのまま

poi["town"] = poi.apply(add_gun, axis=1)

# ------------------------------------------------------------
# 3) TSV で保存
# ------------------------------------------------------------
poi.to_csv(OUT_PATH, sep="\t", header=False, index=False, encoding="utf-8")
print(f"✅ 郡名付与済 TSV を出力しました → {OUT_PATH}")
