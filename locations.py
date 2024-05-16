import json

from titlecase import titlecase

with open("data/locations.json", "r") as f:
    locations = json.load(f)["locations"]

    for location in locations:
        fixed = locations[location].lower()
        fixed = fixed.replace("north east", "north-east")
        fixed = fixed.replace("north west", "north-west")
        fixed = fixed.replace("south east", "south-east")
        fixed = fixed.replace("south west", "south-west")

        locations[location] = titlecase(fixed)

with open("data/locations.json", "w") as f:
    json.dump({"locations": locations}, f, indent=2)
