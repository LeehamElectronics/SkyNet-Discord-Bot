import discord
from discord import app_commands
from discord.ext import commands
from discord import Interaction
from discord.app_commands import AppCommandError
import diagnostics as diagnostics
import configuration as configuration


class LabCommands(commands.Cog):
    # ----- __init__ function runs on reload ----- #
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        bot.tree.on_error = self.on_app_command_error
        self.error_log_channel = self.bot.get_channel(configuration.ChannelObjects.discord_timing_channel_id)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @app_commands.checks.has_any_role('SkyNet Labs', 'Admin')
    @app_commands.command(name="suggest", description="Make a suggestion")
    async def suggest_command(self, interaction: discord.Interaction, suggestion: str) -> None:
        if not suggestion:
            pass
        else:
            await interaction.response.send_message('suggestion made', ephemeral=True)

    @suggest_command.autocomplete('suggestion')
    async def reload_cogs_autocomplete(self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        cogs = ['minecraft', 'discord', 'other']
        return [
            app_commands.Choice(name=cog, value=cog)
            for cog in cogs if current.lower() in cog.lower()
        ]

    # error handler
    async def on_app_command_error(self, interaction: Interaction, error: AppCommandError):
        embed = diagnostics.log_error('severe', 'command', 'Command failed to run', str(error), 'lab_commands.py')
        await self.error_log_channel.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(LabCommands(bot))

