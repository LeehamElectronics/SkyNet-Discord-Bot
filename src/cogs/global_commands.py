import discord
from discord import app_commands
from discord.ext import commands
from discord import Interaction
from discord.app_commands import AppCommandError

from mcstatus import JavaServer

import diagnostics as diagnostics
import configuration as configuration


class GlobalCommands(commands.Cog):
    # ----- __init__ function runs on reload ----- #
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        bot.tree.on_error = self.on_app_command_error
        self.error_log_channel = self.bot.get_channel(configuration.ChannelObjects.discord_timing_channel_id)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @app_commands.checks.has_any_role('Member', 'Admin')
    @app_commands.command(name="online", description="See MC Server status")
    async def online_command(self, interaction: discord.Interaction, server: str) -> None:
        if not server:
            pass
        else:
            if server == 'minecraft':
                server = JavaServer.lookup("192.168.99.49:28871")
                status = server.status()
                await interaction.response.send_message('SkynetMC has {0} players and replied in {1} ms'.format(status.players.online, status.latency), ephemeral=False)

    @online_command.autocomplete('server')
    async def reload_cogs_autocomplete(self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        servers = ['minecraft', 'discord', 'other']
        return [
            app_commands.Choice(name=server, value=server)
            for server in servers if current.lower() in server.lower()
        ]

    # error handler
    async def on_app_command_error(self, interaction: Interaction, error: AppCommandError):
        embed = diagnostics.log_error('severe', 'command', 'Command failed to run', str(error), 'global_commands.py')
        await self.error_log_channel.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GlobalCommands(bot))

