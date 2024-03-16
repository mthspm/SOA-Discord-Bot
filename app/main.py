import os
import asyncio
import discord
import time

from typing import Callable, Union

from discord import app_commands, Client, Intents, Activity, ActivityType
from dotenv import load_dotenv

from commands import Essentials
from tester import Test
from music import MusicPlayer
from cripto import CriptoCurrency
from settings import COMMANDS
from utils import debug, get_member
from webscrap import PatchNotes
from tibiantis import Analyser, Hunted, Team

class SOABOT(Client):
    def __init__(self) -> None:
        intents = Intents.all()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.essentials = Essentials()
        self.tibiantis = Analyser()
        self.patchnotes = PatchNotes(self)
        self.hunted = Hunted(self)
        self.team = Team(self)
        self.test = Test(self)
        self.music_player = MusicPlayer(self)
        self.cripto = CriptoCurrency(self)
    
    # setup slash commands
    async def setup_hook(self):
        for guild in self.guilds:
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        await self.__setup_commands()

    async def on_ready(self):
        #change presence
        await self.change_presence(activity=Activity(type=ActivityType.listening, name=COMMANDS))
        guilds = [guild.name for guild in self.guilds]
        debug(f'{self.user} has connected to Discord on servers {guilds}', function="client.on_ready", type="INFO")
        await self.runtasks()
        
    async def runtasks(self):
        self.tasks = {
            self.hunted.spotter : 60*5,
            self.team.spotter : 60*5,
            self.tibiantis.Compare : 60*5,
            #self.patchnotes.getLatestUpdates : 60*60
        }
        debug("Initiating courotines for tasks", function="client.runtasks")
        for task, interval in self.tasks.items():
            self.loop.create_task(self.schedule_task(task, interval))
        
    async def schedule_task(self, task, interval):
        while True:
            await task()
            debug(f"Task {task.__name__} finished", function="client.schedule_task")
            await asyncio.sleep(interval)
            
    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        else:
            debug(f"{message.channel} {message.author} {message.content}", function="client.on_message")

    async def on_voice_state_update(self, member, before, after):
        # Check for disconnection
        if member == self.user and before.channel is not None and after.channel is None:
            # Check if the bot is playing
            if self.music_player.voice_client is not None:
                await self.music_player.voice_client.disconnect(force=True)
            self.music_player.voice_client = None
            self.music_player.running = False
            debug(f'voice_client uptaded -> None', function="client.on_voice_state_update")
            # Forced clear music folder/queue
            self.music_player.queue.clear()
            await self.music_player.clear_all_musics_path()
   
    async def __setup_commands(self):
        
        commands = (
            # General Commands and DEBUG
            self.essentials.help,
            self.essentials.clear,
            self.essentials.invite,
            self.essentials.cfg,
            self.essentials.edit,
            self.test.test,
            
            # Music Commands
            self.music_player.join,
            self.music_player.leave,
            self.music_player.musicinfo,
            self.music_player.play,
            self.music_player.stop,
            self.music_player.pause,
            self.music_player.resume,
            self.music_player.skip,
            self.music_player.mqueue,
            
            # Cripto Commands
            self.cripto.price,
            self.cripto.mycripto,
            
            #Webscrap Tree Commands
            self.patchnotes.char,
            
            #Tibiantis
            self.tibiantis.check,
            self.tibiantis.clear_data,
            self.hunted.hunted,
            self.team.team
        )
        
        for cmd in commands:
            self.tree.command()(cmd)
        
if __name__ == "__main__":
    client = SOABOT()
    load_dotenv()
    client.run(os.getenv("TTT"))