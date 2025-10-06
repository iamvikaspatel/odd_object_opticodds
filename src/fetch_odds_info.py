from curl_cffi import requests
import base64
import zlib
import re
import pandas as pd
from datetime import datetime
from pathlib import Path


# =====================================================
# 🔹 Configuration
# =====================================================
API_URL = "https://api3.hotstreak.gg/graphql"
HEADERS = {
    'accept': 'application/graphql-response+json, application/json',
    'origin': 'https://hs3.hotstreak.gg',
    'referer': 'https://hs3.hotstreak.gg/',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
    'x-hs3-version': '2',
    'x-requested-with': 'web',
    'privy-id-token': 'YOUR_TOKEN_HERE'  # 🔐 Replace with active token
}


# =====================================================
# 1️⃣ --- Fetch Odds Info ---
# =====================================================
def fetch_odds_info():
    """Fetch odds info and return DataFrame with player name + markets64"""
    query_odds = """
    query search($query: String, $page: Int, $filters: SearchFilterInput) {
      search(query: $query, page: $page, filters: $filters) {
        results {
          markets64
          participant {
            player {
              firstName
              fullName
            }
          }
        }
      }
    }
    """

    variables_odds = {
        "filters": {
            "activeMarketsOnly": True,
            "sport": "Z2lkOi8vaHMzL1Nwb3J0LzI"  # Football
        }
    }

    payload = {
        "query": query_odds,
        "variables": variables_odds,
        "operationName": "search"
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, impersonate="chrome", timeout=20)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Error fetching odds info: {e}")
        return pd.DataFrame()

    results = data.get("data", {}).get("search", {}).get("results", [])
    if not results:
        print("⚠️ No results found in API response.")
        return pd.DataFrame()

    records = []
    for r in results:
        player = r.get("participant", {}).get("player", {}) or {}
        first_name = player.get("firstName", "Unknown")
        full_name = player.get("fullName", "Unknown")
        markets64 = r.get("markets64", "")
        if markets64:
            records.append({
                "firstName": first_name,
                "fullName": full_name,
                "markets64": markets64
            })

    df = pd.DataFrame(records)
    print(f"✅ Extracted {len(df)} players with markets64 data.")
    return df


# =====================================================
# 2️⃣ --- Decode + Extract Categories ---
# =====================================================
def fix_base64_padding(s: str) -> str:
    """Ensures Base64 string has valid padding."""
    return s + "=" * (-len(s) % 4)


def decode_markets64_and_extract_categories(encoded_market64):
    """Decode one markets64 string and extract all category IDs."""
    if not encoded_market64:
        return []

    try:
        decoded = base64.b64decode(encoded_market64)
        try:
            decompressed = zlib.decompress(decoded)
        except:
            decompressed = decoded
    except Exception:
        return []

    category_ids = re.findall(rb'Z2lkOi8vaHMzL0NhdGVnb3J5Lz[A-Za-z0-9+/=]+', decompressed)
    category_ids = [cid.decode(errors="ignore") for cid in category_ids]

    decoded_rows = []
    for cid in sorted(set(category_ids)):
        padded = fix_base64_padding(cid)
        try:
            decoded_val = base64.b64decode(padded).decode()
        except Exception:
            decoded_val = "(invalid base64)"
        numeric_id = re.search(r'/Category/(\d+)', decoded_val)
        decoded_rows.append({
            "raw": cid,
            "decoded": decoded_val,
            "numeric_id": numeric_id.group(1) if numeric_id else None
        })
    return decoded_rows


def build_category_dataframe(df_markets):
    """Decode all player markets64 values into a combined category DataFrame."""
    if df_markets.empty:
        print("⚠️ No odds info available to decode.")
        return pd.DataFrame()

    all_records = []
    for _, row in df_markets.iterrows():
        player = row.get("fullName") or row.get("firstName") or "Unknown"
        encoded_market64 = row.get("markets64", "")
        if not encoded_market64:
            continue

        decoded_rows = decode_markets64_and_extract_categories(encoded_market64)
        for r in decoded_rows:
            all_records.append({
                "fullName": player,
                "raw": r["raw"],
                "decoded": r["decoded"],
                "numeric_id": r["numeric_id"]
            })

    df_combined = pd.DataFrame(all_records)
    print(f"✅ Combined {len(df_combined)} category records from {len(df_markets)} players.")
    return df_combined


# =====================================================
# 3️⃣ --- Save Results ---
# =====================================================
def save_odds_data(df_markets, df_all_categories):
    """Save both market and decoded data with timestamped folders."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_dir = Path(f"data/raw/odds/{timestamp}")
    base_dir.mkdir(parents=True, exist_ok=True)

    try:
        df_markets.to_csv(base_dir / "odds_markets_raw.csv", index=False)
        df_all_categories.to_csv(base_dir / "odds_categories_decoded.csv", index=False)
        print(f"📁 Saved data to {base_dir}")
    except Exception as e:
        print(f"❌ Failed to save CSVs: {e}")


# =====================================================
# 4️⃣ --- Main Runner ---
# =====================================================
def run_odds_pipeline():
    """Complete odds fetching + decoding pipeline."""
    print("🚀 Fetching HotStreak odds data...")
    df_markets = fetch_odds_info()

    if df_markets.empty:
        print("⚠️ No odds data to process. Exiting.")
        return

    df_all_categories = build_category_dataframe(df_markets)
    save_odds_data(df_markets, df_all_categories)
    print("✅ Odds pipeline completed successfully.")


# =====================================================
# 🔹 Entry Point
# =====================================================
if __name__ == "__main__":
    run_odds_pipeline()
