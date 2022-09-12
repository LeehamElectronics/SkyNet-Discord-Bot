###################################
#   Import modules into program   #
###################################
# Discord related API packages #
import discord
from discord.ext import commands
from discord.utils import get
from discord.ext import tasks  # For scheduling repeated function calls such as timers.
import asyncio  # For running asynchronous code...

import re  # For removing all non integers form a string, this is for converting @mentions into user ID

from database_related import check_if_user_is_mc_linked, write_user_data
from misc_functions import convert_variable_to_mem_obj, send_dm, _unban, punishments, \
    generate_level_picture, manual_add_experience, find_invite_by_code, update_member_data
from check_routines import check_roles
from messages import member_does_not_have_permision  # Messages are stored here
from mathmatical_functions import _map, find_members_rank, get_pretty_date_format
from messages import kick_message_to_kicked_user
from messages import ban_message_to_banned_user
from messages import warn_message_to_warned_user
from messages import unban_message_to_banned_user
from load_configs import share_global_config_dict_elsewhere  # Use this to find role ID's from config.yml
from main import share_users_dict_of_dict_elsewhere
from main import import_users_dict_of_dict_db
import random
from datetime import date
from datetime import datetime
import json
import yaml


class Events(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = share_global_config_dict_elsewhere()
        self.user_db_path = self.config['general_info']['user_db_path'] + '.json'
        self.channel_ids = self.config['discord_channel_ids']

    @commands.Cog.listener()
    async def on_ready(self):
        print("🟢 Events.py loaded successfully.\n-----")
        self.config = share_global_config_dict_elsewhere()
        self.user_db_path = self.config['general_info']['user_db_path'] + '.json'
        self.channel_ids = self.config['discord_channel_ids']

    @commands.Cog.listener()
    async def on_invite_create(self, member):
        # A way to make the following code run just before on_member_join occurs? I need to do this in order to keep
        # track of who invited who on my server. Thanks
        invites_after_join = await member.guild.invites()

    @commands.Cog.listener()
    async def on_invite_delete(self, member):
        # A way to make the following code run just before on_member_join occurs? I need to do this in order to keep
        # track of who invited who on my server. Thanks
        invites_after_join = await member.guild.invites()


def setup(client):
    client.add_cog(Events(client))
