import requests, discord, inspect

from discord import app_commands
from settings import *
from datetime import datetime
from utils import debug, load_json, save_json, new_exist
from requests.exceptions import JSONDecodeError

class PatchNotes:
    """
    PatchNotes Class
    ~~~~
    Class for getting game updates and pushing them to a Discord channel.
    Created based on https://api.axsddlr.xyz/:
    
    An Unofficial REST API for various gaming website and others, Made by Andre Saddler
    
    Methods:
        >>> getJsonUpdates(url) -> dict
        >>> pushUpdate(previous_update, new_update, path) -> bool
        >>> getUpdate(api, path, node=0) -> dict
        >>> sendUpdateMessage(data) -> bool
        >>> getLatestUpdates() -> None
    """
    def __init__(self, client) -> None:
        self.client = client
        self.channel = PATCH_NOTES_CHANNEL
    
    def getJsonUpdates(self, url):
        try:
            response = requests.get(url)
            return response.json()
        except JSONDecodeError:
            debug(f"Error decoding json from {url}", function="PatchNotes.getJsonUpdates", type="ERROR")
            return None

    def pushUpdate(self,previous_update, new_update, path):
        """
        Push a new update to the specified path if the previous data is different that the new.

        Args:
            previous_update (dict): The previous update data.
            new_update (dict): The new update data.
            path (str): The path to save the update.

        Returns:
            bool: True if the update was pushed successfully, False otherwise.
        """
        
        function_pusher = inspect.currentframe().f_back.f_code.co_name
        
        if not previous_update:
            save_json(path, new_update)
            debug(f"File {path} cant be opened, created new", function=f"PatchNotes.{function_pusher}", type="INFO")
            return
        elif "title" in previous_update.keys() and previous_update["title"] == new_update["title"]:
            return False
        elif "id" in previous_update.keys() and previous_update["id"] == new_update["id"]:
            return False
        else:
            save_json(path, new_update)
            return True
        
    async def getUpdate(self, api, path, node=0):
        """
        Args:
            api (request): url to the api that will be used to get the json data.
            path (str): path to the json file that will be used to save the data.
            node (int, optional): node that indicates the key from the dict to be extracted. Defaults to 0.    
        
        Nodes:
            0 : ["data"][0]\n
            1 : ["data"]["segments"][0]\n
            2 : ["data"]["featured"][0]\n

        Returns:
            _type_: _description_
        """

        json_response = self.getJsonUpdates(api)
        
        if node == 0:
            new_update = json_response["data"][0]
        elif node == 1:
            new_update = json_response["data"]["segments"][0] 
        elif node == 2:
            new_update = json_response["data"]["featured"][0]
        elif node == 3:
            new_update = json_response["news"][0]

        new_exist(path, new_update)
        previous_update = load_json(path)
        
        if not self.pushUpdate(previous_update, new_update, path):
            return False
        
        return new_update
        
    async def sendUpdateMessage(self, data):
        embed = discord.Embed(title=data["title"],
                              description=data["description"],
                              url=data["url"],
                              color=data["color"])
        
        embed.set_image(url=data["thumbnail"])
        embed.set_thumbnail(url=data["thumbnail"])
        embed.set_author(name=data["name"])
        embed.set_footer(text=f"{TITLE} | {VERSION}")
        embed.add_field(name="Date", value=data["date"], inline=True)
        embed.add_field(name="Author", value=data["author"], inline=True)
            
        await self.client.get_channel(self.channel).send(embed=embed)
        debug(f"{data['name']} send to patch-notes channel", function="PatchNotes.sendUpdateMessage", type="INFO")
        return True
    
    async def getLatestUpdates(self):
        debug("Getting latest updates...", function="PatchNotes.getLatestUpdates", type="INFO")

        for game in PATCH_NOTES_DATA:
            try:
                if "https://api.tibiadata.com" in game["path"]:
                    currentUpdate = await self.getUpdate(game["path"], game["filepath"], node=game["node"])
                else:
                    currentUpdate = await self.getUpdate("https://api.axsddlr.xyz" + game["path"], game["filepath"], node=game["node"])
                    
                if not currentUpdate:
                    debug(f"No new update for {game['name']}", function="PatchNotes.getLatestUpdates", type="INFO")
                    continue
                
                if "mapping" in game.keys():
                    for key, value in game["mapping"].items():
                        currentUpdate[key] = currentUpdate[value]
                        del currentUpdate[value]
                
                if "default" in game.keys():
                    for key, value in game["default"].items():
                        if key not in currentUpdate.keys() or currentUpdate[key] == "": 
                            currentUpdate[key] = value
                
                debug(f"New update for {game['name']} found.", function="PatchNotes.getLatestUpdates", type="INFO")
                
                try:
                    date = datetime.fromisoformat(currentUpdate["date"])
                except:
                    date = currentUpdate["date"]


                if "customUrl" in game.keys():
                    currentUpdate["url"] = game["customUrl"] + currentUpdate["url"]

                data = {
                    "name": game["name"],
                    "title": currentUpdate["title"],
                    "author": currentUpdate["author"],
                    "description": currentUpdate["description"],
                    "url": currentUpdate["url"],
                    "thumbnail": currentUpdate["thumbnail"],
                    "color": game["color"],
                    "date": date
                }
                
                await self.sendUpdateMessage(data)
            except Exception as e:
                debug(f"Error getting latest updates for {game['name']}:\n{e}", function="PatchNotes.getLatestUpdates", type="ERROR")
                continue
            
    @app_commands.describe(name="Name of the character to get info")
    async def char(self, interaction, name:str):
        """Get character info from tibia.com"""
        url = "https://api.tibiadata.com/v4/character/" + name
        r = self.getJsonUpdates(url)
        user = interaction.user
        
        try:
            data = r["character"]
        except KeyError:
            await interaction.response.send_message("Something wrong with request, report to devs", ephemeral=True)
            debug(f"Failed to load tibia api: {KeyError}", function="PatchNotes.char", type="INFO")
            return
        if not r:
            await interaction.response.send_message("Character not found", ephemeral=True)
            debug(f"{user} Character {name} not found", function="PatchNotes.char", type="INFO")
            return
        if not data["character"]["name"]:
            await interaction.response.send_message("Character not found", ephemeral=True)
            debug(f"{user} Character {name} not found", function="PatchNotes.char", type="INFO")
            return
        
        tibia_url = "https://www.tibia.com/community/?name=" + name.replace(" ", "+")
        timestamp = r["information"]["timestamp"]
        timestamp = datetime.fromisoformat(timestamp)
        
        
        default = {
            "character": "Not Avaliable",
            "account_information": "Not Avaliable",
            "deaths": "Not Avaliable",
            "other_characters": "Not Avaliable",
            "achievements": "Not Avaliable",
            "account_badges": "Not Avaliable"
        }
        
        for key in default.keys():
            if key in data.keys():
                default[key] = data[key]
    
        dict_embed = {
            "title": tibia_url,
            "description": "Character info from tibia.com",
            "color": 0xFF0000,
            "url": tibia_url,
            "author" : {
                "name": f"{name.capitalize()} Character Info",
                "url": tibia_url,
                "icon_url": TIBIA_CHAR_ICON,
            },
            "thumbnail": {
                "url": TIBIA_PNG},
            "footer" : {
                "text": f"{TITLE} | {VERSION} | /char {name}",
                }
        }
        
        embed = discord.Embed.from_dict(dict_embed)
        embed.add_field(name="🔍General Information", value="", inline=False)
        
        #General Information
        for key, obj in default["character"].items():
            if isinstance(obj, str) or isinstance(obj, int):
                embed.add_field(name=key.capitalize(), value=obj, inline=True)
        #Guild
        for key, obj in default["character"].items():
            if isinstance(obj, dict):
                if not obj:
                    embed.add_field(name=f"⚔️{key.capitalize()}", value="None", inline=False)
                else:
                    embed.add_field(name=f"⚔️{key.capitalize()}", value="", inline=False)
                    for k, v in obj.items():
                        embed.add_field(name=k.capitalize(), value=v, inline=True)
                        
        
        debug(f"{user} Character {name} found", function="PatchNotes.char", type="INFO")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        


#debug
if __name__ == "__main__":
    patch = PatchNotes("client")