import requests
import time
import pandas as pd
from typing import Optional, List

SEC_BASE = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
COMPANY_TICKER_URL = "https://www.sec.gov/files/company_tickers.json"

# ---------- Helper Functions ----------
def pad_cik(cik: str) -> str:
    """Pad CIK to 10 digits with leading zeros."""
    return "".join(ch for ch in cik if ch.isdigit()).zfill(10)


def sec_get(url: str, ua: str, retries=5, backoff=1.5):
    """Fetch JSON from SEC with retry logic."""
    sess = requests.Session()
    headers = {
        "User-Agent": ua,
        "Accept-Encoding": "gzip, deflate",
        "Host": "data.sec.gov"
    }
    
    for i in range(retries):
        try:
            r = sess.get(url, headers=headers, timeout=30)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(backoff ** (i + 1))
                continue
            r.raise_for_status()
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(backoff ** (i + 1))
    
    raise RuntimeError(f"Fetch failed after {retries} retries")


def obs_for_metric(facts, metric, allow_units=("USD",)):
    """Extract observations for a single metric from SEC facts."""
    obj = facts.get("us-gaap", {}).get(metric, {})
    rows = []
    
    for unit, arr in obj.get("units", {}).items():
        if unit not in allow_units:
            continue
        for o in arr:
            rows.append({
                "metric": metric,
                "unit": unit,
                "value": pd.to_numeric(o.get("val"), errors="coerce"),
                "start": pd.to_datetime(o.get("start"), errors="coerce"),
                "end": pd.to_datetime(o.get("end"), errors="coerce"),
                "fy": o.get("fy"),
                "fp": o.get("fp"),
                "form": o.get("form"),
                "filed": pd.to_datetime(o.get("filed"), errors="coerce"),
                "frame": o.get("frame"),
            })
    
    return pd.DataFrame(rows)


def pick_quarterly(df):
    """Select one row per fiscal quarter, preferring 10-Q filings."""
    if df.empty:
        return df
    
    q = df[df["fp"].isin(["Q1", "Q2", "Q3", "Q4"])].copy()
    if q.empty:
        return q
    
    # Prefer 10-Q forms
    q["__ord"] = q["form"].eq("10-Q").astype(int)
    q = (q.sort_values(["fy", "fp", "__ord", "filed", "end"])
          .groupby(["fy", "fp"], as_index=False)
          .tail(1)
          .drop(columns="__ord"))
    
    q["Quarter"] = q["end"].dt.to_period("Q").astype(str)
    return q


def filter_by_date_range(df, start_date: Optional[str], end_date: Optional[str]):
    """Filter dataframe columns by date range."""
    if df.empty or (start_date is None and end_date is None):
        return df
    
    # Parse quarter strings to dates
    valid_cols = []
    for col in df.columns:
        try:
            # Convert quarter string like "2023Q1" to date
            quarter_date = pd.Period(col, freq='Q').to_timestamp()
            
            if start_date and quarter_date < pd.to_datetime(start_date):
                continue
            if end_date and quarter_date > pd.to_datetime(end_date):
                continue
            
            valid_cols.append(col)
        except:
            valid_cols.append(col)  # Keep column if parsing fails
    
    return df[valid_cols]


def format_usd_short(value):
    """Format USD values in short form."""
    if pd.isna(value):
        return None
    
    abs_val = abs(value)
    sign = "-" if value < 0 else ""
    
    if abs_val >= 1e9:
        return f"{sign}${abs_val/1e9:.2f}B"
    elif abs_val >= 1e6:
        return f"{sign}${abs_val/1e6:.2f}M"
    elif abs_val >= 1e3:
        return f"{sign}${abs_val/1e3:.2f}K"
    else:
        return f"{sign}${abs_val:.2f}"

def build_income_statement(
    cik: str,
    ua: str,
    required_fields: List[str],
    output_type: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Build income statement based on parameters."""
    cikp = pad_cik(cik)
    data = sec_get(SEC_BASE.format(cik=cikp), ua=ua)
    facts = data.get("facts", {})
    company_name = data.get("entityName", "Unknown")
    
    # Define metric mappings
    income_alias = {
        # Revenue
        "Total Revenues": [
            "Revenues",
            "SalesRevenueNet",
            "RevenueFromContractWithCustomerExcludingAssessedTax"
        ],
        # Cost & Gross Profit
        "Cost of Revenue": ["CostOfRevenue", "CostOfGoodsAndServicesSold"],
        "Cost Of Revenues": ["CostOfRevenue", "CostOfGoodsAndServicesSold"],
        "Gross Profit": ["GrossProfit"],
        # Operating Expenses
        "R&D": ["ResearchAndDevelopmentExpense"],
        "R&D Expenses": ["ResearchAndDevelopmentExpense"],
        "SG&A": [
            "SellingGeneralAndAdministrativeExpense",
            "SellingAndMarketingExpense"
        ],
        "Selling General & Admin Expenses": [
            "SellingGeneralAndAdministrativeExpense"
        ],
        "Operating Expenses": ["OperatingExpenses"],
        "Other Operating Expenses": [
            "OtherOperatingIncomeExpenseNet",
            "OtherCostAndExpenseOperating"
        ],
        "Other Operating Expenses, Total": [
            "OtherOperatingIncomeExpenseNet",
            "OtherCostAndExpenseOperating"
        ],
        # Operating Income
        "Operating Income": ["OperatingIncomeLoss"],
        "EBIT": ["OperatingIncomeLoss"],
        # Interest & Non-Operating
        "Interest Expense, Total": [
            "InterestExpense",
            "InterestExpenseDebt"
        ],
        "Interest And Investment Income": [
            "InvestmentIncomeInterest",
            "InterestAndDividendIncomeOperating",
            "InterestIncomeExpenseNonoperatingNet"
        ],
        "Net Interest Expenses": [
            "InterestExpense",
            "InterestIncomeExpenseNet"
        ],
        "Other Non Operating Expenses, Total": [
            "NonoperatingIncomeExpense",
            "OtherNonoperatingIncomeExpense"
        ],
        # Pre-Tax Income
        "EBT, Excl. Unusual Items": [
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest"
        ],
        "EBT, Incl. Unusual Items": [
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"
        ],
        "Gain (Loss) On Sale Of Assets": [
            "GainLossOnSaleOfPropertyPlantEquipment",
            "GainLossOnDispositionOfAssets"
        ],
        "Other Unusual Items, Total": [
            "UnusualOrInfrequentItemNetOfInsuranceProceeds",
            "GainLossRelatedToLitigationSettlement"
        ],
        # Tax & Net Income
        "Income Tax": ["IncomeTaxExpenseBenefit"],
        "Income Tax Expense": ["IncomeTaxExpenseBenefit"],
        "Net Income": ["NetIncomeLoss"],
        "Net Income to Company": [
            "NetIncomeLoss",
            "ProfitLoss"
        ],
        "Minority Interest": [
            "MinorityInterest",
            "NetIncomeLossAttributableToNoncontrollingInterest"
        ],
        "Net Income to Common Excl. Extra Items": [
            "NetIncomeLossAvailableToCommonStockholdersBasic"
        ],
        "Preferred Dividend and Other Adjustments": [
            "PreferredStockDividendsAndOtherAdjustments",
            "DividendsPreferredStock"
        ],
        # EPS
        "Basic EPS - Continuing Operations": [
            "EarningsPerShareBasic",
            "IncomeLossFromContinuingOperationsPerBasicShare"
        ],
        "Diluted EPS - Continuing Operations": [
            "EarningsPerShareDiluted",
            "IncomeLossFromContinuingOperationsPerDilutedShare"
        ],
        # Shares Outstanding
        "Basic Weighted Average Shares Outstanding": [
            "WeightedAverageNumberOfSharesOutstandingBasic"
        ],
        "Diluted Weighted Average Shares Outstanding": [
            "WeightedAverageNumberOfDilutedSharesOutstanding"
        ],
        # Dividends
        "Dividend Per Share": [
            "CommonStockDividendsPerShareDeclared",
            "CommonStockDividendsPerShareCashPaid"
        ],
        # EBITDA (Note: Usually calculated, rarely reported directly)
        "EBITDA": [
            "EarningsBeforeInterestTaxesDepreciationAndAmortization"
        ],
    }
    # Extract data for each metric
    raw_rows = {}
    all_quarters = set()
    for friendly in required_fields:
        tags = income_alias.get(friendly, [])
        if not tags:
            raw_rows[friendly] = pd.Series(dtype=float, name=friendly)
            continue
        df_all = pd.concat(
            [obs_for_metric(facts, t) for t in tags],
            ignore_index=True
        ) if tags else pd.DataFrame()
        if df_all.empty:
            raw_rows[friendly] = pd.Series(dtype=float, name=friendly)
            continue
        # Filter to USD only
        if "USD" in df_all.get("unit", pd.Series()).unique():
            df_all = df_all[df_all["unit"] == "USD"].copy()
        dq = pick_quarterly(df_all)
        if dq.empty:
            raw_rows[friendly] = pd.Series(dtype=float, name=friendly)
            continue
        ser = dq.set_index("Quarter")["value"].sort_index()
        ser.name = friendly
        raw_rows[friendly] = ser
        all_quarters.update(ser.index.tolist())
    # Create master column index
    master_cols = sorted(all_quarters)
    # Align all rows to master columns
    aligned_rows = []
    for name in required_fields:
        s = raw_rows.get(name, pd.Series(dtype=float, name=name))
        s = s.reindex(master_cols)
        s.name = name
        aligned_rows.append(s)
    is_q = pd.DataFrame(aligned_rows)
    is_q = is_q.apply(pd.to_numeric, errors="coerce")
    
    # --- [START OF LOGIC CHANGE] ---
    
    # Do NOT filter by date yet.
    # First, calculate TTM if requested, using the *full* DataFrame
    if output_type == "ttm":
        # Calculate TTM on the *entire* quarterly dataset
        data_to_filter = is_q.T.rolling(4, min_periods=4).sum().T
    else:
        # If not TTM, just use the quarterly data
        data_to_filter = is_q

    # NOW, filter the resulting DataFrame (either TTM or Q) by date
    result_df = filter_by_date_range(data_to_filter, start_date, end_date)

    # --- [END OF LOGIC CHANGE] ---

    # Format output
    output_data = {}
    for idx in result_df.index:
        output_data[idx] = {}
        for col in result_df.columns:
            val = result_df.loc[idx, col]
            output_data[idx][col] = {
                "raw": float(val) if pd.notna(val) else None,
                "formatted": format_usd_short(val)
            }

    return {
        "company_name": company_name,
        "data": output_data,
        "periods": list(result_df.columns)
    }