import json, functools, uuid, requests, os, logging, matplotlib.pyplot as plt
import discord
from datetime import datetime
from dotenv import load_dotenv
from colorama import Fore, Style
from urllib.parse import urlparse
from pathlib import Path
from typing import Union

logging.basicConfig(filename=f"{Path(__file__).parent}/logs/{datetime.now().strftime('%Y-%m-%d')}.log", level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def time_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def debug(message, type="INFO", function=None):
    """Print a debug message
    
    Args:
        message (str): message to be printed
        type (str, optional): type of the message. Defaults to "INFO".
        function (str, optional): function where the message was printed. Defaults to None.
    
    Returns:
        None
    """
    logging.info(f"{function} {message}")
    print(f"[{time_now()}]{Fore.LIGHTBLUE_EX} {type}{Style.RESET_ALL}{Fore.MAGENTA} {function}{Style.RESET_ALL} {message}")

def ddbug(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        debug(f"executed with params {args} {kwargs}", function=func.__name__, type="INFO")
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            debug(f"failed with error {e}", function=func.__name__, type="ERROR")
            return False
        finally:
            if result:
                debug(f"returned {result}", function=func.__name__, type="INFO")
            else:
                debug(f"-> {result}", function=func.__name__, type="ALERT")
    return wrapper

def flagger(roles, *args):
    """Check if user has the specified roles
    
    Args:
        roles (list): list of ojebct roles of the user
        *args (list): roles_ids to be checked
        
    Returns:
        (bool): True if the user has the role, False if not
    """
    if not args:
        return False
    for role in roles:
        if role.id in args:
            return True
    return False

def load_json(path):
    """Load a json file
    
    Args:
        path (str): path to the json file
        
    Returns:
        (dict): json file
    """
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        debug(f"failed with error {e}", function="load_json", type="ERROR")
        return False
    
def save_json(path, data):
    """Save a json file
    
    Args:
        path (str): path to the json file
        data (dict): data to be saved
    
    Returns:
        None
    """
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def url_checker(url):
    """Check if the url is a valid youtube url
    
    Args:
        url (str): url to be checked
        
    Returns:
        (bool): True if the url is valid, False if not
    """
    try:
        result = urlparse(url)
        return all([result.scheme in ["http", "https"], "youtube.com" in result.netloc, "watch" in result.path])
    except ValueError:
        return False
    
def random_hash_gen():
    """Generate a random hash
    
    Returns:
        (str): random hash
    """
    return str(uuid.uuid4()).replace("-", "")[:10]

def filter_str(string):
    patern = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]
    for char in patern:
        string = string.replace(char, "")
    return string

async def del_file(path):
    if os.path.exists(path):
        os.remove(path)
        debug(f"deleted {path}", function="del_file", type="INFO")
        return True
    else:
        debug(f"file {path} not found", function="del_file", type="ALERT")
        return False
    
def new_exist(path, data):
    """Check if a json file exists and create one if not with the specified data passed as argument"""
    if not os.path.exists(path):
        save_json(path, data)
        debug(f"created {path}", function="new_exist", type="INFO")
        return False
    else:
        return True

async def AutoClearBOTMSG(channel, bot):
    async for message in channel.history(limit=100):
        if message.author == bot:
            try:
                await message.delete()
            except discord.Forbidden:
                # You don't have permission to delete the message
                debug(f"Permission denied to delete message: {message.content}")
            except discord.NotFound:
                # Message was already deleted or doesn't exist
                debug(f"Message not found: {message.content}")
            except discord.HTTPException as e:
                # Some other error occurred
                debug(f"Failed to delete message: {message.content}. Error: {e}")

async def get_member(user: discord.User, guild: Union[discord.Guild, list[discord.Guild]]) -> Union[discord.Member, discord.User]:
    if isinstance(guild, list):
        for g in guild:
            member = g.get_member(user.id)
            if member:
                return member
    else:
        member = guild.get_member(user.id)
        if member:
            return member
    return user

class ImageManager:
    """Class to upload images to imgur"""
    def __init__(self):
        load_dotenv()
        self.__setup()

    def __setup(self):
        self.api = {"Authorization": f"Client-ID {os.getenv('II')}"}
        debug("ImageManager Loaded", function="ImageManager.__setup", type="INFO")

    async def upload(self, path):
        """Upload a image to imgur
        
        Args:
            path (str): path to the image
            
        Returns:
            (str): url to the image
        """
        try:
            with open(path, "rb") as f:
                r = requests.post("https://api.imgur.com/3/image", headers=self.api, data={"image": f.read()})
                return r.json()["data"]["link"]
        except Exception as e:
            debug(f"failed with error {e}", function="ImageUploader.upload", type="ERROR")
            return False
        
    async def plot(self, klines, title, x, y, path):
        """Generate a plot and upload it to imgur

        Args:
            kline (list): list of klines
            title (str): title of the plot
            x (str): title of the x axis
            y (str): title of the y axis
            path (str): path where the image is going to be saved

        Returns:
            (str): url to the image
        """
        closes = [float(entry[4]) for entry in klines]
        plt.plot(closes)
        plt.title(title)
        plt.xlabel(x)
        plt.ylabel(y)
        plt.savefig(path)
        plt.close()
        return await self.upload(path)
    