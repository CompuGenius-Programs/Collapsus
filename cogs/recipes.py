import json

import discord
from discord import Option
from discord.ext import commands
from titlecase import titlecase

import cascade_recipes
import parsers
from utils import create_embed, clean_text, create_paginator


def setup(bot):
    bot.add_cog(Recipes(bot))


class Recipes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.krak_pot_image_url = "https://cdn.discordapp.com/emojis/866763396108386304.png"
        self.item_images_url = "https://www.woodus.com/den/gallery/graphics/dq9ds/item/%s.png"
        self.weapon_images_url = "https://www.woodus.com/den/gallery/graphics/dq9ds/weapon/%s.png"
        self.armor_images_url = "https://www.woodus.com/den/gallery/graphics/dq9ds/armor/%s.png"
        self.shield_images_url = "https://www.woodus.com/den/gallery/graphics/dq9ds/shield/%s.png"
        self.accessory_images_url = "https://www.woodus.com/den/gallery/graphics/dq9ds/accessory/%s.png"

    async def get_recipes(self, ctx: discord.AutocompleteContext):
        with open("data/recipes.json", "r", encoding="utf-8") as fp:
            data = json.load(fp)
        recipes = data["recipes"]
        results = []
        for r in recipes:
            recipe = parsers.Recipe.from_dict(r)
            if ctx.value.lower() in recipe.result.lower():
                results.append(titlecase(recipe.result))
        return results

    @discord.slash_command(name="recipe", description="Sends info about a recipe.")
    async def _recipe(self, ctx, creation_name: Option(str, "Creation (Ex. Special Medicine)", autocomplete=get_recipes,
                                                       required=True)):
        with open("data/recipes.json", "r", encoding="utf-8") as fp:
            data = json.load(fp)

        recipes = data["recipes"]

        index = next(filter(lambda r: clean_text(r["result"]) == clean_text(creation_name.lower()), recipes), None)

        if index is None:
            embed = create_embed(
                "Ahem! Oh dear. I'm afraid I don't seem to be\nable to make anything with that particular"
                "\ncreation name of `%s`." % creation_name, image=self.krak_pot_image_url)
            return await ctx.respond(embed=embed)

        recipe = parsers.Recipe.from_dict(index)

        title = ":star: %s :star:" % titlecase(recipe.result) if recipe.alchemiracle else titlecase(recipe.result)
        color = discord.Color.gold() if recipe.alchemiracle else discord.Color.green()

        if recipe.image == "":
            recipe_images_url = ""
            if recipe.type.lower() in parsers.item_types:
                recipe_images_url = self.item_images_url
            elif recipe.type.lower() in parsers.weapon_types:
                recipe_images_url = self.weapon_images_url
            elif recipe.type.lower() in parsers.armor_types:
                recipe_images_url = self.armor_images_url
            elif recipe.type.lower() in parsers.accessory_types:
                recipe_images_url = self.accessory_images_url
            elif recipe.type.lower() == "shields":
                recipe_images_url = self.shield_images_url

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

    @discord.slash_command(name="recipe_cascade", description="Sends cascading info about a recipe.")
    async def _recipe_cascade(self, ctx,
                              creation_name: Option(str, "Creation (Ex. Special Medicine)", autocomplete=get_recipes,
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
                recipe_images_url = self.item_images_url
            elif recipe.type.lower() in parsers.weapon_types:
                recipe_images_url = self.weapon_images_url
            elif recipe.type.lower() in parsers.armor_types:
                recipe_images_url = self.armor_images_url
            elif recipe.type.lower() in parsers.accessory_types:
                recipe_images_url = self.accessory_images_url
            elif recipe.type.lower() == "shields":
                recipe_images_url = self.shield_images_url

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
                                     cascade_description + "\n\n" + location_description.replace("\n\n", "\n"),
                                     image=image)
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
            embed = create_embed(
                "Ahem! Oh dear. I'm afraid I don't seem to be\nable to make anything with that particular"
                "\ncreation name of `%s`." % creation_name, image=self.krak_pot_image_url)
            return await ctx.respond(embed=embed)
