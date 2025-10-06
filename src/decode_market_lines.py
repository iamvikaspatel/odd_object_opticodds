import base64, zlib, re, struct
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime


# =====================================================
# 🔹 Utility — Locate Latest File
# =====================================================
def get_latest_file(path: Path, pattern: str):
    """Return latest file matching a pattern (e.g., startswith)."""
    try:
        files = [f for f in path.glob(pattern) if f.is_file()]
        if not files:
            return None
        return max(files, key=lambda f: f.stat().st_mtime)
    except Exception as e:
        print(f"❌ Error scanning files: {e}")
        return None


# =====================================================
# 🔹 Decode a Single markets64 String
# =====================================================
def decode_market64(encoded_market64):
    """Decode a single markets64 string and extract numeric_id, final_line, top_values."""
    if not encoded_market64 or not isinstance(encoded_market64, str):
        return pd.DataFrame()

    try:
        decoded = base64.b64decode(encoded_market64)
        try:
            data = zlib.decompress(decoded)
        except zlib.error:
            data = decoded
    except Exception:
        return pd.DataFrame()

    cat_positions = [
        (m.start(), m.group())
        for m in re.finditer(rb'Z2lkOi8vaHMzL0NhdGVnb3J5Lz[A-Za-z0-9+/=]+', data)
    ]
    if not cat_positions:
        return pd.DataFrame()

    records = []
    for i, (pos, cat_bytes) in enumerate(cat_positions):
        next_pos = cat_positions[i + 1][0] if i + 1 < len(cat_positions) else len(data)
        window = data[pos:next_pos]

        vals = []
        for j in range(0, len(window) - 4, 4):
            try:
                v = struct.unpack("<f", window[j:j + 4])[0]
                if 0.3 <= abs(v) <= 400:
                    vals.append(round(v, 2))
            except Exception:
                pass

        cat_raw = cat_bytes.decode()
        padded = cat_raw + "=" * (-len(cat_raw) % 4)
        try:
            cat_decoded = base64.b64decode(padded).decode()
        except Exception:
            cat_decoded = "(invalid)"
        num_id = re.findall(r'/Category/(\d+)', cat_decoded)
        num_id = num_id[0] if num_id else None

        # Normalize numeric values
        top_vals = sorted(vals, reverse=True)[:3]
        norm_vals = []
        for v in top_vals:
            if v > 100:
                norm_vals.append(v)
            elif 10 <= v <= 100:
                norm_vals.append(round(v / 3.5, 2))
            else:
                norm_vals.append(v)
        avg_val = np.mean(norm_vals) if norm_vals else None

        records.append({
            "numeric_id": num_id,
            "final_line": round(avg_val, 2) if avg_val else None,
            "top_values": norm_vals
        })

    return pd.DataFrame(records)


# =====================================================
# 🔹 Decode All Players
# =====================================================
def decode_all_players(df_merged, df_markets):
    """Decode markets64 for all players and merge with category mapping."""
    decoded_results = []

    for player in df_merged["fullName"].unique():
        try:
            encoded_market64 = df_markets.loc[df_markets["fullName"] == player, "markets64"].iloc[0]
        except IndexError:
            print(f"⚠️ No markets64 found for {player}")
            continue

        print(f"🔍 Decoding {player} ...")
        df_decoded = decode_market64(encoded_market64)
        if df_decoded.empty:
            print(f"⚠️ No decodable data for {player}")
            continue
        df_decoded["fullName"] = player
        decoded_results.append(df_decoded)

    if not decoded_results:
        print("⚠️ No decoded results generated.")
        return pd.DataFrame()

    df_lines = pd.concat(decoded_results, ignore_index=True)

    # ✅ Fix: Ensure consistent merge key type
    df_merged["numeric_id"] = df_merged["numeric_id"].astype(str)
    df_lines["numeric_id"] = df_lines["numeric_id"].astype(str)

    # --- Merge Data ---
    df_final = df_merged.merge(
        df_lines,
        how="left",
        on=["fullName", "numeric_id"]
    )[
        ["fullName", "raw", "numeric_id", "category_name", "group", "sport", "final_line", "top_values"]
    ]

    print(f"✅ Created final dataframe with {len(df_final)} rows.")
    return df_final


# =====================================================
# 🔹 Main Runner
# =====================================================
def run_marketline_decoding():
    """Full pipeline: load, decode, merge, save."""
    merged_dir = Path("data/processed")
    odds_dir = Path("data/raw/odds")

    latest_merged = get_latest_file(merged_dir, "player_category_map_*.json")
    latest_odds_folder = max([d for d in odds_dir.iterdir() if d.is_dir()], key=lambda d: d.stat().st_mtime, default=None)

    if not latest_merged or not latest_odds_folder:
        print("❌ Missing required data files. Run previous pipelines first.")
        return

    markets_file = latest_odds_folder / "odds_markets_raw.json"
    print(f"📂 Using:\n  Merged → {latest_merged}\n  Markets → {markets_file}")

    try:
        df_merged = pd.read_json(latest_merged)
        df_markets = pd.read_json(markets_file)
    except Exception as e:
        print(f"❌ Error reading JSON files: {e}")
        return

    df_final = decode_all_players(df_merged, df_markets)
    if df_final.empty:
        print("⚠️ No decoded lines to save.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = Path("data/odd_object")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"player_lines_final_{timestamp}.json"
    # --- Transform to user requested schema ---
    # Desired fields: id, market, player_name, decimal_odds
    def map_market(category_name, group_name):
        if not category_name:
            return None
        cn = category_name.lower()
        gn = (group_name or "").lower()
        # Heuristics to map various category names to canonical market types
        if "points" in cn or "pts" in cn or "points" in gn:
            return "player_points"
        if "total" in cn or "over" in cn or "under" in cn or "total" in gn:
            return "team_total"
        if "money" in cn or "moneyline" in cn or "ml" in cn:
            return "moneyline"
        # fallback: slugify the category name
        return cn.replace(" ", "_")

    def pick_decimal_odds(top_values, final_line):
        # Prefer the first top_value if it's a numeric (already decimal odds)
        try:
            if isinstance(top_values, (list, tuple)) and len(top_values) > 0:
                v = top_values[0]
                return float(v) if v is not None else None
            # Fallback: if final_line looks like an odds value, return it
            if final_line is not None:
                return float(final_line)
        except Exception:
            return None
        return None

    # Ensure required columns exist
    for c in ["numeric_id", "category_name", "group", "fullName", "final_line", "top_values"]:
        if c not in df_final.columns:
            df_final[c] = None

    # Build unique id as "raw-numeric_id". Fall back to whichever part exists.
    def build_unique_id(row):
        raw = row.get("raw")
        nid = row.get("numeric_id")
        # normalize strings
        raw = None if (pd.isna(raw) or raw is None or str(raw).strip() == "") else str(raw)
        nid = None if (pd.isna(nid) or nid is None or str(nid).strip() == "" or str(nid) == "nan") else str(nid)
        if raw and nid:
            return f"{raw}-{nid}"
        if raw:
            return raw
        if nid:
            return nid
        return None

    df_final["id"] = df_final.apply(build_unique_id, axis=1)
    df_final["market"] = df_final.apply(lambda r: map_market(r.get("category_name"), r.get("group")), axis=1)
    df_final["player_name"] = df_final.get("fullName")
    df_final["decimal_odds"] = df_final.apply(lambda r: pick_decimal_odds(r.get("top_values"), r.get("final_line")), axis=1)

    df_out = df_final[["id", "market", "player_name", "decimal_odds"]].copy()

    try:
        df_out.to_json(output_path, orient='records', indent=2)
        print(f"📁 Final decoded lines (requested schema) saved → {output_path}")
    except Exception as e:
        print(f"❌ Failed to save decoded file: {e}")


# =====================================================
# 🔹 Entry Point
# =====================================================
if __name__ == "__main__":
    run_marketline_decoding()
