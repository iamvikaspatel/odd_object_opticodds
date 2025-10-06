# 🧩 HotStreak Sports Odds Data Pipeline

A **fully automated Python ETL pipeline** that fetches, decodes, and structures **sports betting odds data** from the **HotStreak GraphQL API**.
The pipeline extracts encoded `markets64` payloads, decodes market lines, maps them with sports categories, and produces clean **JSON outputs** for analytics or downstream integration.

---

## 📁 Project Overview

| Stage                        | Script                            | Description                                                                                       |
| ---------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------- |
| **1️⃣ Fetch Odds Data**      | `fetch_odds_info.py`              | Queries the HotStreak GraphQL API for player markets (encoded `markets64`)                        |
| **2️⃣ Fetch Category Names** | `fetch_category_names.py`         | Retrieves sport and category metadata (category name, group, sport)                               |
| **3️⃣ Combine Data**         | `combine_odds_with_categories.py` | Merges decoded market IDs with category metadata                                                  |
| **4️⃣ Decode Market Lines**  | `decode_market_lines.py`          | Decompresses `markets64` payloads, extracts numeric odds, and normalizes lines                    |
| **5️⃣ Run Full Pipeline**    | `main.py`                         | Orchestrates the entire ETL workflow with logs, structure validation, and final output generation |

---

## ⚙️ Features

* 🔄 **Automated ETL Pipeline** — Fetch, decode, and process HotStreak betting data in one command
* 🔓 **Base64 + zlib Decoding** — Handles compressed `markets64` payloads and extracts valid category identifiers
* 📊 **Odds Mapping** — Links raw categories to readable names and groups (e.g., *Passing Yards*, *Rushing TDs*)
* 🧠 **Market Line Normalization** — Converts binary-decoded floats into usable decimal odds
* 💾 **Versioned Data Storage** — Saves all data with timestamped folders for reproducibility
* 🧩 **Final JSON Output Schema** —

  ```json
  [
    {
      "id": "Z2lkOi8vaHMzL0NhdGVnb3J5Lzc0-74",
      "market": "rushing_yards",
      "player_name": "Patrick Mahomes",
      "decimal_odds": 1.94
    }
  ]
  ```

---

## 🏗️ Project Structure

```
HotStreak-Odds-Pipeline/
│
├── src/
│   ├── fetch_odds_info.py
│   ├── fetch_category_names.py
│   ├── combine_odds_with_categories.py
│   ├── decode_market_lines.py
│
├── data/
│   ├── raw/
│   │   ├── odds/
│   │   └── category_names/
│   ├── processed/
│   └── odd_object/
│
├── odd_object/
│   └── player_lines_final_<timestamp>.json
│
├── main.py
└── README.md
```

---

## 🚀 How It Works

### 🧩 Step 1 — Fetch Odds Data (`fetch_odds_info.py`)

* Calls the HotStreak GraphQL API
* Retrieves encoded `markets64` for each active player
* Decodes and extracts category identifiers
* Saves to `data/raw/odds/<timestamp>/`

Output:

```json
[
  { "fullName": "Patrick Mahomes", "markets64": "eJzj..." }
]
```

---

### 🧩 Step 2 — Fetch Category Metadata (`fetch_category_names.py`)

* Extracts category names, groups, and sport mappings
* Saves to `data/raw/category_names/<timestamp>/`

Output:

```json
[
  { "category_id": "Z2lkOi8vaHMzL0NhdGVnb3J5Lzc0", "category_name": "Rushing yards", "group": "offense", "sport": "Football" }
]
```

---

### 🧩 Step 3 — Combine Data (`combine_odds_with_categories.py`)

* Joins decoded category IDs with category names
* Produces a player–category mapping
* Saves merged JSON to `data/processed/player_category_map_<timestamp>.json`

Output Columns:
`[fullName, raw, decoded, numeric_id, category_name, group, sport]`

---

### 🧩 Step 4 — Decode Market Lines (`decode_market_lines.py`)

* Decodes compressed binary odds data
* Extracts floating-point numbers from binary buffers
* Normalizes “top values” and computes average odds
* Saves clean dataset to `data/odd_object/player_lines_final_<timestamp>.json`

Output Columns:
`[player_name, category_name, group, sport, final_line, top_values]`

---

### 🧩 Step 5 — Full Orchestration (`main.py`)

Runs the full pipeline sequentially:

```
1️⃣ Fetch Odds Data
2️⃣ Fetch Category Names
3️⃣ Merge Categories
4️⃣ Decode Market Lines
5️⃣ Copy Final JSON → /odd_object/
```

Console Example:

```
================================================================================
🧩 🔥 Starting HotStreak Full Data Pipeline 🔥
================================================================================
✅ Folder structure validated.
🚀 Fetching HotStreak odds data...
✅ Extracted 38 players with markets64 data.
✅ Combined 353 category records from 38 players.
📁 Saved data to data/raw/odds/2025-10-06_11-34-15
...
🏁 PIPELINE COMPLETE
✅ All tasks finished successfully in 42.6 seconds.
```

---

## 📦 Output Example

Example of final JSON output (`player_lines_final_2025-10-06_11-34-15.json`):

```json
[
  {
    "id":"Z2lkOi8vaHMzL0NhdGVnb3J5Lzc0-74",
    "market":"rushing_yards",
    "player_name":"Patrick Mahomes",
    "decimal_odds":384.0
  },
  {
    "id":"Z2lkOi8vaHMzL0NhdGVnb3J5Lzc1-75",
    "market":"rushing_tds",
    "player_name":"Patrick Mahomes",
    "decimal_odds":1.94
  },
  {
    "id":"Z2lkOi8vaHMzL0NhdGVnb3J5Lzc2-76",
    "market":"interceptions_thrown",
    "player_name":"Patrick Mahomes",
    "decimal_odds":1.94
  }
]
```

---

## 🧠 Technical Highlights

| Technique                     | Description                                                     |
| ----------------------------- | --------------------------------------------------------------- |
| **GraphQL Querying**          | Uses parameterized queries to extract player and system data    |
| **Data Decoding**             | Decodes zlib-compressed Base64 payloads into binary streams     |
| **Pattern Extraction**        | Regex-driven category parsing (`Z2lkOi8vaHMzL0NhdGVnb3J5Lz...`) |
| **Dynamic Folder Versioning** | Automatically timestamps and saves each pipeline run            |
| **Robust Error Handling**     | Graceful fallback for failed API or file operations             |

---

## 🧰 Installation & Usage

### Prerequisites

* Python **3.9+**
* Dependencies:

  ```bash
  pip install pandas curl_cffi numpy
  ```

### Run Full Pipeline

```bash
python main.py
```

> ⚠️ Replace `privy-id-token` inside both `fetch_odds_info.py` and `fetch_category_names.py` with a valid HotStreak authentication token.

---

## 📈 Data Flow Summary

```
HotStreak API
   │
   ├──► fetch_odds_info.py         →  markets64 odds
   ├──► fetch_category_names.py    →  category metadata
   ├──► combine_odds_with_categories.py
   │        └─ merges categories with decoded IDs
   ├──► decode_market_lines.py
   │        └─ extracts numeric lines, top odds, and averages
   └──► main.py                    →  orchestrates entire process
```
---

## 🚀 Future Improvements (Advanced Implementation)

* 🧩 **Odds–Match UI Display** – Develop a visual dashboard that mirrors HotStreak’s live odds interface, displaying real-time player and match data.
* ⚡ **Real-Time Updates** – Integrate WebSocket or Pusher subscriptions to automatically refresh odds and match statuses.
* 🧠 **Smart Scraping Engine** – Add asynchronous or batched API calls for faster, more efficient data collection across multiple sports.
* 🔄 **Data Flow Intelligence** – Map dependencies between matches, odds, and categories to reflect the platform’s internal data flow more accurately.
* 🛡️ **Performance Optimization** – Implement caching, retry logic, and parallel decoding to improve scalability and reliability for high-volume use.


---
