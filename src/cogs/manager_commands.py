import discord
from discord import app_commands
from discord.ext import commands
from discord import Interaction
from discord.app_commands import AppCommandError
import src.diagnostics as diagnostics
import src.configuration as configuration


# clear and mute command
class ManagerCommands(commands.Cog):
    # ----- __init__ function runs on reload ----- #
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        bot.tree.on_error = self.on_app_command_error
        self.error_log_channel = self.bot.get_channel(configuration.ChannelObjects.discord_timing_channel_id)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.command(name="clear", description="clear channel messages")
    async def clear_command(self, interaction: discord.Interaction, messages: int) -> None:
        if not messages:
            await interaction.response.send_message('Clearing 10 messages', ephemeral=True)
            await interaction.channel.purge(limit=10)
        else:
            val = messages
            try:
                val = int(messages)
            except Exception as error:
                await interaction.response.send_message(f"That's not a number...", ephemeral=True)
                return
            await interaction.response.send_message(f'Clearing {messages} messages', ephemeral=True)
            await interaction.channel.purge(limit=messages)

    @app_commands.checks.has_any_role('Owner', 'Admin', 'Moderator')
    @app_commands.command(name="mute", description="mute a member")
    async def mute_command(self, interaction: discord.Interaction, member: discord.Member) -> None:
        if not member:
            await interaction.response.send_message('What Member?', ephemeral=True)
            return

        owner_role = interaction.guild.get_role(configuration.RoleIDObjects.owner_role_id)
        admin_role = interaction.guild.get_role(configuration.RoleIDObjects.admin_role_id)
        mod_role = interaction.guild.get_role(configuration.RoleIDObjects.mod_role_id)
        muted_role = interaction.guild.get_role(configuration.RoleIDObjects.chat_muted_role_id)

        # check if member is an mod, admin, or owner
        members_roles = member.roles
        super_roles = [owner_role, admin_role, mod_role, muted_role]
        for super_role in super_roles:
            if super_role in members_roles:
                # cancel this mute command because the member has super roles
                await interaction.response.send_message('Sorry but this Member can not be muted', ephemeral=True)
                return

        await member.add_roles(muted_role)
        embed = discord.Embed(title="User Muted!",
                              description="**{0}** was muted by **{1}**!".format(member, interaction.user),
                              color=0xff00f6)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.checks.has_any_role('Owner', 'Admin', 'Moderator')
    @app_commands.command(name="unmute", description="unmute a member")
    async def unmute_command(self, interaction: discord.Interaction, member: discord.Member) -> None:
        if not member:
            await interaction.response.send_message('What Member?', ephemeral=True)
        else:
            muted_role = interaction.guild.get_role(configuration.RoleIDObjects.chat_muted_role_id)
            await member.remove_roles(muted_role)
            embed = discord.Embed(title="User no longer Muted!",
                                  description="**{0}** was unmuted by **{1}**!".format(member, interaction.user),
                                  color=0xff00f6)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    # error handler
    async def on_app_command_error(self, interaction: Interaction, error: AppCommandError):
        embed = diagnostics.log_error('severe', 'command', 'Command failed to run', str(error), 'manager_commands.py')
        await self.error_log_channel.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ManagerCommands(bot))

