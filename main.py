import json
import os

import discord
import dotenv
from discord import Option

import parsers

dotenv.load_dotenv()
token = os.getenv("TOKEN")

bot = discord.Bot()

guild_id = 655390550698098700
quests_channel = 766039065849495574

logo_url = "https://cdn.discordapp.com/emojis/856330729528361000.png"
website_url = "https://dq9.carrd.co"


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                        name="for commands in The Quester's Rest. Type /help."))


@bot.slash_command(name="help", description="Get help for using the bot.", guild_ids=[guild_id])
async def help(ctx):
    description = '''
    A bot created by <@496392770374860811> for The Quester's Rest.

    /quest_info [1-184] | Displays all info for a specific quest
    /help | Displays this message
    '''

    embed = create_embed(title="Collapsus v2 Help", description=description, color=discord.Color.green(),
                         image=logo_url, url=website_url,
                         footer="© CompuGenius Programs. All rights reserved.")
    await ctx.respond(embed=embed)


@bot.slash_command(name="parse_quests", description="Parses the quests.", guild_ids=[guild_id])
async def parse_quests(ctx):
    await ctx.defer()

    quests = []
    channel = bot.get_channel(quests_channel)
    for thread in channel.threads:
        messages = await thread.history(oldest_first=True).flatten()
        for message in messages:
            quests.append(parsers.parse_regex(parsers.Quest, message.content))

    data = {
        "quests": quests
    }
    with open("quests.json", "w+", encoding="utf-8") as fp:
        json.dump(data, fp, indent=4)

    await ctx.followup.send("%i Quests Parsed Successfully" % len(quests))


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
        None, color, "Pre-reqs: %s" % quest.prerequisite
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

    await ctx.respond(embed=embed)


def create_embed(title, description, color, footer, image="", *, url="", author="", author_url=""):
    embed = discord.Embed(title=title, description=description, url=url, color=color)
    embed.set_footer(text=footer)
    embed.set_thumbnail(url=image)
    embed.set_author(name=author, url=author_url)
    return embed


bot.run(token)
