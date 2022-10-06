import typing

import discord
from discord import app_commands
from discord.ext import commands
from discord import Interaction
from discord.utils import get
from discord.app_commands import AppCommandError
import diagnostics as diagnostics
import configuration as configuration


# verify user command
class AdminCommands(commands.Cog):
    # ----- __init__ function runs on reload ----- #
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        bot.tree.on_error = self.on_app_command_error
        self.error_log_channel = self.bot.get_channel(configuration.ChannelObjects.discord_timing_channel_id)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @app_commands.checks.has_any_role('Owner', 'Admin')
    @app_commands.command(name="verify", description="verify user into server")
    async def verify_user_command(self, interaction: discord.Interaction, discord_user: typing.Optional[discord.Member] = None, mc_username: typing.Optional[str] = None) -> None:
        if not discord_user and not mc_username:
            await interaction.response.send_message('Please specify a discord or MC username or both', ephemeral=True)

        elif mc_username is None:
            # only verify Discord member
            member_role = get(interaction.guild.roles, id=543039798668034048)
            if member_role in discord_user.roles:
                await interaction.response.send_message(f'{discord_user.mention} is already verified!', ephemeral=True)
            else:
                await interaction.response.send_message(f'Verifying {discord_user.mention} on Discord...', ephemeral=True)
                await discord_user.add_roles(member_role)
        elif discord_user is None:
            # only verify MC username
            await interaction.response.send_message(f'Verifying {mc_username} on the MC server...', ephemeral=True)
        else:
            # verify both discord and MC accounts and link them together!
            await interaction.response.send_message(f'Verifying {discord_user.mention} on Discord and {mc_username} on MC', ephemeral=True)

    # error handler
    async def on_app_command_error(self, interaction: Interaction, error: AppCommandError):
        embed = diagnostics.log_error('severe', 'command', 'Command failed to run', str(error), 'admin_commands.py')
        await self.error_log_channel.send(embed=embed)
        await interaction.response.send_message(f'Oops the command failed!', ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AdminCommands(bot))

