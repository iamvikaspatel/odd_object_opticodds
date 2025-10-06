# 🎯 OpticOdds - HotStreak Data Pipeline

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive data pipeline for fetching, decoding, and processing sports betting odds data from HotStreak API. This project automatically retrieves player odds, decodes market lines, and combines them with category information to produce analysis-ready datasets.

---

## 📋 Table of Contents

- [Features](#-features)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Pipeline Workflow](#-pipeline-workflow)
- [Data Output](#-data-output)
- [API Documentation](#-api-documentation)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Features

- 🔄 **Automated Data Fetching**: Retrieves odds and category data from HotStreak GraphQL API
- 🔓 **Market Decoding**: Decodes base64-encoded market data with zlib decompression
- 📊 **Data Processing**: Combines and transforms raw data into structured formats
- 🗂️ **Organized Storage**: Timestamped data organization for version control
- 🎯 **Player-Level Analysis**: Extracts player-specific betting lines and odds
- 🏷️ **Category Mapping**: Maps numerical category IDs to human-readable names
- 🔍 **Comprehensive Logging**: Detailed status updates throughout the pipeline

---

## 📁 Project Structure

```
z-odd-object/
├── main.py                          # Main pipeline orchestrator
├── README.md                        # This file
├── requirements.txt                 # Python dependencies (to be created)
├── .gitignore                      # Git ignore file (recommended)
│
├── src/                            # Source code modules
│   ├── fetch_odds_info.py          # Fetches player odds data
│   ├── fetch_category_names.py     # Fetches category definitions
│   ├── combine_odds_with_categories.py  # Merges odds with categories
│   └── decode_market_lines.py      # Decodes base64 market data
│
├── data/                           # Data storage directory
│   ├── raw/                        # Raw API responses
│   │   ├── odds/                   # Timestamped odds data
│   │   └── category_names/         # Timestamped category data
│   └── processed/                  # Processed/merged datasets
│
├── odd_object/                     # Final output destination
│   └── player_lines_final_*.csv    # Ready-to-use datasets
│
└── venv/                           # Virtual environment (not in git)
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.9 or higher**
- **pip** (Python package manager)
- **Active HotStreak API token** (privy-id-token)

### Step 1: Clone the Repository

```bash
git clone https://github.com/iamvikaspatel/opticOdds.git
cd z-odd-object
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install curl_cffi pandas numpy
```

**Core Dependencies:**

- `curl_cffi` - HTTP requests with browser impersonation
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical operations

### Step 4: Create requirements.txt (Optional)

```bash
pip freeze > requirements.txt
```

---

## ⚙️ Configuration

### API Authentication

Before running the pipeline, you **must** configure your HotStreak API token:

1. **Obtain Your Token:**

   - Visit [https://hs3.hotstreak.gg](https://hs3.hotstreak.gg)
   - Open browser Developer Tools (F12)
   - Go to Network tab
   - Look for GraphQL requests
   - Find the `privy-id-token` in request headers

2. **Update Token in Source Files:**

   Edit the following files and replace `YOUR_TOKEN_HERE` with your actual token:

   - `src/fetch_odds_info.py` (line ~21)
   - `src/fetch_category_names.py` (line ~25)

   ```python
   'privy-id-token': 'YOUR_ACTUAL_TOKEN_HERE'
   ```

⚠️ **Security Note:** Keep your token private. Consider using environment variables for production deployments.

---

## 💻 Usage

### Running the Full Pipeline

Execute the complete data pipeline:

```bash
python main.py
```

This runs all 5 steps sequentially:

1. Fetches odds data
2. Fetches category names
3. Combines odds with categories
4. Decodes market lines
5. Moves final output to `odd_object/`

### Running Individual Modules

You can also run modules independently:

```bash
# Fetch only odds data
python -c "from src.fetch_odds_info import run_odds_pipeline; run_odds_pipeline()"

# Fetch only category names
python -c "from src.fetch_category_names import run_category_names_pipeline; run_category_names_pipeline()"

# Decode market lines
python -c "from src.decode_market_lines import run_marketline_decoding; run_marketline_decoding()"
```

---

## 🔄 Pipeline Workflow

### Step 1: Fetch Odds Information

**Module:** `src/fetch_odds_info.py`

- Queries HotStreak GraphQL API for player odds
- Extracts player names and encoded market data (`markets64`)
- Parses category IDs from binary data
- **Output:** `data/raw/odds/<timestamp>/odds_categories_decoded.csv`

**Key Fields:**

- `fullName`: Player's full name
- `markets64`: Base64-encoded market data
- `category_id`: Numerical category identifier

---

### Step 2: Fetch Category Names

**Module:** `src/fetch_category_names.py`

- Retrieves sports and category definitions
- Maps category IDs to human-readable names
- **Output:** `data/raw/category_names/<timestamp>/category_names_raw.csv`

**Key Fields:**

- `sport_id`: Sport identifier
- `sport_name`: Sport name (e.g., "Basketball")
- `category_id`: Category identifier
- `category_name`: Category name (e.g., "Points", "Rebounds")
- `group_name`: Category grouping

---

### Step 3: Combine Odds with Categories

**Module:** `src/combine_odds_with_categories.py`

- Merges odds data with category definitions
- Performs left join on `category_id`
- Adds human-readable labels to odds data
- **Output:** `data/processed/odds_with_categories_<timestamp>.csv`

---

### Step 4: Decode Market Lines

**Module:** `src/decode_market_lines.py`

- Decodes base64 + zlib compressed market data
- Extracts betting lines and odds values
- Processes binary data structure
- **Output:** `data/processed/player_lines_final_<timestamp>.csv`

**Decoded Fields:**

- `numeric_id`: Market identifier
- `final_line`: Betting line value
- `top_over_value`: Over odds value
- `top_under_value`: Under odds value

---

### Step 5: Move Final Output

**Module:** `main.py`

- Copies the latest processed file to `odd_object/`
- Provides clean access to final dataset
- **Output:** `odd_object/player_lines_final_<timestamp>.csv`

---

## 📊 Data Output

### Final Dataset Schema

The final CSV file (`player_lines_final_*.csv`) contains:

| Column            | Type   | Description                                 |
| ----------------- | ------ | ------------------------------------------- |
| `fullName`        | string | Player's full name                          |
| `category_id`     | int    | Numerical category identifier               |
| `sport_name`      | string | Sport name (e.g., "Basketball", "Football") |
| `category_name`   | string | Bet category (e.g., "Points", "Assists")    |
| `group_name`      | string | Category group/classification               |
| `numeric_id`      | int    | Market identifier                           |
| `final_line`      | float  | Betting line value                          |
| `top_over_value`  | float  | Odds for "over" bet                         |
| `top_under_value` | float  | Odds for "under" bet                        |

### Sample Data

```csv
fullName,category_id,sport_name,category_name,group_name,numeric_id,final_line,top_over_value,top_under_value
LeBron James,42,Basketball,Points,Scoring,12345,25.5,1.91,1.91
Steph Curry,43,Basketball,Three Pointers Made,Scoring,12346,4.5,2.05,1.80
```

---

## 🔌 API Documentation

### HotStreak GraphQL API

**Base URL:** `https://api3.hotstreak.gg/graphql`

#### Odds Query

```graphql
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
```

**Variables:**

```json
{
  "query": "",
  "page": 1,
  "filters": {
    "periods": ["FULL_EVENT"],
    "sportsIds": ["basketball"]
  }
}
```

#### System/Categories Query

**Endpoint:** `https://api3.hotstreak.gg/graphql?query=...&operationName=system`

Returns sports and category definitions with IDs and names.

---

## 🛠️ Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError: No module named 'curl_cffi'

**Solution:**

```bash
pip install curl_cffi pandas numpy
```

#### 2. API Returns 401 Unauthorized

**Solution:**

- Your `privy-id-token` has expired
- Obtain a new token from the browser (see [Configuration](#-configuration))
- Update the token in source files

#### 3. Empty Dataset / No Results

**Possible Causes:**

- API endpoint might be down
- Token authentication failed
- Query filters too restrictive

**Solution:**

```bash
# Check API status
curl -I https://api3.hotstreak.gg/graphql

# Verify token is correctly set in source files
grep -r "privy-id-token" src/
```

#### 4. Decoding Errors

**Solution:**

- Ensure `markets64` field is not empty
- Check for API response format changes
- Verify base64 and zlib libraries are installed

#### 5. Permission Errors

**Solution:**

```bash
# Ensure data directories exist
mkdir -p data/raw/odds data/raw/category_names data/processed odd_object

# Check write permissions
ls -la data/
```

---

## 🧪 Testing

### Manual Testing

```bash
# Test individual components
python -c "from src.fetch_odds_info import fetch_odds_info; print(fetch_odds_info().head())"

# Validate pipeline structure
python -c "from main import validate_project_structure; validate_project_structure()"
```

### Data Validation

```python
import pandas as pd

# Load final output
df = pd.read_csv('odd_object/player_lines_final_<timestamp>.csv')

# Basic checks
print(df.info())
print(df.head())
print(df.describe())

# Check for nulls
print(df.isnull().sum())
```

---

## 📈 Future Enhancements

- [ ] Add support for more sports
- [ ] Implement real-time data updates
- [ ] Add data visualization dashboard
- [ ] Create automated scheduling (cron jobs)
- [ ] Add unit tests for each module
- [ ] Implement error recovery mechanisms
- [ ] Add database storage option (SQLite/PostgreSQL)
- [ ] Create REST API wrapper
- [ ] Add email notifications for pipeline failures
- [ ] Implement data quality checks

---
