import asyncio
import typing

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
        self.theocratic_channel = self.bot.get_channel(configuration.ChannelObjects.theocratic_channel_id)
        self.tech_channel = self.bot.get_channel(784976527447293962)
        self.amongus_text_channel = self.bot.get_channel(1044114906397544500)
        self.amongus_vc_channel = self.bot.get_channel(1044118756655382600)
        self.jackbox_text_channel = self.bot.get_channel(832516473426935869)
        self.jackbox_vc_channel = self.bot.get_channel(832516334222311435)
        self.movienight_text_channel = self.bot.get_channel(760027390923243540)
        self.movienight_vc_channel = self.bot.get_channel(760027477334294550)
        self.minigames_text_channel = self.bot.get_channel(760425082404339732)
        self.minigames_vc_channel = self.bot.get_channel(1044120888666238996)

        # self.lounge_category = self.bot.get_channel(543031470927773706)

        # voice channels
        self.lounge_one_vc_channel = self.bot.get_channel(1035470361782919178)
        self.lounge_two_vc_channel = self.bot.get_channel(1035489990899138560)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.command(name="clear", description="clear channel messages")
    async def clear_command(self, interaction: discord.Interaction, messages: int, discord_user: typing.Optional[discord.Member] = None) -> None:
        def is_user(req_user):
            return req_user.author == discord_user
        if not messages:
            if not discord_user:
                await interaction.response.send_message('Clearing 10 messages', ephemeral=True)
                await interaction.channel.purge(limit=10)
            else:
                await interaction.response.send_message(f'Clearing 10 messages from {discord_user.mention}', ephemeral=True)
                await interaction.channel.purge(limit=10, check=is_user)
        else:
            val = messages
            try:
                val = int(messages)
            except Exception as error:
                await interaction.response.send_message(f"That's not a number...", ephemeral=True)
                return
            if not discord_user:
                await interaction.response.send_message(f'Clearing {messages} messages', ephemeral=True)
                await interaction.channel.purge(limit=messages)
            else:
                await interaction.response.send_message(f'Clearing {messages} messages from {discord_user.mention}',
                                                        ephemeral=True)
                await interaction.channel.purge(limit=messages, check=is_user)

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
    @app_commands.command(name="bubblewrap", description="bubble-wrap a member")
    async def bubblewrap_command(self, interaction: discord.Interaction, member: discord.Member, status: bool) -> None:
        if not member:
            await interaction.response.send_message('What Member?', ephemeral=True)
            return

        owner_role = interaction.guild.get_role(configuration.RoleIDObjects.owner_role_id)
        admin_role = interaction.guild.get_role(configuration.RoleIDObjects.admin_role_id)
        mod_role = interaction.guild.get_role(configuration.RoleIDObjects.mod_role_id)
        bubblewraped_role = interaction.guild.get_role(1034728199994740776)
        lounge_category = discord.utils.get(interaction.guild.categories, id=543031470927773706)

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
            await lounge_category.set_permissions(member, view_channel=False)
            # await self.memes_channel.set_permissions(member, view_channel=False)
            # await self.theocratic_channel.set_permissions(member, view_channel=False)
            # await self.tech_channel.set_permissions(member, view_channel=False)
            # await self.lounge_one_vc_channel.set_permissions(member, view_channel=False)
            # await self.lounge_two_vc_channel.set_permissions(member, view_channel=False)
            embed = discord.Embed(title="User Bubblewraped!",
                                  description="**{0}** was bubblewraped by **{1}**!".format(member, interaction.user,),
                                  color=0xff00f6)
        else:
            # disable bubblewrap
            await member.remove_roles(bubblewraped_role)
            await lounge_category.set_permissions(member, view_channel=True)
            # await self.memes_channel.set_permissions(member, view_channel=True)
            # await self.theocratic_channel.set_permissions(member, view_channel=True)
            # await self.tech_channel.set_permissions(member, view_channel=True)
            # await self.lounge_one_vc_channel.set_permissions(member, view_channel=True)
            # await self.lounge_two_vc_channel.set_permissions(member, view_channel=True)
            embed = discord.Embed(title="User no longer Bubblewraped!",
                                  description="**{0}** had their bubblewrap removed by **{1}**!".format(member, interaction.user, ),
                                  color=0xff00f6)

        await interaction.response.send_message(embed=embed, ephemeral=True)
        await self.mod_log_channel.send(embed=embed)

    # goes through a list of already bubble-wrapped members and updates their permissions
    @app_commands.checks.has_any_role('Owner', 'Admin')
    @app_commands.command(name="re-bubblewrap-all", description="goes through a list of already bubble-wrapped members and updates their permissions")
    async def rebubblewrap_command(self, interaction: discord.Interaction) -> None:

        bubblewraped_role = interaction.guild.get_role(1034728199994740776)
        lounge_category = discord.utils.get(interaction.guild.categories, id=543031470927773706)

        for member in interaction.guild.members:
            if bubblewraped_role in member.roles:
                await lounge_category.set_permissions(member, view_channel=False)
                await member.add_roles(bubblewraped_role)
                embed = discord.Embed(title="User re-bubblewraped!",
                                      description="**{0}** was re-bubblewraped by **{1}**!".format(member, interaction.user, ),
                                      color=0xff00f6)
                await self.mod_log_channel.send(embed=embed)

        await interaction.response.send_message('re-wrapped everyone!', ephemeral=True)

    @mute_command.autocomplete('mute_type')
    async def mute_command_type_autocomplete(self, interaction: discord.Interaction, mute_type: str
                                       ) -> list[app_commands.Choice[str]]:
        mute_types = ['voice', 'chat']
        return [
            app_commands.Choice(name=mute_type, value=mute_type)
            for mute_type in mute_types if mute_type.lower() in mute_type.lower()
        ]

    @app_commands.checks.has_any_role('Owner', 'Admin', 'Event Manager')
    @app_commands.command(name="events", description="start and stop events!")
    async def events_command(self, interaction: discord.Interaction, event: str, status: bool) -> None:
        if not event:
            await interaction.response.send_message('What Event?', ephemeral=True)
            return

        member_role = interaction.guild.get_role(configuration.RoleIDObjects.member_role_id)

        if event == 'amongus':
            await self.amongus_vc_channel.set_permissions(member_role, view_channel=status)
            await self.amongus_text_channel.set_permissions(member_role, view_channel=status)
        elif event == 'movie':
            await self.movienight_vc_channel.set_permissions(member_role, view_channel=status)
            await self.movienight_text_channel.set_permissions(member_role, view_channel=status)
        elif event == 'jackbox':
            await self.jackbox_vc_channel.set_permissions(member_role, view_channel=status)
            await self.jackbox_text_channel.set_permissions(member_role, view_channel=status)
        elif event == 'minigames-comp':
            await self.minigames_vc_channel.set_permissions(member_role, view_channel=status)
            await self.minigames_text_channel.set_permissions(member_role, view_channel=status)

        embed = discord.Embed(title=f"{event} Event Started!",
                              description="**{0}** event started by **{1}**!".format(event, interaction.user, ),
                              color=0xff00f6)
        await interaction.response.send_message(embed=embed, ephemeral=False)
        await self.mod_log_channel.send(embed=embed)

    @events_command.autocomplete('event')
    async def event_command_type_autocomplete(self, interaction: discord.Interaction, current: str
                                              ) -> list[app_commands.Choice[str]]:
        event_types = ['amongus', 'movie', 'minigames-comp', 'jackbox']
        return [
            app_commands.Choice(name=discord_event, value=discord_event)
            for discord_event in event_types if current.lower() in discord_event.lower()
        ]

    # error handler
    async def on_app_command_error(self, interaction: Interaction, error: AppCommandError):
        embed = diagnostics.log_error('severe', 'command', 'Command failed to run', str(error), str(interaction.user.name), 'manager_commands.py')
        await self.error_log_channel.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ManagerCommands(bot))

