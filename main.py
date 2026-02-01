# main.py - Main entry point integrating the multi-agent procurement system

import asyncio
import sys

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from vendors import get_vendors
from agents.crew import ProcurementCrew, CrewResult
from db import get_constraints


async def run_procurement_async(
    qty: int, 
    budget: float = None, 
    deadline: int = None
) -> CrewResult:
    """
    Run the full procurement workflow asynchronously.
    
    Args:
        qty: Order quantity
        budget: Budget constraint (uses DB default if None)
        deadline: Deadline in days (uses DB default if None)
    
    Returns:
        CrewResult with complete workflow data
    """
    # Get constraints from database if not provided
    if budget is None or deadline is None:
        db_budget, db_deadline = get_constraints()
        budget = budget or db_budget
        deadline = deadline or db_deadline
    
    # Fetch vendors concurrently (with retry logic)
    suppliers, fetch_metadata = await get_vendors(qty)
    
    # Run procurement crew workflow
    crew = ProcurementCrew()
    result = await crew.run(
        suppliers=suppliers,
        fetch_metadata=fetch_metadata,
        quantity=qty,
        budget=budget,
        deadline=deadline
    )
    
    return result


def run_backend(qty: int, budget: float = None, deadline: int = None) -> tuple:
    """
    Synchronous wrapper for Streamlit compatibility.
    Returns legacy format: (best, cheapest, explanation, success, suppliers)
    Plus new CrewResult for extended data.
    """
    result = asyncio.run(run_procurement_async(qty, budget, deadline))
    
    # Extract legacy format for backwards compatibility
    best = result.final_supplier
    explanation = result.workflow_log
    success = result.success
    suppliers = result.all_suppliers
    
    # Find cheapest for comparison
    if suppliers:
        cheapest = min(suppliers, key=lambda x: x.get("negotiated_price", x["price"]))
    else:
        cheapest = None
    
    return best, cheapest, explanation, success, suppliers, result


# -----------------------
# CLI Test Mode
# -----------------------
if __name__ == "__main__":
    print("=" * 60)
    print("🏭 Multi-Agent Procurement System - CLI Test")
    print("=" * 60)
    
    qty_test = 100
    best, cheapest, explanation, success, suppliers, crew_result = run_backend(qty_test)
    
    print(explanation)
    print("\n" + "=" * 60)
    
    if best:
        print(f"\n✅ Final Result:")
        print(f"   Supplier: {best['name']}")
        price_key = "negotiated_price" if "negotiated_price" in best else "price"
        print(f"   Price: ${best[price_key]:.2f}")
        print(f"   Delivery: {best['delivery']} days")
        print(f"   Order Success: {success}")
    else:
        print("\n❌ No valid supplier found.")
