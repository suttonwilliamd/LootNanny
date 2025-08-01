import json
import sys
import os
from decimal import Decimal
from helpers import resource_path

ALL_WEAPONS = {}
data_filename = resource_path("data/raw/weapons.json")


with open(data_filename, 'r') as f:
    data = json.loads(f.read())
    # Handle both old and new JSON structures
    weapons_data = data.get("data", data)
    for name, weapon_data in weapons_data.items():
        if isinstance(weapon_data, dict):
            weapon_data["decay"] = Decimal(weapon_data["decay"])
            ALL_WEAPONS[name] = weapon_data

FIELDS = ("name", "class", "type", "damage", "decay", "ammo")

if __name__ == "__main__":
    import sys

    all_weapons = {}

    for fn in sys.argv[1:]:
        with open(fn, 'r') as f:
            header = True
            for line in f.readlines():
                if header:
                    header = False
                    continue
                try:
                    data = dict(zip(FIELDS, line.split(";")))
                    data["decay"] = Decimal(data["decay"] if data["decay"].strip() else "0.0") / Decimal(100.0)
                    data["ammo"] = int(data["ammo"] if data["ammo"].strip() else 0)

                    all_weapons[data["name"]] = {
                        "type": data["class"],
                        "decay": str(data["decay"]),
                        "ammo": data["ammo"]
                    }

                except:
                    break

    if all_weapons:
        output = open(data_filename, 'w')
        output.write(json.dumps(all_weapons, indent=2, sort_keys=True))
