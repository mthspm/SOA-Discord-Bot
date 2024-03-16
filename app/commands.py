import discord
from discord import app_commands
from settings import *
from game import GameSettings
from utils import debug, flagger

class Essentials:
    """ Package that handle some basics commands.

    Methods: 
                >>> help(interaction) -> None : Display a help message with a list of commands.
                >>> cfg(interaction, game: str) -> None : Display the best perfomance settings for a game.
                >>> edit(interaction, game: str, setting: str, value: str) -> None : Edit the best perfomance settings for a game.
                >>> clear(interaction, quantity: int) -> None : Clears a number of messages in the current channel.
                >>> invite(interaction) -> None : Create a invite to the server.
    """
    
    def __init__(self):
        pass

    async def help(self, interaction):
        """Displays a help message with a list of commands."""

        embed = discord.Embed(
            title=f"Help Menu - {TITLE} {VERSION}",
            description=HELP_MESSAGE,
            color=discord.Color.green()
        )
        embed.set_footer(text=f"{TITLE} | {VERSION} | {AUTHOR}")
        embed.set_thumbnail(url=HELP_IMAGE)
        debug(f"Help requested to {interaction.user}", function="client.help", type="CMD")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    @app_commands.describe(game="See the best settings for this game")
    async def cfg(self, interaction, game: str):
        """Display the best perfomance settings for a game."""

        gameset = GameSettings(game)
        if gameset.support:
            description = ""
            for setting, value in gameset.settings.items():
                if isinstance(value, dict):
                    description += f"\n{setting.upper()} CONFIG:\n"
                    for subsetting, subvalue in value.items():
                        description += f"{subsetting}: {subvalue}\n"
                elif setting != "image":
                    description += f"{setting}: {value}\n"

            embed = discord.Embed(
                title=f"{game.upper()} Cfg - {TITLE} {VERSION}",
                description=description,
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Requested by {interaction.user}")
            embed.set_thumbnail(url=gameset.image)
            debug(f"Game settings for {game} requested to {interaction.user}", function="client.config", type="CMD")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            debug(f"Game help settings for {game} requested to {interaction.user}", function="client.config", type="CMD")
            await interaction.response.send_message(CONFIG_HELP, ephemeral=True)

    @app_commands.describe(game="Target game to edit the config", setting="The setting you want to change", value="The value you want to set")
    async def edit(self, interaction, game: str, setting: str, value: str):
        """Edit the best perfomance settings for a game."""

        flag = flagger(interaction.user.roles, UNHOLY_ONES_ID, PRESIDENT_ID, VICE_PRESIDENT_ID, MANOFMAYHEM_ID, DEV_ID)
        if not flag:
            debug(f"{interaction.user} tried to change {setting} to {value} on {game} FAILED", function="client.edit", type="CMD")
            await interaction.response.send_message(ACCESS_DENIED, ephemeral=True)
            return
        
        gameset = GameSettings(game)

        callback = gameset.update_settings(setting, value, interaction.user)

        if callback:
            debug(f"{interaction.user} changed {setting} to {value} on {game} OK", function="client.edit", type="CMD")
            await interaction.response.send_message(f"Changed {setting} to {value} on {game}", ephemeral=True)
        else:
            debug(f"{interaction.user} tried to change {setting} to {value} on {game} FAILED", function="client.edit", type="CMD")
            await interaction.response.send_message(f"Failed to change {setting} to {value} on {game}{EDIT_HELP}", ephemeral=True)

    @app_commands.describe(quantity="The number of messages to clear")
    async def clear(self, interaction, quantity: int):
        """Clears a number of messages in the current channel."""
        if not flagger(interaction.user.roles, PRESIDENT_ID, MANOFMAYHEM_ID, VICE_PRESIDENT_ID, ADM_TIBIANTIS):
            return await interaction.response.send_message(ACCESS_DENIED, ephemeral=True)

        channel = interaction.channel
        msgs = []
        quantity_MAX = 200
        if quantity <= quantity_MAX:
            async for message in channel.history(limit=quantity):
                msgs.append(message)
        else:
            debug(f"{interaction.user} tryed and failed to clear {quantity} messages", function="client.clear", type="CMD")
            return await interaction.response.send_message(f"Failed to clear {quantity} messages, max is {quantity_MAX}", ephemeral=True)

        debug(f"{interaction.user} is about to clear {quantity} messages", function="client.clear", type="CMD")
        try:
            await interaction.response.send_message(f"Cleaning {quantity} messages", ephemeral=True)
            await channel.delete_messages(msgs)
            debug(f"{interaction.user} cleared {quantity} messages", function="client.clear", type="CMD")
        except:
            debug(f"{interaction.user} failed to clear {quantity} messages", function="client.clear", type="CMD")
        finally:
            return
        
    async def invite(self, interaction):
        """Create a invite to the server."""
        invite = await interaction.channel.create_invite(max_age=3000)
        debug(f"{interaction.user} requested invite", function="client.invite", type="CMD")
        await interaction.response.send_message(INVITE_TO_SERVER.format(invite.url), ephemeral=True)
        