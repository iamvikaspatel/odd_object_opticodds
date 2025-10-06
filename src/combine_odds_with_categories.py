import pandas as pd
from pathlib import Path
from datetime import datetime


# =====================================================
# 🔹 Utility — Find Latest Subfolder
# =====================================================
def get_latest_subdir(path: Path):
    """Return the newest subdirectory in a given path."""
    try:
        subdirs = [d for d in path.iterdir() if d.is_dir()]
        if not subdirs:
            return None
        return max(subdirs, key=lambda d: d.stat().st_mtime)
    except Exception as e:
        print(f"❌ Error while locating subfolders: {e}")
        return None


# =====================================================
# 🔹 Combine Odds + Category Names
# =====================================================
def combine_odds_with_categories():
    """Merge decoded odds with category name data and save with timestamp."""
    odds_root = Path("data/raw/odds")
    categories_root = Path("data/raw/category_names")

    latest_odds = get_latest_subdir(odds_root)
    latest_categories = get_latest_subdir(categories_root)

    if not latest_odds or not latest_categories:
        print("❌ Missing odds or category data folder. Please run both pipelines first.")
        return

    odds_file = latest_odds / "odds_categories_decoded.csv"
    categories_file = latest_categories / "category_names_raw.csv"

    print(f"📂 Using:\n  Odds → {odds_file}\n  Categories → {categories_file}")

    # --- Read CSVs Safely ---
    try:
        df_odds = pd.read_csv(odds_file)
        df_categories = pd.read_csv(categories_file)
    except Exception as e:
        print(f"❌ Error reading one of the CSVs: {e}")
        return

    if df_odds.empty or df_categories.empty:
        print("⚠️ One or both CSVs are empty. Skipping merge.")
        return

    # --- Merge Data ---
    try:
        df_merged = df_odds.merge(
            df_categories,
            how="left",
            left_on="raw",
            right_on="category_id"
        )[
            ["fullName", "raw", "decoded", "numeric_id", "category_name", "group", "sport"]
        ]

        print(f"✅ Successfully merged {len(df_merged)} rows.")
    except Exception as e:
        print(f"❌ Error during merge: {e}")
        return

    # --- Save to Processed Folder ---
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"player_category_map_{timestamp}.csv"

    try:
        df_merged.to_csv(output_path, index=False)
        print(f"📁 Merged data saved → {output_path}")
    except Exception as e:
        print(f"❌ Failed to save merged file: {e}")

    return df_merged


# =====================================================
# 🔹 Run Script
# =====================================================
if __name__ == "__main__":
    combine_odds_with_categories()
