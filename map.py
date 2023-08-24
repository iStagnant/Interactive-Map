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

#Don't change code under here unless you know what you're doing
output = "\"markers\": [\n\t"
description = "\"description\": \""
quotes = '"'
id = 1

#Takes in a planet and outputs what it has
def planet_attributes(planet: str):
    for node in planet_nodes:
        if (node.node_type == "planet"):
            if (node.name() == planet or node.name() == "\"" + planet + "\""):
                return {planet : [
                    "-Has Spaceport\\n" if node.spaceport() else "-No Spaceport\\n",
                    "-Has Shipyard\\n" if node.shipyards() else "-No Shipyard\\n",
                    "-Has Outfitter\\n" if node.outfitters() else "-No Outfitter\\n",
                                  ]}

for node in system_nodes:
    #The node.name() checks are to remove the systems that are from the other pug galaxy
    if (node.node_type == "system") and not (node.name().strip(quotes) == "Terra Incognita" or node.name().strip(quotes) == "Over the Rainbow"
    or node.name().strip(quotes) == "World's End"):
        if("Quarg" in node.government()): #Because there's Quarg (Gegno), Quarg (Hai) etc...
            government = "Quarg"
        elif (node.government() == '"Kor Sestor"'): #Once the player completes the wanderer middle missions they become uninhabited
            government = "Uninhabited"
        elif ("Bunrodea" in node.government()): #In the game file they are split to Bunrodea and Bunrodea (Guard)
            government = "Bunrodea"
        elif ("Pirate" in node.government()): #There's a hidden system with government Pirate (Devil-Run Gang)
            if (node.name() == "Men"):
                government = "Independent"
            else:
                government = "Pirate"
        elif ("Pug" in node.government()): #In the game files they are split to Pug and Pug (Wanderer)
            government = "Pug"
        else:
            government = node.government().strip(quotes)

        #Create a blacklist so wormholes can be removed instead of counted as planets
        wormholes = []
        for object in node.objects():
            if ("wormhole" in object.sprite()):
                wormholes.append(object.name())

        planets = []
        #Quarg systems can have ringworlds which show up as multiple planets so we check if a Quarg system has more than 3 planets to detect ringworlds, and that's also the case for all Heliarch systems but just in case in the future non ringworld Heliarch systems are added we check
        if not ((government == "Quarg" or government == "Heliarch") and len(node.planets()) > 3):
            #Loops through system planets and populates the planets list and then using that info it populates fills
            for planet in node.planets():
                if not (planet in wormholes):
                    planets.append(planet_attributes(planet))
            for p in planets:
                #If last planet in system add the government at the end
                if (list(p)[0] == list(list(planets)[-1])[0]):
                    name = list(p)[0]
                    description += f" '''{name.strip(quotes)}'''\\n  {p[name][0]}  {p[name][1]}  {p[name][2]}''{government}''\""
                #If not add an extra \\n to keep the wiki style
                else:
                    name = list(p)[0]
                    description += f" '''{name.strip(quotes)}'''\\n  {p[name][0]}  {p[name][1]}  {p[name][2]}\\n"
        #If above conditions are met then we should only take the name of the first planet since the rest are the same
        else:
            planets = ["Quarg"]
            planet = planet_attributes(node.planets()[0])
            name = list(planet)[0]
            description += f" '''{name.strip(quotes)}'''\\n  {planet[name][0]}  {planet[name][1]}  {planet[name][2]}''{government}''\""

        if (not planets):
            description += f"  -No Spaceport\\n  -No Shipyard\\n  -No Outfitter\\n''{government}''\""

        #These guys have so many planets that it caused fandom to error, and I can't be bothered doing checks for things like this so here's a janky solution
        if (node.name() == "Arculus"):
            description = "\"description\": \" '''Seraglio''', '''Eminonu''', '''Babiali''', '''Kumkapi''', '''Xerolophos''', '''Topkapi''', '''Aksaray''', '''Yedikule'''\\n  -No Spaceport\\n  -No Shipyard\\n  -No Outfitter\\n\\n '''Viminal'''\\n  -Has Spaceport\\n  -Has Shipyard\\n  -Has Outfitter\\n''Remnant''\""
        elif (node.name() == "Pantica"):
            description = "\"description\": \" '''Capitoline''', '''Quirinal''', '''Servian'''\\n  -No Spaceport\\n  -No Shipyard\\n  -No Outfitter\\n\\n '''Aventine'''\\n  -Has Spaceport\\n  -Has Shipyard\\n  -Has Outfitter\\n\\n '''Esquiline'''\\n  -Has Spaceport\\n  -No Shipyard\\n  -No Outfitter\\n''Remnant''\""
        elif (node.name() == "Cinxia"):
            description = "\"description\": \" '''Caelian'''\\n  -Has Spaceport\\n  -Has Shipyard\\n  -Has Outfitter\\n\\n '''Tibernia''', '''Janiculum''', '''Vatican''', '''Palatine''', '''Pincian'''\\n  -No Spaceport\\n  -No Shipyard\\n  -No Outfitter\\n''Remnant''\""

        name = node.name().strip(quotes) #Some systems have "" in their name in the map file so we remove them
        position = node.position()
        x = "{:.3f}".format(base_position[0] + position[0])
        y = "{:.3f}".format(base_position[1] + position[1])
        output += f"""{{
            "categoryId": "{ids[government]}",
            "position": [
                {x},
                {y}
            ],
            "popup": {{
                "title": "{name}",
                {description},
                "link": {{
                    "url": "",
                    "label": ""
                }}
            }},
            "id": "{id}"
        }},
        """
        id += 1
        description = "\"description\": \"" #Clear the description for the next system to use

with open("map.txt", "w") as file:
    file.write(output + "]")
