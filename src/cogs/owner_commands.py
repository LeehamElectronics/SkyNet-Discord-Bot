import discord
from discord import app_commands
from discord.ext import commands
from discord import Interaction
from discord.app_commands import AppCommandError
import src.diagnostics as diagnostics
from src.db import configuration

# sync command


class OwnerCommands(commands.Cog):
    # ----- __init__ function runs on reload ----- #
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        bot.tree.on_error = self.on_app_command_error
        self.error_log_channel = self.bot.get_channel(configuration.ChannelObjects.discord_timing_channel_id)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @app_commands.checks.has_any_role('Owner')
    @app_commands.command(name="sync", description="sync elements")
    async def sync_command(self, interaction: discord.Interaction, element: str) -> None:
        if not element:
            await interaction.response.send_message('Sync what?', ephemeral=True)
        else:
            await self.bot.tree.sync(guild=interaction.guild)
            await interaction.response.send_message('Tree has been synced', ephemeral=True)

    @sync_command.autocomplete('element')
    async def sync_elements_autocomplete(self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        elements = ['tree', 'other']
        return [
            app_commands.Choice(name=element, value=element)
            for element in elements if current.lower() in element.lower()
        ]

    # error handler
    async def on_app_command_error(self, interaction: Interaction, error: AppCommandError):
        embed = diagnostics.log_error('severe', 'command', 'Command failed to run', str(error), 'owner_commands.py')
        await self.error_log_channel.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(OwnerCommands(bot))

