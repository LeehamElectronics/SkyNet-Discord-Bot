import asyncio

import discord
from discord import app_commands
from discord.ext import commands
from discord import Interaction
from discord.app_commands import AppCommandError
import diagnostics as diagnostics
import configuration as configuration


# clear and mute command
class ManagerCommands(commands.Cog):
    # ----- __init__ function runs on reload ----- #
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        bot.tree.on_error = self.on_app_command_error
        self.error_log_channel = self.bot.get_channel(configuration.ChannelObjects.discord_timing_channel_id)
        self.mod_log_channel = self.bot.get_channel(configuration.ChannelObjects.mod_log_channel_id)
        self.memes_channel = self.bot.get_channel(configuration.ChannelObjects.memes_channel_id)

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
    async def mute_command(self, interaction: discord.Interaction, member: discord.Member, mute_time: int, mute_type: str) -> None:
        if not member:
            await interaction.response.send_message('What Member?', ephemeral=True)
            return
        if not mute_time:
            await interaction.response.send_message('For how long?', ephemeral=True)
            return

        owner_role = interaction.guild.get_role(configuration.RoleIDObjects.owner_role_id)
        admin_role = interaction.guild.get_role(configuration.RoleIDObjects.admin_role_id)
        mod_role = interaction.guild.get_role(configuration.RoleIDObjects.mod_role_id)
        muted_role = interaction.guild.get_role(configuration.RoleIDObjects.chat_muted_role_id)
        voice_muted_role = interaction.guild.get_role(1034705488467734548)

        # check if member is an mod, admin, or owner
        members_roles = member.roles
        super_roles = [owner_role, admin_role, mod_role]
        for super_role in super_roles:
            if super_role in members_roles:
                # cancel this mute command because the member has super roles
                await interaction.response.send_message('Sorry but this Member can not be muted', ephemeral=True)
                return
        if mute_type == 'voice':
            await member.add_roles(voice_muted_role)
            embed = discord.Embed(title="User Muted!",
                                  description="**{0}** was voice muted by **{1}** for {2} minutes!".format(member,
                                                                                                     interaction.user,
                                                                                                     mute_time),
                                  color=0xff00f6)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await self.mod_log_channel.send(embed=embed)

            await asyncio.sleep(int(mute_time * 60))
            await member.remove_roles(voice_muted_role)
        else:
            await member.add_roles(muted_role)
            embed = discord.Embed(title="User Chat Muted!",
                                  description="**{0}** was chat muted by **{1}** for {2} minutes!".format(member, interaction.user, mute_time),
                                  color=0xff00f6)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await self.mod_log_channel.send(embed=embed)

            await asyncio.sleep(int(mute_time * 60))
            await member.remove_roles(muted_role)

    @mute_command.autocomplete('mute_type')
    async def mute_command_type_autocomplete(self, interaction: discord.Interaction, mute_type: str
                                       ) -> list[app_commands.Choice[str]]:
        mute_types = ['voice', 'chat']
        return [
            app_commands.Choice(name=mute_type, value=mute_type)
            for mute_type in mute_types if mute_type.lower() in mute_type.lower()
        ]

    @app_commands.checks.has_any_role('Owner', 'Admin', 'Moderator')
    @app_commands.command(name="unmute", description="unmute a member")
    async def unmute_command(self, interaction: discord.Interaction, member: discord.Member, mute_type: str) -> None:
        if not member:
            await interaction.response.send_message('What Member?', ephemeral=True)
        else:
            muted_role = interaction.guild.get_role(configuration.RoleIDObjects.chat_muted_role_id)
            voice_muted_role = interaction.guild.get_role(1034705488467734548)
            if mute_type == 'voice':
                await member.remove_roles(voice_muted_role)
            else:
                await member.remove_roles(muted_role)
            embed = discord.Embed(title=f"User no longer {mute_type} Muted!",
                                  description="**{0}** was {1} unmuted by **{2}**!".format(member, mute_type, interaction.user),
                                  color=0xff00f6)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @unmute_command.autocomplete('mute_type')
    async def unmute_command_type_autocomplete(self, interaction: discord.Interaction, mute_type: str
                                       ) -> list[app_commands.Choice[str]]:
        mute_types = ['voice', 'chat']
        return [
            app_commands.Choice(name=mute_type, value=mute_type)
            for mute_type in mute_types if mute_type.lower() in mute_type.lower()
        ]

    @app_commands.checks.has_any_role('Owner', 'Admin', 'Moderator')
    @app_commands.command(name="bubblewrap", description="mute a member")
    async def bubblewrap_command(self, interaction: discord.Interaction, member: discord.Member, status: bool) -> None:
        if not member:
            await interaction.response.send_message('What Member?', ephemeral=True)
            return

        owner_role = interaction.guild.get_role(configuration.RoleIDObjects.owner_role_id)
        admin_role = interaction.guild.get_role(configuration.RoleIDObjects.admin_role_id)
        mod_role = interaction.guild.get_role(configuration.RoleIDObjects.mod_role_id)
        bubblewraped_role = interaction.guild.get_role(1034728199994740776)

        # check if member is an mod, admin, or owner
        members_roles = member.roles
        super_roles = [owner_role, admin_role, mod_role]
        for super_role in super_roles:
            if super_role in members_roles:
                # cancel this mute command because the member has super roles
                await interaction.response.send_message('Sorry but this Member can not be Bubblewraped', ephemeral=True)
                return
        if status:
            # enable bubblewrap
            await member.add_roles(bubblewraped_role)
            await self.memes_channel.set_permissions(member, view_channel=False)
            embed = discord.Embed(title="User Bubblewraped!",
                                  description="**{0}** was bubblewraped by **{1}**!".format(member, interaction.user,),
                                  color=0xff00f6)
        else:
            # disable bubblewrap
            await member.remove_roles(bubblewraped_role)
            await self.memes_channel.set_permissions(member, view_channel=True)
            embed = discord.Embed(title="User no longer Bubblewraped!",
                                  description="**{0}** had their bubblewrap removed by **{1}**!".format(member, interaction.user, ),
                                  color=0xff00f6)

        await interaction.response.send_message(embed=embed, ephemeral=True)
        await self.mod_log_channel.send(embed=embed)

    @mute_command.autocomplete('mute_type')
    async def mute_command_type_autocomplete(self, interaction: discord.Interaction, mute_type: str
                                       ) -> list[app_commands.Choice[str]]:
        mute_types = ['voice', 'chat']
        return [
            app_commands.Choice(name=mute_type, value=mute_type)
            for mute_type in mute_types if mute_type.lower() in mute_type.lower()
        ]

    # error handler
    async def on_app_command_error(self, interaction: Interaction, error: AppCommandError):
        embed = diagnostics.log_error('severe', 'command', 'Command failed to run', str(error), 'manager_commands.py')
        await self.error_log_channel.send(embed=embed)



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ManagerCommands(bot))

