# analyzer.py

def choose_best_supplier(suppliers, cheapest_supplier=None, budget=None, deadline=None):
    """
    Choose the best supplier based on score.
    Returns:
        best_supplier (dict), explanation (str)
    """

    best = max(suppliers, key=lambda x: x["score"])
    cheapest = cheapest_supplier if cheapest_supplier else min(suppliers, key=lambda x: x["price"])

    explanation = f"🔹 Decision Explanation:\n"
    explanation += f"Chosen Supplier: {best['name']}\n"
    explanation += f"- Price: {best['price']} (Cheapest: {cheapest['price']})\n"
    explanation += f"- Delivery: {best['delivery']} days\n"
    explanation += f"- Reliability: {best['reliability']*100:.1f}%\n"
    explanation += f"- Score: {best['score']}\n\n"

    explanation += "📌 Other suppliers considered:\n"
    for s in suppliers:
        if s != best:
            explanation += (
                f"  - {s['name']}: Price={s['price']}, "
                f"Delivery={s['delivery']}, Reliability={s['reliability']*100:.1f}%, "
                f"Score={s['score']}\n"
            )

    # Show filtered-out suppliers if constraints are given
    if budget is not None and deadline is not None:
        explanation += "\n⚠ Suppliers filtered out due to constraints:\n"
        filtered_out = [
            s for s in suppliers
            if s["price"] > budget or s["delivery"] > deadline
        ]
        if filtered_out:
            for f in filtered_out:
                explanation += (
                    f"  - {f['name']}: Price={f['price']}, Delivery={f['delivery']}, "
                    f"Reliability={f['reliability']*100:.1f}%\n"
                )
        else:
            explanation += "  None\n"

    return best, explanation



