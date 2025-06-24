from fastapi import FastAPI
from models import ScopeRequest
from airtable_client import get_room_id_by_name, get_task_ids_by_room_id, get_filtered_tasks
from openai_client import generate_scope_texts
from utils import build_budget_items

app = FastAPI()

@app.post("/generate-scope")
async def generate_scope(request: ScopeRequest):
    all_outputs = []

    for room in request.rooms:
        room_id = get_room_id_by_name(room)
        
        if not room_id:
            continue

        task_ids = get_task_ids_by_room_id(room_id)
        tasks = get_filtered_tasks(task_ids, request.project_type, request.level_of_work, request.finish_level)

        scope_en, scope_es = generate_scope_texts(room, tasks, request.description)
        budget_items = build_budget_items(tasks)

        all_outputs.append({
            "room": room,
            "tasks": budget_items,
            "scope_english": scope_en,
            "scope_spanish": scope_es
        })
    return all_outputs