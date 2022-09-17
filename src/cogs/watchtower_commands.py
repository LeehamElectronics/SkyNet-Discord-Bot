import os
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from discord import Interaction
from discord.utils import get
from discord.app_commands import AppCommandError
import src.diagnostics as diagnostics
from src.db import configuration


class WatchtowerCommands(commands.Cog):
    # ----- __init__ function runs on reload ----- #
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        bot.tree.on_error = self.on_app_command_error
        self.error_log_channel = self.bot.get_channel(configuration.ChannelObjects.discord_timing_channel_id)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @app_commands.checks.has_any_role('Owner', 'Admin', 'Conductor Helper')
    @app_commands.command(name="watchtower", description="Watchtower Commands")
    async def watchtower(self, interaction: discord.Interaction, action: str) -> None:
        if not action:
            await interaction.response.send_message('Please type a command argument', ephemeral=True)
        else:
            if action == 'start':
                await interaction.response.send_message('Starting WT', ephemeral=True)
                category = discord.utils.get(interaction.guild.categories, id=698306289473814550)
                role = interaction.guild.get_role(543039798668034048)
                await category.set_permissions(role, read_messages=True, send_messages=True, connect=True, speak=True, view_channel=True)
            elif action == 'stop':
                await interaction.response.send_message('Stopping WT', ephemeral=True)
                category = discord.utils.get(interaction.guild.categories, id=698306289473814550)
                role = interaction.guild.get_role(543039798668034048)
                await category.set_permissions(role, read_messages=False, send_messages=False, connect=False, speak=False, view_channel=False)

    @watchtower.autocomplete('action')
    async def watchtower_autocomplete(self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        actions = ['start', 'stop']
        return [
            app_commands.Choice(name=action, value=action)
            for action in actions if current.lower() in action.lower()
        ]

    # error handler
    async def on_app_command_error(self, interaction: Interaction, error: AppCommandError):
        embed = diagnostics.log_error('severe', 'command', 'Command failed to run', str(error), 'watchtower_commands.py')
        await self.error_log_channel.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(WatchtowerCommands(bot))

