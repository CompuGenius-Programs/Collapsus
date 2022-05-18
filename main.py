import json
import os

import aiohttp
import discord
import dotenv
from discord import Option
from discord.ext.pages import Paginator, Page
from parsel import Selector

import parsers

dotenv.load_dotenv()
token = os.getenv("TOKEN")

bot = discord.Bot()

guild_id = 655390550698098700
quests_channel = 766039065849495574

logo_url = "https://cdn.discordapp.com/emojis/856330729528361000.png"
website_url = "https://dq9.carrd.co"

grotto_search_url = "https://www.yabd.org/apps/dq9/grottosearch.php"


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                        name="over The Quester's Rest. Type /help ."))


@bot.slash_command(name="help", description="Get help for using the bot.", guild_ids=[guild_id])
async def help(ctx):
    description = '''
    A bot created by <@496392770374860811> for The Quester's Rest.

    /quest_info [Quest Number (1-184)] | Displays all info for a specific quest
    /grotto_info [Material (Ex. Granite)] [Environment (Ex. Tunnel)] [Suffix (Ex. Woe)] [Level (Ex. 1)] <Location (Ex. 05)>
    /help | Displays this message
    '''

    embed = create_embed(title="Collapsus v2 Help", description=description, color=discord.Color.green(),
                         image=logo_url, url=website_url)
    await ctx.respond(embed=embed)


@bot.slash_command(name="parse_quests", description="Parses the quests.", guild_ids=[guild_id])
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

    embed = create_embed("%i Quests Parsed Successfully" % len(quests), None, discord.Color.green())
    await ctx.followup.send(embed=embed)


@bot.slash_command(name="quest_info", description="Sends info about a quest.", guild_ids=[guild_id])
async def quest_info(ctx, quest_number: Option(int, "Quest Number (1-184)", required=True)):
    with open("quests.json", "r", encoding="utf-8") as fp:
        data = json.load(fp)

    quests = data["quests"]
    quest = parsers.Quest.from_dict(quests[quest_number - 1])

    title = ":star: Quest #%i - %s :star:" % (quest.number, quest.name) if quest.story \
        else "Quest #%i - %s" % (quest.number, quest.name)
    color = discord.Color.gold() if quest.story else discord.Color.green()
    embed = create_embed(
        title,
        None, color,
    )
    if quest.location != "":
        embed.add_field(name="Location", value=quest.location, inline=False)
    if quest.request != "":
        embed.add_field(name="Request", value=quest.request, inline=False)
    if quest.solution != "":
        embed.add_field(name="Solution", value=quest.solution, inline=False)
    if quest.reward != "":
        embed.add_field(name="Reward", value=quest.reward, inline=False)
    embed.add_field(name="Repeat", value="Yes" if quest.repeat else "No", inline=False)
    embed.add_field(name="Pre-reqs", value=quest.prerequisite, inline=False)

    await ctx.respond(embed=embed)


@bot.slash_command(name="grotto_info", description="Sends info about a grotto.", guild_ids=[guild_id])
async def quest_info(ctx,
                     material: Option(str, "Material (Ex. Granite)", required=True),
                     environment: Option(str, "Environment (Ex. Tunnel)", required=True),
                     suffix: Option(str, "Suffix (Ex. Woe)", required=True),
                     level: Option(int, "Level (Ex. 1)", required=True),
                     location: Option(str, "Location (Ex. 05)", required=False)):
    async with aiohttp.ClientSession() as session:
        params = {
            "search": "Search",
            "prefix": str(parsers.grotto_prefixes.index(material.title()) + 1),
            "envname": str(parsers.grotto_environments.index(environment.title()) + 1),
            "suffix": str(parsers.grotto_suffixes.index(suffix.title()) + 1),
            "level": str(level),
        }

        if location != "":
            params["loc"] = str(int(location, base=16))

        async with session.get(grotto_search_url, params=params) as response:
            text = await response.text()
            selector = Selector(text=text)
            selector.xpath('//div[@class="minimap"]').remove()
            divs = selector.xpath('//div[@class="inner"]//text()')
            grottos = divs.getall()

            entries = []

            for parsed in parsers.create_grotto(grottos):
                special = parsers.is_special(parsed)
                color = discord.Color.gold() if special else discord.Color.green()
                embed = create_embed(None, None, color)

                if special:
                    parsed = parsed[1:]

                zipped = zip(range(len(parsed)), parsers.grotto_keys, parsed)

                for i, key, value in zipped:
                    if key == "Name":
                        if special:
                            value = ":star: %s :star:" % value
                        embed.title = value
                    else:
                        if key == "Chests (S - I)":
                            ranks = ["**S**", "**A**", "**B**", "**C**", "**D**", "**E**", "**F**", "**G**", "**H**", "**I**"]
                            values = [str(x) for x in parsed[i:i + 10]]
                            chests = list(zip(ranks, values))
                            value = ", ".join([': '.join(x) for x in chests])
                        embed.add_field(name=key, value=value, inline=False)
                embed.url = str(response.url)
                entries.append(embed)

            if len(entries) == 1:
                embed = entries[0]
            elif len(entries) == 0:
                embed = create_embed("Invalid Grotto", None, discord.Color.green())

        if len(entries) > 1:
            pages = []
            for entry in entries:
                pages.append(Page(embeds=[entry]))
            paginator = Paginator(pages=pages)
            await paginator.respond(ctx.interaction)
        else:
            await ctx.respond(embed=embed)


def create_embed(title, description, color, footer="© CompuGenius Programs. All rights reserved.", image="", *, url="",
                 author="", author_url=""):
    embed = discord.Embed(title=title, description=description, url=url, color=color)
    embed.set_footer(text=footer)
    embed.set_thumbnail(url=image)
    embed.set_author(name=author, url=author_url)
    return embed


bot.run(token)
