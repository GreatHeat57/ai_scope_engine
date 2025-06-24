from openai import OpenAI, RateLimitError
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_scope_texts(room, tasks, description):
    task_names = [t['fields']['description'] for t in tasks]
    prompt = f"""A user is remodeling their {room}. The tasks include: {', '.join(task_names)}.
The user described the project as: "{description}".

Write a professional Scope of Work for this room in English and Spanish.
Make sure it's suitable for a client contract and field workers.
Label the sections clearly with "English Version:" and "Spanish Version:"
"""

    try:
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        output = res.choices[0].message.content.strip()

        _, _, english_and_rest = output.partition("**English Version:**")
        english_text, _, spanish_text = english_and_rest.partition("**Spanish Version:**")

        scope_english = english_text.strip()
        scope_spanish = spanish_text.strip()

        return scope_english, scope_spanish
    except RateLimitError as e:
        print("Rate limit exceeded or insufficient quota.")
        return "Error: Rate limit exceeded", "Error: Rate limit exceeded"
