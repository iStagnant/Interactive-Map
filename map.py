from endlessparser import parse
#Put your map file location here
system_map = "/usr/share/games/endless-sky/data/map systems.txt" 
planet_map = "/usr/share/games/endless-sky/data/map planets.txt"

with open(system_map, "r") as file:
    system_nodes = parse(file.read())

with open(planet_map, "r") as file:
    planet_nodes = parse(file.read())

#The position of the pixels that represents 0, 0
base_position = (1626, 1066)

#If any new species are added they should be added here and in the categories in the wiki
ids = {
    "Bunrodea": "24",
    "Coalition": "1",
    "Drak": "2",
    "Free Worlds": "3",
    "Gegno": "21",
    "Gegno Scin": "23",
    "Gegno Vi": "22",
    "Hai": "4",
    "Hai (Unfettered)": "5",
    "Heliarch": "6",
    "Independent": "7",
    "Korath": "10",
    "Kor Efret": "8",
    "Kor Mereti": "9",
    "Pirate": "12",
    "Pug": "13",
    "Quarg": "14",
    "Remnant": "20",
    "Republic": "15",
    "Syndicate": "16",
    "Uninhabited": "18",
    "Wanderer": "19"
}

#Systems to not be parsed
remove = ["Terra Incognita", "Over the Rainbow", "World's End"]

#Don't change code under here unless you know what you're doing (I love how this implies I know what I'm doing... I really don't)
output = "\t"
description = "\"description\": \""
quotes = '"'
id = 1

#Takes in a planet and outputs what it has
def planet_attributes(planet: str):
    for node in planet_nodes:
        if node.node_type == "planet":
            if node.name().strip(quotes) == planet:
                return {planet : [
                    "-Has Spaceport\\n" if node.spaceport() else "-No Spaceport\\n",
                    "-Has Shipyard\\n" if node.shipyards() else "-No Shipyard\\n",
                    "-Has Outfitter\\n" if node.outfitters() else "-No Outfitter\\n",
                                  ]}

for node in system_nodes:
    if (node.node_type == "system") and not (node.name().strip(quotes) in remove):

        #Getting the government of the system
        if "Quarg" in node.government(): #Because there's Quarg (Gegno), Quarg (Hai) etc...
            government = "Quarg"
        elif node.government() == '"Kor Sestor"': #Once the player completes the wanderer middle missions they become uninhabited
            government = "Uninhabited"
        elif "Bunrodea" in node.government(): #In the game file they are split to Bunrodea and Bunrodea (Guard)
            government = "Bunrodea"
        elif "Pirate" in node.government(): #There's a hidden system with government Pirate (Devil-Run Gang)
            if node.name() == "Men":
                government = "Independent"
            else:
                government = "Pirate"
        elif "Pug" in node.government(): #In the game files they are split to Pug and Pug (Wanderer)
            government = "Pug"
        else:
            government = node.government().strip(quotes)

        #Create a blacklist so wormholes can be removed instead of counted as planets
        wormholes = []
        for object in node.objects():
            if ("wormhole" in object.sprite()):
                wormholes.append(object.name())

        #Loops through system planets and populates the planets list and then using that info we fill description
        planets = []
        encountered_planets = []
        for planet in node.planets():
            #Ringworlds contain multiple planets with the same name so we check if the planet is already in the list
            if not (planet in wormholes) and not (planet in encountered_planets):
                encountered_planets.append(planet)
                planets.append(planet_attributes(planet.strip(quotes)))

        for p in planets:
            #If last planet in system add the government at the end
            if list(p)[0] == list(list(planets)[-1])[0]:
                name = list(p)[0]
                description += f" '''{name}'''\\n  {p[name][0]}  {p[name][1]}  {p[name][2]}''{government}''\""

            #If not add an extra \\n to keep the wiki style
            else:
                name = list(p)[0]
                description += f" '''{name}'''\\n  {p[name][0]}  {p[name][1]}  {p[name][2]}\\n"

        if (not planets):
            description += f"  -No Spaceport\\n  -No Shipyard\\n  -No Outfitter\\n''{government}''\""

        #These guys have so many planets that it caused fandom to error, and I can't be bothered doing checks for things like this so here's a janky solution
        if (node.name() == "Arculus"):
            description = "\"description\": \" '''Seraglio''', '''Eminonu''', '''Babiali''', '''Kumkapi''', '''Xerolophos''', '''Topkapi''', '''Aksaray''', '''Yedikule'''\\n  -No Spaceport\\n  -No Shipyard\\n  -No Outfitter\\n\\n '''Viminal'''\\n  -Has Spaceport\\n  -Has Shipyard\\n  -Has Outfitter\\n''Remnant''\""
        elif (node.name() == "Pantica"):
            description = "\"description\": \" '''Capitoline''', '''Quirinal''', '''Servian'''\\n  -No Spaceport\\n  -No Shipyard\\n  -No Outfitter\\n\\n '''Aventine'''\\n  -Has Spaceport\\n  -Has Shipyard\\n  -Has Outfitter\\n\\n '''Esquiline'''\\n  -Has Spaceport\\n  -No Shipyard\\n  -No Outfitter\\n''Remnant''\""
        elif (node.name() == "Cinxia"):
            description = "\"description\": \" '''Caelian'''\\n  -Has Spaceport\\n  -Has Shipyard\\n  -Has Outfitter\\n\\n '''Tibernia''', '''Janiculum''', '''Vatican''', '''Palatine''', '''Pincian'''\\n  -No Spaceport\\n  -No Shipyard\\n  -No Outfitter\\n''Remnant''\""

        name = node.name().strip(quotes)
        position = node.position()
        x = "{:.3f}".format(base_position[0] + position[0])
        y = "{:.3f}".format(base_position[1] + position[1])

        #Determine if system is inhabited by checking if any of it's planets has a spaceport
        if "-Has Spaceport" in description:
            catid = ids[government]
        else:
            catid = ids["Uninhabited"]

        output += f"""{{
            "categoryId": "{catid}",
            "position": [
                {x},
                {y}
            ],
            "popup": {{
                "title": "{name}",
                {description},
                "link": {{
                    "url": "{name}",
                    "label": "{name}'s wiki page"
                }}
            }},
            "id": "{id}"
        }},
        """

        id += 1
        description = "\"description\": \"" #Clear the description for the next system to use

with open("map.txt", "w") as file:
    file.write(output)
