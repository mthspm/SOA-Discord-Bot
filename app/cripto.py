import asyncio
import os
import json
import inspect
import discord
import enum
from decimal import Decimal
from discord import app_commands
from binance.client import Client
from dotenv import load_dotenv
from settings import *
from pathlib import Path
from utils import debug, flagger, ddbug, random_hash_gen, ImageManager, time_now


class CriptoCurrency:
    def __init__(self, client) -> None:
        """
        Initializes the CriptoCurrency class.

        Args:
            client (object): The Discord client object.
        """
        self.client = client
        self.imgmng = ImageManager()
        load_dotenv()
        self.plotpath_target = Path(__file__).parent / "plots"
        self.path = Path(__file__).parent / "users" / "tokens.json"
        self.__setup()

    def __connect(self):
        """
        Connects to the Binance API using the provided API key and secret.
        """
        try:
            self.api = Client(os.getenv("BK"), os.getenv("BS"))
            debug("Binance Connected", function="cripto.__connect", type="INFO")
        except Exception as e:
            debug("Can't connect to Binance API", function="cripto.__conect", type="ERROR")

    def __load_users(self):
        """
        Loads the user data from the tokens.json file.
        """
        try:
            with open(self.path, "r") as file:
                self.users = json.load(file)
            debug("Loaded users cripto data", function="cripto.__load_users", type="INFO")
        except Exception as e:
            debug(f"Failed to load users cripto data {e}", function="cripto.__load_users", type="ERROR")

    def __save_users(self):
        """
        Saves the user data to the tokens.json file.
        """
        try:
            with open(self.path, "w") as file:
                json.dump(self.users, file, indent=4, sort_keys=True)
            debug("Saved users", function="cripto.__save_users", type="INFO")
        except Exception as e:
            debug(f"Failed to save users {e}", function="cripto.__save_users", type="ERROR")

    def __setup(self):
        """
        Sets up the CriptoCurrency class by connecting to Binance and loading user data.
        """
        self.__connect()
        self.__load_users()

    def get_user_data(self, user):
        """
        Retrieves the data for a specific user.

        Args:
            user (object): The Discord user object.

        Returns:
            dict or bool: The user data if found, False otherwise.
        """
        name = user.name
        if name in self.users:
            return self.users[name]
        else:
            return False
        
    def create_user(self, user):
        """
        Creates a new user entry in the user data.

        Args:
            user (object): The Discord user object.

        Returns:
            bool: True if the user was created successfully, False otherwise.
        """
        name = user.name
        if name not in self.users:
            self.users[name] = {
                "date" : time_now(),
                "id" : user.id,
                "tokens" : []
            }
            self.__save_users()
            return True
        else:
            return False
    
    def remove_user(self, user):
        """
        Removes a user entry from the user data.

        Args:
            user (object): The Discord user object.

        Returns:
            bool: True if the user was removed successfully, False otherwise.
        """
        name = user.name
        if name in self.users:
            del self.users[name]
            self.__save_users()
            return True
        else:
            return False

    def clear_tokens(self, user):
        """
        Clears the tokens for a specific user.

        Args:
            user (object): The Discord user object.

        Returns:
            bool: True if the tokens were cleared successfully, False otherwise.
        """
        name = user.name
        if name in self.users:
            self.users[name]["tokens"] = []
            self.users[name]["date"] = time_now()
            self.__save_users()
            return True
        else:
            return False
        
    def add_token(self, user, token, pair):
        """
        Adds a token to the user's token list.

        Args:
            user (object): The Discord user object.
            token (str): The token symbol.
            pair (str): The pair symbol.

        Returns:
            bool: True if the token was added successfully, False otherwise.
        """
        request = self.get_tkpair(token, pair)
        if not request:
            return False
        name = user.name
        
        if name in self.users:
            for tk in self.users[name]["tokens"]:
                if tk["token"] == token and tk["pair"] == pair:
                    return False
                
            self.users[name]["tokens"].append({
                "token" : token,
                "pair" : pair,
                "price" : str(request['price'])
            })
            self.users[name]["date"] = time_now()
            self.__save_users()
            return True
        else:
            return False
        
    def remove_token(self, user, token, pair):
        """
        Removes a token from the user's token list.

        Args:
            user (object): The Discord user object.
            token (str): The token symbol.
            pair (str): The pair symbol.

        Returns:
            bool: True if the token was removed successfully, False otherwise.
        """
        name = user.name
        if name in self.users:
            for tk in self.users[name]["tokens"]:
                if tk["token"] == token and tk["pair"] == pair:
                    self.users[name]["tokens"].remove(tk)
                    self.users[name]["date"] = time_now()
                    self.__save_users()
                    return True
            return False
        else:
            return False
        
    def update_prices(self, user):
        """
        Updates the prices of the tokens in the user's token list.

        Args:
            user (object): The Discord user object.

        Returns:
            bool: True if the prices were updated successfully, False otherwise.
        """
        name = user.name
        if name in self.users:
            if not self.users[name]["tokens"]:
                return False
            for tk in self.users[name]["tokens"]:
                request = self.get_tkpair(tk["token"], tk["pair"])
                if request:
                    tk["price"] = request['price']
            self.__save_users()
            return True
        else:
            return False

    def get_tkpair(self, token, pair="USDT"):
        """
        Retrieves the ticker information for a specific token pair.

        Args:
            token (str): The token symbol.
            pair (str): The pair symbol.

        Returns:
            dict or bool: The ticker information if found, False otherwise.
        """
        token = token.upper()
        pair = pair.upper()
        symbol = f"{token}{pair}"
        
        try:
            info = self.api.get_symbol_ticker(symbol=symbol) #[symbol], [price]
            ticker = self.api.get_ticker(symbol=symbol)
        except Exception as e:
            debug(f"Failed to get {token}{pair} {e}", function="cripto.get_tkpair", type="ERROR")
            return False
        info.update(ticker)

        important_keys = ["price", "priceChange", "lastPrice",
                          "weightedAvgPrice", "openPrice", "prevClosePrice",
                          "highPrice", "lowPrice", "volume"]
        
        for key in important_keys:
            info[key] = Decimal(info[key])

            if info[key] > 1:
                info[key] = info[key].quantize(Decimal("0.00"))
            else:
                info[key] = info[key].quantize(Decimal("0.0000001"))
            
            
        
        debug(f"Got {token}{pair}", function="cripto.get_tkpair", type="INFO")
        return info
    
    def get_all_tkpair(self, token, is_pair=False):
        """
        Retrieves the ticker information for all token pairs containing a specific token.

        Args:
            token (str): The token symbol.
            is_pair (bool, optional): Whether to search for pairs starting or ending with the token symbol. Defaults to False.

        Returns:
            dict: A dictionary of token pairs and their prices.
        """
        data = {}
        token = token.upper()
        call = self.api.get_all_tickers()

        prefix_condition = lambda pair: pair['symbol'].startswith(token)
        suffix_condition = lambda pair: pair['symbol'].endswith(token)

        condition = suffix_condition if is_pair else prefix_condition

        for pair in filter(condition, call):
            data[pair['symbol']] = pair['price']

        return data
    
    @app_commands.describe(token=TOKEN_TXT, pair=PAIR_TXT)
    async def price(self, interaction: discord.Interaction, token: str, pair: str="USDT"):
        """
        Checks the current prices for a token.

        Args:
            interaction (object): The Discord interaction object.
            token (str): The token symbol.
            pair (str, optional): The pair symbol. Defaults to "USDT".
            
        Returns:
            bool: True if the token was removed successfully, False otherwise.
        """
        token = token.upper()
        pair = pair.upper()
        symbol = f"{token}{pair}"
        user = interaction.user
        debug(f"{user} requested price for {symbol}", function="cripto.price", type="CMD")
        
        info = self.get_tkpair(token, pair)

        if not info:
            await interaction.response.send_message("Token not found!", ephemeral=True)
            return False
        
        await interaction.response.send_message(f"Getting price to {symbol}", ephemeral=True)
        
        interval = Client.KLINE_INTERVAL_1DAY
        #get klines from 1 year from now
        klines = self.api.get_historical_klines(symbol, interval=interval)
        path = self.plotpath_target / f"{symbol}_{random_hash_gen()}.png"

        plot_url = await self.imgmng.plot(klines=klines,
                                    title=(f"{token}-{pair} Price History"),
                                    x="Period (Days)",
                                    y=f"Price ({pair})",
                                    path=path)
        os.remove(path)
        
        embed = discord.Embed(
            title=f"{token}-{pair} Market Value Now",
            description=f"The current data is provided by Binance API.",
            color=discord.Color.green()
        )
        
        embed.set_thumbnail(url=BINANCE_PNG)
        embed.set_image(url=plot_url)
        embed.set_footer(text=f"Requested by {user} | Command: /price {token} {pair}")
        embed.add_field(name="🕒Time", value=time_now(), inline=False)
        embed.add_field(name="💸Price", value=f"**{info['price']} {pair}**", inline=False)
        embed.add_field(name="🔄Price Change", value=info['priceChange'], inline=True)
        embed.add_field(name="📈Price Change%", value=f"{info['priceChangePercent']}%", inline=True)
        embed.add_field(name="📰Last Price", value=info['lastPrice'], inline=True)
        embed.add_field(name="⚖️Average", value=info['weightedAvgPrice'], inline=True)
        embed.add_field(name="🔓Open", value=info['openPrice'], inline=True)
        embed.add_field(name="🔒Close", value=info['prevClosePrice'], inline=True)
        embed.add_field(name="🔼High", value=info['highPrice'], inline=True)
        embed.add_field(name="🔽Low", value=info['lowPrice'], inline=True)
        embed.add_field(name="📊Volume", value=info['volume'], inline=True)
        await interaction.edit_original_response(embed=embed)
        debug(f"Sent {token}-{pair} price to {user}", function="cripto.price", type="CMD")
        return True

    @app_commands.describe(action=ACTION_TXT, token=TOKEN_TXT, pair=PAIR_TXT)
    async def mycripto(self, interaction, action: str="", token: str="", pair: str=""):
        """Menu to manage your saved cripto tokens."""
        user = self.get_user_data(interaction.user)
        if not user:
            self.create_user(interaction.user)
            user = self.get_user_data(interaction.user)
            debug(f"Created new user {interaction.user}", function="cripto.mycripto", type="INFO")

        actions = {"add" : self.add_token,
                   "remove" : self.remove_token,
                   "clear" : self.clear_tokens}
        
        #check if the action is valid
        if action in actions:
            #check if the action needs arguments
            signature = inspect.signature(actions[action])
            if len(signature.parameters) > 2:
                response = actions[action](interaction.user, token, pair)
            else:
                response = actions[action](interaction.user)
            
            if response:
                response = f"**{action.upper()}ED** with **success!**"
                debug(f"{interaction.user} {action}ed {token}{pair}", function="cripto.mycripto", type="CMD")
            else:
                response = f"**FAILED** to **{action}!**"
                debug(f"{interaction.user} failed to {action} {token}{pair}", function="cripto.mycripto", type="CMD")

        elif not action:
            debug(f"{interaction.user} requested mycripto menu", function="cripto.mycripto", type="CMD")
            pass
        else:
            await interaction.response.send_message("Invalid action!", ephemeral=True)
            debug(f"{interaction.user} tried to {action} {token}{pair}", function="cripto.mycripto", type="CMD")
            return

        embed = discord.Embed(
            title=f"{interaction.user.name.upper()} Cripto Tokens Menu",
            description=f"Last edition {user['date']}",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=interaction.user.display_avatar)
        embed.set_footer(text=f"{TITLE} {VERSION} | {interaction.user}")
        embed.add_field(name="Tokens", value=f"**{len(user['tokens'])}**", inline=True)
        embed.add_field(name="Action", value=f"**{action.upper()}**", inline=True)
        embed.add_field(name="Arguments", value=f"**{token.upper()}/{pair.upper()}**", inline=True)
        #list of tokens/pair/price
        if action in actions:
            embed.add_field(name="Response", value=response, inline=False)
        if user["tokens"]:
            for tk in user["tokens"]:
                embed.add_field(name=f"{tk['token'].upper()}-{tk['pair'].upper()}", value=f"{tk['price']}", inline=True)
        else:
            embed.add_field(name="Help", value=NO_TOKENS_SAVED, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


#debug
if __name__ == "__main__":
    cripto = CriptoCurrency("client")