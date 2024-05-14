import json
import os
import random
from asyncio import sleep

import discord
import dotenv
import emoji
from discord import Option
from titlecase import titlecase

import cascade_recipes
import parsers
from utils import create_embed, clean_text, dev_tag, int_from_string, create_paginator

dotenv.load_dotenv()
token = os.getenv("TOKEN")

bot = discord.Bot(intents=discord.Intents.all())

dev_id = 496392770374860811

guild_id = 655390550698098700

testing_channel = 973619817317797919
grotto_bot_commands_channel = 845339551173050389

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

server_invite_url = "https://discord.gg/"
server_invite_code = ""

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

    with open("data/config.json", "r", encoding="utf-8") as fp:
        data = json.load(fp)
        global server_invite_code
        server_invite_code = data["server_invite_code"]

    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="over The Quester's Rest. Type /help ."))


@bot.command(name="help", description="Get help for using the bot.")
async def _help(ctx):
    description = f'''
A bot created by <@{dev_id}> for The Quester's Rest (<{server_invite_url + server_invite_code}>).

**/character** - *Generate a random character*
**/gg** - *Get grotto info (location required) - <#{grotto_bot_commands_channel}> only*
**/grotto** - *Search for a grotto - <#{grotto_bot_commands_channel}> only*
**/monster** - *Get monster info*
**/quest** - *Get quest info*
**/recipe** - *Get an item's recipe*
**/recipe_cascade** - *Get cascading info about a recipe*
**/song** - *Play a song*
**/songs_all** - *Play all songs*
**/stop** - *Stop playing songs*
**/translate** - *Translate a word or phrase*
**/grotto_translate(\_[language])** - *Translate a grotto - <#{grotto_bot_commands_channel}> only*

**/help** - *Displays this message*
'''

    if ctx.guild_id != guild_id:
        description = description.replace(f" - <#{grotto_bot_commands_channel}> only", "")

    embed = create_embed("Collapsus Help [Click For Server Website]", description=description, error="", image=logo_url,
                         url=website_url)
    await ctx.respond(embed=embed)


async def get_songs(ctx: discord.AutocompleteContext):
    return [song for song in parsers.songs if ctx.value.lower() in song.lower()]


@bot.command(name="song", description="Plays a song.")
async def _song(ctx, song_name: Option(str, "Song Name", autocomplete=get_songs, required=True)):
    voice_client = discord.utils.get(bot.voice_clients, guild=bot.get_guild(ctx.guild_id))
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
    voice_client = discord.utils.get(bot.voice_clients, guild=bot.get_guild(ctx.guild_id))
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
    voice_client = discord.utils.get(bot.voice_clients, guild=bot.get_guild(ctx.guild_id))
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
    cascade_file = "cascade_description.md"
    location_file = "location_description.yml"

    ingredients = cascade_recipes.cascade(creation_name)
    if ingredients:
        recipe = ingredients[0]
        ingredients = ingredients[1:]

        cascade_description = ""
        if recipe.location != '':
            cascade_description += f"*{titlecase(', '.join(recipe.location))}*\n\n"

        cascade_description += "**Ingredients**\n"
        cascade_description += "\n".join(
            [f"{' ' * (ing.level - 1)}- {titlecase(ing.name)} x{ing.count} ({ing.total})" for ing in ingredients])

        location_description = ""
        has_location = any(ing.location != '' for ing in ingredients)
        if has_location:
            location_description += "**Locations**\n\n"

            def remove_duplicates(ingredients):
                unique = []
                for ingredient in ingredients:
                    if not any(ingredient.name == ing.name for ing in unique):
                        unique.append(ingredient)
                return unique

            list_of_locations = remove_duplicates([ing for ing in ingredients if ing.location != ''])
            location_description += "\n\n".join(
                f"- {titlecase(ing.name)}: {titlecase(', '.join(ing.location))}" for ing in list_of_locations)

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

        class SendLocationsButton(discord.ui.Button):
            async def callback(self, interaction: discord.Interaction):
                await interaction.response.send_message(file=discord.File(location_file))
                await interaction.message.edit(view=None)

        try:
            embed = create_embed(titlecase(recipe.name),
                                 cascade_description + "\n\n" + location_description.replace("\n\n", "\n"), image=image)
            await ctx.respond(embed=embed)
        except discord.errors.HTTPException:
            cascade_embed = create_embed(titlecase(recipe.name), cascade_description, image=image)

            try:
                location_embed = create_embed(titlecase(recipe.name), location_description.replace("\n\n", "\n"),
                                              image=image)
                paginator = create_paginator([cascade_embed, location_embed])
                await paginator.respond(ctx.interaction)
            except discord.errors.HTTPException:
                try:
                    with open(location_file, "w", encoding="utf-8") as f:
                        f.write(location_description.replace("#", "").replace("*", ""))

                    view = discord.ui.View()
                    view.add_item(SendLocationsButton(label="See Item Locations"))

                    await ctx.respond(embed=cascade_embed, view=view)
                except discord.errors.HTTPException:
                    with open(cascade_file, "w", encoding="utf-8") as f:
                        f.write(cascade_description.replace("*", ""))

                    await ctx.respond(files=[discord.File(cascade_file), discord.File(location_file)])
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


cogs = [f"cogs.{f[:-3]}" for f in os.listdir("cogs") if f.endswith(".py")]
for cog in cogs:
    bot.load_extension(cog)
bot.run(token)
