###################################
#   Import modules into program   #
###################################
import datetime
import random

import discord
from discord.ext import commands
from discord.utils import get

import src.db.configuration as configuration
import src.db.database as database
import src.levelling as levelling
from src.misc_functions import send_need_help_prompt


class MessageEvents(commands.Cog):
    def __init__(self, client):
        self.client = client

        # channel objects:
        self.dm_log_channel = self.client.get_channel(configuration.ChannelObjects.dm_log_channel_id)
        self.admin_member_join_logger_channel = self.client.get_channel(configuration.ChannelObjects.admin_member_join_logger_channel_id)
        self.all_message_log_channel = self.client.get_channel(configuration.ChannelObjects.all_message_log_channel_id)
        self.rules_channel = self.client.get_channel(configuration.ChannelObjects.rules_channel_id)
        self.bot_channel = self.client.get_channel(configuration.ChannelObjects.bot_channel_id)
        self.role_assign_channel = self.client.get_channel(configuration.ChannelObjects.role_assign_channel_id)
        self.dev_progress_channel = self.client.get_channel(configuration.ChannelObjects.dev_progress_channel_id)
        self.error_log_channel = self.client.get_channel(configuration.ChannelObjects.discord_timing_channel_id)

    @commands.Cog.listener()
    async def on_ready(self):
        print("🟢 message_events.py loaded successfully.\n-----")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        now = datetime.datetime.now()
        if str(before.content) == "" and str(after.content) == "":
            return
        if before.author.bot:
            return

        errors, return_data = database.insert_edit_message_log(before, after, after.edited_at)
        if errors is not None:
            await self.error_log_channel.send(embed=errors)
            return
        errors, return_data = database.increment_member_messages_count(after, 'total_message_edits')
        if errors is not None:
            await self.error_log_channel.send(embed=errors)
            return

        embed = discord.Embed(
            title=str(after.author),
            description=str(after.channel),
            color=discord.Colour.orange()
        )
        embed.set_footer(text=str(now.strftime('%H:%M:%S on %A, %B the %dth, %Y')))
        embed.set_thumbnail(url=after.author.display_avatar.url)  # https://i.imgur.com/Iw4o4JF.png"
        embed.set_author(name=after.author, icon_url="https://i.imgur.com/Iw4o4JF.png")
        embed.add_field(name="Before", value=str(before.content).replace('@', 'AT'))
        embed.add_field(name="After", value=str(after.content).replace('@', 'AT'))
        await self.all_message_log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        now = datetime.datetime.now()
        content = str(message.content)
        content_lowered = str(content.lower())
        author = message.author
        channel_of_message = message.channel
        attachments = message.attachments

        if message.author.bot:
            if message.channel == self.dev_progress_channel:
                # Webhook message was sent into dev_progress_channel, adding reactions
                await message.add_reaction(emoji='👍')
                await message.add_reaction(emoji='👎')
            return

        errors, return_data = database.insert_send_message_log(message, message.created_at)
        if errors is not None:
            await self.error_log_channel.send(embed=errors)
            return

        # levelling and statistics code
        added_exp = random.randint(1, 8)  # Generate random XP value...
        errors, return_data = database.fetch_member_last_message_time(author)
        if errors is not None:
            await self.error_log_channel.send(embed=errors)
            return
        levelling.try_to_add_add_experience(author, return_data, added_exp)

        # increase total messages sent & last message sent time statistics
        errors, return_data = database.increment_member_messages_count(message, 'total_messages_sent')
        if errors is not None:
            await self.error_log_channel.send(embed=errors)
            return

        # attempt to level up user
        await levelling.manual_level_up(author, channel_of_message)

        # Check if message was sent in DM:
        if isinstance(message.channel, discord.abc.PrivateChannel):
            embed = discord.Embed(
                title=str(author),
                description="Private DM",
                color=discord.Colour.orange())
            embed.set_footer(text=str(now.strftime('%H:%M:%S on %A, %B the %dth, %Y')))
            embed.set_thumbnail(url=author.display_avatar.url)  # https://i.imgur.com/Iw4o4JF.png"
            embed.set_author(name=author, icon_url="https://i.imgur.com/Iw4o4JF.png")
            embed.add_field(name="Message", value=content.replace('@', 'AT'))
            await self.dm_log_channel.send(embed=embed)
            return
        else:
            embed = discord.Embed(
                title=str(author),
                description=channel_of_message,
                color=discord.Colour.orange())
            embed.set_footer(text=str(now.strftime('%H:%M:%S on %A, %B the %dth, %Y')))
            embed.set_thumbnail(url=author.display_avatar.url)  # https://i.imgur.com/Iw4o4JF.png"
            embed.set_author(name=author, icon_url="https://i.imgur.com/Iw4o4JF.png")
            embed.add_field(name="Message", value=content.replace('@', 'AT'))
            await self.all_message_log_channel.send(embed=embed)

        # Process the message, not sure why, possibly for cogs??
        await self.client.process_commands(message)

        # Check if message was sent into memes channel:
        alright_emoji = get(self.client.emojis, name='alright')
        if message.channel.id == configuration.ChannelObjects.memes_channel_id:
            if message.attachments or "https://" in message.content or "http://" in message.content:
                await message.add_reaction(emoji='👍')
                await message.add_reaction(emoji=alright_emoji)
                await message.add_reaction(emoji='👎')

        # Here we check for a bunch of predefined messages: TODO: move all checks into another file
        if content_lowered == "no u":
            await message.channel.send("no us! *communism intensifies*")
        elif "no us" in content_lowered:
            await message.channel.send("no u?")
        elif "skynet is bad" in content_lowered:
            await message.add_reaction(emoji='👎')
            await message.channel.send("That's where you're wrong")
        elif "skynet bad" in content_lowered:
            await message.add_reaction(emoji='👎')
            await message.channel.send("That's where you're wrong")
        elif "skynet sucks" in content_lowered:
            await message.add_reaction(emoji='👎')
            await message.channel.send("That's where you're wrong")
        elif "server is bad" in content_lowered:
            await message.add_reaction(emoji='👎')
            await message.channel.send("That's where you're wrong")
        elif "i need help" in content_lowered:
            await send_need_help_prompt(message)
        elif "pls help" in content_lowered:
            await send_need_help_prompt(message)
        elif "help me" in content_lowered:
            await send_need_help_prompt(message)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        now = datetime.datetime.now()
        errors, return_data = database.insert_deleted_message_log(message, now)
        if errors is not None:
            await self.error_log_channel.send(embed=errors)
            return
        errors, return_data = database.increment_member_messages_count(message, 'total_message_deletes')
        if errors is not None:
            await self.error_log_channel.send(embed=errors)
            return


async def setup(client):
    await client.add_cog(MessageEvents(client))
