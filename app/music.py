# Path: app/music.py

import os
import asyncio
import random
import discord
from dotenv import load_dotenv
from discord import app_commands
from pytube import YouTube
from pathlib import Path
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException
from settings import *
from utils import debug, flagger, url_checker, filter_str, del_file



class Music:
    """
    Represents a music object with various attributes.

    Attributes:
        name (str): The name of the music.
        artist (str): The artist of the music.
        url (str): The URL of the music.
        path (str): The path of the music file.
        thumbnail (str): The URL of the music's thumbnail.
        publish_date (str): The publish date of the music.
        description (str): The description of the music.
        rating (float): The rating of the music.
        views (int): The number of views of the music.
    """

    def __init__(self, name, artist, url, path, thumbnail, publish_date,
                 description, rating, views) -> None:
        self.name = name
        self.url = url
        self.artist = artist
        self.path = path
        self.thumbnail = thumbnail
        self.publish_date = publish_date
        self.description = description
        self.rating = rating
        self.views = views
        
        self.__setup()

    def __str__(self) -> str:
        return list(self.__dict__.keys())
    
    def __repr__(self) -> str:
        return list(self.__dict__.keys())
    
    def __setup(self):
        if self.description is None:
            self.description = "No description"
        elif len(self.description) > 512:
            self.description = self.description[:512] + "..."
        
        if self.rating is None:
            self.rating = "No Available"
        
        if self.views is None:
            self.views = "No Available"
        
        if self.publish_date is None:
            self.publish_date = "No Available"
            
        if self.artist is None:
            self.artist = "No Available"
        
    

class MusicPlayer:
    """
    Represents a music player that can connect to a voice channel, download music, and perform other related operations.

    Attributes:
        client (discord.Client): The Discord client object.
        voice_client (discord.VoiceClient): The voice client object.
        running (bool): Indicates whether the music player is running or not.
        queue (list): The queue of music to be played.
        __connected (bool): Indicates whether the music player is connected to Spotify or not.
        __api (spotipy.Spotify): The Spotify API object.
    """

    def __init__(self, client):
        self.client = client
        self.voice_client = None
        self.running = False
        self.queue = []
        self.__connected = False
        self.__connect()

    def __connect(self):
        """
        Connects to the Spotify API using the provided client credentials.
        """
        try:
            load_dotenv()
            auth = SpotifyClientCredentials(os.getenv("SI"), os.getenv("SS"))
            self.__api = Spotify(auth_manager=auth)
            self.__connected = True
            debug("Spotify Connected", function="music.MusicPlayer.__connect")
        except Exception as e:
            debug(f'Spotify Connection Error {e}', function="music.MusicPlayer.__connect", type="ERROR")

    def __getinfo(self, name):
        """
        Searches for a song on Spotify and returns the search results.

        Args:
            name (str): The name of the song to search for.

        Returns:
            dict: The search results from Spotify.
        """
        if not self.__connected:
            self.__connect()
        try:
            search = self.__api.search(q=name, limit=1, type='track')
            return search
        except Exception as e:
            debug(f'Spotify Search Error {e}', function="music.MusicPlayer.__getinfo", type="ERROR")

    async def download_music(self, url):
        """
        Download a song from YouTube.

        Args:
            url (str): The URL of the song.

        Returns:
            Union[Music, bool]: A Music object with the song info if the song was downloaded successfully,
                                False if the song was not downloaded.
        """
        output_path = Path(__file__).parent / "music"
        try:
            yt = YouTube(url)
            filename = filter_str(yt.title) + ".mp3"
            yt.streams.filter(only_audio=True).first().download(output_path=output_path, filename=filename)
            music = Music(yt.title,
                          yt.author,
                          yt.watch_url,
                          os.path.join(output_path, filename),
                          yt.thumbnail_url,
                          yt.publish_date,
                          yt.description,
                          yt.rating,
                          yt.views)
            debug(f"Downloaded {url}", function="music.MusicPlayer.download_music")
            return music
        except Exception as e:
            debug(f'YouTube Error {e}', function="music.MusicPlayer.download_music", type="ERROR")
            return False

    async def join(self, interaction):
        """
        Joins the voice channel of the user who sent the interaction.
        
        Note:
            This method don't respond to the interaction if called outside the slash (/) function command.

        Args:
            interaction (discord.Interaction): The interaction object.

        Returns:
            Optional[discord.VoiceClient]: The voice client object if successfully joined the voice channel,
                                            None otherwise.
        """
        voice_channel = interaction.user.voice.channel
        text_channel = interaction.channel
        commanad_name = interaction.command.name
        exterior = False if commanad_name == "join" else True

        if self.voice_client is not None:
            message = IN_VOICE_CHANNEL.format(self.voice_client.channel)
            if not exterior:
                await interaction.response.send_message(message, ephemeral=True)
                debug(f"Bot is already in {self.voice_client.channel}", function="music.MusicPlayer.join", type="ERROR")

            return None
        else:
            self.voice_client = await voice_channel.connect()
            success_message = JOINED_VOICE_CHANNEL.format(voice_channel)
            debug(f"Bot joined {voice_channel}", function="music.MusicPlayer.join")
            if not exterior:
                await interaction.response.send_message(success_message, ephemeral=True)

            return self.voice_client
        
    async def leave(self, interaction):
        """
        Leaves the voice channel the bot is currently in.
        
        Note:
            This method don't respond to the interaction if called outside the slash (/) function command.

        Args:
            interaction (discord.Interaction): The interaction object.

        Returns:
            bool: True if successfully left the voice channel,
                                False if not in the voice channel or not in the user's voice channel,
        """
        voice_channel = interaction.user.voice.channel
        text_channel = interaction.channel
        commanad_name = interaction.command.name
        exterior = False if commanad_name == "leave" else True

        if self.voice_client is None or self.voice_client.channel != voice_channel:
            error_message = NOT_IN_ANY_VOICE_CHANNEL if self.voice_client is None else NOT_IN_YOUR_VOICE_CHANNEL
            if not exterior:
                await interaction.response.send_message(error_message, ephemeral=True)

            debug(f"Bot is not in {voice_channel}", function="music.MusicPlayer.leave", type="ERROR")
            return False

        await self.voice_client.disconnect()

        success_message = LEFT_VOICE_CHANNEL.format(voice_channel)
        
        if not exterior:
            await interaction.response.send_message(success_message, ephemeral=True)

        debug(f"Bot left {voice_channel}", function="music.MusicPlayer.leave")
        return True
     
    def shuffle_queue(self):
        for i in range(len(self.queue)-1, 0, -1):
            j = random.randint(0, i + 1)
            self.queue[i], self.queue[j] = self.queue[j], self.queue[i]
        debug(f"Shuffled queue", function="music.MusicPlayer.shuffle_queue")
        
    @app_commands.describe(query="The url of the song you want to see the info")
    async def musicinfo(self, interaction, query: str):
        """
        Searches for a song on Spotify and shows the info.

        Args:
            interaction (discord.Interaction): The interaction object.
            query (str): The URL of the song.

        Returns:
            bool: True if the song info was found and sent successfully,
                    False otherwise.
        """
        text_channel = interaction.channel
        music_info = ""

        info = self.__getinfo(query)
        if info is None:
            await interaction.response.send_message(SONG_NOT_FOUND, ephemeral=True)
            return False
        else:
            # Perform further operations with the retrieved song info
            image = info['tracks']['items'][0]['album']['images'][0]['url']
            data = {
                "name": info['tracks']['items'][0]['name'],
                "artist": info['tracks']['items'][0]['artists'][0]['name'],
                "url": info['tracks']['items'][0]['external_urls']['spotify'],
                "album": info['tracks']['items'][0]['album']['name'],
                "duration": round((info['tracks']['items'][0]['duration_ms'] / 1000 / 60), 2),
                "explicit": info['tracks']['items'][0]['explicit'],
                "rank/popularity": info['tracks']['items'][0]['popularity'],
                "release date": info['tracks']['items'][0]['album']['release_date'],
                "disc number": info['tracks']['items'][0]['disc_number'],
                "album type": info['tracks']['items'][0]['album']['album_type']
            }
            

            music_info = "\n".join([f"{key.capitalize()} : {value}" for key, value in data.items()])

            embed = discord.Embed(title="See below some interesting info!", description=music_info, color=0x00ff00)
            embed.set_thumbnail(url=image)
            embed.set_footer(text=f"Requested by {interaction.user}")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            return True
  
    async def conditioner(self, interaction):
        """
        Check if the user is in a voice channel and if the bot is in the same voice channel
        
        Args:
            interaction (discord.Interaction): The interaction object.
            
        Returns:
            bool: True if the user is in a voice channel and if the bot is in the same voice channel,
                    False otherwise.
        """
        if not self.voice_client:
            await interaction.response.send_message(NOT_IN_ANY_VOICE_CHANNEL, ephemeral=True)
            return False

        if interaction.user.voice.channel != self.voice_client.channel:
            await interaction.response.send_message(NOT_IN_YOUR_VOICE_CHANNEL, ephemeral=True)
            return False
        
        return True
    
    async def clean_music_path(self, actual_music, actual_path):
        if type(actual_music[0]._process) == discord.utils._MissingSentinel:
            if self.queue and actual_music[1] == self.queue[0][1]:
                debug(f"Can't clean music because is the next song {actual_path}", function="music.MusicPlayer.play", type="ERROR")
                return False
            else:         
                return await del_file(actual_path)
 
    async def clear_all_musics_path(self):
        for file in os.listdir(os.path.join(Path(__file__).parent, "music")):
            await del_file(os.path.join(Path(__file__).parent, "music", file))
            
        debug(f"Cleaned musics folder", function="music.MusicPlayer.clear_all_musics_path")
        return True
        
    @app_commands.describe(query="The url of the song you want to play")
    async def play(self, interaction, query: str):
        """Play a song"""
        text_channel = interaction.channel
        user = interaction.user
        debug(f"{user} requested to play {query}", function="music.MusicPlayer.play")

        # Try to join the voice channel
        await self.join(interaction)

        # Check if the user is in a voice channel
        if interaction.user.voice.channel != self.voice_client.channel:
            await interaction.response.send_message(NOT_IN_YOUR_VOICE_CHANNEL, ephemeral=True)
            debug(f"{user} is not in the voice channel", function="music.MusicPlayer.play", type="ERROR")
            return False
        
        # Check if the url is valid
        if not url_checker(query):
            await interaction.response.send_message(ENTRY_NOT_URL, ephemeral=True)
            debug(f"{user} entered an invalid url {query}", function="music.MusicPlayer.play", type="ERROR")
            return False
        
        # Create the music object and download the song
        music = await self.download_music(query)
        
        # Check if the song was downloaded
        if not music:
            await interaction.response.send_message(SONG_NOT_VALID, ephemeral=True)
            debug(f"{user} entered an invalid url {query}", function="music.MusicPlayer.play", type="ERROR")
            return False
        
        source = discord.FFmpegPCMAudio(music.path)
        queue_song_path = source._process.args[2]
        queue_song_name = os.path.basename(queue_song_path)
        
        self.queue.append((source, queue_song_name))
        

        embed = discord.Embed(
            title=f"{music.name} requested by {str(interaction.user).capitalize()}",
            description=f"Artist: {music.artist}\nURL: {music.url}",
            color=discord.Color.green()
        )
        embed.url = music.url
        embed.set_thumbnail(url=music.thumbnail)
        embed.add_field(name="Publish Date", value=music.publish_date)
        embed.add_field(name="Views", value=music.views)
        embed.add_field(name="Rating", value=music.rating)
        embed.add_field(name="Description", value=music.description)
        embed.add_field(name="Songs in queue", value=len(self.queue))
        embed.add_field(name="Queue", value="\n".join([f"{i+1}. **{song[1]}**" for i, song in enumerate(self.queue)]), inline=False)
        embed.set_footer(text=f"Requested by {interaction.user}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        if self.running:
            return True
        else:
            self.running = True
            while True:
                try:
                    actual_music = self.queue.pop(0)
                    actual_path = actual_music[0]._process.args[2]
                    self.voice_client.play(actual_music[0])

                    while self.voice_client.is_playing():
                        await asyncio.sleep(1)
                        
                    await self.clean_music_path(actual_music, actual_path)
                    
                except Exception as e:
                    debug(f'Error {e}', function="music.MusicPlayer.play", type="ERROR")
                    return False
                
                if len(self.queue) == 0:
                    self.running = False
                    await asyncio.sleep(10)
                    await self.leave(interaction)
                    return True
                else:
                    continue
        
    async def stop(self, interaction):
        """Stop the music, clear the queue and leave the voice channel"""
        username = str(interaction.user).capitalize()
                
        if not await self.conditioner(interaction):
            debug(f"{username} failed to stop the music", function="music.MusicPlayer.stop", type="ERROR")
            return False
        
        if not self.running:
            await interaction.response.send_message(f"Music is not playing", ephemeral=True)
            debug(f"{username} failed to stop the music", function="music.MusicPlayer.stop", type="ERROR")
            return False
        
        response = await self.leave(interaction)
        
        if response:
            await interaction.response.send_message(f"Music Stopped", ephemeral=True)
            debug(f"{username} stopped the music", function="music.MusicPlayer.stop")
            return True
        else:
            await interaction.response.send_message(f"Failed to stop the music", ephemeral=True)
            debug(f"{username} failed to stop the music", function="music.MusicPlayer.stop", type="ERROR")
            return False
  
    async def pause(self, interaction):
        """Pause the music"""
        text_channel = interaction.channel
        
        if not await self.conditioner(interaction):
            debug(f"{interaction.user} failed to pause the song", function="music.MusicPlayer.pause", type="ERROR")
            return False

        if self.voice_client.is_playing():
            self.voice_client.pause()
            await interaction.response.send_message(f"Music Paused", ephemeral=True)
            debug(f"{interaction.user} paused the song", function="music.MusicPlayer.pause")
            return True
        else:
            await interaction.response.send_message(f"Music is not playing", ephemeral=True)
            debug(f"{interaction.user} failed to pause the song", function="music.MusicPlayer.pause", type="ERROR")
            return False
        
    async def resume(self, interaction):
        """Resume the music"""
        text_channel = interaction.channel
        
        if not await self.conditioner(interaction):
            debug(f"{interaction.user} failed to resume the song", function="music.MusicPlayer.resume", type="ERROR")
            return False
        
        if self.voice_client.is_paused():
            self.voice_client.resume()
            await interaction.response.send_message(f"Music Resumed", ephemeral=True)
            debug(f"{interaction.user} resumed the song", function="music.MusicPlayer.resume")
            return True
        else:
            await interaction.response.send_message(f"Music is not paused", ephemeral=True)
            debug(f"{interaction.user} failed to resume the song", function="music.MusicPlayer.resume", type="ERROR")
            return False
        
    async def skip(self, interaction):
        """Skip the current song"""
        text_channel = interaction.channel
        
        if not await self.conditioner(interaction):
            debug(f"{interaction.user} failed to skip the song", function="music.MusicPlayer.skip", type="ERROR")
            return False

        if self.voice_client.is_playing():
            self.voice_client.stop()
            await interaction.response.send_message(f"Music Skipped", ephemeral=True)
            debug(f"{interaction.user} skipped the song", function="music.MusicPlayer.skip")
            return True
        else:
            await interaction.response.send_message(f"Music is not playing", ephemeral=True)
            debug(f"{interaction.user} failed to skip the song", function="music.MusicPlayer.skip", type="ERROR")
            return False
        
    @app_commands.describe(action="The action you want to perform")    
    async def mqueue(self, interaction, action: str = "show"):
        """Show or Clear the queue
        
        Args:
            interaction: The interaction object representing the user's interaction with the bot.
            action (str): The action to perform on the queue. Defaults to "show".
        
        Returns:
            bool: True if the operation is successful, False otherwise.
        """
            
        if not await self.conditioner(interaction):
            debug(f"{interaction.user} failed to perform {action} on the queue", function="music.MusicPlayer.mqueue", type="ERROR")
            return False
        
        action = action.lower()
        
        if action == "show":
            pass
        elif action == "clear":
            self.queue.clear()
        elif action == "shuffle":
            self.shuffle_queue()
        else:
            action = "Invalid"
            
        action = f"{action}ed".capitalize()
        
        embed = discord.Embed(
            title=f"Queue requested by {str(interaction.user).capitalize()}",
            description=f"Valid Arguments for **mqueue: 'clear' 'shuffle'**",
            color=discord.Color.green()
        )
        embed.add_field(name="Songs in queue", value=len(self.queue))
        embed.add_field(name="Action", value=action)
        embed.add_field(name="Queue", value="\n".join([f"{i+1}. **{song[1]}**" for i, song in enumerate(self.queue)]), inline=False)
        embed.set_footer(text=f"Requested by {interaction.user}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        debug(f"{interaction.user} performed {action} on the queue", function="music.MusicPlayer.mqueue")          
        
        return True
    
