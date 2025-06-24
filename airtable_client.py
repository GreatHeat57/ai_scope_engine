import requests
import os
from dotenv import load_dotenv

load_dotenv()

AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
HEADERS = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}

def get_room_id_by_name(room_name):
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/Rooms"
    formula = f"{{name}} = '{room_name}'"
    params = {"filterByFormula": formula}
    
    res = requests.get(url, headers=HEADERS, params=params).json()
    records = res.get("records", [])

    return records[0]["fields"].get("id") if records else None

def get_task_ids_by_room_id(room_id):
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/RoomTasks"
    formula = f"FIND('{room_id}', ARRAYJOIN({{room}}))"
    params = {"filterByFormula": formula}

    res = requests.get(url, headers=HEADERS, params=params).json()
    
    task_ids = []
    for record in res.get("records", []):
        task_ids.extend(record["fields"].get("task", []))

    return list(set(task_ids))

def get_filtered_tasks(task_ids, project_type, level_of_work, finish_level):
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/Tasks"
    id_filters = ",".join([f'RECORD_ID() = "{tid}"' for tid in task_ids])

    formula = f"""AND(
        {{project_type}} = '{project_type}',
        {{level_of_work}} = '{level_of_work}',
        {{finish_level}} = '{finish_level}',
        OR({id_filters})
    )"""

    params = {"filterByFormula": formula}
    res = requests.get(url, headers=HEADERS, params=params).json()

    tasks = res.get("records", [])

    trade_ids = list({
        tid for task in tasks
        for tid in task["fields"].get("trade_id", [])
    })

    line_item_ids = list({
        lid for task in tasks for lid in task["fields"].get("line_item_id", [])
    })

    trade_map = get_construction_trades(trade_ids)
    line_item_map = get_budget_line_items(line_item_ids)

    for task in tasks:
        fields = task["fields"]

        tid = fields.get("trade_id", [None])[0]
        if tid:
            fields["trade"] = trade_map.get(tid, "")

        lid = fields.get("line_item_id", [None])[0]
        if lid:
            fields.update(line_item_map.get(lid, {}))

    return tasks

def get_construction_trades(trade_ids):
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/ConstructionTrades"
    id_filters = ",".join([f'RECORD_ID() = "{tid}"' for tid in trade_ids])
    formula = f"OR({id_filters})"
    params = {"filterByFormula": formula}

    res = requests.get(url, headers=HEADERS, params=params).json()

    return {
        record["id"]: record["fields"].get("name", "")
        for record in res.get("records", [])
    }

def get_budget_line_items(line_item_ids):
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/BudgetLineItems"
    id_filters = ",".join([f'RECORD_ID() = "{lid}"' for lid in line_item_ids])
    formula = f"OR({id_filters})"
    params = {"filterByFormula": formula}

    res = requests.get(url, headers=HEADERS, params=params).json()

    return {
        record["id"]: {
            "budget_category": record["fields"].get("description", ""),
            "allocated_budget": record["fields"].get("allocated_budget", 0),
            "actual_cost": record["fields"].get("actual_cost", 0),
        }
        for record in res.get("records", [])
    }
