###################################
#   Import modules into program   #
###################################
from discord.ext import commands
import configuration


class InviteEvents(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = configuration.ConfigFile.root_conf
        self.user_db_path = self.config['general_info']['user_db_path'] + '.json'
        self.channel_ids = self.config['discord_channel_ids']

    @commands.Cog.listener()
    async def on_ready(self):
        print("🟢 Events.py loaded successfully.\n-----")
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


async def setup(client):
    await client.add_cog(InviteEvents(client))
