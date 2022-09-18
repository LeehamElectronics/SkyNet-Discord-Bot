import datetime
from discord.ext import commands
import configuration as configuration


# this simply logs all commands that members run into a discord channel and the SQL database.
# this cog is compatible with multi guild per bot installations.
class CommandEvents(commands.Cog):
    def __init__(self, client):
        self.client = client

        # channel objects:
        self.rules_channel = self.client.get_channel(configuration.ChannelObjects.rules_channel_id)
        self.bot_channel = self.client.get_channel(configuration.ChannelObjects.bot_channel_id)
        self.role_assign_channel = self.client.get_channel(configuration.ChannelObjects.role_assign_channel_id)
        self.dev_progress_channel = self.client.get_channel(configuration.ChannelObjects.dev_progress_channel_id)
        # logger channels:
        self.rule_breaker_log_channel = self.client.get_channel(configuration.ChannelObjects.rule_breaker_log_channel_id)
        self.error_log_channel = self.client.get_channel(configuration.ChannelObjects.discord_timing_channel_id)
        self.dm_log_channel = self.client.get_channel(configuration.ChannelObjects.dm_log_channel_id)
        self.admin_member_join_logger_channel = self.client.get_channel(
            configuration.ChannelObjects.admin_member_join_logger_channel_id)
        self.command_logger_channel = self.client.get_channel(configuration.ChannelObjects.commands_logger_channel_id)

    @commands.Cog.listener()
    async def on_ready(self):
        print("🟢 command_events.py loaded successfully.\n-----")

    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction, command):
        now = datetime.datetime.now()
        await self.command_logger_channel.send(f'{interaction.user.name}#{interaction.user.discriminator} ran /{command.name} {interaction.data["options"][0]["value"]}')


async def setup(client):
    await client.add_cog(CommandEvents(client))
