import re
from dataclasses import dataclass

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

    def print_data(self):
        print("""\
Number: %i
Name: %s
Story: %s
Location: %s
Request: %s
Solution: %s
Reward: %s
Prerequisite: %s
Repeat: %s
""" % (self.number, self.name, self.story, self.location, self.request, self.solution, self.reward, self.prerequisite,
       self.repeat))


quests_regex = r'^(?:(?:(⭐) )?\*\*Quest #(\d+) - (.+)\*\*(?: \1)?(?:```yml)?|(\w+): (.+?)(?:```)?)$'


def parse_regex(type, string):
    regex = ""
    if type == Quest:
        regex = quests_regex

    matches = re.findall(regex, string, flags=re.MULTILINE)

    # for match in matches:
    #     print(match)

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
