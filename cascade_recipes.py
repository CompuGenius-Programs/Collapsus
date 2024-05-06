import json
from dataclasses import dataclass

from titlecase import titlecase

locates = [["agate of evolution", "quest #178"], ["aggressence", "rank E grotto chest, yore"],
           ["agility ring", "rank G grotto chest, cyclown, whirly girly, liquid metal slime, goresby-purrvis"],
           ["angel bell",
            "Bloomingdale shop, Dourbridge shop, Gleeba shop, goretress shop, Porth Llaffan shop, Slurry Quay shop, Upover shop, Wormwood Creek shop, rank H grotto chest, common enemy drop"],
           ["angel's bow", "rank S grotto chest"], ["angel's robe", "tyrannosaurus wrecks"], ["antidotal herb",
                                                                                              "Angel Falls shop, Batsureg shop, Bloomingdale shop, Coffinwell shop, Dourbridge shop, Gleeba shop, goretress shop, Slurry Quay shop, Stornway shop, Swinedimples Academy shop, Porth Llaffan shop, Upover shop, Wormwood Creek shop, rank I grotto chest, common enemy drop"],
           ["apprentice's gloves", "shogum"], ["archer's armguard", "Batsureg shop"],
           ["ascetic robe", "quest #93, wight priest"],
           ["astral plume", "rank A grotto chest, rank D grotto chest, quest #121"], ["bad axe", "rank S grotto chest"],
           ["bandana", "Angel Falls shop, Stornway shop"],
           ["battle fork", "Bloomingdale shop, Gleeba shop, deadcurion"],
           ["battle axe", "Batsureg shop, Gleeba shop, Wormwood Creek shop"],
           ["beast claws", "rank B grotto chest, vermillion"],
           ["belle cap", "Western Coffinwell, Eastern Wormwood, morphean mushroom, mushroom mage"],
           ["billowing bow", "quest #83"], ["blowy bow", "Upover shop, Wormwood Creek shop"],
           ["blue orb", "quest #180"],
           ["boomer briefs", "Dourbridge shop, Porth Llaffan shop, Slurry Quay shop, boss troll"],
           ["boomerang", "Porth Llaffan shop"], ["boss shield", "Dourbridge shop, freaky tiki"],
           ["bow tie", "Dourbridge shop, Gleeba shop, Slurry Quay shop, expload"], ["boxer shorts", "sacksquatch"],
           ["brain drainer", "sir sanguinus"], ["brainy bracer", "quest #45"], ["bright staff", "rank S grotto chest"],
           ["brighten rock", "djust desert, Wormwood canyon, goodybag, cosmic chimaera, rashaverak"],
           ["bronze knife", "Coffinwell shop, Stornway shop"], ["bruiser's bracers", "Wormwood Creek shop"],
           ["bunny tail", "Porth Llaffan shop, Zere shop, rank I grotto chest"],
           ["butterfly wing", "batterfly, betterfly, dread admiral"], ["catholicon ring", "quest #143"],
           ["cautery sword", "Bloomingdale shop, Dourbridge shop, axolhotl, infernal armour, grim grinner"],
           ["celestial skein", "lleviathan"], ["chain mail", "Coffinwell shop, Stornway shop, skeleton soldier"],
           ["chain whip", "Bloomingdale shop, Gleeba shop"], ["chronocrystal", "lonely coast, tower of nod"],
           ["circlet", "Bloomingdale shop"], ["clever clogs", "Stornway shop"],
           ["cloak of evasion", "Porth Llaffan shop, tearwolf, sluggernaught"],
           ["clogs", "Coffinwell shop, Zere shop, beakon"],
           ["coagulant", "Batsureg shop, Western Stornway, Wormwood Creek shop, Upover shop, betterfly, cumaulus"],
           ["cobra claws", "Stornway shop, hammer horror"], ["cobra fan", "Batsureg shop, seavern"],
           ["corundum", "rank G grotto chest"],
           ["cotton gloves", "Angel Falls shop, Stornway shop, Wormwood Creek chest, skeleton"],
           ["cowpat", "Zere (region), bag o' laughs, mudraker, swinoceros"],
           ["crimson coral", "Eastern Wormwood, crabid, spinchilla, belisha beakon"],
           ["critical fan", "rank S grotto chest"],
           ["crow's claws", "Bloomingdale shop, Gleeba shop, weaken beakon, icikiller"],
           ["dancer's costume", "Porth Llaffan shop"], ["dangerous bikini top", "Dourbridge shop"],
           ["dangerous bustier", "rank E grotto chest"], ["dangerous midriff wrap", "Dourbridge shop"],
           ["dark robe", "Upover shop"], ["dark shield", "fright knight, night knight"],
           ["deadly night blade", "Bloomingdale shop, handsome crab"], ["deft dagger", "rank S grotto chest"],
           ["demon whip", "rank D grotto chest, alphyn"],
           ["densinium", "rank C grotto chest, rank D grotto chest, wishmaster"],
           ["depressing shoes", "rank C grotto chest, quest #181"], ["disturbin' turban", "Gleeba shop"],
           ["divine dagger", "Coffinwell shop, Stornway shop"],
           ["dragon claws", "Upover shop, Wormwood Creek shop, red dragon, drakulord"],
           ["dragon robe", "Cap'n Max Meddlin' prize"], ["dragon rod", "Stornway shop"], ["dragon scale",
                                                                                          "riptide, drakularge, seasaur, mandrake marauder, green dragon, abyss diver, mandrake marshal, wyrtoise, red dragon, drakulard, rashaverak, mandrake monarch, drakulord, grand lizzier, greygnarl, nodoph"],
           ["dragon top", "Wormwood Creek shop"], ["dragon trousers", "Wormwood Creek shop"],
           ["dragonlord claws", "rank S grotto chest"], ["dragonsbane", "Wormwood Creek shop, mandrake marshal"],
           ["driller pillar", "Batsureg shop, Gleeba shop"], ["edged boomerang", "Batsureg shop, Bloomingdale shop"],
           ["elfin charm", "quest #27"], ["elfin elixir", "Cap'n Max Meddlin' store, quest #38, cobra cardinal"],
           ["emerald moss", "Western Wormwood, salamarauder, green dragon, lleviathan"],
           ["enchanted stone", "rank B grotto chest, quest #60"], ["ethereal stone", "rank A grotto chest, quest #51"],
           ["evencloth", "djust desert, ondor cliffs, dark skeleton, ragged reaper, geothaum"],
           ["falcon blade", "Stornway shop, slionheart, prime slime"],
           ["feather fan", "Angel Falls shop, Stornway shop, mecha-mynah"], ["feather headband", "Bloomingdale shop"],
           ["feathered cap", "Porth Llaffan shop"], ["feline fan", "Swinedimples Academy shop"],
           ["finessence", "rank E grotto chest, quest #37"], ["fire blade", "Upover shop, scarlet fever"],
           ["fire claws", "Upover shop, nemean"], ["fishnet stockings", "Dourbridge shop, Slurry Quay shop"],
           ["fisticup", "Western Stornway, rank G grotto chest, rank H grotto chest"],
           ["fizzle-retardant suit", "quest #95, python priest, cobra cardinal"],
           ["flametang boomerang", "Stornway shop"],
           ["flintstone", "The Gittish Empire (region), rank F grotto chest, mad moai, grinade, stone golem, geothaum"],
           ["flurry feather", "Bloomingdale (region), mt. ulbaruun, weaken beakon, chimaera"],
           ["foehn fan", "Bloomingdale shop, Dourbridge shop"],
           ["fowl fan", "Gleeba shop, terrorhawk, bird of terrordise"],
           ["fresh water", "mt. ulzuun, slurry coast, cheeky tiki"], ["full moon ring", "quest #130"],
           ["fur hood", "Dourbridge shop, Slurry Quay shop"], ["fur poncho", "great gruffon"],
           ["garish garb", "Coffinwell shop, slugger"], ["giant's hammer", "Stornway shop, atlas"],
           ["gladius", "Stornway shop"],
           ["glass frit", "djust desert, wyrmwing, cyclown, parched peckerel, power hammer, stale whale"],
           ["gloomy gloves", "quest #124"], ["gold bar",
                                             "rank S grotto chest, rank B grotto chest, quest #161, drakularge, gem jamboree, gem slime, au-1000, pandora's box, tyrannosaurus wrecks"],
           ["gold bracer", "Dourbridge shop, Porth Llaffan shop, rank H grotto chest, cannibox"], ["gold ring",
                                                                                                   "Dourbridge shop, Stornway shop, Porth Llaffan shop, rank H grotto chest, drackyma, gold golem, aggrosculpture, mimic"],
           ["gold rosary", "lesionnaire, wight priest"], ["great bow", "Upover shop"], ["green orb", "quest #169"],
           ["green tights", "Batsureg shop"], ["gringham whip", "rank S grotto chest"],
           ["groundbreaker", "rank S grotto chest"], ["grubby bandage", "mummy boy, blood mummy, mummy"],
           ["gusterang", "Upover shop"], ["hades' helm", "rank D grotto chest, bad karmour, hell's gatekeeper"],
           ["hairband", "Stornway shop"], ["hallowed helm", "hammibal"],
           ["handrills", "Batsureg shop, Gleeba shop, Wormwood Creek shop, robo-robin, corrupt carter, cyber spider"],
           ["headsman's axe", "Dourbridge shop"], ["heavy handwear", "Dourbridge shop, sluggerslaught, hammer horror"],
           ["hela's hammer", "rank D grotto chest, hell's gatekeeper"],
           ["hephaestus' flame", "rank D grotto chest, rank E grotto chest, rockbomb, magmalice, flamin' drayman"],
           ["hero's boots", "trauminator"], ["high heels", "Dourbridge shop, Stornway shop, morag"],
           ["holy lance", "Bloomingdale shop, Dourbridge shop, Gleeba shop, trigertaur"], ["holy water",
                                                                                           "Batsureg shop, Bloomingdale shop, Western Coffinwell, Coffinwell shop, Dourbridge shop, Gleeba shop, goretress shop, Slurry Quay shop, Stornway shop, Swinedimples Academy shop, Porth Llaffan shop, Upover shop, Wormwood Creek shop, Zere shop, rank I grotto chest, common enemy drop"],
           ["horse manure", "iluugazar plains, white trigertaur, sick trigertaur, godsteed, tantamount"],
           ["hunter's bow", "Batsureg shop, hunter mech"], ["hunter's hat", "Batsureg shop"],
           ["ice axe", "Stornway shop"], ["ice crystal",
                                          "snowberian coast, snowberia, brrearthenwarrior, freezing fog, shivery shrubbery, firn fiend, uncommon cold"],
           ["icicle dirk", "Wormwood Creek shop, quest #67, uncommon cold"], ["invincible trousers", "nemean"],
           ["iron spear", "Coffinwell shop"],
           ["iron armour", "alltrades abbey merchant, Porth Llaffan shop, restless armour"],
           ["iron axe", "Porth Llaffan shop"], ["iron bar", "Bloomingdale shop, Dourbridge shop"],
           ["iron broadsword", "Coffinwell shop, slime knight, restless armour, gum shield"],
           ["iron claws", "Coffinwell shop, Stornway shop, bewarewolf"],
           ["iron cuirass", "Coffinwell shop, lesionnaire"], ["iron fan", "Coffinwell shop, Stornway shop"],
           ["iron gauntlets", "Coffinwell shop, Porth Llaffan shop, wight knight"],
           ["iron helmet", "Porth Llaffan shop, metal slime knight, axolhotl"], ["iron kneecaps", "Coffinwell shop"],
           ["iron lance", "Coffinwell shop, Stornway shop, chariot chappie"],
           ["iron mask", "Bloomingdale shop, rank H grotto chest, deadcurion, harmour, alarmour"],
           ["iron nails", "rank H grotto chest"],
           ["iron ore", "Western coffinewell, lonely coast, rank G grotto chest, robo-robin, bad karmour"],
           ["iron sabatons", "Coffinwell shop, Porth Llaffan shop"], ["iron shield", "alltrades abbey, salamarauder"],
           ["iron whip", "Batsureg shop, Gleeba shop"], ["kestrel claws", "quest #75"], ["king axe", "Upover shop"],
           ["kitty litter", "djust desert, clawcerer, parched peckerel, purrestidigitator, power hammer"],
           ["kitty shield", "quest #16"], ["knockout rod", "rank S grotto chest"],
           ["kung fu shoes", "Bloomingdale shop"],
           ["lambswool", "Batsureg shop, Stornway shop (chest), Wormwood Creek shop, quest #126, ram raider, drackal"],
           ["laundry pole", "Stornway shop"],
           ["lava lump", "rank H grotto chest, bagma, live lava, scarlet fever, master of nu'un"],
           ["leather boots", "Coffinwell shop, Zere shop"], ["leather cape", "Zere shop, bodkin bowyer"],
           ["leather hat", "Stornway shop, Zere shop, bodkin archer, bodkin bowyer"],
           ["leather kilt", "Coffinwell shop, Zere shop, hammerhood, brownie"],
           ["leather whip", "Angel Falls shop, Stornway shop, lunatick"], ["life ring", "quest #19"],
           ["light gauntlets", "Upover shop"],
           ["light shield", "Bloomingdale shop, Dourbridge shop, metal slime knight, gum shield"],
           ["lightning lance", "Upover shop"], ["lightning staff", "Batsureg shop, Gleeba shop, cumulus rex"],
           ["long spear", "alltrades abbey, zumeanie"], ["loud trousers", "Bloomingdale shop"],
           ["lucida shard", "Wormwood Creek chest, rank C grotto chest, quest #61, cosmic chimaera"],
           ["lunar fan", "quest #22"], ["lunaria", "prism peacock, boogie manguini"],
           ["magic armour", "Gleeba shop, lethal armour, charmour"], ["magic beast hide",
                                                                      "badboon, bewarewolf, big badboon, scarewolf, tearwolf, trigertaur, boppin' badger, badger mager, knocktopus, brainy badboon, splatterhorn, moosifer, dreadful drackal, octagoon, master moosifer, bling badger, hexagoon, rover"],
           ["magic beast horn",
            "splatterhorn, swinoceros, rampage, shocktopus, claw hammer, battering ram, seasaur, dreadful drackal"],
           ["magic mittens", "Gleeba shop"], ["magic shield", "Gleeba shop, cheeky tiki, grim grinner"], ["magic water",
                                                                                                          "Batsureg shop, Bloomingdale shop, Dourbridge shop, Gleeba shop, goretress shop, Porth Llaffan shop, Slurry Quay shop, Swinedimples Academy shop, Upover shop, Wormwood Creek shop, rank E grotto chest, rank F grotto chest, rank I grotto chest, common enemy drop"],
           ["magical hat", "Upover shop"], ["magical mace", "Upover shop"],
           ["magical robes", "Gleeba shop, shaman, sorcerer"], ["mail coif", "Batsureg shop"],
           ["majestic mantle", "quest #12"],
           ["malicite", "rank F grotto chest, mummy, blood mummy, grrrgoyle, hottingham-gore"],
           ["manky mud", "the gittish empire, rank F grotto chest, mortoad, toxic zombie, ghoul, apeckalypse"],
           ["mayoress's mittens", "Upover shop"], ["medicinal herb",
                                                   "Angel Falls shop, Batsureg shop, Bloomingdale shop, Coffinwell shop, Dourbridge shop, Gleeba shop, goretress shop, Slurry Quay shop, Stornway shop, Swinedimples Academy shop, Porth Llaffan shop, Upover shop, Wormwood Creek shop, Zere shop, rank I grotto chest, common enemy drop"],
           ["megaton hammer", "rank B grotto chest"], ["mental mittens", "Wormwood Creek shop"],
           ["mercury's bandana", "Cap'n Max Meddlin' prize"], ["metal slime armour", "rank A grotto chest"],
           ["metal slime gauntlets", "rank A grotto chest"], ["metal slime helm", "rank A grotto chest"],
           ["metal slime shield", "rank A grotto chest"], ["metal slime sollerets", "rank A grotto chest"],
           ["metal slime spear", "rank A grotto chest"], ["metal slime sword", "rank A grotto chest"],
           ["meteorang", "rank S grotto chest"], ["meteorite bracer", "Cap'n Max Meddlin' prize"],
           ["mighty armlet", "quest #128"], ["miracle sword", "Cap'n Max Meddlin' prize, shogum"],
           ["mirror armour", "Upover shop"], ["mirrorstone", "rank F grotto chest, mega moai, alphyn"],
           ["mistick", "Upover shop, Wormwood Creek shop, cumulus hex"],
           ["moon axe", "Upover shop, Wormwood Creek shop"], ["moonwort bulb",
                                                              "Batsureg shop, Bloomingdale shop, Coffinwell shop, Dourbridge shop, Gleeba shop, Porth Llaffan shop, Slurry Quay shop, Swinedimples Academy shop, Upover shop, Wormwood Creek shop, Zere shop, rank I grotto chest, common enemy drop"],
           ["mystifying mixture", "rank D grotto chest, mudraker"],
           ["mythril ore", "Western Coffinwell, rank B grotto chest, rank D grotto chest, void droid"],
           ["narspicious", "Western Wormwood, rank E grotto chest, sculpture vulture, moai minstrel"],
           ["nectar", "snowberian coast, rank F grotto chest"], ["nightmare gown", "tower of nod"],
           ["oaken club", "rank I grotto chest, hammerhood, troll, cyclops, boss troll"],
           ["oaken pole", "alltrades abbey merchant, Coffinwell shop"], ["oh-no bow", "rank D grotto chest"],
           ["orichalcum",
            "Cap'n Max Meddlin' store, rank S grotto chest, rank A grotto chest, quest #144, quest #162, metal king slime, gem slime, greygnarl"],
           ["panacea", "rank E grotto chest, blastoad, cureslime"],
           ["partisan", "Batsureg shop, Swinedimples Academy shop, stenchurion, sick trigertaur"],
           ["pentarang", "rank B grotto chest"], ["perfect panacea", "rank C grotto chest"],
           ["pink pearl", "Dourbridge shop, Gleeba shop, goodybag"], ["pixie boots", "Cap'n Max Meddlin' store"],
           ["platinum headgear", "Gleeba shop"],
           ["platinum ore", "snowberian coast, quest #28, drackal, octagoon, platinum king jewel"],
           ["pointy hat", "Dourbridge shop, Slurry Quay shop, jinkster"],
           ["poison moth knife", "Coffinwell shop, crabber dabber doo, king crab"],
           ["poison needle", "Bloomingdale shop, Dourbridge shop, peckerel"], ["poker", "rank S grotto chest"],
           ["pop socks", "Dourbridge shop, Porth Llaffan shop, rank I grotto chest"],
           ["potshot bow", "Batsureg shop, Wormwood Creek shop"], ["power shield", "Dourbridge shop, Upover shop"],
           ["prayer ring", "Cap'n Max Meddlin' store,  quest #17, hocus chimaera, genie sanguini"],
           ["prince's pea coat", "quest #53"], ["princess's robe", "quest #54"], ["purblind bow", "Stornway shop"],
           ["purple orb", "quest #182"], ["queen's whip", "Stornway shop"],
           ["raging bull helm", "Wormwood Creek shop, barbatos"],
           ["raging ruby", "brainy badboon, drastic drackal, master moosifer, tyrannosaura wrecks"],
           ["rapier", "Coffinwell shop, Stornway shop"], ["razor-wing boomerang", "Batsureg shop, Wormwood Creek shop"],
           ["reckless necklace", "rank A grotto chest"], ["red orb", "dragonlord, malroth"],
           ["red tights", "Gleeba shop, belisha beakon"],
           ["reset stone", "Cap'n Max Meddlin' store, rank S grotto chest, stone guardian, firn fiend"],
           ["resurrock", "rank G grotto chest, stone golem, living statue, stone guardian, grrrgoyle"],
           ["rober of serenity", "alltrades abbey"],
           ["rockbomb shard", "rank H grotto chest, quest #55, grinade, rockbomb, bomboulder, flamin' drayman"],
           ["royal soil", "rank H grotto chest, drastic drackal, terror troll, barriearthenwarrior, ragin' contagion"],
           ["ruby of protection", "quest #30, king godfrey"], ["ruinous shield", "rank C grotto chest, alarmour"],
           ["rune staff", "Wormwood Creek shop"], ["rusty helmet", "Cap'n Max Meddlin' prize"],
           ["sacred armour", "Cap'n Max Meddlin' prize, sir sanguinus"],
           ["safety shoes", "Wormwood Creek shop, gramarye gruffon"], ["sagacious sandals", "freezing fog"],
           ["sage's elixir",
            "rank S grotto chest, rank A grotto chest, rank B grotto chest, rank C grotto chest, dreadmaster, hottingham-gore"],
           ["sage's staff", "Stornway shop"],
           ["saint's ashes", "Cap'n Max Meddlin' store, rank C grotto chest, rank F grotto chest,  quest #21, seavern"],
           ["sainted soma", "rank S grotto chest"],
           ["sandstorm spear", "Batsureg shop, Gleeba shop, Wormwood Creek shop"],
           ["scale armour", "Stornway shop, icikiller"], ["scale shield", "Stornway shop, Zere shop, earthenwarrior"],
           ["seashell", "Eastern Stornway, hermany, spinchilla, crabber dabber doo"], ["sensible sandals", "elusid"],
           ["short bow", "Porth Llaffan shop"],
           ["silk robe", "Stornway shop, Zere shop, spirit, meowgician, mean spirit"],
           ["silver mail", "Bloomingdale shop, infernal armour, harmour"], ["silver orb", "quest #153"],
           ["silver platter", "rank H grotto chest"], ["silver tiara", "Porth Llaffan shop"],
           ["siren sandals", "Bloomingdale shop"], ["skull helm", "night knight, blight knight"],
           ["skull ring", "rank D grotto chest, aggrosculpture"],
           ["sleeping hibiscus", "Eastern Wormwood, quest #1, funghoul, ram raider, king crab"],
           ["sleepy stick", "Batsureg shop"], ["slime crown", "king slime, king cureslime, metal king slime"],
           ["slime earrings", "Dourbridge shop, Porth Llaffan shop, slime stack"], ["slimedrop",
                                                                                    "slime, she-slime, bubble slime, healslime, slime knight, slime stack, medislime, metal medley, king slime, sootheslime, cureslime, king cureslime, darkonium slime"],
           ["slipweed", "Eastern Coffinwell, Western Wormwood"], ["smart suit", "Bloomingdale shop, dark skeleton"],
           ["snakeskin", "flython, sail serpent, diethon"],
           ["snakeskin whip", "Bloomingdale shop, Dourbridge shop, sail serpent"],
           ["softwort", "Bloomingdale shop, man o'war, bud brother, bagma"],
           ["soldier's sword", "Angel Falls shop, Stornway shop, wooper trooper"],
           ["sorcerer's stone", "rank F grotto chest"], ["spangled dress", "Bloomingdale shop, cannibelle"],
           ["spiked steel whip", "quest #73"], ["spirit bracer", "quest #155"], ["spring breeze hat", "fowleye"],
           ["staff of sentencing", "Coffinwell shop, clawcerer"], ["star's suit", "quest #119"],
           ["stardust sword", "rank S grotto chest"], ["stellar fan", "Upover shop"], ["stiletto heels", "quest #20"],
           ["stolos' staff", "Bloomingdale shop, Dourbridge shop, purrestidigitator"],
           ["strength ring", "rank G grotto chest, walking corpse, big badboon, gigantes"],
           ["strong antidote", "Gleeba shop, Upover shop, rank H grotto chest, common enemy drop"], ["strong medicine",
                                                                                                     "Batsureg shop, Gleeba shop, Upover shop, Wormwood Creek shop, rank I grotto chest, common enemy drop"],
           ["strongsam", "Batsureg shop"], ["sturdy slacks", "Dourbridge shop"],
           ["superior medicine", "easter Wormwood, Bloomingdale shop, rank H grotto chest, bud brother, pale whale"],
           ["swallowtail", "Upover shop, Wormwood Creek shop"], ["sword breaker", "Upover shop, fright knight"],
           ["tangleweb",
            "Batsureg shop, Upover shop, Wormwood Creek shop, cumaulus, window's pique, cyber spider, tyrantula"],
           ["terra firmer", "quest #81"], ["terra tamper", "Upover shop"],
           ["terrible tattoo", "gruffon, bloody manguini, barbatos, freaky tiki, garth goyle"],
           ["thinkincense", "cringle coast, Western Wormwood, wyrmtail"],
           ["thinking cap", "Swinedimples Academy shop, Wormwood Creek shop, darkonium slime"],
           ["thunderball", "hermany, wyrmwing, cumulus rex, cumulus vex"],
           ["tint-tastic tutu", "Stornway shop, prism peacock"],
           ["toad oil", "rank G grotto chest, gastropog, mortoad, expload, gloomy gastropog, blastoad"],
           ["tortoiseshell", "Dourbridge shop, Porth Llaffan shop, Slurry Quay shop, crabid, wyrtoise, wonder wyrtle"],
           ["tortoiseshell fan", "Bloomingdale shop"],
           ["tough guy tattoo", "quest #89, claw hammer, ghoul, mega moai, goreham-hogg"],
           ["training top", "Stornway shop"], ["training trousers", "Stornway shop"], ["trident", "stale whale"],
           ["tropotoga", "atlas"], ["turban", "Coffinwell shop, mummy boy"], ["tussler's top", "Bloomingdale shop"],
           ["tussler's trousers", "Bloomingdale shop"], ["ultramarine mittens", "shaman"],
           ["unhappy hat", "rank C grotto chest,  quest #11"], ["utility belt", "quest #14"],
           ["valkyrie sword", "Batsureg shop, Wormwood Creek shop, prime slime"], ["velvet cape", "Gleeba shop"],
           ["vesta gauntlets", "equinox"], ["victorious armour", "excalipurr"], ["wakerobin", "Bloomingdale shop"],
           ["war fan", "Coffinwell shop"], ["war hammer", "Batsureg shop, Gleeba shop, Wormwood Creek shop"],
           ["warrior's helm", "Bloomingdale shop"], ["warrior's shield", "Wormwood Creek shop"],
           ["watermaul wand", "Bloomingdale shop, Gleeba shop, python priest, abyss diver, slugly betty"],
           ["white shield", "quest #87"], ["white tights", "Swinedimples Academy shop"], ["wing of bat",
                                                                                          "bloody manguini, manguini, drackmage, flython, drackyma, diethon, gruffon, great gruffon, gramarye gruffon, boogie manguini"],
           ["wizard's staff", "Coffinwell shop, Stornway shop, blinkster"], ["wizard's trousers", "Gleeba shop"],
           ["yellow orb", "quest #175"],
           ["yggdrasil leaf", "rank S grotto chest, quest #123, quest #160, bling badger, barbarus, greygnarl"],
           ["rusty armour", "quest #177"], ["rusty gauntlets", "quest #178"], ["rusty shield", "quest #49"],
           ["rusty sword", "Realm of the Mighty"]]

with open("data/recipes.json", "r") as data:
    recipes_data = json.load(data)["recipes"]
recipes = [[recipe["result"]] + [item for i in range(1, 4) if recipe[f"item{i}"] for item in
                                 [recipe[f"item{i}"], recipe[f"qty{i}"]]] for recipe in recipes_data]


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

    return ingredients


def cascade_recursive(recipe, count, mult, ingredients, trail, level):
    if recipe is None:
        return ingredients

    if recipe in trail:
        ingredients.append(Ingredient(recipe, count, count * mult, level, ''))
        return ingredients

    for item in recipes:
        if item[0] == recipe:
            location = next((loc for loc in locates if loc[0] == recipe), None)
            recipe_type = next((rec["type"] for rec in recipes_data if rec["result"] == recipe), '')
            ingredients.append(Ingredient(item[0], count, count * mult, level, location[1] if location else '', recipe_type))

            trail.append(item[0])
            for i in range(1, len(item), 2):
                cascade_recursive(item[i], int(item[i + 1]), count * mult, ingredients, trail, level + 1)
            trail.pop()
            return ingredients

    location = next((loc for loc in locates if loc[0] == recipe), None)
    if location:
        ingredients.append(Ingredient(recipe, count, count * mult, level, location[1]))

    return ingredients


if __name__ == "__main__":
    cascade()
