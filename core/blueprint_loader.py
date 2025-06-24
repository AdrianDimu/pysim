import os
import json
from core.blueprint import Blueprint

def load_blueprints(folder="data/blueprints"):
    blueprints = []
    for filename in os.listdir(folder):
        if filename.endswith(".json"):
            path = os.path.join(folder, filename)
            with open(path) as f:
                data = json.load(f)
                blueprints.append(Blueprint(data["name"], data["components"]))
    return blueprints
