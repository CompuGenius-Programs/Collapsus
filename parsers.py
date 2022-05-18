import re
from dataclasses import dataclass, field
from typing import Dict

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Quest:
    """Class for a quest."""
    number: int = 0
    name: str = ""
    story: bool = False
    location: str = ""
    request: str = ""
    solution: str = ""
    reward: str = ""
    prerequisite: str = ""
    repeat: bool = False


@dataclass_json
@dataclass
class Grotto:
    """Class for a grotto."""
    seed: str = ""
    rank: str = ""
    name: str = ""
    boss: str = ""
    type: str = ""
    floors: int = 0
    monster_rank: str = ""
    chests: Dict[str, int] = field(default_factory=dict)
    locations: int = 0
    grotto_special: bool = False


grotto_bosses = [
    "Equinox",
    "Nemean",
    "Shogum",
    "Trauminator",
    "Elusid",
    "Sir Sanguinus",
    "Atlas",
    "Hammibal",
    "Fowleye",
    "Excalipurr",
    "Tyrannosaurus Wrecks",
    "Greygnarl"
]

grotto_prefixes = [
    "Clay",
    "Rock",
    "Granite",
    "Basalt",
    "Graphite",
    "Iron",
    "Copper",
    "Bronze",
    "Steel",
    "Silver",
    "Gold",
    "Platinum",
    "Ruby",
    "Emerald",
    "Sapphire",
    "Diamond"
]

grotto_environments = [
    "Cave",
    "Tunnel",
    "Mine",
    "Crevasse",
    "Marsh",
    "Lair",
    "Icepit",
    "Lake",
    "Crater",
    "Path",
    "Snowhall",
    "Moor",
    "Dungeon",
    "Crypt",
    "Nest",
    "Ruins",
    "Tundra",
    "Waterway",
    "World",
    "Abyss",
    "Maze",
    "Glacier",
    "Chasm",
    "Void"
]

grotto_suffixes = [
    "Joy",
    "Bliss",
    "Glee",
    "Doubt",
    "Woe",
    "Dolour",
    "Regret",
    "Bane",
    "Fear",
    "Dread",
    "Hurt",
    "Gloom",
    "Doom",
    "Evil",
    "Ruin",
    "Death"
]

grotto_types = [
    "Caves",
    "Ruins",
    "Ice",
    "Water",
    "Fire"
]

grotto_special = "Has a special floor"
grotto_keys = ("Seed", "Rank", "Name",
               "Boss", "Type", "Floors",
               "Monster Rank", "Chests (S - I)")

quests_regex = r'^(?:(?:(⭐) )?\*\*Quest #(\d+) - (.+)\*\*(?: \1)?(?:```yml)?|(\w+): (.+?)(?:```)?)$'
grotto_cleanup_regex = r'([\w\d\.\-:/() ]+)'


def _hex(value):
    n = int(value)
    if n <= 16:
        return n
    n = int(value, base=16)

    hex_str = str.upper(hex(n)[2:])
    return hex_str.zfill(4)


def is_special(data: tuple):
    try:
        return data[0] == grotto_special
    except ValueError:
        return False


def create_grotto(datas):
    converters = (_hex, int, str)

    magic = 17
    ye = []

    for data in datas:
        match_found = re.compile(grotto_cleanup_regex).match(data)

        if match_found:
            stripped = str.strip(match_found.group(), "' ")

            if stripped != "":
                for i, converter in enumerate(converters):
                    try:
                        converted = converter(stripped)
                    except Exception:
                        converted = None
                        continue
                    else:
                        if isinstance(converted, str):
                            if converted.find(":") > -1:
                                continue
                            elif converted == grotto_special:
                                magic = 18
                                ye.insert(0, converted)
                            else:
                                ye.append(converted)
                        else:
                            ye.append(converted)
                        break
                    finally:
                        if len(ye) == magic:
                            yield tuple(ye)
                            magic = 17
                            ye = []

    if len(ye) > 0:
        yield tuple(ye)


def parse_regex(type, string):
    regex = ""
    if type == Quest:
        regex = quests_regex

    matches = re.findall(regex, string, flags=re.MULTILINE)

    # for match in matches:
    #     print(match)

    if type == Quest:
        number = int(matches[0][1])
        name = matches[0][2]
        story = matches[0][0] == "⭐"

        location = ""
        request = ""
        solution = ""
        reward = ""
        prerequisite = ""
        repeat = False

        for info in matches[1:]:
            title = info[3].lower()
            data = info[4].strip()
            if title == "location":
                location = data
            if title == "request":
                request = data
            if title == "solution":
                solution = data
            if title == "reward":
                reward = data
            if title == "prerequisite":
                prerequisite = data
            if title == "repeat":
                repeat = data.lower() == "yes"

        quest = Quest(number, name, story, location, request, solution, reward, prerequisite, repeat)
        return quest.to_dict()
