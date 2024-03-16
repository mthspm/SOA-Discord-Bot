import requests, json, time, discord, aiohttp
from pathlib import Path
from bs4 import BeautifulSoup
from settings import *
from discord import app_commands
from utils import debug, flagger, AutoClearBOTMSG
from typing import List
from operator import attrgetter

class Character:
    """Class for handling character data"""
    
    def __init__(self, name, level, vocation, url):
        self.name = name
        self.level = level
        self.vocation = vocation
        self.url = url
        self.guild = "None"
        self.house = "None"
        self.deaths = "None"
        self.outchars = "None"
        self.online = False
        
    def __str__(self):
        return f"{self.name} - {self.level} {self.vocation} - {self.guild}"
    
    def __repr__(self):
        return f"{self.name} - {self.level} {self.vocation} - {self.guild}"
    
    def __eq__(self, other):
        if isinstance(other, Character):
            return self.name == other.name
        elif isinstance(other, str):
            return self.name == other
        else:
            return False
    
    def __hash__(self):
        return hash(self.name)
    
    def update(self):
        return Hooker().GetCharacter(self.name)
    

class Hooker:
    """Class for handling hooks and managing the data from requests"""
    def __init__(self):
        pass
    
    def GetOnline(self) -> List[Character]:
        response = requests.get(WHOISONLINE)
        soup = BeautifulSoup(response.text, 'html.parser')
        charlist = []
        
        table = soup.find('table', class_='tabi')
        
        for tr in table.find_all('tr', class_='hover'):
            td = tr.find_all('td')
            name = td[0].text
            url = "https://tibiantis.online/" + td[0].find('a')['href']
            level = td[1].text
            vocation = td[2].text
            charlist.append(Character(name, level, vocation, url))
        
        return charlist
    
    async def GetCharacter(self, name: str) -> Character:
        """Returns a character object from the server Tibiantis.online"""
        async with aiohttp.ClientSession() as session:
            async with session.get(SEARCHCHAR.format(name)) as response:
                try:
                    response.raise_for_status()
                    html = await response.text()

                    soup = BeautifulSoup(html, 'html.parser')
                    news = soup.find('div', class_='news')
                    tables = news.find_all('table', class_='tabi')
            
                    char_info = tables[0]
                    #last_deaths = tables[1]
                    #account_info = tables[2]
                    #characters = tables[3]
                    
                    char = {}
                    
                    rows = char_info.find_all('tr', class_='hover')
                    for row in rows:
                        cells = row.find_all('td')
                        key = cells[0].text.strip()
                        value = cells[1].text.strip()
                        char[key.rstrip(":")] = value
                    
                    failed_char = Character(name, "Unable to load", "Unable to load", SEARCHCHAR.format(name))
                        
                    if "Name" not in char:
                        return failed_char
                    
                    character = Character(char["Name"], char["Level"], char["Vocation"], SEARCHCHAR.format(name))
                    
                    if "Guild Membership" in char:
                        character.guild = char["Guild Membership"]
                        
                    return character
                except aiohttp.ClientError as e:
                    debug(e)
                    return failed_char
    
class Analyser:
    """Class for handling the data from the Hooker"""
    def __init__(self):
        self.hook = Hooker()
        self.path = Path(__file__).parent / "users" / "data.json"
        self.loadData()
        self.online = self.hook.GetOnline()
        
    def save(self, data):
        with open(self.path, 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)
            
    def loadData(self):
        try:
            with open(self.path, 'r') as f:
                self.data = json.load(f)
        except:
            debug("No makers data file found, creating a new one", function="tibiantis.analyser.loadData", type="INFO")
            self.data = {}
            json.dump(self.data, open(self.path, 'w'))
            
    async def Compare(self):
        """Compares the online list with the data from the last scan"""
        debug("Comparing online list with data", function="tibiantis.analyser.Compare", type="INFO")
        before = self.online
        now = self.hook.GetOnline()
        loggedOut = []
        loggedIn = []
        
        for char in before:
            if char.name not in [c.name for c in now]:
                loggedOut.append(char)
                
        for char in now:
            if char.name not in [c.name for c in before]:
                loggedIn.append(char)
                
        for char in loggedOut:
            for maker in loggedIn:
                if char.name in self.data:
                    # Verifica se a chave "makers" existe no dicionário self.data[char.name]
                    if "makers" in self.data[char.name]:
                        for m in self.data[char.name]["makers"]:
                            if m["name"] == maker.name:
                                m["count"] += 1
                                if m["count"] >= 4:
                                    debug(f"{maker.name} possivelmente eh maker de {char.name}!", function="tibiantis.analyser.Compare", type="INFO")
                                break
                        else:
                            # Se nenhum maker com o mesmo nome for encontrado, adiciona um novo maker
                            self.data[char.name]["makers"].append({"name": maker.name, "count": 1})
                    else:
                        # Se a chave "makers" não existir, cria uma lista de makers
                        self.data[char.name]["makers"] = [{"name": maker.name, "count": 1}]
                else:
                    # Se a chave char.name não existir em self.data, cria um novo dicionário para ela
                    self.data[char.name] = {"makers": [{"name": maker.name, "count": 1}]}
                    
        self.online = now
        self.save(self.data)
        debug("Finished comparing online list with data", function="tibiantis.analyser.Compare", type="INFO")
        
    @app_commands.describe(name="name of the character")
    async def check(self, interaction, name: str):
        """Check the makers of a character from Tibiantis."""
        result = []
        if name in self.data:
            for maker in self.data[name]["makers"]:
                if maker["count"] >= 4:
                    result.append(maker)
        else:
            result = "No character found"
            
        if isinstance(result, list):
            if result:
                result = "\n".join([f"{maker['name']} | Accuracy:{maker['count']}" for maker in result])
            else:
                result = "No makers found"
            
        
        embed = discord.Embed(
            title=f"Makers List - Tibiantis Online",
            description=f"List of makers for {name}:\n{result}",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"{TITLE} | {VERSION} | {AUTHOR}")
        embed.set_thumbnail(url=TIBIA_CHAR_ICON)
        debug(f"{interaction.user} requested makers for {name}", function="tibiantis.makercheck", type="CMD")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    @app_commands.describe(incidents="Reference of incidents that the data must clean")
    async def clear_data(self, interaction, incidents : int):
        """Clear all data from tibiantis makers with less incidents that was referenced."""
        if not flagger(interaction.user.roles, PRESIDENT_ID, ADM_TIBIANTIS):
            return await interaction.response.send_message(ACCESS_DENIED, ephemeral=True)
        
        #clear all makers with x incident makers on self.data
        for char in self.data:
            self.data[char]["makers"] = [maker for maker in self.data[char]["makers"] if maker["count"] > incidents]
            
        self.save(self.data)
        await interaction.response.send_message(f"Data cleared with {incidents} incidents as reference", ephemeral=True)
        debug(f"{interaction.user} cleared data with {incidents} incidents as reference", function="tibiantis.clear_data", type="CMD")
        
class Handler:
    def __init__(self, client, filename, channel) -> None:
        self.path = Path(__file__).parent / "users" / filename
        self.client : discord.Client = client
        self.hook : Hooker = Hooker()
        self.channel = channel
        self._running = False
        self.loadData()
        
        self.actions = {
            "add": self.add,
            "remove": self.remove,
            "edit": self.edit,
            "online": self.online_check
        }
        
    async def handle_actions(self, action: str, name: str, reason: str):
        try:
            if action in self.actions:
                return await self.actions[action](name=name, reason=reason)
            else:
                return None
        except Exception as e:
            debug(f"An error occurred: {e}", function="tibiantis.handle_actions", type="ERROR")
            return "Can't perform the action"
        
    def save(self, data):
        with open(self.path, 'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)
            
    def loadData(self):
        """Load data from the file or create a new file if it doesn't exist"""
        if not self.path.exists():
            # Se o arquivo não existir, cria um novo arquivo e retorna um dicionário vazio
            json.dump({}, open(self.path, 'w'))
            self.data = {}
        try:
            # Tenta abrir o arquivo e carregar os dados
            with open(self.path, 'r') as f:
                self.data = json.load(f)
        except Exception as e:
            # Em caso de erro, imprime o erro e retorna um dicionário vazio
            print(f"Error loading data: {e}")
            self.data = {}
            
    def toggle_running(self):
        """Function to toggle the running attribute of the class"""
        self._running = not self._running
        
    def is_runing(self):
        """Function to check if the class is running"""
        return self._running
    
    async def add(self, name: str, reason: str = "None"):
        """Add a character to the list"""
        if name in self.data:
            return f"{name} already in list"
        
        char = await self.hook.GetCharacter(name)
        if char.level == 'Unable to load':
            return f"{name} not exist"
        
        self.data[name] = {"reason": reason}
        self.save(self.data)
        return f"{name} added to list"
    
    async def remove(self, name: str, reason: str = "None"):
        """Remove a character from the list"""
        if name not in self.data:
            return f"{name} not found in list"
        
        del self.data[name]
        self.save(self.data)
        return f"{name} removed from list"
    
    async def edit(self, name: str, reason: str = "None"):
        """Edit a character from the list"""
        if name not in self.data:
            return f"{name} not found in list"
        
        self.data[name] = {"reason": reason}
        self.save(self.data)
        return f"reason {reason} edited in {name} from list"
    
    async def online_check(self, name: str = "None", reason: str = "None"):
        """Check the list and players online and send a message of all players online"""
        online = await self.hook.GetOnline()
        online = [char for char in online if char.name in self.data]
        if online:
            online = "\n".join([f"{char.name} - {char.level} {char.vocation}" for char in online])
            return online
        else:
            return "No players online"
        
    async def spotter(self) -> None:
        """Event that sends the updated list every set interval"""
        debug(f"Starting {self.__class__.__name__} spotter", function=f"tibiantis.{self.__class__.__name__}.spotter", type="INFO")
        self.toggle_running()
        online = self.hook.GetOnline()
        channel = self.client.get_channel(self.channel)
        
        await AutoClearBOTMSG(channel, self.client.user)
        
        timenow = time.strftime("%H:%M:%S")
        message = f"```diff\n{self.__class__.__name__.upper()} BOARD Last Updated in {timenow}\n"
        if self.data:
            for char, value in self.data.items():
                status = "+ " if char in online else "- "
                obj = await self.hook.GetCharacter(char)
                pre_result = f"{status}{obj.name.ljust(30)} {obj.level} {obj.vocation.ljust(20)} Guild: {obj.guild.ljust(35)} Reason: {value['reason'].ljust(30)}\n"
                if len(message) + len(pre_result) > 2000:
                    message += "```"
                    await channel.send(message)
                    message = "```diff\n"
                    debug(f"Sent {self.__class__.__name__} list to {channel}", function=f"tibiantis.{self.__class__.__name__}.spotter", type="INFO")
                else:
                    message += pre_result
        else:
            message += "No players"
            
        message += "```"
        await channel.send(message)
        self.toggle_running()
        debug(f"Finnished sending {self.__class__.__name__} list to {channel}", function=f"tibiantis.{self.__class__.__name__}.spotter", type="INFO")
        
class Hunted(Handler):
    def __init__(self, client):
        super().__init__(client, "hunted.json", HUNTED_CHANNEL)
        
    @app_commands.describe(action="add/remove/online/edit", name="name of the character", reason="reason for hunted")
    async def hunted(self, interaction, action: str = "None", name: str = "None", reason: str = "None"):
        """Command to see the hunted list and add or remove characters from it"""
        
        permission = flagger(interaction.user.roles, MOD_TIBIANTIS, ADM_TIBIANTIS)
        if not permission:
            return await interaction.response.send_message(ACCESS_DENIED, ephemeral=True)
        
        if self.is_runing():
            return await interaction.response.send_message(AWAIT_HUNTED_TASK, ephemeral=True)
        
        result = await self.handle_actions(action, name, reason)
        
        if result is None:
            result = "".join([f"{char} - {self.data[char]['reason']}\n" for char in self.data])

        embed = discord.Embed(
            title=f"Hunted List - Tibiantis Online\n",
            description=result,
            color=discord.Color.red()
        )
        embed.set_footer(text=f"{TITLE} | {VERSION} | {AUTHOR}")
        embed.set_thumbnail(url=TIBIA_CHAR_ICON)
        debug(f"{interaction.user} used hunted cmd with {action} on {name}", function="tibiantis.hunted", type="CMD")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
class Team(Handler):
    def __init__(self, client):
        super().__init__(client, "team.json", TEAM_CHANNEL)
        
    @app_commands.describe(action="add/remove/edit", name="name of the character", reason="note for the character ex: maker de rhasta")
    async def team(self, interaction, action: str = "None", name: str = "None", reason: str = "None"):
        """Command to see the team list and add or remove characters from it"""
        
        permission = flagger(interaction.user.roles, MOD_TIBIANTIS, ADM_TIBIANTIS)
        if not permission:
            return await interaction.response.send_message(ACCESS_DENIED, ephemeral=True)
        
        if self.is_runing():
            return await interaction.response.send_message(AWAIT_TEAM_TASK, ephemeral=True)
        
        result = await self.handle_actions(action, name, reason)
        
        if result is None:
            result = "".join([f"{char} - {self.data[char]['reason']}\n" for char in self.data])
            
        embed = discord.Embed(
            title=f"Team List - Tibiantis Online\n",
            description=result,
            color=discord.Color.red()
        )
        embed.set_footer(text=f"{TITLE} | {VERSION} | {AUTHOR}")
        embed.set_thumbnail(url=TIBIA_CHAR_ICON)
        debug(f"{interaction.user} used team cmd with {action} on {name}", function="tibiantis.team", type="CMD")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        
class Wiki:
    def __init__(self, client):
        self.client = client
        
    def hook(self):
        request = requests.get("https://tibiantis.info/library/items")
        soup = BeautifulSoup(request.text, 'html.parser')
        #find div with id =items
        items = soup.find('div', id='items')
        for tr in items.find_all('tr'):
            print(tr)
        print(items)
    
        
if __name__ == "__main__":
    wiki = Wiki(None)
    wiki.hook()