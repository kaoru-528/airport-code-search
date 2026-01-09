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

# ISO国コードから日本語国名へのマッピング
COUNTRY_JP_MAP = {
    "AD": "アンドラ",
    "AE": "アラブ首長国連邦",
    "AF": "アフガニスタン",
    "AG": "アンティグア・バーブーダ",
    "AI": "アンギラ",
    "AL": "アルバニア",
    "AM": "アルメニア",
    "AO": "アンゴラ",
    "AQ": "南極",
    "AR": "アルゼンチン",
    "AS": "アメリカ領サモア",
    "AT": "オーストリア",
    "AU": "オーストラリア",
    "AW": "アルバ",
    "AX": "オーランド諸島",
    "AZ": "アゼルバイジャン",
    "BA": "ボスニア・ヘルツェゴビナ",
    "BB": "バルバドス",
    "BD": "バングラデシュ",
    "BE": "ベルギー",
    "BF": "ブルキナファソ",
    "BG": "ブルガリア",
    "BH": "バーレーン",
    "BI": "ブルンジ",
    "BJ": "ベナン",
    "BL": "サン・バルテルミー",
    "BM": "バミューダ",
    "BN": "ブルネイ",
    "BO": "ボリビア",
    "BQ": "カリブ・オランダ",
    "BR": "ブラジル",
    "BS": "バハマ",
    "BT": "ブータン",
    "BV": "ブーベ島",
    "BW": "ボツワナ",
    "BY": "ベラルーシ",
    "BZ": "ベリーズ",
    "CA": "カナダ",
    "CC": "ココス諸島",
    "CD": "コンゴ民主共和国",
    "CF": "中央アフリカ",
    "CG": "コンゴ共和国",
    "CH": "スイス",
    "CI": "コートジボワール",
    "CK": "クック諸島",
    "CL": "チリ",
    "CM": "カメルーン",
    "CN": "中国",
    "CO": "コロンビア",
    "CR": "コスタリカ",
    "CU": "キューバ",
    "CV": "カーボベルデ",
    "CW": "キュラソー",
    "CX": "クリスマス島",
    "CY": "キプロス",
    "CZ": "チェコ",
    "DE": "ドイツ",
    "DJ": "ジブチ",
    "DK": "デンマーク",
    "DM": "ドミニカ国",
    "DO": "ドミニカ共和国",
    "DZ": "アルジェリア",
    "EC": "エクアドル",
    "EE": "エストニア",
    "EG": "エジプト",
    "EH": "西サハラ",
    "ER": "エリトリア",
    "ES": "スペイン",
    "ET": "エチオピア",
    "FI": "フィンランド",
    "FJ": "フィジー",
    "FK": "フォークランド諸島",
    "FM": "ミクロネシア",
    "FO": "フェロー諸島",
    "FR": "フランス",
    "GA": "ガボン",
    "GB": "イギリス",
    "GD": "グレナダ",
    "GE": "ジョージア",
    "GF": "フランス領ギアナ",
    "GG": "ガーンジー",
    "GH": "ガーナ",
    "GI": "ジブラルタル",
    "GL": "グリーンランド",
    "GM": "ガンビア",
    "GN": "ギニア",
    "GP": "グアドループ",
    "GQ": "赤道ギニア",
    "GR": "ギリシャ",
    "GS": "サウスジョージア・サウスサンドウィッチ諸島",
    "GT": "グアテマラ",
    "GU": "グアム",
    "GW": "ギニアビサウ",
    "GY": "ガイアナ",
    "HK": "香港",
    "HM": "ハード島とマクドナルド諸島",
    "HN": "ホンジュラス",
    "HR": "クロアチア",
    "HT": "ハイチ",
    "HU": "ハンガリー",
    "ID": "インドネシア",
    "IE": "アイルランド",
    "IL": "イスラエル",
    "IM": "マン島",
    "IN": "インド",
    "IO": "イギリス領インド洋地域",
    "IQ": "イラク",
    "IR": "イラン",
    "IS": "アイスランド",
    "IT": "イタリア",
    "JE": "ジャージー",
    "JM": "ジャマイカ",
    "JO": "ヨルダン",
    "JP": "日本",
    "KE": "ケニア",
    "KG": "キルギス",
    "KH": "カンボジア",
    "KI": "キリバス",
    "KM": "コモロ",
    "KN": "セントクリストファー・ネイビス",
    "KP": "北朝鮮",
    "KR": "韓国",
    "KW": "クウェート",
    "KY": "ケイマン諸島",
    "KZ": "カザフスタン",
    "LA": "ラオス",
    "LB": "レバノン",
    "LC": "セントルシア",
    "LI": "リヒテンシュタイン",
    "LK": "スリランカ",
    "LR": "リベリア",
    "LS": "レソト",
    "LT": "リトアニア",
    "LU": "ルクセンブルク",
    "LV": "ラトビア",
    "LY": "リビア",
    "MA": "モロッコ",
    "MC": "モナコ",
    "MD": "モルドバ",
    "ME": "モンテネグロ",
    "MF": "サン・マルタン",
    "MG": "マダガスカル",
    "MH": "マーシャル諸島",
    "MK": "北マケドニア",
    "ML": "マリ",
    "MM": "ミャンマー",
    "MN": "モンゴル",
    "MO": "マカオ",
    "MP": "北マリアナ諸島",
    "MQ": "マルティニーク",
    "MR": "モーリタニア",
    "MS": "モントセラト",
    "MT": "マルタ",
    "MU": "モーリシャス",
    "MV": "モルディブ",
    "MW": "マラウイ",
    "MX": "メキシコ",
    "MY": "マレーシア",
    "MZ": "モザンビーク",
    "NA": "ナミビア",
    "NC": "ニューカレドニア",
    "NE": "ニジェール",
    "NF": "ノーフォーク島",
    "NG": "ナイジェリア",
    "NI": "ニカラグア",
    "NL": "オランダ",
    "NO": "ノルウェー",
    "NP": "ネパール",
    "NR": "ナウル",
    "NU": "ニウエ",
    "NZ": "ニュージーランド",
    "OM": "オマーン",
    "PA": "パナマ",
    "PE": "ペルー",
    "PF": "フランス領ポリネシア",
    "PG": "パプアニューギニア",
    "PH": "フィリピン",
    "PK": "パキスタン",
    "PL": "ポーランド",
    "PM": "サンピエール島・ミクロン島",
    "PN": "ピトケアン諸島",
    "PR": "プエルトリコ",
    "PS": "パレスチナ",
    "PT": "ポルトガル",
    "PW": "パラオ",
    "PY": "パラグアイ",
    "QA": "カタール",
    "RE": "レユニオン",
    "RO": "ルーマニア",
    "RS": "セルビア",
    "RU": "ロシア",
    "RW": "ルワンダ",
    "SA": "サウジアラビア",
    "SB": "ソロモン諸島",
    "SC": "セーシェル",
    "SD": "スーダン",
    "SE": "スウェーデン",
    "SG": "シンガポール",
    "SH": "セントヘレナ",
    "SI": "スロベニア",
    "SJ": "スヴァールバル諸島およびヤンマイエン島",
    "SK": "スロバキア",
    "SL": "シエラレオネ",
    "SM": "サンマリノ",
    "SN": "セネガル",
    "SO": "ソマリア",
    "SR": "スリナム",
    "SS": "南スーダン",
    "ST": "サントメ・プリンシペ",
    "SV": "エルサルバドル",
    "SX": "シント・マールテン",
    "SY": "シリア",
    "SZ": "エスワティニ",
    "TC": "タークス・カイコス諸島",
    "TD": "チャド",
    "TF": "フランス領南方・南極地域",
    "TG": "トーゴ",
    "TH": "タイ",
    "TJ": "タジキスタン",
    "TK": "トケラウ",
    "TL": "東ティモール",
    "TM": "トルクメニスタン",
    "TN": "チュニジア",
    "TO": "トンガ",
    "TR": "トルコ",
    "TT": "トリニダード・トバゴ",
    "TV": "ツバル",
    "TW": "台湾",
    "TZ": "タンザニア",
    "UA": "ウクライナ",
    "UG": "ウガンダ",
    "UM": "合衆国領有小離島",
    "US": "アメリカ",
    "UY": "ウルグアイ",
    "UZ": "ウズベキスタン",
    "VA": "バチカン",
    "VC": "セントビンセント・グレナディーン",
    "VE": "ベネズエラ",
    "VG": "イギリス領ヴァージン諸島",
    "VI": "アメリカ領ヴァージン諸島",
    "VN": "ベトナム",
    "VU": "バヌアツ",
    "WF": "ウォリス・フツナ",
    "WS": "サモア",
    "XK": "コソボ",
    "YE": "イエメン",
    "YT": "マヨット",
    "ZA": "南アフリカ",
    "ZM": "ザンビア",
    "ZW": "ジンバブエ",
}


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
        iso_country = row.get("iso_country", "")
        
        # country_jp: 既存データ優先、なければマッピングから取得
        country_jp = existing_airport.get("country_jp", "") or COUNTRY_JP_MAP.get(iso_country, "")
        
        airport = {
            "iata_code": iata_code,
            "name": row.get("name", ""),
            "municipality": row.get("municipality", ""),
            "iso_country": iso_country,
            "country_jp": country_jp,
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
