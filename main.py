import json
import os
import random

import aiohttp
import discord
import dotenv
from discord import Option
from discord.ext.pages import Paginator, Page
from parsel import Selector
from titlecase import titlecase

import parsers

dotenv.load_dotenv()
token = os.getenv("TOKEN")

bot = discord.Bot()

guild_id = 655390550698098700
quests_channel = 766039065849495574

logo_url = "https://cdn.discordapp.com/emojis/856330729528361000.png"
website_url = "https://dq9.carrd.co"

grotto_search_url = "https://www.yabd.org/apps/dq9/grottosearch.php"

monster_images_url = "https://www.woodus.com/den/gallery/graphics/dq9ds/monster/%s.webp"

krak_pop_image_url = "https://cdn.discordapp.com/attachments/698157074420334612/982389321506099300/unknown.png"
item_images_url = "https://www.woodus.com/den/gallery/graphics/dq9ds/item/%s.png"
weapon_images_url = "https://www.woodus.com/den/gallery/graphics/dq9ds/weapon/%s.png"
armor_images_url = "https://www.woodus.com/den/gallery/graphics/dq9ds/armor/%s.png"
accessory_images_url = "https://www.woodus.com/den/gallery/graphics/dq9ds/accessory/%s.png"
recipe_images_urls = [item_images_url, weapon_images_url, armor_images_url, accessory_images_url]


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                        name="over The Quester's Rest. Type /help ."))


@bot.slash_command(name="help", description="Get help for using the bot.")
async def help(ctx):
    description = '''
A bot created by <@496392770374860811> for The Quester's Rest.


`/quest [Quest Number]` | Displays all info for a specific quest

`/grotto [Material] [Environment] [Suffix] [Level] <Location>` | Displays all grotto info for a name combination

`/gg [Material] [Environment] [Suffix] [Level] [Location]` | Displays all grotto info for a name combination with location required

`/recipe [Creation]` | Displays all info for a recipe

`/monster [Monster Identifier]` | Displays all info for a monster

`/character` | Displays info for a random character

`/help` | Displays this message
'''

    embed = create_embed("Collapsus v2 Help", description=description, image=logo_url, url=website_url)
    await ctx.respond(embed=embed)


@bot.slash_command(name="parse_quests", description="Parses the quests.")
async def parse_quests(ctx):
    await ctx.defer()

    quests = []
    channel = bot.get_channel(quests_channel)
    archived_threads = await channel.archived_threads().flatten()
    for thread in archived_threads:
        messages = await thread.history(oldest_first=True).flatten()
        for message in messages:
            quests.append(parsers.parse_regex(parsers.Quest, message.content))

    data = {
        "quests": quests
    }
    with open("quests.json", "w+", encoding="utf-8") as fp:
        json.dump(data, fp, indent=4)

    embed = create_embed("%i Quests Parsed Successfully" % len(quests))
    await ctx.followup.send(embed=embed)


@bot.slash_command(name="quest", description="Sends info about a quest.")
async def _quest(ctx, quest_number: Option(int, "Quest Number (1-184)", required=True)):
    with open("quests.json", "r", encoding="utf-8") as fp:
        data = json.load(fp)

    quests = data["quests"]
    index = quest_number - 1
    if index >= len(quests) or index < 0:
        embed = create_embed("No quest found with the number `%s`. Please check number and try again." % quest_number)
        return await ctx.respond(embed=embed)

    quest = parsers.Quest.from_dict(quests[index])

    title = ":star: Quest #%i - %s :star:" % (quest.number, quest.name) if quest.story \
        else "Quest #%i - %s" % (quest.number, quest.name)
    color = discord.Color.gold() if quest.story else discord.Color.green()
    embed = create_embed(title, color=color)
    if quest.location != "":
        embed.add_field(name="Location", value=quest.location, inline=False)
    if quest.request != "":
        embed.add_field(name="Request", value=quest.request, inline=False)
    if quest.solution != "":
        embed.add_field(name="Solution", value="||%s||" % quest.solution, inline=False)
    if quest.reward != "":
        embed.add_field(name="Reward", value=quest.reward, inline=False)
    embed.add_field(name="Repeat", value="Yes" if quest.repeat else "No", inline=False)
    embed.add_field(name="Pre-reqs", value=quest.prerequisite, inline=False)

    await ctx.respond(embed=embed)


@bot.slash_command(name="recipe", description="Sends info about a recipe.")
async def _recipe(ctx, creation_name: Option(str, "Creation (Ex. Special Medicine)", required=True)):
    with open("recipes.json", "r", encoding="utf-8") as fp:
        data = json.load(fp)

    recipes = data["recipes"]
    index = next(filter(lambda r: r["result"] == creation_name.lower(), recipes), None)

    if index is None:
        embed = create_embed("Ahem! Oh dear. I'm afraid I don't seem to be\nable to make anything with that particular"
                             "\ncreation name of `%s`." % creation_name, image=krak_pop_image_url)
        return await ctx.respond(embed=embed)

    recipe = parsers.Recipe.from_dict(index)

    title = ":star: %s :star:" % titlecase(recipe.result) if recipe.alchemiracle else titlecase(recipe.result)
    color = discord.Color.gold() if recipe.alchemiracle else discord.Color.green()

    if recipe.image == "":
        recipe_images_url = ""
        for url in recipe_images_urls:
            async with aiohttp.ClientSession() as session:
                async with session.get(url % clean_text(recipe.result, False)) as resp:
                    if resp.status == 200:
                        recipe_images_url = url
                        break
        if recipe_images_url != "":
            recipe.image = recipe_images_url % clean_text(recipe.result, False)
    embed = create_embed(title, color=color, image=recipe.image)

    embed.add_field(name="Type", value=recipe.type, inline=False)
    if recipe.item1 != "":
        embed.add_field(name="Item 1", value="%ix %s" % (recipe.qty1, titlecase(recipe.item1)), inline=False)
    if recipe.item2 != "":
        embed.add_field(name="Item 2", value="%ix %s" % (recipe.qty2, titlecase(recipe.item2)), inline=False)
    if recipe.item3 != "":
        embed.add_field(name="Item 3", value="%ix %s" % (recipe.qty3, titlecase(recipe.item3)), inline=False)
    if recipe.notes != "":
        embed.add_field(name="Notes", value="%s" % recipe.notes, inline=False)

    await ctx.respond(embed=embed)


@bot.slash_command(name="monster", description="Sends info about a monster.")
async def _monster(ctx,
                   monster_identifier: Option(str, "Monster Identifier (Ex. Slime or 1)", required=True)):
    with open("monsters.json", "r", encoding="utf-8") as fp:
        data = json.load(fp)

    monsters = data["monsters"]
    if int_from_string(monster_identifier) == "":
        indexes = list(filter(lambda r: clean_text(r["name"].lower()) == clean_text(monster_identifier.lower()) or
                              clean_text(r.get("altname", "").lower()) == clean_text(monster_identifier.lower()), monsters))
    else:
        indexes = list(filter(lambda r: int_from_string(r["number"]) == int_from_string(monster_identifier), monsters))

    if len(indexes) == 0:
        embed = create_embed("No monster found with the identifier `%s`. Please check spelling and try again."
                             % monster_identifier)
        return await ctx.respond(embed=embed)

    embeds = []
    for index in indexes:
        index["num_str"] = index["number"]
        index["number"] = int_from_string(index["number"])

        monster = parsers.Monster.from_dict(index)

        title = "%s - %s (Level: %s)" % (monster.num_str, titlecase(monster.name), monster.level)
        description = '''
**Family:** %s | **EXP:** %s | **Gold:** %s

**HP:** %s | **MP:** %s | **ATK:** %s | **DEF:** %s | **AGI:** %s

**Fire:** %s | **Ice:** %s | **Wind:** %s
**Blast:** %s | **Earth:** %s | **Dark:** %s | **Light:** %s

**Haunts:** %s
''' % (monster.family, monster.exp, monster.gold,
       monster.hp, monster.mp, monster.atk, monster.defn, monster.agi,
       monster.fire, monster.ice, monster.wind,
       monster.blast, monster.earth, monster.dark, monster.light,
       titlecase(monster.haunts))
        if monster.drop1 != "":
            description += "\n**__Drop 1 | Common Drop__**\n%s\n" % titlecase(monster.drop1)
        if monster.drop2 != "":
            description += "\n**__Drop 2 | Rare Drop__**\n%s\n" % titlecase(monster.drop2)
        if monster.drop3 != "":
            description += "\n**__Drop 3__**\n%s\n" % titlecase(monster.drop3)

        if monster.image == "":
            monster.image = monster_images_url % clean_text(monster.name, False)

        embed = create_embed(title, description, image=monster.image)
        embeds.append(embed)

    if len(embeds) > 1:
        paginator = create_paginator(embeds)
        await paginator.respond(ctx.interaction)
    else:
        await ctx.respond(embed=embeds[0])


@bot.slash_command(name="character", description="Sends info for a random character.")
async def _character(ctx):
    gender = random.choice(["Male", "Female"])
    body_type = random.randint(1, 5)
    hair_style = random.randint(1, 10)
    hair_color = random.randint(1, 10)
    face_style = random.randint(1, 10)
    skin_tone = random.randint(1, 8)
    eye_color = random.randint(1, 8)

    description = '''
**Gender:** %s
    
**Body Type:** %s
    
**Hair Style:** %s
    
**Hair Color:** %s
    
**Face Style:** %s
    
**Skin Tone:** %s
    
**Eye Color:** %s
''' % (gender, body_type, hair_style, hair_color, face_style, skin_tone, eye_color)
    embed = create_embed("Random Character Generator", description)

    await ctx.respond(embed=embed)


@bot.slash_command(name="grotto", description="Sends info about a grotto.")
async def _grotto(ctx,
                  material: Option(str, "Material (Ex. Granite)", choices=parsers.grotto_prefixes, required=True),
                  environment: Option(str, "Environment (Ex. Tunnel)", choices=parsers.grotto_environments,
                                      required=True),
                  suffix: Option(str, "Suffix (Ex. Woe)", choices=parsers.grotto_suffixes, required=True),
                  level: Option(int, "Level (Ex. 1)", required=True),
                  location: Option(str, "Location (Ex. 05)", required=False)):
    await grotto_func(ctx, material, environment, suffix, level, location)


@bot.slash_command(name="gg", description="Sends info about a grotto with location required.")
async def _grotto_location(ctx,
                  material: Option(str, "Material (Ex. Granite)", choices=parsers.grotto_prefixes, required=True),
                  environment: Option(str, "Environment (Ex. Tunnel)", choices=parsers.grotto_environments,
                                      required=True),
                  suffix: Option(str, "Suffix (Ex. Woe)", choices=parsers.grotto_suffixes, required=True),
                  level: Option(int, "Level (Ex. 1)", required=True),
                  location: Option(str, "Location (Ex. 05)", required=True)):
    await grotto_func(ctx, material, environment, suffix, level, location)


async def grotto_func(ctx, material, environment, suffix, level, location):
    async with aiohttp.ClientSession() as session:
        params = {
            "search": "Search",
            "prefix": str(parsers.grotto_prefixes.index(titlecase(material)) + 1),
            "envname": str(parsers.grotto_environments.index(titlecase(environment)) + 1),
            "suffix": str(parsers.grotto_suffixes.index(titlecase(suffix)) + 1),
            "level": str(level),
        }

        if location is not None:
            params["loc"] = str(int(location, base=16))

        async with session.get(grotto_search_url, params=params) as response:
            text = await response.text()
            selector = Selector(text=text)
            selector.xpath('//div[@class="minimap"]').drop()
            divs = selector.xpath('//div[@class="inner"]//text()')
            grottos = divs.getall()

            embeds = []

            for parsed in parsers.create_grotto(grottos):
                special = parsers.is_special(parsed)
                color = discord.Color.gold() if special else discord.Color.green()
                embed = create_embed(None, color=color)

                if special:
                    parsed = parsed[1:]

                zipped = zip(range(len(parsed)), parsers.grotto_keys, parsed)

                for i, key, value in zipped:
                    if key == "Name":
                        if special:
                            value = ":star: %s :star:" % value
                        embed.title = "%s\n[Click For Full Info]" % value
                    else:
                        if key == "Chests":
                            values = [str(x) for x in parsed[i:i + 10]]
                            chests = list(zip(parsers.grotto_ranks, values))
                            value = ", ".join([': '.join(x) for x in chests])
                        embed.add_field(name=key, value=value, inline=False)
                embed.url = str(response.url)
                embeds.append(embed)

            if len(embeds) == 1:
                embed = embeds[0]
            elif len(embeds) == 0:
                embed = create_embed("No grotto found. Please check parameters and try again.")

        if len(embeds) > 1:
            paginator = create_paginator(embeds)
            await paginator.respond(ctx.interaction)
        else:
            await ctx.respond(embed=embed)


def int_from_string(string):
    integer = ''.join(filter(str.isdigit, string))
    if integer != "":
        return int(integer)
    else:
        return ""


def clean_text(text, remove_spaces=True):
    text = text.lower().replace("'", "").replace("-", "").replace("ñ", "n")
    if remove_spaces:
        text = text.replace(" ", "")
    else:
        text = text.replace(" ", "_")

    return text


def create_paginator(embeds):
    pages = []
    for entry in embeds:
        pages.append(Page(embeds=[entry]))
    return Paginator(pages=pages)


def create_embed(title, description=None, color=discord.Color.green(),
                 footer="© CompuGenius Programs. All rights reserved.", image="", *, url="",
                 author="", author_url=""):
    embed = discord.Embed(title=title, description=description, url=url, color=color)
    embed.set_footer(text=footer)
    embed.set_thumbnail(url=image)
    embed.set_author(name=author, url=author_url)
    return embed


bot.run(token)
