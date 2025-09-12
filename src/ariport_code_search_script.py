import sys
import json
import unicodedata

query = sys.argv[1]
normalized_query = unicodedata.normalize('NFC', query).lower()

results = []

# JSONファイルを読み込む
with open('airports.json', 'r', encoding='utf-8') as f:
    airports_data = json.load(f)

# ロードしたデータをループ処理
for airport in airports_data:
    search_target_raw = (
        f"{airport.get('name', '')} "
        f"{airport.get('municipality', '')} "
        f"{airport.get('country_jp', '')} "
        f"{airport.get('state_jp', '')} "
        f"{airport.get('city_jp', '')}"
    )

    normalized_search_target = unicodedata.normalize('NFC', search_target_raw).lower()

    if normalized_query in normalized_search_target:
        iata_code = airport.get('iata_code', '')
        iso_country = airport.get('iso_country', '') # 国コードを取得

        # サブタイトルを生成
        subtitle_parts = [part for part in [airport.get('city_jp'), airport.get('state_jp'), airport.get('country_jp')] if part]
        if subtitle_parts:
            subtitle = " - ".join(subtitle_parts)
        else:
            subtitle = f"{airport.get('municipality', '')}, {iso_country}"

        icon_path = f"flags/{iso_country}.png"

        item = {
            "uid": iata_code,
            "title": f"{airport.get('name', '')} ({iata_code})",
            "subtitle": subtitle,
            "arg": iata_code,
            "icon": {
                "path": icon_path
            }
        }
        results.append(item)

alfred_results = json.dumps({"items": results[:50]})
sys.stdout.write(alfred_results)