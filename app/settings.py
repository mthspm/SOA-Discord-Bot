#Path: app/settings.py

from datetime import datetime
from pathlib import Path

AUTHOR = "mths"
VERSION = "1.0.3"
TITLE = "Sons of Anarchy"

SOA = 224900203218468864
TIBIANTIS = 1208886343934017547
ADM_TIBIANTIS = 1208918082752483349
MOD_TIBIANTIS = 1209342636595613760
PRESIDENT_ID = 308414272013336583
VICE_PRESIDENT_ID = 527301647819341825
DEV_ID = 1174722748292010096
BALUDO_ID = 985121876089139230
UNHOLY_ONES_ID = 531891206678904832
MANOFMAYHEM_ID = 1105685490088288266

TEAM_CHANNEL = 1208917111020453909
HUNTED_CHANNEL = 1209342359754506311
PATCH_NOTES_CHANNEL = 853493671798505492

INVITE = "https://discord.gg/kJ6vaJ9"
WHOISONLINE = "https://tibiantis.online/?page=whoisonline"
SEARCHCHAR = "https://tibiantis.online/?page=character&name={0}"

ACCESS_DENIED = "Sorry but you dont have the roles to edit this setting."
INVITE_TO_SERVER = "Here is the invite to the server: {0}"

COMMANDS = "/help /play /price /mycripto /cfg"

JOINED_VOICE_CHANNEL = "Joined {0}"
LEFT_VOICE_CHANNEL = "Left {0}"
IN_VOICE_CHANNEL = "I'm already in a voice channel! {0}"
NOT_IN_VOICE_CHANNEL = "You need to be in a voice channel to use this command!"
NOT_IN_YOUR_VOICE_CHANNEL = "I'm not in your voice channel!"
NOT_IN_ANY_VOICE_CHANNEL = "I'm not in any voice channel!"
START_MUSIC = "Started playing {0} requested by {1}"
FINISHED_MUSIC = "Finished playing all the querys! "
ALREADY_PLAYING = "Already playing a song, {0} added to queue!"
QUEUE_FINISHED = "Queue finished!"

PLAYING_SONG = "Playing {0} {1}"
SONG_NOT_FOUND = "Song not found!"
ENTRY_INVALID = "Entry is not a url or songname from youtube!"
SONG_NOT_VALID = "Your song was not validated to be processed!"

AWAIT_TEAM_TASK = "Aguarde a lista de times ser atualizada/enviada!"
AWAIT_HUNTED_TASK = "Aguarde a lista de hunteds ser atualizada/enviada!"
ACTION_TXT = "The action you want to do on mycripto dashboard"
TOKEN_TXT = "The token you want to check the price"
PAIR_TXT = "The pair of the tokem you want to check the price"
BINANCE_PNG = "https://w7.pngwing.com/pngs/792/230/png-transparent-binance-macos-bigsur-icon.png"
NO_PLOT_PNG = "https://upload.wikimedia.org/wikipedia/commons/d/d1/Image_not_available.png"
NO_TOKENS_SAVED = """
You **dont have** any tokens saved!

Try to add your **first token/pair**:
Example: **/mycrpto add btc usdt**

Other commands:
**/mycripto remove token pair**
**/mycripto clear**
"""
EDIT_HELP = """
```
You are typing the name or the setting wrong.
You need to specify the game, the setting and the value you want to set.

Example: /edit cs2 Boots Player Contrast DISABLED
         /edit cs2 jumpthrow bind "space;+jump;-attack"
```
"""
CONFIG_HELP = """
```
Your game is not supported yet. Please contact the developer to add support for your game.
Try using the command like this (upper or lower case doenst matter):
Example:  /config cs2
          /config dota2

Games that are currently supported:
-CS2
-DOTA2
-TARKOV
```
"""

HELP_IMAGE = "https://i.pinimg.com/564x/3c/f9/8e/3cf98ed2c9a777391da19d375603fae9.jpg"
HELP_MESSAGE = """
😎 **GENERAL COMMANDS**:
**/help** - Displays this message
**/join** - Joins the voice channel of the user who sent the interaction
**/leave** - Leaves the voice channel of the user who sent the interaction
**/clear [quantity]** - Clears a number of messages in the current channel
**/invite** - Creates a invite to the server

🎮 **GAMES COMMANDS**:
**/cfg [game]** - Displays the best perfomance settings for a game
**/edit [game]** - Edit the best perfomance settings for a game
**/char [name]** - Displays info about a character from tibia.com

🧙‍♂️ **TIBIANTIS COMMANDS**:
**/check [name]** - Check the makers of the character
**/hunted [action][name][reason]** - Manage the hunted list, actions: **add, remove, online**

📻 **MUSIC COMMANDS**:
**/musicinfo [name]** - Displays info about a song based on spotify data
**/play [url]** - Plays a song from a url 
**/mqueue** - Displays the queue. Possible arguments: **clear** **shuffle**
**/stop** - Stops the queue and leaves the voice channel
**/skip** - Skips the current song
**/pause** - Pauses the music
**/resume** - Resumes the music

🪙 **CRIPTO COMMANDS**:
**/price [token] [pair]** - Check the current prices for a token and the plot graph
**/mycripto** - Display all your saved tokens
**/mycripto [action] [token] [pair]** - Manage your tokens, actions: **add, remove, clear**
"""

TIBIA_PNG = "https://p1.hiclipart.com/preview/30/103/592/tibia-ico-tibia-render-style-png-clipart.jpg"
TIBIA_CHAR_ICON = "https://www.tibiawiki.com.br/images/7/76/Tibia_icon.png"






PN_PATH = Path(__file__).parent / "patchnotes"
PATCH_NOTES_DATA = [
            {
                "name": "Rainbow Six Siege Update Patch",
                "color": 0x000000,
                "path": "/dotesports/rainbow-6",
                "filepath": PN_PATH / "r6.json",
                "node": 2,
                "default": {
                        "author": "dotesports",
                        "date": datetime.now().strftime("%d/%m/%Y")
                    }
            },
            {
                "name": "Apex Legends Update Patch",
                "color": 0x00FFFF,
                "path": "/dotesports/apex-legends",
                "filepath": PN_PATH / "apex.json",
                "node": 2,
                "default": {
                        "author": "dotesports",
                        "date": datetime.now().strftime("%d/%m/%Y")
                    }
            },
            {
                "name": "Fortnite Update Patch",
                "color": 0x0000FF,
                "path": "/dotesports/fortnite",
                "filepath": PN_PATH / "fortnite.json",
                "node": 2,
                "default": {
                        "author": "dotesports",
                        "date": datetime.now().strftime("%d/%m/%Y")
                    }
            },
            {
                "name": "PUBG Update Patch",
                "color": 0xFFA500,
                "path": "/dotesports/pubg",
                "filepath": PN_PATH / "pubg.json",
                "node": 2,
                "default": {
                        "author": "dotesports",
                        "date": datetime.now().strftime("%d/%m/%Y")
                    }
            },
            {
                "name": "Dota 2 Update Patch",
                "color": 0xFF0000,
                "path": "/dotesports/dota-2",
                "filepath": PN_PATH / "dota.json",
                "node": 2,
                "default": {
                        "author": "dotesports",
                        "date": datetime.now().strftime("%d/%m/%Y")
                    }
            },
             {
                 "name": "New World Update Patch",
                 "color": 0x000000,
                 "path": "/newworld/news/updates",
                 "filepath": PN_PATH / "newworld.json",
                 "node": 0,
                 "default": {
                        "author": "Amazon Games",
                        "date": datetime.now().strftime("%d/%m/%Y")
                    }
             },
            {
                "name": "Valorant Updates Patch",
                "color": 0x800080,
                "path": "/valorant/en-us/patch-notes",
                "customUrl": "https://playvalorant.com/en-us",
                "filepath": PN_PATH / "valorant.json",
                "node": 1,
                "mapping": {
                    "url": "url_path"
                },
                "default": {
                    "author": "Riot Games",
                    "date": datetime.now().strftime("%d/%m/%Y")
                }
            },
            {
                "name": "Valorant Reddit Posts",
                "color": 0x800080,
                "path": "/reddit/Valorant",
                "filepath": PN_PATH / "valorantreddit.json",
                "customUrl": "https://www.reddit.com/r/Valorant/",
                "node": 1,
                "mapping": {
                    "description": "flair",
                    "thumbnail": "thumbnail_url",
                    "url": "url_path"
                },
                "default": {
                    "author": "Reddit Post",
                    "date": datetime.now().strftime("%d/%m/%Y")
                }
            },
            {
                "name": "Valorant Competitive News",
                "color": 0x800080,
                "path": "/reddit/ValorantComp",
                "customUrl": "https://www.reddit.com/r/ValorantComp/",
                "filepath": PN_PATH / "valorantcomp.json",
                "node": 1,
                "mapping": {
                    "description": "flair",
                    "thumbnail": "thumbnail_url",
                    "url": "url_path"
                },
                "default": {
                    "author": "Reddit Post",
                    "date": datetime.now().strftime("%d/%m/%Y")
                }
            },
            {
                "name": "TFT Updates Patch",
                "color": 0x800080,
                "path": "/tft/en-us/patch_notes",
                "customUrl": "https://teamfighttactics.leagueoflegends.com/en-us",
                "filepath": PN_PATH / "tft.json",
                "node": 1,
                "mapping": {
                    "url": "url_path",
                },
                "default": {
                    "author": "Riot Games",
                    "date": datetime.now().strftime("%d/%m/%Y")
                }
            },
            {
                "name": "League Of Legends Updates Patch",
                "color": 0x0000FF,
                "path": "/lol/en-us/patch_notes",
                "customUrl": "https://na.leagueoflegends.com",
                "filepath": PN_PATH / "lol.json",
                "node": 1,
                "mapping": {
                    "url": "url_path"
                },
                "default": {
                    "author": "Riot Games",
                    "date": datetime.now().strftime("%d/%m/%Y")
                }
            },
            {
                "name": "Tibia Notice",
                "color": 0xFFA500,
                "path": "https://api.tibiadata.com/v3/news/archive",
                "filepath": PN_PATH / "tibia.json",
                "node": 3,
                "mapping": {
                    "description": "news",
                    "title": "category",
                },
                "default": {
                    "title": "Tibia Notice",
                    "description": "Tibia Description",
                    "author": "Tibia Forum",
                    "date": datetime.now().strftime("%d/%m/%Y"),
                    "thumbnail": "https://3.bp.blogspot.com/-nyus8VfJSfQ/XGxUhS8AiEI/AAAAAAAANmc/Tfj44yln3xMjcjSA2Z4KpaYKNpJSbMBJgCLcBGAs/s1600/hq720.jpg",
                }
                
            }
        ]