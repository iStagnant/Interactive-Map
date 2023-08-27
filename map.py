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
    "Kor Sestor": "25",
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
output = "    \"markers\": [\n\t"
description = "\"description\": \""
quotes = '"'
id = 1

#Takes in a planet and outputs what it has
def planet_attributes(planet: str):
    for node in planet_nodes:
        if node.node_type == "planet":
            if node.name().strip(quotes) == planet:
                return [
                    "-Has Spaceport\\n" if node.spaceport() else "-No Spaceport\\n",
                    "-Has Shipyard\\n" if node.shipyards() else "-No Shipyard\\n",
                    "-Has Outfitter\\n" if node.outfitters() else "-No Outfitter\\n",
                                  ]

for node in system_nodes:
    if (node.node_type == "system") and not (node.name().strip(quotes) in remove):

        #Getting the government of the system
        if "Quarg" in node.government(): #Because there's Quarg (Gegno), Quarg (Hai) etc...
            government = "Quarg"
        elif "Bunrodea" in node.government(): #In the game file they are split to Bunrodea and Bunrodea (Guard)
            government = "Bunrodea"
        elif "Pirate" in node.government(): #There's a hidden system with government Pirate (Devil-Run Gang)
            government = "Pirate"
        elif "Pug" in node.government(): #In the game files they are split to Pug and Pug (Wanderer)
            government = "Pug"
        else:
            government = node.government().strip(quotes)

        #Create a blacklist so wormholes can be removed instead of counted as planets
        wormholes = []
        for object in node.objects():
            if ("wormhole" in object.sprite()):
                wormholes.append(object.name().strip(quotes))

        #Loops through system planets and populates the planets list and then using that info we fill description
        planets = {}
        for planet in node.planets():
            planet = planet.strip(quotes)
            #Ringworlds contain multiple planets with the same name so we check if the planet is already in the list
            if not (planet in wormholes) and not (planet in planets):
                planets[planet] = planet_attributes(planet)

        #If the system has more than 4 planets description would be too long and cause fandom to error
        if len(planets) > 4:
            grouped_planets = {}
            #We populate grouped_planets which has the attributes of planets as key and the planets that have those attributes as value
            for name in planets:
                planet_key = "  ".join(planets[name])
                if not planet_key in grouped_planets:
                    grouped_planets[planet_key] = []

                grouped_planets[planet_key].append(name)

            #Using the information in grouped_planets we fill description
            for planet_key, planet_list in grouped_planets.items():
                description += "".join([f" '''{name}'''," for name in planet_list])
                description = "\\n  ".join(description.rsplit(",", 1))
                attributes = planet_key

                if planet_key == list(grouped_planets)[-1]:
                    description += attributes + f"''{government}''\""

                else:
                    description += attributes + "\\n"

        else:
            for name, attributes in planets.items():
                #If last planet in system add the government at the end
                if name == list(planets)[-1]:
                    description += f" '''{name}'''\\n  {attributes[0]}  {attributes[1]}  {attributes[2]}''{government}''\""

                #If not add an extra \\n to keep the wiki style
                else:
                    description += f" '''{name}'''\\n  {attributes[0]}  {attributes[1]}  {attributes[2]}\\n"

        if (not planets):
            description += f"  -No Spaceport\\n  -No Shipyard\\n  -No Outfitter\\n''{government}''\""

        planet = node.name().strip(quotes)
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
                "title": "{planet}",
                {description},
                "link": {{
                    "url": "{planet}",
                    "label": "{planet}'s wiki page"
                }}
            }},
            "id": "{id}"
        }},
        """

        id += 1
        description = "\"description\": \"" #Clear the description for the next system to use

with open("map.txt", "w") as file:
    file.write("".join(output.rsplit(",\n", 1)) + "\n    ]")
