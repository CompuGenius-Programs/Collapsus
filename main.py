import io
import json
import os
import random
from asyncio import sleep

import discord
import dotenv
import emoji
from discord import Option
from discord.ext.pages import Page as _Page
from titlecase import titlecase

import cascade_recipes
import parsers
from utils import create_embed, clean_text, dev_tag, int_from_string, create_paginator, create_collage

dotenv.load_dotenv()
token = os.getenv("TOKEN")

bot = discord.Bot(intents=discord.Intents.all())

dev_id = 496392770374860811

guild_id = 655390550698098700
testing_channel = 973619817317797919

quests_channel = 766039065849495574

welcome_channel = 965688638295924766
rules_channel_en = 688480621856686196
rules_channel_fr = 965694046049800222
rules_channel_de = 965693961907875850
rules_channel_jp = 965693827568529448
rules_channel_es = 1221871725663223818

role_en = 879436700256964700
role_fr = 965696709290262588
role_de = 965696853951795221
role_jp = 859563030220374057
role_es = 1221871392451203113
role_celestrian = 655438935278878720

stream_channel = 655390551138631704

logo_url = "https://cdn.discordapp.com/emojis/856330729528361000.png"
website_url = "https://dq9.carrd.co"
server_invite_url = "https://discord.gg/DQ9"

character_image_url = "https://www.woodus.com/den/games/dq9ds/characreate/index.php?"

monster_images_url = "https://www.woodus.com/den/gallery/graphics/dq9ds/monster/%s.webp"

krak_pot_image_url = "https://cdn.discordapp.com/emojis/866763396108386304.png"
item_images_url = "https://www.woodus.com/den/gallery/graphics/dq9ds/item/%s.png"
weapon_images_url = "https://www.woodus.com/den/gallery/graphics/dq9ds/weapon/%s.png"
armor_images_url = "https://www.woodus.com/den/gallery/graphics/dq9ds/armor/%s.png"
shield_images_url = "https://www.woodus.com/den/gallery/graphics/dq9ds/shield/%s.png"
accessory_images_url = "https://www.woodus.com/den/gallery/graphics/dq9ds/accessory/%s.png"


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="over The Quester's Rest. Type /help ."))


@bot.command(name="help", description="Get help for using the bot.")
async def _help(ctx):
    description = '''
A bot created by <@%s> for The Quester's Rest (<%s>).

**/character** - *Generate a random character*
**/gg** - *Get grotto info (location required)*
**/grotto** - *Search for a grotto*
**/monster** - *Get monster info*
**/quest** - *Get quest info*
**/recipe** - *Get an item's recipe*
**/song** - *Play a song*
**/songs_all** - *Play all songs*
**/stop** - *Stop playing songs*
**/translate** - *Translate a word or phrase*
**/grotto_translate(\_[language])** - *Translate a grotto*

**/help** - *Displays this message*
''' % (dev_id, server_invite_url)

    embed = create_embed("Collapsus v2 Help [Click For Server Website]", description=description, error="",
                         image=logo_url, url=website_url)
    await ctx.respond(embed=embed)


@bot.command(name="migrate_resources")
async def _migrate_resources(ctx):
    await ctx.defer()

    test_mode = os.getenv("TEST_MODE", "FALSE").lower() == "true"

    test_resources_channel = 1142886986949087272
    resources_channel = 1143509536783736965

    if test_mode:
        resources_channel = test_resources_channel

    migrations = [
        {"test_channel": 1142195240833388655, "channel": 891711067976249375, "thread": True, "title": "Grotto Info"},
        {"test_channel": 1142195242494337034, "channel": 788454671684468771, "thread": True, "title": "Vocation Info"},
        {"test_channel": 1142195244264345670, "channel": 655463607030644747, "title": "EXP Manipulation", },
        {"test_channel": 1142195245661032479, "channel": 706892011718049802, "title": "Seed Farming", },
        {"test_channel": 1142195247158411274, "channel": 691066485279424582, "title": "Alchemy", },
        {"test_channel": 1142195248429269022, "channel": 766039065849495574, "thread": True, "title": "Quests List"},
        {"test_channel": 1142195249721118780, "channel": 688861170236391626, "title": "Hoimi Table", },
        {"test_channel": 1142195251159765044, "channel": 695401106305712228, "title": "Accolades", },
        {"test_channel": 1142195255446356030, "channel": 655392079819833354, "title": "Other Info"}]

    large_messages = []

    for migration in reversed(migrations):
        if test_mode:
            migration["channel"] = migration["test_channel"]

        if migration.get("thread", False):
            all_messages = []

            archived_threads = await bot.get_channel(migration["channel"]).archived_threads().flatten()
            for thread in archived_threads:
                messages = await thread.history().flatten()
                messages.sort(key=lambda message: message.created_at)
                all_messages.append(messages)

            all_messages.sort(key=lambda messages: messages[0].created_at)

            first_message_too_long = True
            while first_message_too_long:
                try:
                    post = await bot.get_channel(resources_channel).create_thread(migration["title"],
                                                                                  all_messages[0][0].content)
                    message = await post.fetch_message(post.id)
                    await message.edit(files=[await f.to_file() for f in all_messages[0][0].attachments])
                    first_message_too_long = False
                except discord.errors.HTTPException as ex:
                    if "Must be 2000 or fewer in length." in str(ex):
                        large_messages.append(all_messages[0][0])
                        all_messages[0] = all_messages[0][1:]

            all_messages[0] = all_messages[0][1:]

            for t, messages in enumerate(all_messages):
                for i, message in enumerate(messages):
                    try:
                        await post.send(content=message.content, files=[await f.to_file() for f in message.attachments])
                    except discord.errors.HTTPException as ex:
                        if "Must be 2000 or fewer in length." in str(ex):
                            large_messages.append(message)

            await post.edit(locked=True)

            embed = create_embed("Migrated messages from <#%s> to <#%s>." % (migration["channel"], post.id))
            await ctx.send(embed=embed)

        else:
            messages = await bot.get_channel(migration["channel"]).history().flatten()
            messages.sort(key=lambda message: message.created_at)

            first_message_too_long = True
            while first_message_too_long:
                try:
                    if migration["title"] == "Accolades":
                        first_part = """**Game Completion Accolades In order of Priority**:
```yml
Light-Speed Champion - clear time under 12 hours
Jot to Trot - clear time 12-19 hours
Sleeper on the Job - clear time 228+ hours
Easy Rider - clear time 152-227:59 hours
Exterminator - win 1500 battles
Shopaholic - wardrobe collection at 50%
Pacifist - 250 or fewer battles
Socialite - multiplayer time is 50%+ of total time played
Philanthropist - 60 quests cleared
Cartographer - 30 grottos cleared
Mighty Inviter - 50 tags (or maybe it's multiplayer sessions)
Entitled Adventurer - 60 accolades
Completely Potty - alchemy 120 times
Zoologist - defeated monster list 75%+
Punchbag - party wiped out 24+ times
Snappy Dresser - wardrobe collection at 38-49%
Recipe Researcher - recipes at 30%+
Moneybags - 90000+ gold (carried money + bank)
Grievous Angel - party wiped out 16-23 times
Monster Masher - 1000-1499 battles
Fleet Completer - clear time 19-26:59 hours
Steady Eddie/Edwina - clear time 76-151:59 hours
Party Hopper - multiplayer is 30% but less than 50% total time played
Immaculate Completion - party wiped out 0 times
Guardian Angel/Lionheart/Sent from Above/Watched-over One/Storied Saviour: Default titles. They depend on your class/level when completing.```"""
                        second_part = """**Grotto Accolades**:
```yml
1: Celestial Sentinel -- Awarded to xxx on the occasion of his/her victory over various renowned denizens of the depths.
[Defeat all Legacy Bosses.]

2: Heralded Hero/Heralded Heroine -- Awarded to xxx to commemorate his/her victory over a grotto boss of level 25 or above.

3: Superhero/Superheroine -- Awarded to xxx to commemorate his/her victory over a grotto boss of level 50 or above.

4: Heavenly Hero/Heavenly Heroine -- Awarded to xxx to commemorate his/her victory over a grotto boss of level 75 or above.

5: Legendary Hero/Legendary Heroine -- Awarded to xxx to commemorate his/her victory over a grotto boss of level 99.

6: Spelunker -- Presented to xxx for clearance of a grotto of level 25 or above.

7: Spunky Spelunker -- Presented to xxx for clearance of a grotto of level 50 or above.

8: Spelunking Specialist -- Presented to xxx for clearance of a grotto of level 75 or above.

9: Supreme Spelunker -- Presented to xxx for clearance of a grotto of level 99.

10: Cave Dweller -- Awarded to xxx on the occasion of his/her 10th grotto clearance.

11: Cave Craver -- Awarded to xxx on the occasion of his/her 50th grotto clearance.

12: From Cradle to Cave -- Awarded to xxx on the occasion of his/her 100th grotto clearance.

13: Stalag Mighty -- Awarded to xxx on the occasion of his/her 500th grotto clearance.

14: Caving Lunatic -- The Cavers' Cooperative would like to congratulate xxx for the outstanding achievement of completing 1000 grottoes.```"""

                        post = await bot.get_channel(resources_channel).create_thread(migration["title"], first_part)
                        await post.send(content=second_part)
                    else:
                        post = await bot.get_channel(resources_channel).create_thread(migration["title"],
                                                                                      messages[0].content)
                        message = await post.fetch_message(post.id)
                        await message.edit(files=[await f.to_file() for f in messages[0].attachments])
                    first_message_too_long = False
                except discord.errors.HTTPException as ex:
                    if "Must be 2000 or fewer in length." in str(ex):
                        large_messages.append(messages[0])
                        messages = messages[1:]

            for message in messages[1:]:
                try:
                    await post.send(content=message.content, files=[await f.to_file() for f in message.attachments])
                except discord.errors.HTTPException as ex:
                    if "Must be 2000 or fewer in length." in str(ex):
                        large_messages.append(message)

            await post.edit(locked=True)

            embed = create_embed("Migrated messages from <#%s> to <#%s>." % (migration["channel"], post.id))
            await ctx.send(embed=embed)

    if large_messages:
        desc = ""
        for message in large_messages:
            desc += "%s\n" % message.jump_url

        embed = create_embed("The following messages were too large to migrate.", desc)
        await ctx.send(embed=embed)

    embed = create_embed("Finished migration.")
    await ctx.followup.send(embed=embed)


@bot.command(name="migrate_challenges")
async def _migrate_challenges(ctx):
    await ctx.defer()

    test_mode = os.getenv("TEST_MODE", "FALSE").lower() == "true"

    test_challenges_channel = 1143641065560227910
    challenges_channel = 1143670710443716680

    if test_mode:
        challenges_channel = test_challenges_channel

    migrations = [{"test_channel": 1142195226312704061, "channel": 1020384998567706694, "title": "Challenges"},
                  {"test_channel": 1142195227742969877, "channel": 724610856565997599, "title": "Challenge Runs"}]

    large_messages = []

    for migration in reversed(migrations):
        if test_mode:
            migration["channel"] = migration["test_channel"]

        archived_threads = await bot.get_channel(migration["channel"]).archived_threads().flatten()
        for thread in archived_threads:
            messages = await thread.history().flatten()
            messages.sort(key=lambda message: message.created_at)

            first_message_too_long = True
            while first_message_too_long:
                try:
                    post = await bot.get_channel(challenges_channel).create_thread(
                        migration["title"] + " - " + thread.name.replace(" " + migration["title"], ""),
                        messages[0].content)
                    message = await post.fetch_message(post.id)
                    await message.edit(files=[await f.to_file() for f in messages[0].attachments])
                    first_message_too_long = False
                except discord.errors.HTTPException as ex:
                    if "Must be 2000 or fewer in length." in str(ex):
                        large_messages.append(messages[0])
                        messages = messages[1:]

            messages = messages[1:]

            for i, message in enumerate(messages):
                try:
                    await post.send(content=message.content, files=[await f.to_file() for f in message.attachments])
                except discord.errors.HTTPException as ex:
                    if "Must be 2000 or fewer in length." in str(ex):
                        large_messages.append(message)

            await post.edit(locked=True)

            embed = create_embed("Migrated messages from <#%s> to <#%s>." % (thread.id, post.id))
            await ctx.send(embed=embed)

    if large_messages:
        desc = ""
        for message in large_messages:
            desc += "%s\n" % message.jump_url

        embed = create_embed("The following messages were too large to migrate.", desc)
        await ctx.send(embed=embed)

    embed = create_embed("Finished migration.")
    await ctx.followup.send(embed=embed)


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

        with open("data/songs.json", "r", encoding="utf-8") as fp:
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

        with open("data/songs.json", "r", encoding="utf-8") as fp:
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

    data = {"quests": sorted(quests, key=lambda quest: quest["number"])}
    with open("data/quests.json", "w+", encoding="utf-8") as fp:
        json.dump(data, fp, indent=2)

    embed = create_embed("%i Quests Parsed Successfully" % len(quests))
    await ctx.followup.send(embed=embed)


@bot.command(name="quest", description="Sends info about a quest.")
async def _quest(ctx, quest_number: Option(int, "Quest Number (1-184)", required=True)):
    with open("data/quests.json", "r", encoding="utf-8") as fp:
        data = json.load(fp)

    quests = data["quests"]
    index = quest_number - 1
    if index >= len(quests) or index < 0:
        embed = create_embed("No quest found with the number `%s`. Please check number and try again." % quest_number)
        return await ctx.respond(embed=embed)

    quest = parsers.Quest.from_dict(quests[index])

    title = ":star: Quest #%i - %s :star:" % (quest.number, quest.name) if quest.story else "Quest #%i - %s" % (
        quest.number, quest.name)
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
async def _translate(ctx, phrase: Option(str, "Word or Phrase (Ex. Copper Sword)", required=True),
                     language_input: Option(str, "Input Language (Ex. English)", choices=parsers.translation_languages,
                                            required=True),
                     language_output: Option(str, "Output Language (Ex. Japanese)",
                                             choices=parsers.translation_languages, required=False)):
    data = {"translations": []}
    for file in parsers.translation_files:
        with open("data/" + file, "r", encoding="utf-8") as fp:
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
    all_languages = [translation.english, translation.japanese, translation.spanish, translation.french,
                     translation.german, translation.italian]

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


async def get_recipes(ctx: discord.AutocompleteContext):
    with open("data/recipes.json", "r", encoding="utf-8") as fp:
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
    with open("data/recipes.json", "r", encoding="utf-8") as fp:
        data = json.load(fp)

    recipes = data["recipes"]

    index = next(filter(lambda r: clean_text(r["result"]) == clean_text(creation_name.lower()), recipes), None)

    if index is None:
        embed = create_embed("Ahem! Oh dear. I'm afraid I don't seem to be\nable to make anything with that particular"
                             "\ncreation name of `%s`." % creation_name, image=krak_pot_image_url)
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
        elif recipe.type.lower() == "shields":
            recipe_images_url = shield_images_url

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


@bot.command(name="recipe_cascade", description="Sends cascading info about a recipe.")
async def _recipe_cascade(ctx, creation_name: Option(str, "Creation (Ex. Special Medicine)", autocomplete=get_recipes,
                                                     required=True)):
    location_file = "location_description.yml"

    ingredients = cascade_recipes.cascade(creation_name)
    if ingredients:
        recipe = ingredients[0]
        ingredients = ingredients[1:]

        main_description = ""
        if recipe.location != '':
            main_description += f"*{titlecase(recipe.location)}*\n\n"

        main_description += "**Ingredients**\n"
        main_description += "\n".join(
            [f"{' ' * (ing.level - 1)}- {titlecase(ing.name)} x{ing.count} ({ing.total})" for ing in ingredients])

        location_description = ""
        has_location = any(ing.location != '' for ing in ingredients)
        if has_location:
            location_description += "Locations\n\n"

            def remove_duplicates(ingredients):
                unique = []
                for ingredient in ingredients:
                    if not any(ingredient.name == ing.name for ing in unique):
                        unique.append(ingredient)
                return unique

            list_of_locations = remove_duplicates([ing for ing in ingredients if ing.location != ''])
            location_description += "\n\n".join(
                f"- {titlecase(ing.name)}: {titlecase(ing.location)}" for ing in list_of_locations)

        with open(location_file, "w", encoding="utf-8") as f:
            f.write(location_description.replace("#", ""))

        recipe_images_url = ""
        if recipe.type.lower() in parsers.item_types:
            recipe_images_url = item_images_url
        elif recipe.type.lower() in parsers.weapon_types:
            recipe_images_url = weapon_images_url
        elif recipe.type.lower() in parsers.armor_types:
            recipe_images_url = armor_images_url
        elif recipe.type.lower() in parsers.accessory_types:
            recipe_images_url = accessory_images_url
        elif recipe.type.lower() == "shields":
            recipe_images_url = shield_images_url

        if recipe_images_url != "":
            image = recipe_images_url % clean_text(recipe.name, False, True)
        else:
            image = None

        main_embed = create_embed(titlecase(recipe.name), main_description, image=image)
        # location_embed = create_embed(titlecase(recipe.name), location_description, image=image)
        # paginator = create_paginator([main_embed, location_embed])
        # await paginator.respond(ctx.interaction)
        await ctx.respond(embed=main_embed)
        await ctx.send(file=discord.File(location_file))
    else:
        embed = create_embed("Ahem! Oh dear. I'm afraid I don't seem to be\nable to make anything with that particular"
                             "\ncreation name of `%s`." % creation_name, image=krak_pot_image_url)
        return await ctx.respond(embed=embed)


async def get_monsters(ctx: discord.AutocompleteContext):
    with open("data/monsters.json", "r", encoding="utf-8") as fp:
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
    with open("data/monsters.json", "r", encoding="utf-8") as fp:
        data = json.load(fp)

    monsters = data["monsters"]

    monster_number = 0

    if " - " in monster_identifier:
        monster_number = monster_identifier.split(" - ")[0]
        indexes = list(filter(lambda r: clean_text(r["name"].lower()) == clean_text(
            monster_identifier.split(" - ")[1].lower()) or clean_text(r.get("altname", "").lower()) == clean_text(
            monster_identifier.split(" - ")[1].lower()), monsters))
    else:
        indexes = list(filter(
            lambda r: clean_text(r["name"].lower()) == clean_text(monster_identifier.lower()) or clean_text(
                r.get("altname", "").lower()) == clean_text(monster_identifier.lower()), monsters))
        if not indexes:
            monster_number = "#" + "%03d" % int_from_string(monster_identifier) + monster_identifier[-1] if \
                monster_identifier[-1].isalpha() else ""
            indexes = list(
                filter(lambda r: int_from_string(r["number"]) == int_from_string(monster_identifier), monsters))

    if len(indexes) == 0:
        embed = create_embed(
            "No monster found with the identifier `%s`. Please check spelling and try again." % monster_identifier)
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
''' % (monster.family, monster.exp, monster.gold, monster.hp, monster.mp, monster.atk, monster.defn, monster.agi,
       monster.fire, monster.ice, monster.wind, monster.blast, monster.earth, monster.dark, monster.light,
       titlecase(monster.haunts))
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

    keys = {"headcolor": skin_tone, "hairnum": hair_style, "haircolor": hair_color, "eyecolor": eye_color, }

    remapped_eyes_female = {1: 1, 2: 2, 3: 3, 4: 12, 5: 13, 6: 14, 7: 15, 8: 16, 9: 17, 10: 20, }

    remapped_eyes_male = {1: 4, 2: 5, 3: 6, 4: 7, 5: 8, 6: 9, 7: 10, 8: 11, 9: 18, 10: 19, }

    if gender == "Male":
        keys["hairnum"] += 10
        keys["eyesnum"] = remapped_eyes_male[face_style]
    else:
        keys["eyesnum"] = remapped_eyes_female[face_style]

    description = '''
**Gender:** %s
    
**Body Type:** %s
    
**Hair Style:** %s
    
**Hair Color:** %s
    
**Face Style:** %s
    
**Skin Tone:** %s
    
**Eye Color:** %s
''' % (gender, body_type, hair_style, hair_color, face_style, skin_tone, eye_color)

    params = ""
    for key, value in keys.items():
        params += "%s=%s&" % (key, value)

    embed = create_embed("Random Character Generator", description, image=character_image_url + params[:-1])

    await ctx.respond(embed=embed)


class TourneySelection(discord.ui.Select):
    def __init__(self, data):
        self.data = data
        super().__init__(placeholder="Vote for Your Choice!", min_values=1, max_values=1,
                         options=[discord.SelectOption(label=choice) for choice in self.data])

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("You voted for %s!" % interaction.data["values"][0], ephemeral=True)


@bot.command(name="tourney", description="Generates a tournament.")
async def _tourney(ctx, name: Option(str, "Name (Ex. Cutest Monster)", required=True),
                   amount: Option(int, "Amount (Ex. 8)", required=True),
                   data: Option(str, "Data (Ex. Monster)", choices=parsers.tourney_data_types, required=True)):
    await ctx.defer()

    data_type = data.lower()
    with open("data/%s.json" % data_type, "r", encoding="utf-8") as fp:
        json_data = json.load(fp)

    data_list = json_data[data_type]

    parser = getattr(parsers, data_type[:-1].capitalize())
    data_picked = [parser.from_dict(data) for data in random.sample(data_list, amount)]
    for item in data_picked:
        if item.image == "":
            image_url = getattr(__import__(__name__), data_type[:-1] + "_images_url")
            item.image = image_url % clean_text(item.name, False, True)

    data_images = [item.image for item in data_picked]

    embed = create_embed(name, ", ".join(
        [f"**{index + 1}:** {titlecase(item.name)}" for index, item in enumerate(data_picked)]))

    file_name = "tourney.png"
    create_collage(data_images, file_name)
    with open(file_name, 'rb') as fp:
        data = io.BytesIO(fp.read())
    file = discord.File(data, file_name)
    embed.set_image(url="attachment://%s" % file_name)

    view = discord.ui.View(timeout=None)
    view.add_item(TourneySelection(data=[titlecase(item.name) for item in data_picked]))
    await ctx.followup.send(embed=embed, file=file, view=view)


@bot.event
async def on_raw_reaction_add(payload):
    emoji_name = emoji.demojize(payload.emoji.name)
    channel = bot.get_channel(payload.channel_id)
    guild = bot.get_guild(payload.guild_id)
    user = guild.get_member(payload.user_id)

    rules_channels = [bot.get_channel(rules_channel_en), bot.get_channel(rules_channel_fr),
                      bot.get_channel(rules_channel_de), bot.get_channel(rules_channel_jp),
                      bot.get_channel(rules_channel_es)]

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
        if emoji_name == ":Spain:":
            role_id = role_es

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
        if emoji_name == ":Spain:":
            role_id = role_es

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


cogs = [f"cogs.{f[:-3]}" for f in os.listdir("cogs") if f.endswith(".py")]
for cog in cogs:
    bot.load_extension(cog)
bot.run(token)
