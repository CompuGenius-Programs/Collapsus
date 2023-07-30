import io
import json
import math
import os
import random
from asyncio import sleep

import aiohttp
import discord
import dotenv
import emoji
from PIL import Image
from discord import Option
from discord.ext.pages import Paginator, Page as _Page
from parsel import Selector
from titlecase import titlecase

import parsers

dotenv.load_dotenv()
token = os.getenv("TOKEN")

bot = discord.Bot(intents=discord.Intents.all())

dev_id = 496392770374860811
dev_tag = "@CompuGeniusPrograms"
dev_paypal = "paypal.me/cgprograms | venmo.com/CompuGeniusCode"

guild_id = 655390550698098700
testing_channel = 973619817317797919

quests_channel = 766039065849495574

welcome_channel = 965688638295924766
rules_channel_en = 688480621856686196
rules_channel_fr = 965694046049800222
rules_channel_de = 965693961907875850
rules_channel_jp = 965693827568529448

role_en = 879436700256964700
role_fr = 965696709290262588
role_de = 965696853951795221
role_jp = 859563030220374057
role_celestrian = 655438935278878720

grotto_bot_channel = 845339551173050389

stream_channel = 655390551138631704

logo_url = "https://cdn.discordapp.com/emojis/856330729528361000.png"
website_url = "https://dq9.carrd.co"
server_invite_url = "https://discord.gg/DQ9"

grotto_search_url = "https://www.yabd.org/apps/dq9/grottosearch.php"

monster_images_url = "https://www.woodus.com/den/gallery/graphics/dq9ds/monster/%s.webp"

krak_pop_image_url = "https://cdn.discordapp.com/attachments/698157074420334612/982389321506099300/unknown.png"
item_images_url = "https://www.woodus.com/den/gallery/graphics/dq9ds/item/%s.png"
weapon_images_url = "https://www.woodus.com/den/gallery/graphics/dq9ds/weapon/%s.png"
armor_images_url = "https://www.woodus.com/den/gallery/graphics/dq9ds/armor/%s.png"
accessory_images_url = "https://www.woodus.com/den/gallery/graphics/dq9ds/accessory/%s.png"


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                        name="over The Quester's Rest. Type /help ."))


@bot.command(name="help", description="Get help for using the bot.")
async def _help(ctx):
    description = '''
A bot created by <@%s> for The Quester's Rest (<%s>).

**/character** - *Displays randomly-generated info for a character*
**/gg** - *Displays all info for a grotto (location required)*
**/grotto** - *Displays all info for a grotto*
**/monster** - *Displays all info for a monster*
**/quest** - *Displays all info for a specific quest*
**/recipe** - *Displays all info for a recipe*
**/song** - *Plays a song*
**/songs_all** - *Plays all songs*
**/stop** - *Stops playing a song*
**/translate** - *Translate a word or phrase*
**/translate_grotto(\_[language])** - *Translate a grotto name*

**/help** - *Displays this message*
''' % (dev_id, server_invite_url)

    embed = create_embed("Collapsus v2 Help [Click For Server Website]", description=description, error="",
                         image=logo_url, url=website_url)
    await ctx.respond(embed=embed)


async def get_songs(ctx: discord.AutocompleteContext):
    return [song for song in parsers.songs if ctx.value.lower() in song.lower()]


@bot.command(name="song", description="Plays a song.")
async def _song(ctx, song_name: Option(str, "Song Name", autocomplete=get_songs, required=True)):
    voice_client = discord.utils.get(bot.voice_clients, guild=bot.get_guild(guild_id))
    if voice_client is None or not voice_client.is_playing():
        voice_state = ctx.author.voice
        if voice_state is None:
            embed = create_embed("You need to be in a voice channel to use this command.")
            return await ctx.respond(embed=embed, ephemeral=True)

        channel = voice_state.channel.id
        if channel == stream_channel:
            embed = create_embed("You can't use this command in the stream channel.")
            return await ctx.respond(embed=embed, ephemeral=True)

        await ctx.defer()

        with open("songs.json", "r", encoding="utf-8") as fp:
            data = json.load(fp)
        songs = data["songs"]

        index = next(filter(lambda s: s["title"].lower() == song_name.lower(), songs), None)
        song = parsers.Song.from_dict(index)

        if voice_client is None:
            voice_client = await bot.get_channel(channel).connect()
        await play(ctx, voice_client, song, channel)

        embed = create_embed("Playing `%s` in <#%s>" % (song.title, channel))
        await ctx.followup.send(embed=embed)

        while voice_client.is_playing():
            await sleep(1)
        await voice_client.disconnect()
    else:
        embed = create_embed("I'm already playing a song. Please wait until it's finished.")
        return await ctx.respond(embed=embed, ephemeral=True)


@bot.command(name="songs_all", description="Plays all songs.")
async def _all_songs(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=bot.get_guild(guild_id))
    if voice_client is None or not voice_client.is_playing():
        voice_state = ctx.author.voice
        if voice_state is None:
            embed = create_embed("You need to be in a voice channel to use this command.")
            return await ctx.respond(embed=embed, ephemeral=True)

        channel = voice_state.channel.id
        if channel == stream_channel:
            embed = create_embed("You can't use this command in the stream channel.")
            return await ctx.respond(embed=embed, ephemeral=True)

        await ctx.respond("Playing all songs. Please wait...")

        with open("songs.json", "r", encoding="utf-8") as fp:
            data = json.load(fp)
        songs = data["songs"]

        if voice_client is None:
            voice_client = await bot.get_channel(channel).connect()

        message = None
        for index, s in enumerate(songs):
            if not voice_client.is_connected():
                break

            song = parsers.Song.from_dict(s)
            await play(ctx, voice_client, song, channel)

            embed = create_embed("Playing all songs. Currently playing `%s` in <#%s>" % (song.title, channel))
            try:
                await message.edit(embed=embed)
            except:
                message = await ctx.send(embed=embed)

            while voice_client.is_playing():
                await sleep(1)
        await voice_client.disconnect()
    else:
        embed = create_embed("I'm already playing a song. Please wait until it's finished.")
        return await ctx.respond(embed=embed, ephemeral=True)


@bot.command(name="stop", description="Stops playing a song.")
async def _stop_song(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=bot.get_guild(guild_id))
    if voice_client is None or not voice_client.is_playing():
        embed = create_embed("I'm not playing a song.")
        return await ctx.respond(embed=embed, ephemeral=True)

    await voice_client.disconnect()

    embed = create_embed("Stopped playing.")
    await ctx.respond(embed=embed)


async def play(ctx, voice_client, song: parsers.Song, channel):
    if voice_client.is_connected():
        source = discord.FFmpegPCMAudio(song.url, executable="ffmpeg")
        voice_client.play(source)


@bot.command(name="parse_quests", description="Parses the quests.")
async def _parse_quests(ctx):
    await ctx.defer()

    quests = []
    channel = bot.get_channel(quests_channel)
    archived_threads = await channel.archived_threads().flatten()
    for thread in archived_threads:
        messages = await thread.history().flatten()
        for message in messages:
            quests.append(parsers.parse_regex(parsers.Quest, message.content))

    data = {
        "quests": sorted(quests, key=lambda quest: quest["number"])
    }
    with open("quests.json", "w+", encoding="utf-8") as fp:
        json.dump(data, fp, indent=2)

    embed = create_embed("%i Quests Parsed Successfully" % len(quests))
    await ctx.followup.send(embed=embed)


@bot.command(name="quest", description="Sends info about a quest.")
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


@bot.command(name="translate", description="Translate a word or phrase to a different language.")
async def _translate(ctx,
                     phrase: Option(str, "Word or Phrase (Ex. Copper Sword)", required=True),
                     language_input: Option(str, "Input Language (Ex. English)", choices=parsers.translation_languages,
                                            required=True),
                     language_output: Option(str, "Output Language (Ex. Japanese)",
                                             choices=parsers.translation_languages, required=False)):
    data = {
        "translations": []
    }
    for file in parsers.translation_files:
        with open(file, "r", encoding="utf-8") as fp:
            data["translations"] += json.load(fp)["translations"]

    translations = data["translations"]

    index = next(filter(lambda r: clean_text(r[parsers.translation_languages_simple[
        parsers.translation_languages.index(language_input)]].lower()) == clean_text(phrase.lower()), translations),
                 None)
    if index is None:
        embed = create_embed("No word or phrase found matching `%s`. Please check phrase and try again." % phrase,
                             error="Any errors? Want to contribute? Please speak to %s" % dev_tag)
        return await ctx.respond(embed=embed)

    translation = parsers.Translation.from_dict(index)
    all_languages = [
        translation.english,
        translation.japanese,
        translation.spanish,
        translation.french,
        translation.german,
        translation.italian
    ]

    title = "Translation of: %s" % titlecase(all_languages[parsers.translation_languages.index(language_input)])
    color = discord.Color.green()
    embed = create_embed(title, color=color, error="Any errors? Want to contribute? Please speak to %s" % dev_tag)
    if language_output is not None:
        value = titlecase(all_languages[parsers.translation_languages.index(language_output)])
        if value != "":
            embed.add_field(name=language_output, value=value, inline=False)
        else:
            embed = create_embed("The word or phrase `%s` has not been translated to `%s`." % (phrase, language_output),
                                 error="Any errors? Want to contribute? Please speak to %s" % dev_tag)
            return await ctx.respond(embed=embed)
    else:
        for language, translation in zip(parsers.translation_languages, all_languages):
            if translation != "":
                embed.add_field(name=language, value=titlecase(translation), inline=False)

    await ctx.respond(embed=embed)


@bot.command(name="translate_grotto", description="Translate a grotto from English to a different language.")
async def _translate_grotto_english(ctx,
                                    material: Option(str, "Material (Ex. Granite)", choices=parsers.grotto_prefixes,
                                                     required=True),
                                    environment: Option(str, "Environment (Ex. Tunnel)",
                                                        choices=parsers.grotto_environments,
                                                        required=True),
                                    suffix: Option(str, "Suffix (Ex. Woe)", choices=parsers.grotto_suffixes,
                                                   required=True),
                                    language_output: Option(str, "Output Language (Ex. Japanese)",
                                                            choices=parsers.translation_languages, required=False),
                                    level: Option(int, "Level (Ex. 1)", required=False),
                                    location: Option(str, "Location (Ex. 05)", required=False)):
    await translate_grotto_command(ctx, material, environment, suffix, 0, language_output, level, location)


@bot.command(name="translate_grotto_japanese", description="Translate a grotto from Japanese to a different language.")
async def _translate_grotto_japanese(ctx,
                                     material: Option(str, "Material (Ex. Granite)",
                                                      choices=parsers.grotto_prefixes_japanese, required=True),
                                     suffix: Option(str, "Suffix (Ex. Woe)", choices=parsers.grotto_suffixes_japanesh,
                                                    required=True),
                                     environment: Option(str, "Environment (Ex. Tunnel)",
                                                         choices=parsers.grotto_environments_japanesh, required=True),
                                     language_output: Option(str, "Output Language (Ex. Japanese)",
                                                             choices=parsers.translation_languages, required=False),
                                     level: Option(int, "Level (Ex. 1)", required=False),
                                     location: Option(str, "Location (Ex. 05)", required=False)):
    await translate_grotto_command(ctx, material, environment, suffix, 1, language_output, level, location)


@bot.command(name="translate_grotto_spanish", description="Translate a grotto from Spanish to a different language.")
async def _translate_grotto_spanish(ctx,
                                    environment: Option(str, "Environment (Ex. Tunnel)",
                                                        choices=parsers.grotto_environments_spanish, required=True),
                                    material: Option(str, "Material (Ex. Granite)",
                                                     choices=parsers.grotto_prefixes_spanish, required=True),
                                    suffix: Option(str, "Suffix (Ex. Woe)", choices=parsers.grotto_suffixes_spanish,
                                                   required=True),
                                    language_output: Option(str, "Output Language (Ex. Japanese)",
                                                            choices=parsers.translation_languages, required=False),
                                    level: Option(int, "Level (Ex. 1)", required=False),
                                    location: Option(str, "Location (Ex. 05)", required=False)):
    await translate_grotto_command(ctx, material, environment, suffix, 2, language_output, level, location)


@bot.command(name="translate_grotto_french", description="Translate a grotto from French to a different language.")
async def _translate_grotto_french(ctx,
                                   environment: Option(str, "Environment (Ex. Tunnel)",
                                                       choices=parsers.grotto_environments_french, required=True),
                                   material: Option(str, "Material (Ex. Granite)",
                                                    choices=parsers.grotto_prefixes_french, required=True),
                                   suffix: Option(str, "Suffix (Ex. Woe)", choices=parsers.grotto_suffixes_french,
                                                  required=True),
                                   language_output: Option(str, "Output Language (Ex. Japanese)",
                                                           choices=parsers.translation_languages, required=False),
                                   level: Option(int, "Level (Ex. 1)", required=False),
                                   location: Option(str, "Location (Ex. 05)", required=False)):
    await translate_grotto_command(ctx, material, environment, suffix, 3, language_output, level, location)


@bot.command(name="translate_grotto_german", description="Translate a grotto from German to a different language.")
async def _translate_grotto_german(ctx,
                                   material: Option(str, "Material (Ex. Granite)",
                                                    choices=parsers.grotto_prefixes_german, required=True),
                                   environment: Option(str, "Environment (Ex. Tunnel)",
                                                       choices=parsers.grotto_environments_german, required=True),
                                   suffix: Option(str, "Suffix (Ex. Woe)", choices=parsers.grotto_suffixes_german,
                                                  required=True),
                                   language_output: Option(str, "Output Language (Ex. English)",
                                                           choices=parsers.translation_languages, required=False),
                                   level: Option(int, "Level (Ex. 1)", required=False),
                                   location: Option(str, "Location (Ex. 05)", required=False)):
    await translate_grotto_command(ctx, material, environment, suffix, 4, language_output, level, location)


@bot.command(name="translate_grotto_italian", description="Translate a grotto from Italian to a different language.")
async def _translate_grotto_italian(ctx,
                                    environment: Option(str, "Environment (Ex. Tunnel)",
                                                        choices=parsers.grotto_environments_italian, required=True),
                                    material: Option(str, "Material (Ex. Granite)",
                                                     choices=parsers.grotto_prefixes_italian, required=True),
                                    suffix: Option(str, "Suffix (Ex. Woe)", choices=parsers.grotto_suffixes_italian,
                                                   required=True),
                                    language_output: Option(str, "Output Language (Ex. English)",
                                                            choices=parsers.translation_languages, required=False),
                                    level: Option(int, "Level (Ex. 1)", required=False),
                                    location: Option(str, "Location (Ex. 05)", required=False)):
    await translate_grotto_command(ctx, material, environment, suffix, 5, language_output, level, location)


async def translate_grotto_command(ctx, material, environment, suffix, language_input, language_output, level,
                                   location):
    await ctx.defer()

    embed, material, environment, suffix = await translate_grotto(material, environment, suffix,
                                                                  parsers.translation_languages_simple[language_input],
                                                                  language_output)
    await ctx.followup.send(embed=embed)

    if level is not None:
        await grotto_command(ctx, material, environment, suffix, level, location)


async def get_recipes(ctx: discord.AutocompleteContext):
    with open("recipes.json", "r", encoding="utf-8") as fp:
        data = json.load(fp)
    recipes = data["recipes"]
    results = []
    for r in recipes:
        recipe = parsers.Recipe.from_dict(r)
        if ctx.value.lower() in recipe.result.lower():
            results.append(titlecase(recipe.result))
    return results


@bot.command(name="recipe", description="Sends info about a recipe.")
async def _recipe(ctx, creation_name: Option(str, "Creation (Ex. Special Medicine)", autocomplete=get_recipes,
                                             required=True)):
    with open("recipes.json", "r", encoding="utf-8") as fp:
        data = json.load(fp)

    recipes = data["recipes"]

    index = next(filter(lambda r: clean_text(r["result"]) == clean_text(creation_name.lower()), recipes), None)

    if index is None:
        embed = create_embed("Ahem! Oh dear. I'm afraid I don't seem to be\nable to make anything with that particular"
                             "\ncreation name of `%s`." % creation_name, image=krak_pop_image_url)
        return await ctx.respond(embed=embed)

    recipe = parsers.Recipe.from_dict(index)

    title = ":star: %s :star:" % titlecase(recipe.result) if recipe.alchemiracle else titlecase(recipe.result)
    color = discord.Color.gold() if recipe.alchemiracle else discord.Color.green()

    if recipe.image == "":
        recipe_images_url = ""
        if recipe.type.lower() in parsers.item_types:
            recipe_images_url = item_images_url
        elif recipe.type.lower() in parsers.weapon_types:
            recipe_images_url = weapon_images_url
        elif recipe.type.lower() in parsers.armor_types:
            recipe_images_url = armor_images_url
        elif recipe.type.lower() in parsers.accessory_types:
            recipe_images_url = accessory_images_url

        if recipe_images_url != "":
            recipe.image = recipe_images_url % clean_text(recipe.result, False, True)
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


async def get_monsters(ctx: discord.AutocompleteContext):
    with open("monsters.json", "r", encoding="utf-8") as fp:
        data = json.load(fp)
    monsters = data["monsters"]
    results = []
    for m in monsters:
        monster = parsers.Monster.from_dict(m)
        if ctx.value.lower() in monster.name.lower() or ctx.value.lower() in monster.number.lower():
            results.append(monster.number + " - " + titlecase(monster.name))
    return results


@bot.command(name="monster", description="Sends info about a monster.")
async def _monster(ctx,
                   monster_identifier: Option(str, "Monster Identifier (Ex. Slime or 1)", autocomplete=get_monsters,
                                              required=True)):
    with open("monsters.json", "r", encoding="utf-8") as fp:
        data = json.load(fp)

    monsters = data["monsters"]

    monster_number = 0

    if " - " in monster_identifier:
        monster_number = monster_identifier.split(" - ")[0]
        indexes = list(filter(lambda r: clean_text(r["name"].lower()) == clean_text(
            monster_identifier.split(" - ")[1].lower()) or clean_text(
            r.get("altname", "").lower()) == clean_text(monster_identifier.split(" - ")[1].lower()), monsters))
    else:
        indexes = list(filter(
            lambda r: clean_text(r["name"].lower()) == clean_text(monster_identifier.lower()) or clean_text(
                r.get("altname", "").lower()) == clean_text(
                monster_identifier.lower()), monsters))
        if not indexes:
            monster_number = "#" + "%03d" % int_from_string(monster_identifier) + monster_identifier[-1] if \
                monster_identifier[-1].isalpha() else ""
            indexes = list(
                filter(lambda r: int_from_string(r["number"]) == int_from_string(monster_identifier), monsters))

    if len(indexes) == 0:
        embed = create_embed("No monster found with the identifier `%s`. Please check spelling and try again."
                             % monster_identifier)
        return await ctx.respond(embed=embed)

    proper_page = 0
    embeds = []
    for index in indexes:
        monster = parsers.Monster.from_dict(index)

        title = "%s - %s (Level: %s)" % (monster.number, titlecase(monster.name), monster.level)
        description = '''
**Family:** %s | **EXP:** %s | **Gold:** %s

**HP:** %s | **MP:** %s | **ATK:** %s | **DEF:** %s | **AGI:** %s

**Fire:** %s | **Ice:** %s | **Wind:** %s
**Blast:** %s | **Earth:** %s | **Dark:** %s | **Light:** %s

**Haunts:** %s
''' % (
            monster.family, monster.exp, monster.gold, monster.hp, monster.mp, monster.atk, monster.defn, monster.agi,
            monster.fire, monster.ice, monster.wind, monster.blast, monster.earth, monster.dark, monster.light,
            titlecase(monster.haunts)
        )
        if monster.drop1 != "":
            description += "\n**__Drop 1 | Common Drop__**\n%s\n" % titlecase(monster.drop1)
        if monster.drop2 != "":
            description += "\n**__Drop 2 | Rare Drop__**\n%s\n" % titlecase(monster.drop2)
        if monster.drop3 != "":
            description += "\n**__Drop 3__**\n%s\n" % titlecase(monster.drop3)

        if monster.image == "":
            monster.image = monster_images_url % clean_text(monster.name, False, True)

        embed = create_embed(title, description, image=monster.image)
        embeds.append(embed)

        if monster_number != 0 and monster_number == monster.number:
            proper_page = len(embeds) - 1

    if len(embeds) > 1:
        paginator = create_paginator(embeds, None)
        await paginator.respond(ctx.interaction)
        await paginator.goto_page(proper_page)
    else:
        await ctx.respond(embed=embeds[0])


@bot.command(name="character", description="Sends info for a randomly-generated character.")
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


@bot.command(name="grotto", description="Sends info about a grotto.")
async def _grotto(ctx,
                  material: Option(str, "Material (Ex. Granite)", choices=parsers.grotto_prefixes, required=True),
                  environment: Option(str, "Environment (Ex. Tunnel)", choices=parsers.grotto_environments,
                                      required=True),
                  suffix: Option(str, "Suffix (Ex. Woe)", choices=parsers.grotto_suffixes, required=True),
                  level: Option(int, "Level (Ex. 1)", required=True),
                  location: Option(str, "Location (Ex. 05)", required=False)):
    await grotto_command(ctx, material, environment, suffix, level, location)


@bot.command(name="gg", description="Sends info about a grotto with location required.")
async def _grotto_location(ctx,
                           material: Option(str, "Material (Ex. Granite)", choices=parsers.grotto_prefixes,
                                            required=True),
                           environment: Option(str, "Environment (Ex. Tunnel)", choices=parsers.grotto_environments,
                                               required=True),
                           suffix: Option(str, "Suffix (Ex. Woe)", choices=parsers.grotto_suffixes, required=True),
                           level: Option(int, "Level (Ex. 1)", required=True),
                           location: Option(str, "Location (Ex. 05)", required=True)):
    await grotto_command(ctx, material, environment, suffix, level, location)


async def grotto_command(ctx, material, environment, suffix, level, location):
    if not ctx.response.is_done():
        await ctx.defer()

    embeds, files = await grotto_func(material, environment, suffix, level, location)

    if len(embeds) > 1:
        paginator = create_paginator(embeds, files)
        await paginator.respond(ctx.interaction)
    else:
        if len(embeds) == 1:
            embed = embeds[0]
            fs = [file["file"] for file in files if file["id"] == 0]
            file_name = "collages/collage0.png"
            create_collage(fs, file_name)
            with open(file_name, 'rb') as fp:
                data = io.BytesIO(fp.read())
            file = discord.File(data, file_name.removeprefix("collages/"))
            embed.set_image(url="attachment://%s" % file_name.removeprefix("collages/"))
        else:
            embed = create_embed("No grotto found. Please check parameters and try again.")
            file = None

        if file is not None:
            await ctx.followup.send(embed=embed, file=file)
        else:
            await ctx.followup.send(embed=embed)


async def grotto_func(material, environment, suffix, level, location):
    async with aiohttp.ClientSession() as session:
        params = {
            "search": "Search",
            "prefix": str(parsers.grotto_prefixes.index(titlecase(material)) + 1),
            "envname": str(parsers.grotto_environments.index(titlecase(environment)) + 1),
            "suffix": str(parsers.grotto_suffixes.index(suffix) + 1),
            "level": str(level),
        }

        if location is not None:
            try:
                params["loc"] = str(int(location, base=16))
            except ValueError:
                pass

        async with session.get(grotto_search_url, params=params) as response:
            text = await response.text()
            selector = Selector(text=text)
            divs = selector.xpath('//div[@class="inner"]//text()')
            grottos = divs.getall()

            embeds = []
            files = []

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
                        if key == "Seed":
                            value = str(value).zfill(4)
                        if key == "Chests":
                            values = [str(x) for x in parsed[i:i + 10]]
                            chests = list(zip(parsers.grotto_ranks, values))
                            value = ", ".join([': '.join(x) for x in chests])
                        if key == "Locations":
                            values = [str(x).zfill(2) for x in parsed[i + 9:]]
                            for v in values:
                                files.append({"id": len(embeds), "file": "grotto_images/%s.png" % v})
                            value = ', '.join(values)
                        embed.add_field(name=key, value=value, inline=False)
                embed.url = str(response.url)
                embeds.append(embed)

        return embeds, files


async def translate_grotto(material, environment, suffix, language_input, language_output):
    with open("grottos_translated.json", "r", encoding="utf-8") as fp:
        data = json.load(fp)

    translations = data["translations"]

    translation = parsers.Translation

    translation_english = []
    translation_japanese = []
    translation_spanish = []
    translation_french = []
    translation_german = []
    translation_italian = []

    phrases = [material, environment, suffix]
    for p in phrases:
        index = next(filter(lambda r: r[language_input].lower() == p.lower(), translations), None)

        translation = parsers.Translation.from_dict(index)

        translation_english.append(translation.english)
        translation_japanese.append(translation.japanese)
        translation_spanish.append(translation.spanish)
        translation_french.append(translation.french)
        translation_german.append(translation.german)
        translation_italian.append(translation.italian)

    translation.english = "%s %s %s" % (translation_english[0], translation_english[1], translation_english[2])
    translation.japanese = "%s%s%s" % (translation_japanese[0], translation_japanese[2], translation_japanese[1])
    translation.spanish = "%s %s %s" % (translation_spanish[1], translation_spanish[0], translation_spanish[2])
    translation.french = "%s %s %s" % (translation_french[1], translation_french[0], translation_french[2])
    translation.german = "%s%s %s" % (translation_german[0], translation_german[1], translation_german[2])
    translation.italian = "%s %s %s" % (translation_italian[1], translation_italian[0], translation_italian[2])

    all_languages = [
        translation.english,
        translation.japanese,
        translation.spanish,
        translation.french,
        translation.german,
        translation.italian
    ]

    title = "Translation of: %s" % titlecase(all_languages[parsers.translation_languages_simple.index(language_input)])
    color = discord.Color.green()
    embed = create_embed(title, color=color, error="Any errors? Want to contribute? Please speak to %s" % dev_tag)
    if language_output is not None:
        value = all_languages[parsers.translation_languages.index(language_output)]
        if value != "":
            embed.add_field(name=language_output, value=value, inline=False)
    else:
        for language, translation in zip(parsers.translation_languages, all_languages):
            if translation != "":
                embed.add_field(name=language, value=translation, inline=False)

    return embed, translation_english[0], translation_english[1], translation_english[2]


@bot.event
async def on_raw_reaction_add(payload):
    emoji_name = emoji.demojize(payload.emoji.name)
    channel = bot.get_channel(payload.channel_id)
    guild = bot.get_guild(payload.guild_id)
    user = guild.get_member(payload.user_id)

    rules_channels = [
        bot.get_channel(rules_channel_en),
        bot.get_channel(rules_channel_fr),
        bot.get_channel(rules_channel_de),
        bot.get_channel(rules_channel_jp)
    ]

    message = await channel.fetch_message(payload.message_id)
    if message.channel == bot.get_channel(welcome_channel):
        role_id = 0
        if emoji_name == ":United_Kingdom:":
            role_id = role_en
        if emoji_name == ":France:":
            role_id = role_fr
        if emoji_name == ":Germany:":
            role_id = role_de
        if emoji_name == ":Japan:":
            role_id = role_jp

        await user.add_roles(discord.utils.get(guild.roles, id=role_id), reason="User assigned role to themselves.")

    elif message.channel in rules_channels:
        if emoji_name == ":thumbs_up:":
            await user.add_roles(discord.utils.get(guild.roles, id=role_celestrian), reason="User accepted rules.")
            await message.remove_reaction(payload.emoji, user)


@bot.event
async def on_raw_reaction_remove(payload):
    emoji_name = emoji.demojize(payload.emoji.name)
    channel = bot.get_channel(payload.channel_id)
    guild = bot.get_guild(payload.guild_id)
    user = guild.get_member(payload.user_id)

    message = await channel.fetch_message(payload.message_id)
    if message.channel == bot.get_channel(welcome_channel):
        role_id = 0
        if emoji_name == ":United_Kingdom:":
            role_id = role_en
        if emoji_name == ":France:":
            role_id = role_fr
        if emoji_name == ":Germany:":
            role_id = role_de
        if emoji_name == ":Japan:":
            role_id = role_jp

        await user.remove_roles(discord.utils.get(guild.roles, id=role_id), reason="User removed role from themselves.")


@bot.event
async def on_voice_state_update(member, before, after):
    voice_client = discord.utils.get(bot.voice_clients, guild=bot.get_guild(guild_id))
    if voice_client is None:
        return
    music_voice_channel = voice_client.channel
    if len(music_voice_channel.members) <= 1:
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()


def int_from_string(string):
    integer = ''.join(filter(str.isdigit, string))
    if integer != "":
        return int(integer)
    else:
        return ""


def clean_text(text, remove_spaces=True, url=False):
    text = text.lower().replace("'", "").replace("’", "").replace("ñ", "n").replace("ó", "o").replace(
        ".", "")
    text = text.replace("-", "_") if url else text.replace("-", "")
    if remove_spaces:
        text = text.replace(" ", "")
    else:
        text = text.replace(" ", "_")

    return text


class Page(_Page):
    def update_files(self) -> list[discord.File] | None:
        """Updates :class:`discord.File` objects so that they can be sent multiple
        times. This is called internally each time the page is sent.
        """
        for file in self._files:
            if file.fp.closed and (fn := getattr(file.fp, "name", None)):
                file.fp = open(fn, "rb")
            file.reset()
            file.fp.close = lambda: None
        return self._files


def create_paginator(embeds, files):
    pages = []
    for entry in embeds:
        if files is None:
            page = Page(embeds=[entry])
        else:
            fs = [file["file"] for file in files if file["id"] == embeds.index(entry)]
            file_name = "collages/collage%s.png" % embeds.index(entry)
            create_collage(fs, file_name)
            with open(file_name, 'rb') as fp:
                data = io.BytesIO(fp.read())
            file = discord.File(data, file_name.removeprefix("collages/"))
            entry.set_image(url="attachment://%s" % file_name.removeprefix("collages/"))
            page = Page(embeds=[entry], files=[file])
        pages.append(page)
    return Paginator(pages=pages)


def create_collage(files, file_name):
    columns = math.ceil(math.sqrt(len(files)))
    rows = math.ceil(len(files) / columns)
    collage = Image.new("RGBA", (128 * columns, 96 * rows))
    index = 0
    for row in range(rows):
        for col in range(columns):
            if index < len(files):
                image = Image.open(files[index])
                collage.paste(image, (128 * col, 96 * row))
                index += 1

    collage.save(file_name)


def create_embed(title, description=None, color=discord.Color.green(),
                 footer="Consider supporting the developer at %s" % dev_paypal,
                 error="Any errors? Please report to %s" % dev_tag,
                 image="", *, url="", author=""):
    embed = discord.Embed(title=title, description=description, url=url, color=color)
    embed.set_footer(text="%s\n%s" % (footer, error))
    if image != "":
        embed.set_thumbnail(url=image)
    embed.set_author(name=author)
    return embed


bot.run(token)
