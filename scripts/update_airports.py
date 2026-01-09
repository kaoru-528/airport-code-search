#!/usr/bin/env python3
"""
空港データ更新スクリプト

OurAirportsからCSVをダウンロードし、IATAコードを持つ空港のみを抽出して
airports.jsonを更新します。既存の日本語データ（country_jp, state_jp, city_jp）は保持されます。
"""

import csv
import json
import urllib.request
from pathlib import Path

AIRPORTS_CSV_URL = "https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airports.csv"
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
AIRPORTS_JSON_PATH = PROJECT_ROOT / "src" / "airports.json"


def download_csv(url: str) -> list[dict]:
    """URLからCSVをダウンロードしてリストとして返す"""
    with urllib.request.urlopen(url) as response:
        lines = response.read().decode("utf-8").splitlines()
        reader = csv.DictReader(lines)
        return list(reader)


def load_existing_airports() -> dict[str, dict]:
    """既存のairports.jsonを読み込み、IATAコードをキーとした辞書を返す"""
    if not AIRPORTS_JSON_PATH.exists():
        return {}
    
    with open(AIRPORTS_JSON_PATH, "r", encoding="utf-8") as f:
        airports = json.load(f)
    
    return {airport["iata_code"]: airport for airport in airports}


def convert_airports(csv_data: list[dict], existing: dict[str, dict]) -> list[dict]:
    """CSVデータを変換し、既存の日本語データをマージ"""
    airports = []
    
    for row in csv_data:
        iata_code = row.get("iata_code", "").strip()
        
        # IATAコードがない空港はスキップ
        if not iata_code:
            continue
        
        # 既存データから日本語フィールドを取得
        existing_airport = existing.get(iata_code, {})
        
        airport = {
            "iata_code": iata_code,
            "name": row.get("name", ""),
            "municipality": row.get("municipality", ""),
            "iso_country": row.get("iso_country", ""),
            "country_jp": existing_airport.get("country_jp", ""),
            "state_jp": existing_airport.get("state_jp", ""),
            "city_jp": existing_airport.get("city_jp", ""),
        }
        
        airports.append(airport)
    
    return airports


def main():
    print("Downloading airports.csv from OurAirports...")
    csv_data = download_csv(AIRPORTS_CSV_URL)
    print(f"Downloaded {len(csv_data)} airports from CSV")
    
    print("Loading existing airports.json...")
    existing = load_existing_airports()
    print(f"Loaded {len(existing)} existing airports")
    
    print("Converting and merging data...")
    airports = convert_airports(csv_data, existing)
    print(f"Processed {len(airports)} airports with IATA codes")
    
    # JSONを保存
    with open(AIRPORTS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(airports, f, ensure_ascii=False, indent=2)
    
    print(f"Saved to {AIRPORTS_JSON_PATH}")


if __name__ == "__main__":
    main()
