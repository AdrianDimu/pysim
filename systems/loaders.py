import os
import json
from systems.blueprint import Blueprint

def load_blueprints(folder="data/blueprints"):
    blueprints = []
    for filename in os.listdir(folder):
        if not filename.endswith(".json"):
            continue

        path = os.path.join(folder, filename)
        try:
            with open(path) as f:
                data = json.load(f)
                name = data.get("name", os.path.splitext(filename)[0])
                components = data.get("components", [])
                if components:
                    blueprints.append(Blueprint(name, components))
                else:
                    print(f"[WARN] Skipped blueprint '{filename}' — no components found.")
        except Exception as e:
            print(f"[ERROR] Failed to load blueprint '{filename}': {e}")

    return blueprints
