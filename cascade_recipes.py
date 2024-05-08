import json
import re
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


def get_locations_from_sources():
    def sanitize_reward(strings):
        sanitized = []
        for string in strings:
            if " and " in string:
                strings.extend(string.split(" and "))
                continue
            if "; " in string:
                strings.extend(string.split("; "))
                continue
            if "\n" in string:
                strings.extend(string.split("\n"))
                continue
            string = (string.lower().removeprefix("a ").removeprefix("an ").removeprefix("and ").removesuffix(
                ".").removesuffix(" for showing her the mask").removesuffix(
                " if you decide to give her the mask").removesuffix(" for showing him the robe").removesuffix(
                " if you decide to give him the robe").removesuffix(" for repeat").replace(" (", "(").replace(") ",
                                                                                                              ")"))
            string = re.sub(r'\([^)]*\)', '', string)
            string = re.sub(r'\d', '', string)
            string = string.replace(", ", "").replace("-: ", "")
            if string:
                sanitized.append(string.strip())
        return sanitized

    with open("data/recipes.json", "r") as file:
        recipes = json.load(file)["recipes"]
        all_items = [item.lower() for recipe in recipes for item in
                     [recipe["result"], recipe["item1"], recipe.get("item2", ""), recipe.get("item3", "")] if item]

    with open("data/item_locations.json", "r") as file:
        items = json.load(file)["locations"]
        all_items_with_locations = [item["result"].lower() for item in items]

    with open("data/quests.json", "r", encoding="utf-8") as file:
        quests = [parsers.Quest.from_dict(quest) for quest in json.load(file)["quests"]]
        rewards = [sanitize_reward(quest.reward.split(", ")) for quest in quests]

    with open("data/monsters.json", "r") as file:
        monsters = [parsers.Monster.from_dict(monster) for monster in json.load(file)["monsters"]]
        drops = [sanitize_reward([monster.drop1, monster.drop2, monster.drop3]) for monster in monsters]

    print("Item locations count: " + str(len(all_items_with_locations)))

    all_items_unique = set(all_items)
    all_items_modified = []

    items_dont_exist = [item for item in all_items_with_locations if item not in all_items_unique]
    print("Items that don't exist: " + str(items_dont_exist))

    for item in all_items_unique:
        existing_item = next((i for i in items if i["result"].lower() == item), None)
        if not existing_item:
            modified_item = {"result": item, "location": []}
        else:
            modified_item = existing_item

        for reward, quest in zip(rewards, quests):
            if modified_item["result"].lower() in reward and f"quest #{quest.number}" not in modified_item["location"]:
                modified_item["location"].append(f"quest #{quest.number}")
                print(f"Added quest #{quest.number} to {modified_item['result']}")

        for drop, monster in zip(drops, monsters):
            if modified_item["result"].lower() in drop and monster.name.lower() not in modified_item["location"]:
                if monster.name.lower().startswith("hell ni"):
                    monster.name = "hell niño"
                modified_item["location"].append(monster.name.lower())
                print(f"Added {monster.name} to {modified_item['result']}")

        if modified_item["location"]:
            location_shops = [location.lower() for location in modified_item["location"] if location.lower().endswith("shop")]
            location_quests = [location.lower() for location in modified_item["location"] if location.lower().startswith("quest")]
            location_chests = [location.lower() for location in modified_item["location"] if location.lower().endswith("chest")]
            location_monsters = [location.lower() for location in modified_item["location"] if location.lower() not in location_shops and location.lower() not in location_quests and location.lower() not in location_chests]
            modified_item["location"] = sorted(location_shops) + sorted(location_quests) + sorted(location_chests) + sorted(location_monsters)
            all_items_modified.append(modified_item)

    print("Modified item locations count: " + str(len(all_items_modified)))
    all_items_modified.sort(key=lambda x: x["result"])

    with open("data/item_locations.json", "w") as file:
        json.dump({"locations": all_items_modified}, file, indent=2)


if __name__ == "__main__":
    get_locations_from_sources()
