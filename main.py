import sys
import shutil
from pathlib import Path
from datetime import datetime

# --- Import modular scripts ---
from src.fetch_odds_info import run_odds_pipeline
from src.fetch_category_names import run_category_names_pipeline
from src.combine_odds_with_categories import combine_odds_with_categories
from src.decode_market_lines import run_marketline_decoding


# =====================================================
# 🔹 Utility: Print Banners and Logs
# =====================================================
def print_banner(title: str):
    print("\n" + "=" * 80)
    print(f"🧩 {title}")
    print("=" * 80)


def log(msg: str, status="info"):
    icons = {"info": "🔹", "success": "✅", "warning": "⚠️", "error": "❌"}
    print(f"{icons.get(status, '🔹')} {msg}")


# =====================================================
# 🔹 Validate Folder Structure
# =====================================================
def validate_project_structure():
    """Ensure required folders exist."""
    base_dirs = [
        "data/raw/odds",
        "data/raw/category_names",
        "data/processed",
        "odd_object"  # ✅ Final output folder
    ]
    for d in base_dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    log("✅ Folder structure validated.", "success")


# =====================================================
# 🔹 Move Final Decoded File to odd_object/
# =====================================================
def move_final_output():
    """Move the most recent 'player_lines_final_' file into odd_object/."""
    processed_dir = Path("data/processed")
    odd_object_dir = Path("odd_object")
    odd_object_dir.mkdir(parents=True, exist_ok=True)

    final_files = sorted(processed_dir.glob("player_lines_final_*.csv"), key=lambda f: f.stat().st_mtime, reverse=True)
    if not final_files:
        log("⚠️ No final decoded file found in processed folder.", "warning")
        return

    latest_file = final_files[0]
    destination = odd_object_dir / latest_file.name

    try:
        shutil.copy2(latest_file, destination)
        log(f"📦 Copied final file → {destination}", "success")
    except Exception as e:
        log(f"❌ Failed to copy final file: {e}", "error")


# =====================================================
# 🔹 Full ETL Orchestrator
# =====================================================
def main():
    start_time = datetime.now()
    print_banner("🔥 Starting HotStreak Full Data Pipeline 🔥")

    validate_project_structure()

    # --- Step 1: Fetch Odds ---
    try:
        print_banner("STEP 1️⃣  - Fetching Odds Data")
        run_odds_pipeline()
        log("Odds data fetched and saved successfully.", "success")
    except Exception as e:
        log(f"Odds fetch failed: {e}", "error")
        sys.exit(1)

    # --- Step 2: Fetch Category Names ---
    try:
        print_banner("STEP 2️⃣  - Fetching Category Name Data")
        run_category_names_pipeline()
        log("Category name data fetched and saved successfully.", "success")
    except Exception as e:
        log(f"Category name fetch failed: {e}", "error")
        sys.exit(1)

    # --- Step 3: Combine Odds + Categories ---
    try:
        print_banner("STEP 3️⃣  - Merging Odds and Category Names")
        combine_odds_with_categories()
        log("Merged odds and category name data successfully.", "success")
    except Exception as e:
        log(f"Combine step failed: {e}", "error")
        sys.exit(1)

    # --- Step 4: Decode Market Lines ---
    try:
        print_banner("STEP 4️⃣  - Decoding Market Lines")
        run_marketline_decoding()
        log("Market lines decoded successfully.", "success")
    except Exception as e:
        log(f"Market line decoding failed: {e}", "error")
        sys.exit(1)

    # --- Step 5: Move Final File to odd_object ---
    print_banner("STEP 5️⃣  - Moving Final File to odd_object/")
    move_final_output()

    # --- Done ---
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print_banner("🏁 PIPELINE COMPLETE")
    log(f"All tasks finished successfully in {duration:.2f} seconds.", "success")


# =====================================================
# 🔹 Entry Point
# =====================================================
if __name__ == "__main__":
    main()
