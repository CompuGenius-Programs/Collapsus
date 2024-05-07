import json
from dataclasses import dataclass

import parsers

with open("data/recipes.json", "r") as data:
    recipes_data = json.load(data)["recipes"]
recipes = [[recipe["result"]] + [item for i in range(1, 4) if recipe[f"item{i}"] for item in
                                 [recipe[f"item{i}"], recipe[f"qty{i}"]]] for recipe in recipes_data]

with open("data/item_locations.json", "r") as data:
    location_data = json.load(data)["locations"]
locations = [[location["result"], location["location"]] for location in location_data]


@dataclass
class Ingredient:
    name: str
    count: int
    total: int
    level: int
    location: str
    type: str = ''


def cascade(search_input=""):
    ingredients, trail = [], []
    search_input = search_input.lower() or input("Enter the item you want to search for: ").lower()

    for recipe in recipes:
        if recipe[0].lower() == search_input:
            ingredients = cascade_recursive(recipe[0], 1, 1, ingredients, trail, 0)

    if __name__ == "__main__":
        print('\n'.join(
            [f"{ing.name} x{ing.count} ({ing.total}){' - %s' % ing.location if ing.location else ''}" for ing in
             ingredients]))
    return ingredients


def cascade_recursive(recipe, count, mult, ingredients, trail, level):
    if recipe is None:
        return ingredients

    if recipe in trail:
        ingredients.append(Ingredient(recipe, count, count * mult, level, ''))
        return ingredients

    for item in recipes:
        if item[0] == recipe:
            location = next((loc for loc in locations if loc[0] == recipe), None)
            recipe_type = next((rec["type"] for rec in recipes_data if rec["result"] == recipe), '')
            ingredients.append(
                Ingredient(item[0], count, count * mult, level, location[1] if location else '', recipe_type))

            trail.append(item[0])
            for i in range(1, len(item), 2):
                cascade_recursive(item[i], int(item[i + 1]), count * mult, ingredients, trail, level + 1)
            trail.pop()
            return ingredients

    location = next((loc for loc in locations if loc[0] == recipe), None)
    if location:
        ingredients.append(Ingredient(recipe, count, count * mult, level, location[1]))

    return ingredients


# def jsonify_locates():
#     with open("data/item_locations.json", "w") as file:
#         data = {"locations": []}
#         for item in locations:
#             data["locations"].append({"result": item[0], "location": item[1]})
#         json.dump(data, file, indent=2)


def arrayify_locations():
    with open("data/item_locations.json", "r") as file:
        locations_data = json.load(file)
    locations = locations_data["locations"]
    for item in locations:
        item["location"] = item["location"].split(", ")

    with open("data/item_locations.json", "w") as file:
        json.dump(locations_data, file, indent=2)


def get_locations_from_sources():
    with open("data/quests.json", "r", encoding="utf-8") as fp:
        quest_data = json.load(fp)
    quests = quest_data["quests"]

    rewards = [parsers.Quest.from_dict(quest).reward for quest in quests]


if __name__ == "__main__":
    cascade()
