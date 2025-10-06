from curl_cffi import requests
import pandas as pd
from pathlib import Path
from datetime import datetime


# =====================================================
# 🔹 Configuration
# =====================================================
API_URL = (
    "https://api3.hotstreak.gg/graphql?"
    "query=query+system+%7B+system+%7B+__typename+defaultMargin+maxLegsPerBet+maxMultiplier+"
    "pusherCluster+pusherKey+sports+%7B+__typename+id+categories+%7B+__typename+id+createdAt+"
    "generatedAt+groupName+name+ordinality+updatedAt+%7D+name+%7D+%7D+%7D&variables=%7B%7D&operationName=system"
)

HEADERS = {
    "accept": "application/graphql-response+json, application/json",
    "origin": "https://hs3.hotstreak.gg",
    "referer": "https://hs3.hotstreak.gg/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "x-hs3-version": "2",
    "x-requested-with": "web",
    "privy-id-token": "YOUR_VALID_TOKEN_HERE"  # 🔐 Replace with valid token
}


# =====================================================
# 1️⃣ --- Fetch and Parse Categories ---
# =====================================================
def fetch_category_names():
    """Fetch all sports and category names from the HotStreak system endpoint."""
    print("🚀 Fetching category name data...")

    try:
        response = requests.get(API_URL, headers=HEADERS, impersonate="chrome", timeout=20)
        response.raise_for_status()
        data = response.json()
    except requests.RequestsError as e:
        print(f"❌ Network error: {e}")
        return pd.DataFrame()
    except ValueError:
        print("❌ Invalid JSON response.")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Unexpected error fetching category names: {e}")
        return pd.DataFrame()

    # Extract sports safely
    system_data = data.get("data", {}).get("system", {})
    sports = system_data.get("sports", [])
    if not sports:
        print("⚠️ No sports data found in system response.")
        return pd.DataFrame()

    records = []
    for sport in sports:
        sport_name = sport.get("name", "Unknown")
        for cat in sport.get("categories", []):
            records.append({
                "category_id": cat.get("id"),
                "category_name": cat.get("name", "Unnamed Category"),
                "group": cat.get("groupName", "Unknown"),
                "sport": sport_name
            })

    df = pd.DataFrame(records)
    if df.empty:
        print("⚠️ No categories found in parsed data.")
    else:
        print(f"✅ Loaded {len(df)} categories across {df['sport'].nunique()} sports.")
    return df


# =====================================================
# 2️⃣ --- Save to Timestamped Folder ---
# =====================================================
def save_category_data(df_categories):
    """Save categories DataFrame to timestamped folder."""
    if df_categories.empty:
        print("⚠️ No category data to save.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = Path(f"data/raw/category_names/{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "category_names_raw.csv"

    try:
        df_categories.to_csv(output_file, index=False)
        print(f"📁 Saved category names to {output_file}")
    except Exception as e:
        print(f"❌ Failed to save category names CSV: {e}")


# =====================================================
# 3️⃣ --- Main Runner ---
# =====================================================
def run_category_names_pipeline():
    """Full pipeline: fetch + save category names."""
    df_categories = fetch_category_names()
    save_category_data(df_categories)
    print("✅ Category name pipeline completed successfully.")


# =====================================================
# 🔹 Entry Point
# =====================================================
if __name__ == "__main__":
    run_category_names_pipeline()
