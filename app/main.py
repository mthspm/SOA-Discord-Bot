import discord
import dotenv
import os
import asyncio

from discord import app_commands
from commands import help, cfg, edit, clear, invite
from tester import Test
from music import MusicPlayer
from cripto import CriptoCurrency
from settings import SOA, COMMANDS
from utils import debug
from webscrap import PatchNotes

#!TODO - > Move the data to a postgree database

class Client(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.all()
        super().__init__(intents=intents)
        self.guild = discord.Object(id=SOA) 
        self.tree = app_commands.CommandTree(self)
        self.patchnotes = PatchNotes(self)
        self.patchNotesLoop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        
    async def update_presence(self):
        #!TODO -> https://qwertyquerty.github.io/pypresence/html/doc/presence.html#Presence
        #!TODO -> pypresence, Presence() class, -> create groups? games?
        pass

    # setup slash commands
    async def setup_hook(self):
        self.tree.copy_global_to(guild=self.guild)
        await self.tree.sync(guild=self.guild)

    async def on_ready(self):
        #change presence
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=COMMANDS))
        self.loop.create_task(self.patchNotesTask())
        debug("Logged on as {0}!".format(self.user), function="client.on_ready")
        
    async def patchNotesTask(self):
        """Event that sends patch notes to a channel every setted interval"""
        max_interval = 60*60

        while True:
            #await self.patchnotes.getLatestUpdates()
            debug(f"Sleeping for {max_interval}s for next call for patch notes update...", function="client.patchNotesTask", type="INFO")
            await asyncio.sleep(max_interval)
            
    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        else:
            debug(f"{message.channel} {message.author} {message.content}", function="client.on_message")

class App:
    def __init__(self) -> None:
        self.client = Client()
        self.music_player = MusicPlayer(self.client)
        self.cripto = CriptoCurrency(self.client)
        self.test = Test(self.client)
        
        self.__setup()

    def __setup(self):
        #Commands Tree Commands
        self.client.tree.command()(help)
        self.client.tree.command()(clear)
        self.client.tree.command()(invite)
        
        #Game Config Tree Commands
        self.client.tree.command()(cfg)
        self.client.tree.command()(edit)
        
        #Help Tree Commands
        self.client.tree.command()(self.test.test)
        
        #Music Tree Commands
        self.client.tree.command()(self.music_player.join)
        self.client.tree.command()(self.music_player.leave)
        self.client.tree.command()(self.music_player.musicinfo)
        self.client.tree.command()(self.music_player.play)
        self.client.tree.command()(self.music_player.stop)
        self.client.tree.command()(self.music_player.pause)
        self.client.tree.command()(self.music_player.resume)
        self.client.tree.command()(self.music_player.skip)
        self.client.tree.command()(self.music_player.mqueue)
        
        #Cripto Tree Commands
        self.client.tree.command()(self.cripto.price)
        self.client.tree.command()(self.cripto.mycripto)
        
        #Webscrap Tree Commands
        self.client.tree.command()(self.client.patchnotes.char)

    def run(self):
        dotenv.load_dotenv()
        self.client.run(os.getenv("TTT"))

app = App()
client = app.client
music_player = app.music_player

@client.event
async def on_voice_state_update(member, before, after):
    if member == client.user and before.channel is not None and after.channel is None:
        debug(f'voice_client uptaded -> None', function="client.on_voice_state_update")
        if music_player.voice_client is not None:
        # O bot foi desconectado de uma sala de voz
            await music_player.voice_client.disconnect(force=True)
        music_player.voice_client = None
        music_player.running = False
        music_player.queue.clear()
        await music_player.clear_all_musics_path()

if __name__ == "__main__":
    app.run()