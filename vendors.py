# vendors.py - Vendor APIs reading from CSV with varying response times and retry logic

import asyncio
import random
import csv
import os
from config import Supplier, RETRY_CONFIG, SCORE_WEIGHTS, MAX_PRICE, MAX_DELIVERY

CSV_FILE = "vendors.csv"

def compute_score(price: float, delivery: int, reliability: float) -> float:
    """
    Compute weighted score for a supplier.
    Lower price/delivery is better, higher reliability is better.
    """
    # Normalize to 0-1 scale (inverted for price/delivery since lower is better)
    price_norm = max(0, 1 - (price / MAX_PRICE))
    delivery_norm = max(0, 1 - (delivery / MAX_DELIVERY))
    reliability_norm = reliability
    
    # Apply weights
    score = (
        price_norm * SCORE_WEIGHTS["price"] * 100 +
        delivery_norm * SCORE_WEIGHTS["delivery"] * 100 +
        reliability_norm * SCORE_WEIGHTS["reliability"] * 100
    )
    
    return round(score, 2)


async def retry_with_backoff(func, *args, **kwargs):
    """
    Retry an async function with exponential backoff.
    Returns: (result, attempts_taken) or raises last exception
    """
    max_attempts = RETRY_CONFIG["max_attempts"]
    base_delay = RETRY_CONFIG["base_delay"]
    max_delay = RETRY_CONFIG["max_delay"]
    exp_base = RETRY_CONFIG["exponential_base"]
    
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            result = await func(*args, **kwargs)
            return result, attempt + 1
        except Exception as e:
            last_exception = e
            if attempt < max_attempts - 1:
                delay = min(base_delay * (exp_base ** attempt), max_delay)
                delay += random.uniform(0, delay * 0.1)
                await asyncio.sleep(delay)
    
    raise last_exception


# =======================
# Dynamic Vendor API Simulation
# =======================

def load_vendors_from_csv():
    """Read vendors from CSV file"""
    vendors = []
    if not os.path.exists(CSV_FILE):
        return []
        
    try:
        with open(CSV_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                vendors.append({
                    "name": row["name"],
                    "base_price": float(row["base_price"]),
                    "price_per_unit": float(row["price_per_unit"]),
                    "delivery": int(row["delivery_days"]),
                    "reliability": float(row["reliability"]),
                    "penalty_rate": float(row.get("delay_penalty_percent", 0.0))
                })
    except Exception as e:
        print(f"Error reading CSV: {e}")
    
    return vendors


async def simulate_vendor_api(vendor_data: dict, qty: int) -> dict:
    """
    Simulate an API call for a specific vendor from CSV data.
    """
    # Simulate network latency based on reliability (less reliable = slower/more erratic)
    base_latency = random.uniform(0.5, 1.5)
    unreliability_penalty = (1.0 - vendor_data["reliability"]) * 2.0
    latency = base_latency + random.uniform(0, unreliability_penalty)
    
    await asyncio.sleep(latency)
    
    # Simulate occasional timeouts for low reliability vendors
    failure_threshold = 0.02 + (1.0 - vendor_data["reliability"]) * 0.1
    if random.random() < failure_threshold:
        raise ConnectionError(f"{vendor_data['name']} API timeout")
    
    # Calculate price
    price = vendor_data["base_price"] + (qty * vendor_data["price_per_unit"])
    
    return {
        "name": vendor_data["name"],
        "price": round(price, 2),
        "delivery": vendor_data["delivery"],
        "reliability": vendor_data["reliability"],
        "penalty_rate": vendor_data["penalty_rate"],
        "score": compute_score(price, vendor_data["delivery"], vendor_data["reliability"])
    }


async def fetch_vendor_with_retry(vendor_data, qty: int) -> tuple[dict | None, dict]:
    """
    Fetch from a dynamic vendor with retry logic.
    """
    vendor_name = vendor_data["name"]
    
    try:
        # Pass the simulation function and arguments
        result, attempts = await retry_with_backoff(simulate_vendor_api, vendor_data, qty)
        return result, {
            "vendor": vendor_name,
            "success": True,
            "attempts": attempts,
            "error": None
        }
    except Exception as e:
        return None, {
            "vendor": vendor_name,
            "success": False,
            "attempts": RETRY_CONFIG["max_attempts"],
            "error": str(e)
        }


async def get_vendors(qty: int) -> tuple[list[dict], list[dict]]:
    """
    Fetch all vendors from CSV concurrently.
    Returns: (suppliers_list, fetch_metadata_list)
    """
    csv_vendors = load_vendors_from_csv()
    
    if not csv_vendors:
        return [], [{"vendor": "CSV_LOADER", "success": False, "error": "No vendors found in vendors.csv", "attempts": 1}]

    # Create tasks for all CSV vendors
    tasks = [fetch_vendor_with_retry(v, qty) for v in csv_vendors]
    results = await asyncio.gather(*tasks)
    
    suppliers = []
    metadata = []
    
    for supplier_data, meta in results:
        metadata.append(meta)
        if supplier_data:
            suppliers.append(supplier_data)
    
    return suppliers, metadata
