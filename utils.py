TASK_TO_BUDGET = {
    "Install tile flooring": "09 - Finishes",
    "Install cabinets": "06 - Wood & Plastics"
}

def build_budget_items(tasks):
    items = []
    for task in tasks:
        fields = task['fields']
        items.append({
            "name": fields.get("description"),
            "trade": fields.get("trade"),
            "unit": fields.get("unit", "ea"),
            "qty": fields.get("estimated_qty", 1),
            "budget_category": fields.get("budget_category"),
            "estimated_labor": fields.get("allocated_budget", 0),
            "estimated_material": fields.get("actual_cost", 0),
            "total": fields.get("allocated_budget", 0) + fields.get("actual_cost", 0)
        })
    return items