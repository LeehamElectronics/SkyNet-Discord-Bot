import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_permission
from discord_slash.model import SlashCommandPermissionType

# RSS Feeds and Web interacting #
import feedparser  # for RSS Feeds!
import urllib.request  # For getting web data from JW.org and WOL
from bs4 import BeautifulSoup  # For ciphering HTML data
import urllib.request, io

from mathmatical_functions import generate_leader_board
from mathmatical_functions import find_members_rank
from main import share_users_dict_of_dict_elsewhere
from load_configs import share_global_config_dict_elsewhere
from discord_embed_generators import generate_help_menu


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = share_global_config_dict_elsewhere()

    @commands.Cog.listener()
    async def on_ready(self):
        print('🟢 Slash Commands Cog Ready')
        self.config = share_global_config_dict_elsewhere()  # Is this needed since it's already in __init__ ? must test.

    @cog_ext.cog_slash(name="stat",
                       description="View your personal stats on Discord!",
                       permissions={
                           406262663283343371: [
                               create_permission(
                                   share_global_config_dict_elsewhere()['discord_role_ids']['general_roles']['admin'],
                                   SlashCommandPermissionType.ROLE, True),  # Admin Role
                               create_permission(
                                   share_global_config_dict_elsewhere()['discord_role_ids']['general_roles']['member'],
                                   SlashCommandPermissionType.ROLE, True)  # Member role
                               # of denying a user with a role
                           ]
                       })
    async def _stat(self, ctx: SlashContext):
        embed = discord.Embed(title="Stats Embed")
        await ctx.send(content="Your Stats are!", embeds=[embed])

    @cog_ext.cog_slash(name="leaderboard",
                       description="Display the Discord Leaderboard",
                       permissions={
                           406262663283343371: [
                               create_permission(
                                   share_global_config_dict_elsewhere()['discord_role_ids']['general_roles']['admin'],
                                   SlashCommandPermissionType.ROLE, True),  # Admin Role
                               create_permission(
                                   share_global_config_dict_elsewhere()['discord_role_ids']['general_roles']['member'],
                                   SlashCommandPermissionType.ROLE, True)  # Member role
                               # of denying a user with a role
                           ]
                       })
    async def _leaderboard(self, ctx: SlashContext):
        users_dict_of_dict = share_users_dict_of_dict_elsewhere()  # This fetches the user db dict from memory in main
        message_to_send = generate_leader_board(users_dict_of_dict)
        await ctx.channel.send(message_to_send)

    @cog_ext.cog_slash(name="help",
                       description="A general Help menu",
                       permissions={
                           406262663283343371: [
                               create_permission(
                                   share_global_config_dict_elsewhere()['discord_role_ids']['general_roles']['admin'],
                                   SlashCommandPermissionType.ROLE, True),  # Admin Role
                               create_permission(
                                   share_global_config_dict_elsewhere()['discord_role_ids']['general_roles']['member'],
                                   SlashCommandPermissionType.ROLE, True)  # Member role
                               # of denying a user with a role
                           ]
                       })
    async def _help(self, ctx: SlashContext):
        embed = generate_help_menu()
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="rank",
                       description="View your personal # Rank on Discord!",
                       permissions={
                           406262663283343371: [
                               create_permission(
                                   share_global_config_dict_elsewhere()['discord_role_ids']['general_roles']['admin'],
                                   SlashCommandPermissionType.ROLE, True),  # Admin Role
                               create_permission(
                                   share_global_config_dict_elsewhere()['discord_role_ids']['general_roles']['member'],
                                   SlashCommandPermissionType.ROLE, True)  # Member role
                               # of denying a user with a role
                           ]
                       })
    async def _rank(self, ctx: SlashContext):
        users_dict_of_dict = share_users_dict_of_dict_elsewhere()  # This fetches the user db dict from memory in main
        user_rank = find_members_rank(ctx.message.author.id, users_dict_of_dict)
        print("#" + str(user_rank))
        await ctx.message.channel.send(f"{ctx.message.author.mention} You are rank #" + str(user_rank))

    @cog_ext.cog_slash(name="daily text",
                       description="View today's daily text!",
                       permissions={
                           406262663283343371: [
                               create_permission(
                                   share_global_config_dict_elsewhere()['discord_role_ids']['general_roles']['admin'],
                                   SlashCommandPermissionType.ROLE, True),  # Admin Role
                               create_permission(
                                   share_global_config_dict_elsewhere()['discord_role_ids']['general_roles']['member'],
                                   SlashCommandPermissionType.ROLE, True)  # Member role
                               # of denying a user with a role
                           ]
                       })
    async def _daily_text(self, ctx: SlashContext):
        print("Obtaining Daily Text from WOL")
        embed = discord.Embed(title="Daily Text")
        await ctx.send(content="to be finished!", embeds=[embed])
        daily_text_scripture = urllib.request.urlopen('https://wol.jw.org/en/wol/h/r1/lp-e')
        content = daily_text_scripture.read()
        html_content = BeautifulSoup(content, 'html.parser')
        paragraphs = html_content.prettify()
        # paragraphs = html_content.find_all('p')
        # print(str(type(paragraphs)))
        print(str(paragraphs))

    ####################################################
    #                                                  #
    #               Administration Commands            #
    #                                                  #
    ####################################################
    # Keep in mind that most of the admin and mod commands will be kept in normal_commands.py because I want to keep
    # the slash commands clean since everyone can see them, members included.
    @cog_ext.cog_slash(name="mute",
                       description="Mute a Member with this command /mute @leeham.",
                       permissions={
                           406262663283343371: [
                               create_permission(share_global_config_dict_elsewhere()['discord_role_ids']['general_roles']['admin'], SlashCommandPermissionType.ROLE, True),  # Admin Role
                               create_permission(share_global_config_dict_elsewhere()['discord_role_ids']['general_roles']['member'], SlashCommandPermissionType.ROLE, False)  # Member role
                               # of denying a user with a role
                           ]
                       })
    async def mute(self, ctx: SlashContext):
        await ctx.send(content="Muting Member!")


def setup(bot):
    bot.add_cog(Slash(bot))
