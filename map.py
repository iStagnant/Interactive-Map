from endlessparser import parse
#Put your map file location here
system_map = "/usr/share/games/endless-sky/data/map systems.txt" 
planet_map = "/usr/share/games/endless-sky/data/map planets.txt"

with open(system_map, "r") as file:
    system_nodes = parse(file.read())

with open(planet_map, "r") as file:
    planet_nodes = parse(file.read())

output = "\"markers\": [\n\t"
description = "\"description\": \""
quotes = '"'
planets = []
id = 1
#If any new species are added they should be added here and in the categories in the wiki
ids = {
    "Coalition" : "1",
    "Drak" : "2",
    "Free Worlds" : "3",
    "Hai" : "4",
    "Hai (Unfettered)" : "5",
    "Heliarch" : "6",
    "Independent" : "7",
    "Kor Efret" : "8",
    "Kor Mereti" : "9",
    "Korath" : "10",
    "Neutral" : "11",
    "Pirate" : "12",
    "Pug" : "13",
    "Quarg" : "14",
    "Republic" : "15",
    "Syndicate" : "16",
    "Uninhabited" : "17",
    "Wanderer" : "18",
    "Remnant" : "19",
    "Gegno" : "20",
    "Gegno Vi" : "21",
    "Gegno Scin" : "22",
    "Bunrodea" : "23"
}

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
    if (node.node_type == "system"):
        if("Quarg" in node.government()): #Because there's Quarg (Gegno), Quarg (Hai) etc...
            government = "Quarg"
        elif (node.government() == '"Kor Sestor"'): #Once the player completes the wanderer middle missions they become uninhabited
            government = "Uninhabited"
        elif ("Bunrodea" in node.government()): #In the game file they are split to Bunrodea and Bunrodea (Guard)
            government = "Bunrodea"
        elif ("Pirate" in node.government()): #There's a hidden system with government Pirate (Devil-Run Gang)
            government = "Pirate"
        elif ("Pug" in node.government()): #In the game files they are split to Pug and Pug (Wanderer)
            government = "Pug"
        else:
            government = node.government().strip(quotes)

        #Loops through system planets and populates the planets list and then using that info it populates description
        if node.planets():
            #Quarg systems can have ringworlds which show up as multiple planets so we check if a Quarg system has more than 3 planets to detect ringworlds, and that's also the case for all Heliarch systems but just in case in the future non ringworld Heliarch systems are added we check
            if not ((government == "Quarg" or government == "Heliarch") and len(node.planets()) > 3):
                for planet in node.planets():
                    planets.append(planet_attributes(planet))
                for p in planets:
                    #If last planet in system add the government at the end
                    if (list(p)[0] == list(list(planets)[-1])[0]):
                        name = list(p)[0]
                        description += f" ```{name.strip(quotes)}```\\n  {p[name][0]}  {p[name][1]}  {p[name][2]}``{government}``\""
                    #If not add an extra \\n to keep the wiki style
                    else:
                        name = list(p)[0]
                        description += f" ```{name.strip(quotes)}```\\n  {p[name][0]}  {p[name][1]}  {p[name][2]}\\n"
                planets = [] #Clear the planets list for the next system to use
            #If above conditions are met then we should only take the name of the first planet since the rest are the same
            else:
                planet = planet_attributes(node.planets()[0])
                name = list(planet)[0]
                description += f" ```{name.strip(quotes)}```\\n  {planet[name][0]}  {planet[name][1]}  {planet[name][2]}``{government}``\""
        else:
            description += f"  -No Spaceport\\n  -No Shipyard\\n  -No Outfitter\\n''{government}''\""

        name = node.name().strip(quotes) #Some systems have "" in their name in the map file so we remove them
        output += f"""{{
            "categoryId": "{ids[government]}",
            "position": [

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
