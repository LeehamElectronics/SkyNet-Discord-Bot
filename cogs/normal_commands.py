###################################
#   Import modules into program   #
###################################
import discord
from discord.ext import commands
from discord.utils import get
from database_related import check_if_user_is_mc_linked
from misc_functions import convert_variable_to_mem_obj, send_dm, _unban, punishments, clear_channel, \
    generate_level_picture, manual_add_experience, update_member_data
from check_routines import check_roles
from messages import member_does_not_have_permision  # Messages are stored here
from mathmatical_functions import _map, find_members_rank
from load_configs import share_global_config_dict_elsewhere  # Use this to find role ID's from config.yml
from main import share_users_dict_of_dict_elsewhere
from main import import_users_dict_of_dict_db
from datetime import date
from datetime import datetime


class Commands(commands.Cog):

    def __init__(self, client):
        self.config = share_global_config_dict_elsewhere()
        self.client = client
        self.timings_channel = self.client.get_channel(self.config['discord_channel_ids']
                                                       ['admin_channel_ids']['discord_timing_channel_id'])
        self.mod_log_channel = self.client.get_channel(
            self.config['discord_channel_ids']['admin_channel_ids']['mod_log'])
        self.admin_role_id = self.config['discord_role_ids']['general_roles']['admin']
        self.mc_linked_role_id = self.config['discord_role_ids']['general_roles']['mc_linked']

    @commands.Cog.listener()
    async def on_ready(self):
        print('🟢 Normal Commands Cog Ready')
        self.timings_channel = self.client.get_channel(
            self.config['discord_channel_ids']['admin_channel_ids'][
                'discord_timing_channel_id'])
        self.mod_log_channel = self.mod_log_channel = self.client.get_channel(
            self.config['discord_channel_ids']['admin_channel_ids']['mod_log'])
        self.admin_role_id = self.config['discord_role_ids']['general_roles']['admin']
        self.mc_linked_role_id = self.config['discord_role_ids']['general_roles']['mc_linked']

    ####################################################
    #                                                  #
    #               Administration Commands            #
    #                                                  #
    ####################################################
    # ------------------------------ mute command ------------------------------ #
    @commands.command()
    async def mute(self, ctx, member, *, reason=None):
        print("muting user")
        type_of_pun = 'mute'
        human_called = True
        delete_msg_after = True
        punishment = await punishments(ctx.message.author, ctx, self.client, type_of_pun, member, reason, human_called,
                                       ctx.channel, delete_msg_after, ctx.guild)

    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing required argument, usage: `!mute <@Leeham#1234> [reason]`")
        else:
            raise error

    # ------------------------------ unmute command ------------------------------ #
    @commands.command()
    async def unmute(self, ctx, member, *, reason=None):
        print("un muting user")
        type_of_pun = 'un_mute'
        human_called = True
        delete_msg_after = True
        punishment = await punishments(ctx.message.author, ctx, self.client, type_of_pun, member, reason, human_called,
                                       ctx.channel, delete_msg_after, ctx.guild)

    @unmute.error
    async def un_mute_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing required argument, usage: `!unmute <@Leeham#1234> [reason]`")
        else:
            raise error

    # ------------------------------ kick command ------------------------------ #
    @commands.command()
    async def kick(self, ctx, member, *, reason=None):
        print("kicking user")
        type_of_pun = 'kick'
        human_called = True
        delete_msg_after = True
        punishment = await punishments(ctx.message.author, ctx, self.client, type_of_pun, member, reason, human_called,
                                       ctx.channel, delete_msg_after, ctx.guild)

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing required argument, usage: `!kick <@Leeham#1234> [reason]`")
        else:
            raise error

    # ------------------------------ warn command ------------------------------ #
    @commands.command()
    async def warn(self, ctx, member, *, reason=None):
        print("warning user")
        type_of_pun = 'warn'
        human_called = True
        delete_msg_after = True
        punishment = await punishments(ctx.message.author, ctx, self.client, type_of_pun, member, reason, human_called,
                                       ctx.channel, delete_msg_after, ctx.guild)

    @warn.error
    async def warn_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing required argument, usage: `!warn <@Leeham#1234> [reason]`")
        else:
            raise error

    # ------------------------------ ban command ------------------------------ #
    @commands.command()
    async def ban(self, ctx, member, *, reason=None):
        print("banning User")
        type_of_pun = 'ban'
        human_called = True
        delete_msg_after = True
        punishment = await punishments(ctx.message.author, ctx, self.client, type_of_pun, member, reason, human_called,
                                       ctx.channel, delete_msg_after, ctx.guild)

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing required argument, usage: `!ban <@Leeham#1234> [reason]`")
        else:
            raise error

    # ------------------------------ unban command ------------------------------ #
    @commands.command(aliases=['pardon'])
    async def unban(self, ctx, member, *, reason=None):
        print("unbanning user")
        type_of_pun = 'unban'
        human_called = True
        delete_msg_after = True
        punishment = await punishments(ctx.message.author, ctx, self.client, type_of_pun, member, reason, human_called,
                                       ctx.channel, delete_msg_after, ctx.guild)

    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing required argument, usage: `!unban <leeham#1234 / user_ID> [reason]`")
        else:
            raise error

    # ------------------------- view bans command ------------------------------ #
    @commands.command(aliases=['view_bans'])
    async def banned_users(self, ctx):
        print("displaying bans")
        if not check_roles(ctx.message.author, self.admin_role_id):
            await ctx.channel.send(member_does_not_have_permision(ctx))  # This sends the author a 'no perms' msg
            return

        ban_list = await ctx.guild.bans()
        bans_string = ''
        for ban in ban_list:
            bans_string = bans_string + '\n' + str(ban)
        await ctx.send(bans_string)
        print(str(ban_list))

    @banned_users.error
    async def banned_users_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Command failed, usage: `!view_bans`")
        else:
            raise error

    # ------------------------- view bans command ------------------------------ #
    @commands.command(aliases=['clears'])  # pass_context = True ???
    async def clear(self, ctx, index: int):
        if not check_roles(ctx.message.author, self.admin_role_id):
            await ctx.channel.send(member_does_not_have_permision(ctx))  # This sends the author a 'no perms' msg
            return
        # make it look like the bot is typing...
        async with ctx.typing():
            await clear_channel(index, ctx.message)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing required argument, usage: `!clear <number>`")
        else:
            raise error

    @commands.command(aliases=['stats'])  # pass_context = True ???
    async def stat(self, ctx):
        member = ctx.message.author
        member_id = str(ctx.message.author.id)
        # Here we need to get the current user database into this function, keep in mind that this should be treated as
        # a READ ONLY var because any changes made to this db will be discarded. We can't return it back to the main.py
        # without creating a black hole and ending the entire bots career.
        user_db_dict_of_dict = share_users_dict_of_dict_elsewhere()

        # Use the user_db to get the info we need
        experience = user_db_dict_of_dict[member_id]["experience"]
        level = user_db_dict_of_dict[member_id]["level"]

        # Find the rank of member with provided data
        rank_num = find_members_rank(ctx.message.author.id, user_db_dict_of_dict)

        # Should we only allow this command to run in #bot-commands channel? idk, will decide later...
        is_mc_linked, mc_uuid = check_if_user_is_mc_linked(member)
        
        # Generate image to be sent of rank and exp level info
        generate_level_picture(member, experience, level, rank_num, is_mc_linked, mc_uuid)
        file = discord.File("generated_images/rank.png")  # here we obtain that image file

        # Make a string of when member joined server
        member_joined_server = "{0}-{1}-{2}".format(str(member.joined_at.year), str(member.joined_at.month),
                                                    str(member.joined_at.day))
        
        if is_mc_linked:
            # mc account is linked! We will now check if the user already has their mc_linked role. Will need to add a
            # routine like this everytime someone links their account in MC so this process is already completed,
            # TODO: add check_mc_linked function run when mc player links a Discord account automatically
            if not check_roles(member, self.mc_linked_role_id):
                # User has just linked their account, lets congratulate / reward them!
                xp_reward = 300
                await ctx.message.author.add_roles(get(ctx.guild.roles, id=self.mc_linked_role_id))
                await ctx.channel.send(f":tada: Congrats {ctx.message.author.mention}, "
                                       f"you have linked your MC account! You Receive 300 XP for that.")
                # here we add experience to the member as a reward for linking their MC account
                updated_user_db = await manual_add_experience(member, xp_reward, ctx.channel, user_db_dict_of_dict)
                import_users_dict_of_dict_db(updated_user_db)

            # create stats embed here
            embed = discord.Embed(
                title="Your Stats!",
                description="",
                color=member.colour.value
            )
            
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_author(name=f"SkyNet ~ {member.nick}", icon_url="https://i.imgur.com/Iw4o4JF.png")
            embed.add_field(name="Joined SkyNet", value=member_joined_server, inline=False)
            embed.set_image(url="attachment://generated_images/rank.png")
            embed.set_footer(text="React with 🎮 for your MC stats!")

            msg_ref = await ctx.channel.send(file=file, embed=embed)  # Send the image file and the embed here
            await msg_ref.add_reaction(emoji='🎮')  # add a reaction to the message

        else:
            # No MC account is linked, so we will send a basic embed recommending the member to link their MC account
            embed = discord.Embed(
                title="Your Stats!",
                description="",
                color=member.colour.value
            )

            embed.set_thumbnail(url=ctx.message.author.avatar_url)
            embed.set_author(name=f"SkyNet ~ {member.nick}", icon_url="https://i.imgur.com/Iw4o4JF.png")
            embed.add_field(name="MC Account not linked yet", value="Please link your MC Account to see cool info!",
                            inline=False)
            embed.add_field(name="Joined SkyNet", value=member_joined_server, inline=False)
            embed.set_image(url="attachment://generated_images/rank.png")
            embed.set_footer(text="Click ❓ to learn how to link your MC account")

            msg_ref = await ctx.channel.send(file=file, embed=embed)  # Send the image file and the embed here
            await msg_ref.add_reaction(emoji='🎮')  # add a reaction to the message

    # ------------------------- remove reactions command ------------------------------ #
    @commands.command(aliases=['remove_reactions'])  # pass_context = True ???
    async def remove_reaction(self, ctx):
        if not check_roles(ctx.message.author, self.admin_role_id):
            await ctx.channel.send(member_does_not_have_permision(ctx))  # This sends the author a 'no perms' msg
            return
        # make it look like the bot is typing...
        async with ctx.typing():
            reactions_to_remove = []

    # ------------------------- update user db command ------------------------------ #
    @commands.command(aliases=['update_database'])  # pass_context = True ???
    async def update_db(self, ctx):
        # Run this command if the bot was offline for a while or there was a change to db, this is recourse HEAVY
        if not check_roles(ctx.message.author, self.admin_role_id):
            await ctx.channel.send(member_does_not_have_permision(ctx))  # This sends the author a 'no perms' msg
            return
        # make it look like the bot is typing...
        async with ctx.typing():
            db = share_users_dict_of_dict_elsewhere()
            for member in ctx.guild.members:
                db = update_member_data(member, db)
            # give new db back to main.py
            import_users_dict_of_dict_db(db)
        # ------------------------- remove reactions command ------------------------------ #

    @commands.command(aliases=['lookup'])  # pass_context = True ???
    async def find_user(self, ctx, index: int):
        if not check_roles(ctx.message.author, self.admin_role_id):
            await ctx.channel.send(member_does_not_have_permision(ctx))  # This sends the author a 'no perms' msg
            return
        # make it look like the bot is typing...
        async with ctx.typing():
            # TODO: Make this generate a private channel that only the command issuer can see.

            user = await self.client.fetch_user(index)

            ########################################
            # Find how many days old an account is #
            ########################################

            # date the account was created
            account_created = user.created_at
            year = int(account_created.strftime("%Y"))
            month = int(account_created.strftime("%m"))
            day = int(account_created.strftime("%d"))
            created_date = date(year, month, day)

            # today's date
            now = datetime.now()
            year = int(now.strftime("%Y"))
            month = int(now.strftime("%m"))
            day = int(now.strftime("%d"))
            today = date(year, month, day)

            # Calculate gap
            gap = (today - created_date).days

            who_you_have_invited = "You have invited, "
            for member_id in share_users_dict_of_dict_elsewhere()[str(ctx.message.author.id)]['invited']:
                mem_obj = await self.client.fetch_user(member_id)
                who_you_have_invited = f'{who_you_have_invited} {str(mem_obj.mention)}, '

            await ctx.send("Account created: " + str(user.created_at) + '\n' + f'Account age: {gap}' + '\n' + str(user.avatar_url) + '\n' + str(user.name) + '#' + str(user.discriminator))
            await ctx.send(who_you_have_invited)


def setup(client):
    client.add_cog(Commands(client))
