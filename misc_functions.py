#########################################################
#                                                       #
#         Misc functions for making code cleaner        #
#                                                       #
#########################################################
import discord
from discord.utils import get
import asyncio  # For running asynchronous code...
import datetime
import os
import re  # For removing all non integers form a string, this is for converting @mentions into user ID
from check_routines import check_roles
from discord_embed_generators import gen_punishment_embed_mod_log_embed, gen_unban_embed
from load_configs import share_global_config_dict_elsewhere  # Use this to find role ID's from config.yml
from mathmatical_functions import _map
import requests
from messages import member_does_not_have_permision  # Messages are stored here
from messages import kick_message_to_kicked_user
from messages import ban_message_to_banned_user
from messages import warn_message_to_warned_user
from messages import unban_message_to_banned_user
from messages import mute_message_to_muted_user
from messages import un_mute_message_to_un_muted_user

#############################################################
#                       Image processing                    #
#############################################################
# Pillow is used for dynamic image processing #
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

#####################################
#                                   #
#       Global Variables Here       #
#                                   #
#####################################
config = share_global_config_dict_elsewhere()
admin_role_id = config['discord_role_ids']['general_roles']['admin']
server_id = config['general_info']['guild_id']


# This function converts a user mention string into a user object
def convert_variable_to_mem_obj(guild, user_var, client):
    # user variable provided can one of four things: ID (123456), name (leeham), name+discr: (leehaam#1234),
    # or @mention which actually renders like this: <@!270857271632855040>
    # This function will return (True, member_obj) if the user is 100% found, it will return (False, suggested_member)
    # if it could find similar match, and will (return False, None) if nothing found

    # obtain list of all members in guild
    member_obj_list = guild.members
    # First we check if string is a @mention
    if '@' in str(user_var):
        print("found a @ in username, this is therefore a @mention")

        try:
            # removing all non integers from string:
            formatted_user_mention = re.sub("[^0-9]", "", str(user_var))  # Remove all non integers from
            print(str(formatted_user_mention))
            # convert int ID into member object:
            member_obj = guild.get_member(int(formatted_user_mention))  # try to convert user id int into a member
            return True, member_obj

        except Exception as e:
            # This means the provided @mention was not complete or broken, instead we will try and search for name/discr
            print("Unable to convert @mention, searching for name/discr")
            name = str(user_var).replace('@', '')  # remove @

            for member_obj in member_obj_list:
                if str(member_obj.name) == name:
                    print(f"found name match of {name}")
                    return False, member_obj
            # If we get here, that means we were unable to convert @mention into a member because it was typed wrong
            return False, None

    elif '#' in str(user_var):
        # Here it is clear that the provided user_var is a name+disc
        user_name = str(str(user_var).split('#')[0])
        discriminator = str(str(user_var).split('#')[1])

        for member_obj in member_obj_list:
            if str(member_obj.name).lower() == user_name.lower():
                print(f"found name match of {user_name}")
                if str(member_obj.discriminator) == discriminator:
                    print(f"found perfect match of {user_var}")
                    return True, member_obj
                else:
                    print("only found a likely match, sending suggestion...")
                    return False, member_obj

        # if we get here, no matching names were found in guild
        print("found no matches of name, now searching for matching discr")
        for member_obj in member_obj_list:
            if str(member_obj.discriminator) == discriminator:
                print(f"found discriminator match of {discriminator}")
                if str(member_obj.name).lower() == user_name.lower():
                    print(f"found perfect match of {user_var}")
                    return True, member_obj
                else:
                    print("only found a likely match, sending suggestion...")
                    return False, member_obj

        # If we get to this stage, neither id or name was found in guild. Return None
        print("could not find name or id")
        return False, None

    else:
        # The only logical options left are, the provided data was a ID, or it was a name only.
        # First we test if user_var looks like a 18 digit ID:
        if str(len(str(user_var))) == "18" and str(user_var).isdecimal():
            print("user_var is both 18 digits and a decimal number, this is possibly a user ID")
            try:
                member_obj = guild.get_member(int(user_var))  # try to convert user id int into a member object
                return True, member_obj
            except:
                # two options here, either the provided ID was invalid, or someone managed to have a 18 digit decimal
                # number as their name, which is very odd...
                print("unable to parse user_var as a user ID, proceeding with next attempt")

        # last resort, a simple user name must have been given, if this fails than the user does not exist in guild.
        print("searching for potential member under name")
        for member_obj in member_obj_list:
            # TODO: make a list and append to it all users with matching name as some people have the same name...
            if str(member_obj.name).lower() == str(user_var).lower():
                print(f"found name match of {user_var}")
                return False, member_obj
        # If we get here, nothing was found at all!
        print("could not find name in guilds members list")
        return False, None


# This sends a DM to a member:
async def send_dm(member, content):
    channel = await member.create_dm()
    await channel.send(content)


# Obtain a list of banned users from Discord server
async def list_banned_users(ctx):
    banned_users = await ctx.guild.bans()
    list_of_users = []
    banned_user = {}
    for user in banned_users:
        name_with_tag = str(f"{str(user[1])}")
        banned_user['user_obj'] = user[1]
        banned_user['name'] = name_with_tag
        list_of_users.append(banned_user)
    return list_of_users


# pardon a user
async def _unban(ctx, user_var):
    # First we need to see what user is, is it an ID or username+discriminator?
    list_of_users = await list_banned_users(ctx)
    unbanned = False
    user = str(user_var)
    if "#" in user:
        # This means that the user_name is indeed a username with a discriminator, we will need to search for username
        for banned_user in list_of_users:
            # print("CHECKING: " + str(banned_user['name']) + " against: " + str(user))
            if str(banned_user['name']).lower() == user.lower():
                # print("Found user!")
                await ctx.guild.unban(banned_user['user_obj'])
                # print("user unbanned!")
                unbanned = True
                return unbanned, banned_user['user_obj']
        if not unbanned:
            # the requested user to be unbanned was not found in databse...
            print("user not banned, unable to find NAME in ban list")
            return unbanned, None
    else:
        # This means the moderator has provided us with a user ID, so will search for user ID's
        # removing all non integers from string:
        formatted_user = str(re.sub("[^0-9]", "", user))  # Remove all non integers from

        for banned_user in list_of_users:
            banned_user_id = str(banned_user['user_obj'].id)
            # print("CHECKING: " + banned_user_id + " against: " + searching_for_id)
            if banned_user_id == formatted_user:
                await ctx.guild.unban(banned_user['user_obj'])
                unbanned = True
                return unbanned, banned_user['user_obj']
        if not unbanned:
            # the requested user to be unbanned was not found in databse...
            print("user not banned, unable to find ID in ban list")
            return unbanned, None


# warn a user
async def warn_user(user, reason, public):
    if public:
        print("publicly warning user")
        # send message into desired channel?? TODO: pass optional channel into arg, or default into general
    else:
        print("warning user privately")
        # This will now add the warn into the issued warnings database


async def punishments(author, ctx, client, type_of_pun, punished_user, reason, human_called, channel, delete_msg_after, guild):
    # This section obtains channel objects and role ID's. Can we move this into global vars? only issue is client obj
    ####################################################################################################################
    # Get role ID's and channel objects
    timings_channel = client.get_channel(config['discord_channel_ids']['admin_channel_ids']
                                         ['discord_timing_channel_id'])
    mod_log_channel = client.get_channel(config['discord_channel_ids']['admin_channel_ids']['mod_log'])
    ####################################################################################################################

    if type_of_pun == "ban":
        msg_content = ban_message_to_banned_user(reason)
    elif type_of_pun == "kick":
        msg_content = kick_message_to_kicked_user(reason)
    elif type_of_pun == "mute":
        msg_content = mute_message_to_muted_user(reason)
    elif type_of_pun == "un_mute":
        msg_content = un_mute_message_to_un_muted_user(reason)
    elif type_of_pun == "warn":
        msg_content = warn_message_to_warned_user(reason)
    elif type_of_pun == "unban":
        msg_content = unban_message_to_banned_user(reason)
    else:
        return "invalid pun type"

    # Check permissions on member that issued command:
    if human_called:
        user_that_issued_pun_mentioned = author.mention
        user_that_issued_pun = author
        if not check_roles(author, admin_role_id):
            await channel.send(member_does_not_have_permision(author))  # This sends the author a 'no perms' msg
            return
    else:
        user_that_issued_pun_mentioned = "_internal-bot_"
        user_that_issued_pun = "_internal-bot_"

    if type_of_pun == "unban":
        # we dont need to continue this function as the unban is simple
        print("UNBANNING NOW")
        print(str(user_that_issued_pun))
        unban_completed, unbanned_user = await _unban(ctx, punished_user)
        if unban_completed:
            # send message into mod log
            await mod_log_channel.send(
                embed=gen_unban_embed(reason, user_that_issued_pun, unbanned_user))
        else:
            # failed to unban user for whatever reason:
            await ctx.message.delete()
            await mod_log_channel.send(
                f"Sorry {user_that_issued_pun_mentioned}, we were unable to {type_of_pun} {str(punished_user)}, they don't seem to be in this server?")
        return

    try:
        if human_called:
            # try and convert provided user to a member object so they can be punished
            found, member_obj = convert_variable_to_mem_obj(guild, punished_user, client)
        else:
            # Here we do not need to try and convert into mem  obj because we already know what the member obj is.
            found = True
            member_obj = punished_user
        if found:
            member = member_obj
        else:
            if member_obj is not None:
                # Await admins confirmation as we are not 100% sure on what user they want to punish
                await ctx.channel.send(f"Did you mean {member_obj.name}#{member_obj.discriminator}")
                return 'punishment awaiting confirmation'
            else:
                # no user found
                await ctx.channel.send("Sorry, no user was found with that name")
                return 'user not found'

        # Inform user of punishment in DM
        try:  # try to DM the user, this often fails due to end user settings
            await send_dm(member, msg_content)
        except Exception as e:
            print(f"Unable to send {member.name} a {type_of_pun} message for reason: " + str(
                e))  # Diagnostic purposes.

        await punish_user(ctx, type_of_pun, member, reason, client)
        await mod_log_channel.send(embed=gen_punishment_embed_mod_log_embed(type_of_pun, reason, user_that_issued_pun, member))
    except Exception as e:
        await mod_log_channel.send(
            f"Sorry {user_that_issued_pun_mentioned}, we were unable to {type_of_pun} {punished_user}, they don't seem to be in this server? See error log for details.")
        await timings_channel.send(f"Error detected, unable to {type_of_pun} {member} error:  {str(e)[:1024]}")

    # Delete the kick command from channel:
    if delete_msg_after:
        await ctx.message.delete()
    return "punishment successful"


# Simple function that switches between punishments and carries them out
async def punish_user(ctx, type_of_pun, member, reason, client):
    if type_of_pun == "ban":
        await member.ban(reason=reason)
    elif type_of_pun == "kick":
        await member.kick(reason=reason)
    elif type_of_pun == "mute":
        muted_role = get(ctx.guild.roles, id=config['discord_role_ids']['general_roles']['muted'])
        await member.add_roles(muted_role)
    elif type_of_pun == "un_mute":
        muted_role = get(ctx.guild.roles, id=config['discord_role_ids']['general_roles']['muted'])
        await member.remove_roles(muted_role)
    elif type_of_pun == "warn":
        public = False
        # This does not DM the user at all, as this is already done in the punishments() function, it only optionally
        # sends a public message into channel and also adds the warn into the users database of issued warnings.
        await warn_user(member, reason, public)
    else:
        return "invalid pun type"
    print("")


async def clear_channel(args, message):  # clears a given channel of a given number of messages
    channel = message.channel
    # check to make sure args is a integer value:
    try:
        amount = int(args)
    except Exception as error:
        error_msg = await channel.send(embed=discord.Embed(
            color=discord.Color.red(), description=f"Please provide a valid number {message.author.mention}")
        )
        await asyncio.sleep(3)
        await error_msg.delete()
        await message.delete()
        return
    # Now we will check to make sure the value is not too big or too small
    if 0 < amount < 30:
        pass
    else:
        error_msg = await channel.send(embed=discord.Embed(
            color=discord.Color.red(), description=f"Please provide a valid number {message.author.mention}")
        )
        await asyncio.sleep(3)
        await error_msg.delete()
        await message.delete()
        return

    cleared = -1  # we make is -1 instead of 0 because we don't want to include the !clear command msg itself
    failed = 0
    # Gets a list of given messages in a channel, we add one so the actual !clear command is included
    msg_history_list = channel.history(limit=amount + 1)
    async for msg in msg_history_list:
        try:
            await msg.delete()
            cleared += 1
        except:
            failed += 1
            pass
    failed_str = "\n\nFailed to clear %s message(s)." % failed if failed > 0 else ""
    return_msg = await channel.send(
        embed=discord.Embed(color=discord.Color.blue(), description="Cleared %s message(s).%s" % (cleared, failed_str)))
    await asyncio.sleep(3)
    await return_msg.delete()


# Does not return anything, only saves the image into a file.
def generate_level_picture(member, member_xp, member_lvl, member_rank, is_mc_linked, mc_uuid):
    if is_mc_linked:
        # Assign the first image of Discord, and second will be there MC skin
        profile_pic_main = str(member.avatar_url)
        profile_pic_second = f"https://www.mc-heads.net/combo/{mc_uuid.replace('-', '')}"
    else:
        # In this case we have no MC skin to use, so we will send only a Discord profile pic
        profile_pic_main = str(member.avatar_url)
        profile_pic_second = str(member.avatar_url)

    back_ground_image = Image.open("art_work/stats_basic_transparent_background.png")

    # This is the best API link for a skin image, but currently the API is down, so I'll just leave it here for ref
    # https://minotar.net/bust/{mc_uuid.replace('-', '')}/1000.png

    xp_needed = int(member_lvl ** 4)
    xp_to_go = int(xp_needed) - int(member_xp)
    current_lvls_base_xp_reference = (int(member_lvl) - 1) ** 4
    xp_bar_icon_path = "art_work/mc_xp_bar_" + str(
        _map(int(member_xp), current_lvls_base_xp_reference, int(xp_needed), 1, 17)) + ".png"

    # req = Request(profile_pic_second, headers={'User-Agent': 'Mozilla/5.0'})
    # path_to_mc_skin = urlopen(req).read()

    mc_skin_image = Image.open(requests.get(profile_pic_second, stream=True).raw).resize((800, 800))

    # mc_skin_image = Image.open(path_to_mc_skin).resize((800, 800))
    level_bar_image = Image.open(xp_bar_icon_path).resize((2150, 99))
    back_ground_image.paste(mc_skin_image, (2200, 0))
    back_ground_image.paste(level_bar_image, (0, 700))
    draw = ImageDraw.Draw(back_ground_image)

    # Fonts for reference #
    default_font = "burbank_big_condensed_black"

    # (x,y)::↓↓↓(text)::↓↓(r,g,b)::↓↓↓
    draw.text((0, 0), "Rank #" + str(member_rank), (255, 149, 0), font=get_fonts(default_font, 250))
    draw.text((0, 275), "{} More XP Needed For Level {}".format(str(xp_to_go), str(int(member_lvl) + 1)),
              font=get_fonts(default_font, 150), fill=(255, 149, 0, 255))
    draw.text((800, 570), "{} / {}".format(str(member_xp), str(xp_needed)), font=get_fonts(default_font, 140),
              fill=(255, 149, 0, 255))
    back_ground_image.save('generated_images/rank.png')


def get_fonts(font, size):
    cwd = str(os.getcwd())
    if font == "old_font_skinny":
        dir = r"\fonts\Modern_Sans_Light.otf"
    elif font == "helloria":
        dir = r"\fonts\Helloria.otf"
    elif font == "burbank_big_condensed_black":
        dir = r"\fonts\BurbankBigCondensed-Black.otf"
    elif font == "neitherly_demo_bold":
        dir = r"\fonts\NeitherlyDemoBold.ttf"
    elif font == "verona":
        dir = r"\fonts\Verona.otf"
    else:
        dir = r"\fonts\BurbankBigCondensed-Black.otf"
    return ImageFont.truetype(str(cwd + dir), size)


########################################################################
#                                                                      #
#  EXPERIMENTAL: Add XP and Level Up Users form misc_functions.py      #
#  Then we will need to parse user_db BACK into the main.py though cog #
#                                                                      #
########################################################################
# Simple adds a specific amount of XP to the user
async def manual_add_experience(user, exp, channel, user_db):
    # Here we need to get the current user database into function:
    user_id = str(user.id)
    user_db[user_id]["experience"] += exp
    await manual_level_up(user, channel, user_db)
    return user_db


# Used to check if player can level up or level up MULTIPLE levels, and then it does so and announces it to user.
async def manual_level_up(user, channel, user_db):
    user_id = str(user.id)
    user_finished_leveling_up = False

    initial_lvl = user_db[user_id]["level"]  # We will compare against this at break of loop
    while not user_finished_leveling_up:
        experience = user_db[user_id]["experience"]
        level = user_db[user_id]["level"]
        xp_needed = level ** 4
        if experience > xp_needed:
            # user has leveled up, hooray! (don't announce it yet because they may level up even more!)
            user_db[user_id]["level"] += 1
        else:
            user_finished_leveling_up = True
            if int(initial_lvl) < int(user_db[user_id]["level"]):
                await channel.send(
                    f":tada: Congrats {user.mention}, you levelled up from {initial_lvl} to level " + str(
                        user_db[user_id]["level"]))
            else:
                # I'll keep this for now, but if it gets annoying it will be removed...
                await channel.send(
                    f"😢 Sorry {user.mention}, you did not get enough XP to level up! Maybe next time...")
    return user_db

    # DEPRECATED FOR NOW: We don't run this because I moved the function back into main.py
    # VERY IMPORTANT: We need to give the user db back to the main.py, only here for reference
    # update_users_dict_of_dict_from_elsewhere(user_db_dict_of_dict)


def find_invite_by_code(invite_list, code):
    # Simply looping through each invite in a given invite list
    for inv in invite_list:
        # Check if the invite code in this element
        # of the list is the one we're looking for
        if str(inv.code) == str(code):
            # If it is, we return it.
            return inv


# Run this function to check if member exists in data file, if not, add them
def update_member_data(member_obj, db):
    user_id = str(member_obj.id)

    if user_id in db:
        # User already exists in db, we don't need to create a new db, but we will check to make sure there a no
        # missing keys because they could generate errors in the future
        member = db[user_id]

        # This check sequence could be simplified by doing a hash and comparing the two, or by simply checking the
        # amount of keys in the dictionary to check for missing keys. A hash would be the best option. TODO: hashes here
        if "name" not in member:
            member["name"] = str(member_obj.name)
        if "experience" not in member:
            member["experience"] = 1
        if "level" not in member:
            member["level"] = 2
        if "last_message" not in member:
            member["last_message"] = 0
        if "invited_by" not in member:
            member["invited_by"] = "Unknown"
        if "invited" not in member:
            member["invited"] = []

        # The following will check to make sure no duplicate invites were in user db
        invited_users_old_list = member['invited']
        invited_users_new_list = []
        for i in invited_users_old_list:
            if i not in invited_users_new_list:
                invited_users_new_list.append(i)

        member["invited"] = invited_users_new_list

        if "invites" not in member:
            member["invites"] = 0

        # here we make sure invites is accurate:
        member['invites'] = int(len(member["invited"]))

        if "total_messages" not in member:
            member["total_messages"] = 0
        if "give_aways_won" not in member:
            member["give_aways_won"] = 0
        if "ID" not in member:
            member["ID"] = user_id
        if "left_server" not in member:
            member["left_server"] = 0  # They have left server 0 times
        if "joined_server" not in member:
            member["joined_server"] = \
                str(member_obj.joined_at.day) + "-" + str(member_obj.joined_at.month) + "-" + str(member_obj.joined_at.year)
        if 'member_roles' not in member:
            member['member_roles'] = []

    else:
        # Brand new user, they will have a new user db added to db
        member = {}
        member["name"] = str(member_obj.name)
        member["experience"] = 1
        member["level"] = 2
        member["last_message"] = 0
        member["invited_by"] = "Unknown"  # This gets changed in functions such as on_member_join
        member["invites"] = 0
        member["invited"] = []
        member["total_messages"] = 0
        member["give_aways_won"] = 0
        member["ID"] = user_id
        member["left_server"] = 0
        member["joined_server"] = \
            str(member_obj.joined_at.day) + "-" + str(member_obj.joined_at.month) + "-" + str(member_obj.joined_at.year)
        member['member_roles'] = []
        db[user_id] = member

    return db


# Returns a list of a members last known roles, returns None if the user does not exist in db
def retrieve_members_role_ids(member, db):
    member_id = str(member.id)
    if member_id in db:
        # we found member inside the db, retrieve list of role id's
        members_original_role_id_list = db[member_id]['member_roles']
        print("TEST???::: " + str(members_original_role_id_list))
    else:
        # user does not exist in local db
        members_original_role_id_list = None
    return members_original_role_id_list


# This function is called when a user gets verified, all of their original roles are assigned to them
async def assign_list_of_roles_to_member(member, list_of_role_ids):
    # as a suggestion, list_of_role_ids could be obtained by calling retrieve_members_role_ids()
    members_current_roles = member.roles
    for role_id in list_of_role_ids:
        # get the role object from guild
        role = get(member.guild.roles, id=role_id)
        if role in members_current_roles:
            # member already has this role...
            print("MEMBER ALREADY HAS THIS ROLE")
            continue
        else:
            # member does not have this role, so we will add it to them:
            print("ADDING ROLE RN!!!")
            await member.add_roles(role)


# This function adds a Member role (verified) to a member and sends a message into general chat announcing it
async def verify_member(member, general_channel):
    # as a suggestion, list_of_role_ids could be obtained by calling retrieve_members_role_ids()
    members_current_roles = member.roles
    member_role = get(member.guild.roles, id=config['discord_role_ids']['general_roles']['member'])

    if member_role in members_current_roles:
        # the member is already verified?
        return
    else:
        # member does not have this role, so we will add it to them:
        await member.add_roles(member_role)
    await general_channel.send(f'Welcome {member.name} to the SkyNet Discord Server, you have now been verified!')

