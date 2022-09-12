########################################################################################################################
#                                              --- SkyNet Servers ---                                                  #
#                                             SkyNet Discord Bot main.py                                               #
#                                              Date Started: 8-11-2020                                                 #
#     Keep in mind that this is not a public bot, hence it is designed to be run as one instance PER Discord Server    #
########################################################################################################################

# ██╗░░░░░███████╗███████╗██╗░░██╗░█████╗░███╗░░░███╗██╗░██████╗
# ██║░░░░░██╔════╝██╔════╝██║░░██║██╔══██╗████╗░████║╚█║██╔════╝
# ██║░░░░░█████╗░░█████╗░░███████║███████║██╔████╔██║░╚╝╚█████╗░
# ██║░░░░░██╔══╝░░██╔══╝░░██╔══██║██╔══██║██║╚██╔╝██║░░░░╚═══██╗
# ███████╗███████╗███████╗██║░░██║██║░░██║██║░╚═╝░██║░░░██████╔╝
# ╚══════╝╚══════╝╚══════╝╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░░░░╚═╝░░░╚═════╝░

# ░██████╗░█████╗░███████╗████████╗░██╗░░░░░░░██╗░█████╗░██████╗░███████╗
# ██╔════╝██╔══██╗██╔════╝╚══██╔══╝░██║░░██╗░░██║██╔══██╗██╔══██╗██╔════╝
# ╚█████╗░██║░░██║█████╗░░░░░██║░░░░╚██╗████╗██╔╝███████║██████╔╝█████╗░░
# ░╚═══██╗██║░░██║██╔══╝░░░░░██║░░░░░████╔═████║░██╔══██║██╔══██╗██╔══╝░░
# ██████╔╝╚█████╔╝██║░░░░░░░░██║░░░░░╚██╔╝░╚██╔╝░██║░░██║██║░░██║███████╗
# ╚═════╝░░╚════╝░╚═╝░░░░░░░░╚═╝░░░░░░╚═╝░░░╚═╝░░╚═╝░░╚═╝╚═╝░░╚═╝╚══════╝

###################################
#   Import modules into program   #
###################################
# Discord related API packages #
import discord
from discord.ext import commands
from discord.utils import get
from discord.ext import tasks  # For scheduling repeated function calls such as timers.
import asyncio  # For running asynchronous code...

# misc #
import logging  # Should implement this at some stage...
import json  # We use JSON to dump our Python dictionaries into a JSON file format
import os  # Interact with OS through Python for listing dir's and the like
import random  # Pretty random right?
from difflib import SequenceMatcher  # For checking how similar a string is to another string, like auto correct!
import traceback  # For error logging
import yaml

# Time and Date packages because I am lazy #
import time  # Mr wolf?
import datetime
from datetime import date

# RSS Feeds and Web interacting #
import feedparser  # for RSS Feeds!
import urllib.request  # For getting web data from JW.org and WOL
from bs4 import BeautifulSoup  # For ciphering HTML data
import urllib.request, io

# Networking #
import mysql.connector  # For interacting with the internal MySQL Server

# Pillow is used for dynamic image processing #
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

# These imports are from local .py files:
from load_configs import share_global_config_dict_elsewhere, read_rules_into_mem
from mathmatical_functions import _map, get_pretty_time_format, get_dashed_time_format, get_pretty_date_format
from database_related import write_user_data, read_users_data_into_mem
from discord_embed_generators import generate_help_menu
from database_related import get_mc_stats_embed, check_if_user_is_mc_linked
from misc_functions import update_member_data, check_roles, verify_member, assign_list_of_roles_to_member, retrieve_members_role_ids, punishments


print("Loading Configuration...")
global_configuration_dict = share_global_config_dict_elsewhere()  # Load our configuration file into memory
image_urls = global_configuration_dict['image_links']  # keeps code cleaner when referencing image urls

########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                        Global permanent variables assigned here                                      #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################

intents = discord.Intents.all()
intents.message_content = True
intents.members = True
client = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)

# help command does not work without this statement... idk why
client.remove_command("help")

####################
#  Misc variables  #
####################
os.getcwd()  # Get current working directory of bot location
total_member_count_val = 0
total_bot_count = 4  # For displaying accurate total members count. TODO: Make count dynamic
cycling_status_list = 2  # Used for the cycle_status_function
invites = []  # List of all invites to server.

# Put all cogs into this list for autocorrect purposes: (Will soon be deprecated with slash / cogs)
command_list = ["!stat", "!stats", "!help", '!reload', '!load', '!unload']  # TODO: / Create slash cogs /

# We use this so our program knows that it has just been started and will not update channel names instantly. (This
# helps prevent getting blocked by Discord's servers when I restart the bot three times in a row.)
is_startup_routine = True

###########################################
#                                         #
#     User Database global variables      #
#                                         #
###########################################
user_db_path = str(global_configuration_dict['general_info']['user_db_path']) + '.json'
###########################################
#        Put User Data into memory!       #
###########################################
users_dict_of_dict, users_list_of_dict, time_taken = read_users_data_into_mem(user_db_path)  # Read user data


# This is called in other .py files to get the latest user db
def share_users_dict_of_dict_elsewhere():
    return users_dict_of_dict


# This function is called from other scripts which updates the global user database
def import_users_dict_of_dict_db(db):
    global users_dict_of_dict
    users_dict_of_dict = db
    write_user_data(users_dict_of_dict, user_db_path)  # Update the JSON file right away for testing...


##########################################
# Setup code for bot command and intents #
##########################################

########################
#       Cogs           #
########################
for filename in os.listdir('cogs'):
    if filename.endswith('.py'):
        print('Loading cog: ' + str(filename))
        client.load_extension(f'cogs.{filename[:-3]}')

#############################
#  JW.org RSS Feed Variable #
#############################
news_title_list = []  # Stores a list of each news article from RSS feed
NewsFeed = feedparser.parse("https://www.jw.org/en/news/jw/rss/NewsSubsectionRSSFeed/feed.xml")
for i in NewsFeed.entries:
    # Here we are appending each of the news articles into a list. We do this so we have a reference to compare against
    # when looking for new articles!
    news_title_list.append(i.title)  # Append article to list...

###################################################################
#                    Bot conversation variables                   #
#   Used to store variables when Admins are interacting with Bot  #
#     This will soon be deprecated and replaced with a GUI        #
###################################################################
awaiting_admins_suggestion_reason = False
message_ref_remind_admin_for_suggestions_reason = ""
awaiting_admins_name_for_suggestion_reason = ""
vote_message_embed = ""
suggestion_state = ""

########################################################################################################################
#                                                                                                                      #
#                                                                                                                      #
#                                       Read variables from configuration file                                         #
#                                                                                                                      #
#                                                                                                                      #
########################################################################################################################
###############################
#    General Configuration    #
###############################
server_id = global_configuration_dict['general_info']['guild_id']  # Unique guild ID of the Discord Server.
rules_yml_location = global_configuration_dict['general_info']['rules_message_path']

#############################
#     Discord Role ID's     #
#############################
# general_roles #
general_roles_id_dict = global_configuration_dict['discord_role_ids']['general_roles']  # Get to the root!
admin_role_id = general_roles_id_dict['admin']
mc_linked_role_id = general_roles_id_dict['mc_linked']
skynet_lab_role_id = general_roles_id_dict['skynet_lab']
developers_role_id = general_roles_id_dict['developer']
donor_role_id = general_roles_id_dict['donor']
builders_role_id = general_roles_id_dict['builders']
member_role_id = general_roles_id_dict['member']

# subscription_roles #
subscription_roles_id_dict = global_configuration_dict['discord_role_ids']['subscription_roles']  # Get to the root!
mc_server_updates_sub_role_id = subscription_roles_id_dict['mc_server_updates_sub']
wt_study_sub_role_id = subscription_roles_id_dict['wt_study_sub']
bedwars_notifications_role_id = subscription_roles_id_dict['bedwars_notifications_sub']
mobarena_notifications_role_id = subscription_roles_id_dict['mobarena_notifications_sub']
turfwars_notifications_role_id = subscription_roles_id_dict['mc_server_updates_sub']
mc_give_away_sub_role_id = subscription_roles_id_dict['mc_giveaway_sub']
jw_news_sub_id = subscription_roles_id_dict['jw_news_sub']

# misc_role_ids #
misc_roles_id_dict = global_configuration_dict['discord_role_ids']['misc_role_ids']  # Get to the root!
other_roles_banner_role_id = misc_roles_id_dict['other_roles_banner']
subscriptions_banner_role_id = misc_roles_id_dict['subscription_banner']
mysql_role_id = misc_roles_id_dict['mysql_role']
javascript_role_id = misc_roles_id_dict['javascript_role']
java_role_id = misc_roles_id_dict['java_role']
python_role_id = misc_roles_id_dict['python_role']
cplusplus_role_id = misc_roles_id_dict['cplusplus_role']

####################################
#  Read Rules from YML into list   #
####################################
rules_msg_list = read_rules_into_mem(rules_yml_location)  # Read rules from yml file into a list

########################################################
#                                                      #
#      Discord Self Assign Role Embed Message ID's     #
#          These are used so the bot can monitor       #
#                the role assign embeds                #
#                                                      #
########################################################
rr_embed_id_dict = global_configuration_dict['role_assign_message_embed_ids']  # Get to the root!
skynet_lab_role_assign_msg_id = str(rr_embed_id_dict['skynet_lab_role_assign_msg_id'])
wt_not_role_assign_msg_id = str(rr_embed_id_dict['wt_not_role_assign_msg_id'])
mc_updates_role_assign_msg_id = str(rr_embed_id_dict['mc_updates_role_assign_msg_id'])
programmer_role_assign_msg_id = str(rr_embed_id_dict['programmer_role_assign_msg_id'])
jw_news_role_assign_id = str(rr_embed_id_dict['jw_news_role_assign_id'])

########################################################################################################################
#                                                                                                                      #
#                                        Discord Server Channel ID information                                         #
#                                                                                                                      #
########################################################################################################################
###############################
#      General Channels       #
###############################
general_channel_id_dict = global_configuration_dict['discord_channel_ids']['general_channels']  # Get to the root!
bot_channel_id = general_channel_id_dict['bot_channel_id']
announcements_channel_id = general_channel_id_dict['announcements_channel_id']
memes_channel_id = general_channel_id_dict['memes_channel_id']
bugs_and_suggestions_channel_id = general_channel_id_dict['bugs_and_suggestions_channel_id']
general_channel_id = general_channel_id_dict['general_channel_id']
member_log_channel_id = general_channel_id_dict['member_log_channel_id']
mc_server_updates_channel_id = general_channel_id_dict['mc_server_updates_channel_id']
voting_channel_id = general_channel_id_dict['voting_channel_id']
rules_channel_id = general_channel_id_dict['rules_channel_id']
dev_progress_channel_id = general_channel_id_dict['dev_progress_channel_id']
theocratic_channel_id = general_channel_id_dict['theocratic_channel_id']
donation_info_channel_id = general_channel_id_dict['donation_info_channel_id']
#############################
#      Misc Channel ID's    #
#############################
misc_channel_id_dict = global_configuration_dict['discord_channel_ids']['misc_channel_ids']  # Get to the root!
online_members_vc_channel_id = misc_channel_id_dict['online_members_vc_channel_id']
role_assign_channel_id = misc_channel_id_dict['role_assign_channel_id']
##############################################
#          Bungee Console Channel ID's       #
##############################################
bungee_console_channel_id_dict = global_configuration_dict['discord_channel_ids'][
    'bungee_network_console_channel_ids']  # Get to the root!
sky_block_console_channel_id = bungee_console_channel_id_dict['sky_block_console_channel_id']
creative_console_channel_id = bungee_console_channel_id_dict['creative_console_channel_id']
survival_console_channel_id = bungee_console_channel_id_dict['survival_console_channel_id']
minigames_console_channel_id = bungee_console_channel_id_dict['minigames_console_channel_id']
lobby_console_channel_id = bungee_console_channel_id_dict['lobby_console_channel_id']
##############################################
#           Administration Channel ID's      #
##############################################
administration_channel_id_dict = global_configuration_dict['discord_channel_ids'][
    'admin_channel_ids']  # Get to the root!
all_message_log_channel_id = administration_channel_id_dict['all_message_log_channel_id']
to_do_list_channel_id = administration_channel_id_dict['to_do_list_channel_id']
admin_member_join_logger_channel_id = administration_channel_id_dict['admin_member_join_logger_channel_id']
discord_timing_channel_id = administration_channel_id_dict['discord_timing_channel_id']
mod_log_channel_id = administration_channel_id_dict['mod_log']
dm_log_channel_id = administration_channel_id_dict['dm_log']


######################################################
#                                                    #
#   ON_READY function runs when bot is connected!    #
#                                                    #
######################################################
@client.event
async def on_ready():
    global mc_linked_role
    global admin_role
    global general_channel
    global mc_give_away_sub_role
    global invites
    global guild
    global bot_channel
    global mc_server_updates_channel_id
    global mc_server_updates_channel
    global bugs_and_suggestions_channel
    global role_assign_channel
    global announcements_channel
    global role_assign_channel_id
    global discord_timing_channel
    global member_log_channel
    global announcements_channel
    global skynet_lab_role
    global to_do_list_channel
    global dm_log_channel
    global all_message_log_channel
    global online_members_vc_channel
    global sky_block_console_channel
    global lobby_console_channel
    global minigames_console_channel
    global survival_console_channel
    global creative_console_channel
    global voting_channel
    global dev_progress_channel
    global admin_member_join_logger_channel
    global subscriptions_banner_role
    global rules_channel
    global wt_study_sub_role
    global theocratic_channel
    global mc_server_updates_sub_role
    global bedwars_notifications_role
    global mobarena_notifications_role
    global turfwars_notifications_role
    global other_roles_banner_role
    global mysql_role
    global memes_channel
    global javascript_role
    global java_role
    global python_role
    global cplusplus_role
    global donor_role
    global donation_info_channel
    global builders_role
    global developers_role
    global jw_news_sub
    print("Bot Connected to Server, now running on_ready()")  # TODO: Make this display how long it took to load up!
    guild = client.get_guild(server_id)
    ###########################################
    #  Put Discord Server Invites into JSON!  #
    ###########################################
    invites = await guild.invites()

    # Create list of dict of simplified invites containing invite code and uses
    simplified_invites = {}
    invite_dict = {}
    num_of_invitations = 1
    for invite in invites:
        # create temp dict obj
        invite_dict = {'name': str(invite.inviter.name), 'code': str(invite.code), 'uses': str(invite.uses)}

        # append the dict into a list
        simplified_invites[str(invite.code)] = invite_dict

    with open(str(global_configuration_dict['general_info']['invites_db_path']), 'w') as file:
        yaml.dump(simplified_invites, file)

    ###########################################
    #  Put Discord Server Roles into memory!  #
    ###########################################
    admin_role = get(guild.roles, id=admin_role_id)
    mc_linked_role = get(guild.roles, id=mc_linked_role_id)
    skynet_lab_role = get(guild.roles, id=skynet_lab_role_id)
    developers_role = get(guild.roles, id=developers_role_id)
    donor_role = get(guild.roles, id=donor_role_id)
    builders_role = get(guild.roles, id=builders_role_id)

    # Subscriptions:
    wt_study_sub_role = get(guild.roles, id=wt_study_sub_role_id)
    subscriptions_banner_role = get(guild.roles, id=subscriptions_banner_role_id)
    mc_give_away_sub_role = get(guild.roles, id=mc_give_away_sub_role_id)
    mc_server_updates_sub_role = get(guild.roles, id=mc_server_updates_sub_role_id)
    bedwars_notifications_role = get(guild.roles, id=bedwars_notifications_role_id)
    mobarena_notifications_role = get(guild.roles, id=mobarena_notifications_role_id)
    turfwars_notifications_role = get(guild.roles, id=turfwars_notifications_role_id)
    other_roles_banner_role = get(guild.roles, id=other_roles_banner_role_id)
    mysql_role = get(guild.roles, id=mysql_role_id)
    javascript_role = get(guild.roles, id=javascript_role_id)
    java_role = get(guild.roles, id=java_role_id)
    python_role = get(guild.roles, id=python_role_id)
    cplusplus_role = get(guild.roles, id=cplusplus_role_id)
    jw_news_sub = get(guild.roles, id=jw_news_sub_id)

    # Channel Deceleration #
    bot_channel = client.get_channel(bot_channel_id)  # Channel for bot-spam
    announcements_channel = client.get_channel(announcements_channel_id)
    general_channel = client.get_channel(general_channel_id)
    member_log_channel = client.get_channel(member_log_channel_id)
    all_message_log_channel = client.get_channel(all_message_log_channel_id)
    memes_channel = client.get_channel(memes_channel_id)
    role_assign_channel = client.get_channel(role_assign_channel_id)
    mc_server_updates_channel = client.get_channel(mc_server_updates_channel_id)
    bugs_and_suggestions_channel = client.get_channel(bugs_and_suggestions_channel_id)
    voting_channel = client.get_channel(voting_channel_id)
    to_do_list_channel = client.get_channel(to_do_list_channel_id)
    sky_block_console_channel = client.get_channel(sky_block_console_channel_id)
    lobby_console_channel = client.get_channel(lobby_console_channel_id)
    minigames_console_channel = client.get_channel(minigames_console_channel_id)
    survival_console_channel = client.get_channel(survival_console_channel_id)
    creative_console_channel = client.get_channel(creative_console_channel_id)
    rules_channel = client.get_channel(rules_channel_id)
    admin_member_join_logger_channel = client.get_channel(admin_member_join_logger_channel_id)
    discord_timing_channel = client.get_channel(discord_timing_channel_id)
    dm_log_channel = client.get_channel(dm_log_channel_id)
    dev_progress_channel = client.get_channel(dev_progress_channel_id)
    online_members_vc_channel = client.get_channel(online_members_vc_channel_id)
    theocratic_channel = client.get_channel(theocratic_channel_id)
    donation_info_channel = client.get_channel(donation_info_channel_id)

    # send a restart notification embed:
    await send_restart_notification()

    # Begin cycle operations below:
    cycle_bot_status.start()  # Change status of bot:
    check_jw_rss_feed.start()  # Checks if there is anything new on JW.org
    write_user_data_loop.start()  # Regularly writes user data back onto hard disk
    backup_user_data_loop.start()  # Regularly writes a seperate user db as a backup onto HDD


#########################################################
#                                                       #
#            On reaction add event function.            #
#  This function runs when someone reacts to a message  #
#########################################################
@client.event
async def on_reaction_add(reaction, user):
    global awaiting_admins_suggestion_reason
    global awaiting_admins_name_for_suggestion_reason
    global message_ref_remind_admin_for_suggestions_reason
    global admin_role
    global suggestion_state
    global to_do_list_channel
    global vote_message_embed
    if user.bot:
        # ignore reactions from bots
        return
    # Reacted message channel and content info:
    reacted_channel = reaction.message.channel
    reacted_message = reaction.message.content
    # Reacted message info:
    reacted_message_embeds = reaction.message.embeds
    reacted_message_id = reaction.message.id
    if str(reacted_message_embeds[0].title) == "Confirm Suggestion?":
        print(str(user.nick) + " Reacted to Suggestion Confirmation from " + str(reacted_message_embeds[0].author.name))
        if str(user.nick) == str(reacted_message_embeds[0].author.name):
            print("Original author...")
            # Send suggestion to voting channel...
            if reaction.emoji == "✖":
                await reaction.message.delete()
                return
            else:
                # send to voting channel with priority attached:
                if reaction.emoji == "✖":
                    await reaction.message.delete()
                elif reaction.emoji == "🟢":
                    priority = "Low"
                    await reaction.message.delete()
                elif reaction.emoji == "🟠":
                    priority = "Medium"
                    await reaction.message.delete()
                elif reaction.emoji == "🔴":
                    priority = "High"
                    await reaction.message.delete()
                else:
                    # unknown emoji, remove it...
                    await reaction.remove(user)
                    return
                embed_dict = reaction.message.embeds[0].to_dict()
                suggestion_message = str(embed_dict['fields'][1]['value'])
                voting_embed = discord.Embed(
                    title="Voting Poll",
                    description="",
                    color=discord.Colour.orange()
                )
                voting_embed.set_footer(text="React with 👍 or 👎")
                voting_embed.set_thumbnail(
                    url="https://i.imgur.com/VTQvbGc.png")  # https://i.imgur.com/Iw4o4JF.png"
                voting_embed.set_author(name=str(user.nick) + "'s Suggestion",
                                        icon_url=user.display_avatar.url)
                voting_embed.add_field(name="** **",
                                       value=str(reaction.emoji) + " " + str(priority) + " Priority",
                                       inline=False)
                voting_embed.add_field(name="Suggestion:", value=suggestion_message,
                                       inline=False)
                await reaction.message.channel.send(
                    "Suggestion added in {0.mention}! Thank you.".format(voting_channel))
                voting_embed_ref = await voting_channel.send(embed=voting_embed)
                await voting_embed_ref.add_reaction(emoji="👍")
                await voting_embed_ref.add_reaction(emoji="👎")
                await voting_embed_ref.add_reaction(emoji="✅")
                await voting_embed_ref.add_reaction(emoji="✖")
        else:
            print("No permission")
            await reaction.message.remove_reaction(reaction, user)

    elif str(reacted_message_embeds[0].title) == "Voting Poll":
        if str(reaction.emoji) == "✖":
            members_roles = user.roles
            # print(str(roles))
            if admin_role in members_roles:
                print("Suffecient perms!")
                vote_message_embed = reaction.message
                message_ref_remind_admin_for_suggestions_reason = await reaction.message.channel.send(f"{user.mention} "
                                                                                                      f"Please type a reason for removing this suggestion / bug report")
                awaiting_admins_suggestion_reason = True
                awaiting_admins_name_for_suggestion_reason = user
                suggestion_state = "declined"

            else:
                await reaction.message.remove_reaction(reaction, user)
        elif str(reaction.emoji) == "✅":
            members_roles = user.roles
            if admin_role in members_roles:
                print("Suffecient perms!")
                vote_message_embed = reaction.message
                message_ref_remind_admin_for_suggestions_reason = await reaction.message.channel.send(
                    f"{user.mention} Please type a reason for approving this suggestion / bug report")
                awaiting_admins_suggestion_reason = True
                awaiting_admins_name_for_suggestion_reason = user
                suggestion_state = "approved"

            else:
                await reaction.message.remove_reaction(reaction, user)

    elif str(reacted_message_embeds[0].title) == "Your Stats!":
        # Need to check to make sure reacted user is the user that sent !stat because we need cool downs!
        if str(reaction.emoji) == "🎮":
            is_mc_linked, mc_uuid = check_if_user_is_mc_linked(user)
            if is_mc_linked:
                await reaction.message.channel.send(embed=get_mc_stats_embed(mc_uuid, user))
    elif str(reacted_message_embeds[0].title) == "Need Help?":
        if str(reaction.emoji) == "👍":
            print("THEY WANT HELP")
            await reaction.message.channel.send(embed=generate_help_menu())
        elif str(reaction.emoji) == "👎":
            print("DELETING HELP")
            await reaction.message.delete()

    else:
        print("IGNORING REACTION")


#####################################################################
#                                                                   #
#              On RAW reaction remove event function.               #
#  This function runs when someone removes a reaction to a message  #
#                                                                   #
#####################################################################
@client.event
async def on_raw_reaction_remove(payload):
    """Removes a role based on a reaction emoji."""
    # Make sure that the message the user is reacting to is the one we care about
    emoji_temp = payload.emoji
    reacted_channel_id = payload.channel_id
    reacted_channel_obj = client.get_channel(reacted_channel_id)
    member_temp = get(guild.members, id=payload.user_id)
    message_id_temp = str(payload.message_id)
    message_object = await reacted_channel_obj.fetch_message(payload.message_id)
    reaction = get(message_object.reactions, emoji=payload.emoji.name)

    try:
        print(reaction.custom_emoji)
    except:
        # This must be a custom emoji
        reaction = get(message_object.reactions, emoji=payload.emoji)

    if reacted_channel_id == role_assign_channel_id:
        print(member_temp.name + " has reacted to a role assign embed!")
        members_roles = member_temp.roles
        if message_id_temp == skynet_lab_role_assign_msg_id:
            print("User reacted to a LAB embed")
            print("EMOJI = " + str(emoji_temp))
            if str(emoji_temp) != "🧪":
                print("WRONG EMOJI")
                print("EMOJI: " + str(emoji_temp))
                print(str(type(emoji_temp)))
                if reaction.custom_emoji:
                    print("This is a custom emoji from SkyNet!")
                else:
                    print("This is not a custom Emoji")

                await message_object.remove_reaction(reaction, member_temp)
                return
            print("User Removed LAB role!!")

            if skynet_lab_role in members_roles:
                print("User already has LAB role")
                await bot_channel.send(("We have removed your LAB role {0.mention}!!".format(member_temp)))
                await member_temp.remove_roles(skynet_lab_role)

            else:
                print("They already didnt have the LAB role!")
                await bot_channel.send(
                    ("You did not have the LAB role in the first place?? {0.mention}".format(member_temp)))

        elif message_id_temp == wt_not_role_assign_msg_id:
            print("USER REMOVED WT ROLE")
            if str(emoji_temp) != "📖":
                print("WRONG EMOJI")
                print("EMOJI: " + str(emoji_temp))
                print(str(type(emoji_temp)))
                if reaction.custom_emoji:
                    print("This is a custom emoji from SkyNet!")
                else:
                    print("This is not a custom Emoji")

                await message_object.remove_reaction(reaction, member_temp)
                return
            print("User Removed WT role!!")
            members_roles = member_temp.roles
            if wt_study_sub_role in members_roles:
                print("User already has WT role")
                await bot_channel.send(
                    ("We have removed your Watchtower Notifications role {0.mention}!!".format(member_temp)))
                await member_temp.remove_roles(wt_study_sub_role)

            else:
                print("They already didnt have the LAB role!")
                await bot_channel.send(
                    ("You did not have the Watchtower Notifications role in the first place?? {0.mention}".format(
                        member_temp)))

        elif message_id_temp == jw_news_role_assign_id:
            print("USER REMOVED JW NEWS ROLE")
            if str(emoji_temp) != "📚":
                print("WRONG EMOJI")
                print("EMOJI: " + str(emoji_temp))
                print(str(type(emoji_temp)))
                if reaction.custom_emoji:
                    print("This is a custom emoji from SkyNet!")
                else:
                    print("This is not a custom Emoji")

                await message_object.remove_reaction(reaction, member_temp)
                return
            print("User Removed JW NEWS role!!")
            members_roles = member_temp.roles
            if jw_news_sub in members_roles:
                print("User already has JW NEWS role")
                await bot_channel.send(
                    ("We have removed your JW News Notifications role {0.mention}!!".format(member_temp)))
                await member_temp.remove_roles(jw_news_sub)

            else:
                print("They already didnt have the JW News role!")
                await bot_channel.send(
                    ("You did not have the JW News Notifications role in the first place?? {0.mention}".format(
                        member_temp)))

        elif message_id_temp == mc_updates_role_assign_msg_id:
            print("User Removed MC updates role!!")
            # Get emojis into memory
            bw_emoji = get(client.emojis, name='bedwars')
            tw_emoji = get(client.emojis, name='grass')
            ma_emoji = get(client.emojis, name='creeper')
            if str(emoji_temp) == "🕹":
                print("🕹 EMOJI")
                print("EMOJI: " + str(emoji_temp))
                print(str(type(emoji_temp)))
                if reaction.custom_emoji:
                    print("This is a custom emoji from SkyNet!")
                else:
                    print("This is not a custom Emoji")

                print("User Removed MC Updates role!!")
                members_roles = member_temp.roles
                if mc_server_updates_sub_role in members_roles:
                    print("User already has MC Updates role")
                    await bot_channel.send(
                        ("We have removed your MC Updates Notifications role {0.mention}!!".format(member_temp)))
                    await member_temp.remove_roles(mc_server_updates_sub_role)

                else:
                    print("They already didnt have the MC Updates role!")
                    await bot_channel.send(
                        ("You did not have the MC Updates Notifications role in the first place?? {0.mention}".format(
                            member_temp)))
            elif emoji_temp == bw_emoji:
                print("BW EMOJI")
                print("EMOJI: " + str(emoji_temp))
                print(str(type(emoji_temp)))
                if reaction.custom_emoji:
                    print("This is a custom emoji from SkyNet!")
                else:
                    print("This is not a custom Emoji")

                print("User Removed MC BW role!!")
                members_roles = member_temp.roles
                if bedwars_notifications_role in members_roles:
                    print("User already has bedwars_notifications_role role")
                    await bot_channel.send(
                        ("We have removed your BedWars Games Notifications role {0.mention}!!".format(member_temp)))
                    await member_temp.remove_roles(bedwars_notifications_role)

                else:
                    print("They already didnt have the bedwars_notifications_role role!")
                    await bot_channel.send(
                        (
                            "You did not have the BedWars Games Notifications role in the first place?? {0.mention}".format(
                                member_temp)))
            elif emoji_temp == tw_emoji:
                print("TW EMOJI")
                print("EMOJI: " + str(emoji_temp))
                print(str(type(emoji_temp)))
                if reaction.custom_emoji:
                    print("This is a custom emoji from SkyNet!")
                else:
                    print("This is not a custom Emoji")

                print("User Removed MC TW role!!")
                members_roles = member_temp.roles
                if turfwars_notifications_role in members_roles:
                    print("User already has turfwars_notifications_role role")
                    await bot_channel.send(
                        ("We have removed your TurfWars Games Notifications role {0.mention}!!".format(member_temp)))
                    await member_temp.remove_roles(turfwars_notifications_role)

                else:
                    print("They already didnt have the turfwars_notifications_role role!")
                    await bot_channel.send(
                        (
                            "You did not have the TurfWars Games Notifications role in the first place?? {0.mention}".format(
                                member_temp)))
            elif emoji_temp == ma_emoji:
                print("MA EMOJI")
                print("EMOJI: " + str(emoji_temp))
                print(str(type(emoji_temp)))
                if reaction.custom_emoji:
                    print("This is a custom emoji from SkyNet!")
                else:
                    print("This is not a custom Emoji")

                print("User Removed MC MA role!!")
                members_roles = member_temp.roles
                if mobarena_notifications_role in members_roles:
                    print("User already has mobarena_notifications_role role")
                    await bot_channel.send(
                        ("We have removed your MobArena Games Notifications role {0.mention}!!".format(member_temp)))
                    await member_temp.remove_roles(mobarena_notifications_role)

                else:
                    print("They already didnt have the mobarena_notifications_role role!")
                    await bot_channel.send(
                        (
                            "You did not have the MobArena Games Notifications role in the first place?? {0.mention}".format(
                                member_temp)))

        elif message_id_temp == programmer_role_assign_msg_id:
            print("User Removed Programmer role!!")
            cplusplus_emoji = get(client.emojis, name='cplusplus')
            my_sql_emoji = get(client.emojis, name='mysql')
            python_emoji = get(client.emojis, name='python')
            javascript_emoji = get(client.emojis, name='javascript')
            java_emoji = get(client.emojis, name='java')
            if emoji_temp == cplusplus_emoji:
                print("cplusplus_emoji EMOJI")
                print("EMOJI: " + str(emoji_temp))
                print(str(type(emoji_temp)))
                if reaction.custom_emoji:
                    print("This is a custom emoji from SkyNet!")
                else:
                    print("This is not a custom Emoji")

                print("User Removed cplusplus_emoji role!!")
                members_roles = member_temp.roles
                if cplusplus_role in members_roles:
                    print("User has cplusplus_emoji role")
                    await bot_channel.send(
                        ("We have removed your C++ role {0.mention}!!".format(member_temp)))
                    await member_temp.remove_roles(cplusplus_role)

                else:
                    print("They already didnt have the cplusplus_emoji role!")
                    await bot_channel.send(
                        ("You did not have the C++ role in the first place?? {0.mention}".format(
                            member_temp)))
            elif emoji_temp == my_sql_emoji:
                print("my_sql_emoji EMOJI")
                print("EMOJI: " + str(emoji_temp))
                print(str(type(emoji_temp)))
                if reaction.custom_emoji:
                    print("This is a custom emoji from SkyNet!")
                else:
                    print("This is not a custom Emoji")

                print("User Removed my_sql_emoji role!!")
                members_roles = member_temp.roles
                if mysql_role in members_roles:
                    print("User has mysql_role role")
                    await bot_channel.send(
                        ("We have removed your MySQL role {0.mention}!!".format(member_temp)))
                    await member_temp.remove_roles(mysql_role)

                else:
                    print("They already didnt have the mysql_role role!")
                    await bot_channel.send(
                        ("You did not have the MySQL role in the first place?? {0.mention}".format(
                            member_temp)))
            elif emoji_temp == python_emoji:
                print("python_emoji EMOJI")
                print("EMOJI: " + str(emoji_temp))
                print(str(type(emoji_temp)))
                if reaction.custom_emoji:
                    print("This is a custom emoji from SkyNet!")
                else:
                    print("This is not a custom Emoji")

                print("User Removed python_emoji role!!")
                members_roles = member_temp.roles
                if python_role in members_roles:
                    print("User has python_role role")
                    await bot_channel.send(
                        ("We have removed your Python role {0.mention}!!".format(member_temp)))
                    await member_temp.remove_roles(python_role)

                else:
                    print("They already didnt have the python_role role!")
                    await bot_channel.send(
                        ("You did not have the Python role in the first place?? {0.mention}".format(
                            member_temp)))
            elif emoji_temp == javascript_emoji:
                print("javascript_emoji EMOJI")
                print("EMOJI: " + str(emoji_temp))
                print(str(type(emoji_temp)))
                if reaction.custom_emoji:
                    print("This is a custom emoji from SkyNet!")
                else:
                    print("This is not a custom Emoji")

                print("User Removed javascript_emoji role!!")
                members_roles = member_temp.roles
                if javascript_role in members_roles:
                    print("User has javascript_role role")
                    await bot_channel.send(
                        ("We have removed your JavaScript role {0.mention}!!".format(member_temp)))
                    await member_temp.remove_roles(javascript_role)

                else:
                    print("They already didnt have the mysql_role role!")
                    await bot_channel.send(
                        ("You did not have the JavaScript role in the first place?? {0.mention}".format(
                            member_temp)))
            elif emoji_temp == java_emoji:
                print("java_emoji EMOJI")
                print("EMOJI: " + str(emoji_temp))
                print(str(type(emoji_temp)))
                if reaction.custom_emoji:
                    print("This is a custom emoji from SkyNet!")
                else:
                    print("This is not a custom Emoji")

                print("User Removed java_emoji role!!")
                members_roles = member_temp.roles
                if java_role in members_roles:
                    print("User has java_role role")
                    await bot_channel.send(
                        ("We have removed your Java role {0.mention}!!".format(member_temp)))
                    await member_temp.remove_roles(java_role)

                else:
                    print("They already didnt have the java_role role!")
                    await bot_channel.send(
                        ("You did not have the Java role in the first place?? {0.mention}".format(
                            member_temp)))

        elif message_id_temp == "795095361198096384":
            print("User Removed TBA role!!")
        else:
            print("Unkown role message id??")
            print("Msg ID: " + message_id_temp)


########################################################################
#                                                                      #
#                 On RAW reaction add event function.                  #
#  This function runs when someone adds a (RAW) reaction to a message  #
#                                                                      #
########################################################################
@client.event
async def on_raw_reaction_add(payload):
    """Adds a role based on a reaction emoji."""
    # Make sure that the message the user is reacting to is the one we care about
    emoji_temp = payload.emoji
    reacted_channel_id = payload.channel_id
    reacted_channel_obj = client.get_channel(reacted_channel_id)
    member_temp = payload.member
    message_id_temp = str(payload.message_id)
    message_object = await reacted_channel_obj.fetch_message(payload.message_id)
    reaction = get(message_object.reactions, emoji=payload.emoji.name)

    if member_temp.bot:
        # reactions added by bot are ignored
        return

    try:
        print(reaction.custom_emoji)
    except:
        reaction = get(message_object.reactions, emoji=payload.emoji)
        print("WAS not CUSTOM, EMOJI IS: " + str(reaction))

    if reacted_channel_id == role_assign_channel_id:
        print(member_temp.name + " has reacted to a role assign embed!")
        members_roles = member_temp.roles
        if subscriptions_banner_role in members_roles:
            print("User has banner role, pass")
        else:
            print("Adding banner role...")
            await member_temp.add_roles(subscriptions_banner_role)
        if other_roles_banner_role not in members_roles:
            print("Adding other roles banner:")
            await member_temp.add_roles(other_roles_banner_role)
        if message_id_temp == skynet_lab_role_assign_msg_id:
            if str(emoji_temp) != "🧪":
                print("WRONG EMOJI")
                print("EMOJI: " + str(emoji_temp))
                print(str(type(emoji_temp)))
                if reaction.custom_emoji:
                    print("This is a custom emoji from SkyNet!")
                else:
                    print("This is not a custom Emoji")

                await message_object.remove_reaction(reaction, member_temp)
                return
            print("User Added LAB role!!")
            members_roles = member_temp.roles
            if skynet_lab_role in members_roles:
                print("User already has LAB role")
                await bot_channel.send(("You already have the LAB role {0.mention}!!".format(member_temp)))

            else:
                print("Adding LAB role!")
                await member_temp.add_roles(skynet_lab_role)
                await bot_channel.send((
                    "Good job {0.mention}, you now have the SkyNet LAB Role giving you access to cool channels like {1.mention}".format(
                        member_temp, dev_progress_channel)))

        elif message_id_temp == wt_not_role_assign_msg_id:
            print("User Added WT Study role!!")
            if str(emoji_temp) != "📖":
                print("WRONG EMOJI")
                print("EMOJI: " + str(emoji_temp))
                print(str(type(emoji_temp)))
                if reaction.custom_emoji:
                    print("This is a custom emoji from SkyNet!")
                else:
                    print("This is not a custom Emoji")

                await message_object.remove_reaction(reaction, member_temp)
                return
            print("User Added WT role!!")
            members_roles = member_temp.roles
            if wt_study_sub_role in members_roles:
                print("User already has WT role")
                await bot_channel.send(
                    ("You already have the Watchtower Study Notifications role {0.mention}!!".format(member_temp)))

            else:
                print("Adding WT role!")
                await member_temp.add_roles(wt_study_sub_role)
                await bot_channel.send((
                    "Good job {0.mention}, you now have the Watchtower Study Notifications Role, you will now be automatically notified about Watchtower Study groups".format(
                        member_temp)))

        elif message_id_temp == jw_news_role_assign_id:
            print("User Added JW News role!!")
            if str(emoji_temp) != "📚":
                print("WRONG EMOJI")
                print("EMOJI: " + str(emoji_temp))
                print(str(type(emoji_temp)))
                if reaction.custom_emoji:
                    print("This is a custom emoji from SkyNet!")
                else:
                    print("This is not a custom Emoji")

                await message_object.remove_reaction(reaction, member_temp)
                return
            members_roles = member_temp.roles
            if jw_news_sub in members_roles:
                print("User already has JW News role")
                await bot_channel.send(
                    ("You already have the JW News Notifications role {0.mention}!!".format(member_temp)))

            else:
                print("Adding JW News role!")
                await member_temp.add_roles(jw_news_sub)
                await bot_channel.send((
                    "Good job {0.mention}, you now have the JW News Notifications Role, you will now be automatically notified about new items on JW.org".format(
                        member_temp)))

        elif message_id_temp == mc_updates_role_assign_msg_id:
            print("User Added MC updates role!!")
            # Get emojis into memory
            bw_emoji = get(client.emojis, name='bedwars')
            tw_emoji = get(client.emojis, name='grass')
            ma_emoji = get(client.emojis, name='creeper')
            if str(emoji_temp) == "🕹":
                print("🕹 EMOJI")
                print(str(type(emoji_temp)))
                if reaction.custom_emoji:
                    print("This is a custom emoji from SkyNet!")
                else:
                    print("This is not a custom Emoji")

                members_roles = member_temp.roles
                if mc_server_updates_sub_role in members_roles:
                    print("User already has MC Updates role")
                    await bot_channel.send(("You already have the MC Updates role {0.mention}!!".format(member_temp)))

                else:
                    print("Adding MC Updates role!")
                    await member_temp.add_roles(mc_server_updates_sub_role)
                    await bot_channel.send((
                        "Good job {0.mention}, you now have the MC Updates Role, notifications are sent in {1.mention}".format(
                            member_temp, announcements_channel)))
            elif str(emoji_temp) == "🎉":
                print("🎉 EMOJI")
                print(str(type(emoji_temp)))
                if reaction.custom_emoji:
                    print("This is a custom emoji from SkyNet!")
                else:
                    print("This is not a custom Emoji")

            elif emoji_temp == bw_emoji:
                print("BW EMOJI")
                print(str(type(emoji_temp)))
                if reaction.custom_emoji:
                    print("This is a custom emoji from SkyNet!")
                else:
                    print("This is not a custom Emoji")

                members_roles = member_temp.roles
                if bedwars_notifications_role in members_roles:
                    print("User already has bedwars_notifications_role role")
                    await bot_channel.send(
                        ("You already have the BedWars Game Notifications role {0.mention}!!".format(member_temp)))

                else:
                    print("Adding bedwars_notifications_role role!")
                    await member_temp.add_roles(bedwars_notifications_role)
                    await bot_channel.send((
                        "Good job {0.mention}, you now have the BedWars Game Notifications Role, notifications are sent in {1.mention}".format(
                            member_temp, mc_server_updates_channel)))
            elif emoji_temp == tw_emoji:
                print("tw_emoji EMOJI")
                print(str(type(emoji_temp)))
                if reaction.custom_emoji:
                    print("This is a custom emoji from SkyNet!")
                else:
                    print("This is not a custom Emoji")

                members_roles = member_temp.roles
                if turfwars_notifications_role in members_roles:
                    print("User already has turfwars_notifications_role")
                    await bot_channel.send(
                        ("You already have the TurfWars Game Notifications role {0.mention}!!".format(member_temp)))

                else:
                    print("Adding turfwars_notifications_role!")
                    await member_temp.add_roles(turfwars_notifications_role)
                    await bot_channel.send((
                        "Good job {0.mention}, you now have the TurfWars Game Notifications Role, notifications are sent in {1.mention}".format(
                            member_temp, mc_server_updates_channel)))
            elif emoji_temp == ma_emoji:
                print("ma_emoji EMOJI")
                print(str(type(emoji_temp)))
                if reaction.custom_emoji:
                    print("This is a custom emoji from SkyNet!")
                else:
                    print("This is not a custom Emoji")

                members_roles = member_temp.roles
                if mobarena_notifications_role in members_roles:
                    print("User already has mobarena_notifications_role")
                    await bot_channel.send(
                        ("You already have the MobArena Game Notifications role {0.mention}!!".format(member_temp)))

                else:
                    print("Adding mobarena_notifications_role!")
                    await member_temp.add_roles(mobarena_notifications_role)
                    await bot_channel.send((
                        "Good job {0.mention}, you now have the MobArena Game Notifications Role, notifications are sent in {1.mention}".format(
                            member_temp, mc_server_updates_channel)))

        elif message_id_temp == programmer_role_assign_msg_id:
            print("User Added Programmer role!!")
            cplusplus_emoji = get(client.emojis, name='cplusplus')
            my_sql_emoji = get(client.emojis, name='mysql')
            python_emoji = get(client.emojis, name='python')
            javascript_emoji = get(client.emojis, name='javascript')
            java_emoji = get(client.emojis, name='java')

            if emoji_temp == cplusplus_emoji:
                print("cplusplus_emoji EMOJI")
                print("EMOJI: " + str(emoji_temp))
                print(str(type(emoji_temp)))
                if reaction.custom_emoji:
                    print("This is a custom emoji from SkyNet!")
                else:
                    print("This is not a custom Emoji")
                members_roles = member_temp.roles
                if cplusplus_role in members_roles:
                    print("User already has cplusplus_emoji role")
                    await bot_channel.send(("You already have the C++ role {0.mention}!!".format(member_temp)))

                else:
                    print("Adding cplusplus_role role!")
                    await member_temp.add_roles(cplusplus_role)
                    await bot_channel.send((
                        "Good job {0.mention}, you now have the C++ Role".format(
                            member_temp)))
            elif emoji_temp == my_sql_emoji:
                print("my_sql_emoji EMOJI")
                print("EMOJI: " + str(emoji_temp))
                print(str(type(emoji_temp)))
                if reaction.custom_emoji:
                    print("This is a custom emoji from SkyNet!")
                else:
                    print("This is not a custom Emoji")
                members_roles = member_temp.roles
                if mysql_role in members_roles:
                    print("User already has mysql_role role")
                    await bot_channel.send(("You already have the MySQL role {0.mention}!!".format(member_temp)))

                else:
                    print("Adding mysql_role role!")
                    await member_temp.add_roles(mysql_role)
                    await bot_channel.send((
                        "Good job {0.mention}, you now have the MySQL".format(
                            member_temp)))
            elif emoji_temp == python_emoji:
                print("python_emoji EMOJI")
                print("EMOJI: " + str(emoji_temp))
                print(str(type(emoji_temp)))
                if reaction.custom_emoji:
                    print("This is a custom emoji from SkyNet!")
                else:
                    print("This is not a custom Emoji")
                members_roles = member_temp.roles
                if python_role in members_roles:
                    print("User already has python_emoji role")
                    await bot_channel.send(("You already have the Python role {0.mention}!!".format(member_temp)))

                else:
                    print("Adding python_emoji role!")
                    await member_temp.add_roles(python_role)
                    await bot_channel.send((
                        "Good job {0.mention}, you now have the Python Role".format(
                            member_temp)))
            elif emoji_temp == javascript_emoji:
                print("javascript_emoji EMOJI")
                print("EMOJI: " + str(emoji_temp))
                print(str(type(emoji_temp)))
                if reaction.custom_emoji:
                    print("This is a custom emoji from SkyNet!")
                else:
                    print("This is not a custom Emoji")
                members_roles = member_temp.roles
                if javascript_role in members_roles:
                    print("User already has javascript_emoji role")
                    await bot_channel.send(("You already have the JavaScript role {0.mention}!!".format(member_temp)))

                else:
                    print("Adding python_emoji role!")
                    await member_temp.add_roles(javascript_role)
                    await bot_channel.send((
                        "Good job {0.mention}, you now have the JavaScript Role".format(
                            member_temp)))
            elif emoji_temp == java_emoji:
                print("java_emoji EMOJI")
                print("EMOJI: " + str(emoji_temp))
                print(str(type(emoji_temp)))
                if reaction.custom_emoji:
                    print("This is a custom emoji from SkyNet!")
                else:
                    print("This is not a custom Emoji")
                members_roles = member_temp.roles
                if java_role in members_roles:
                    print("User already has java_role role")
                    await bot_channel.send(("You already have the Java role {0.mention}!!".format(member_temp)))

                else:
                    print("Adding java_role role!")
                    await member_temp.add_roles(java_role)
                    await bot_channel.send((
                        "Good job {0.mention}, you now have the Java Role".format(
                            member_temp)))
            else:
                print("Wrong emoji!")
                await message_object.remove_reaction(reaction, member_temp)
                return

        elif message_id_temp == "795095361198096384":
            print("User Added TBA role!!")
        else:
            print("Unkown role message id??")
            print("Msg ID: " + message_id_temp)
    elif reacted_channel_id == admin_member_join_logger_channel_id:
        # first we check if the reaction was on a verification embed or not!

        if reaction.message.embeds:
            # this was indeed a message containing an embed
            reacted_message_embed = reaction.message.embeds[0]
        else:
            # message does not contain a embed, return
            return

        if str(reacted_message_embed.title) != "Verification Needed":
            # reacted message was not a verification embed, return
            return
        # this was indeed a verification message, continue by getting the member object to be verified:
        user_requesting_verification_id = int(reacted_message_embed.footer.text)
        user_requesting_verification = message_object.guild.get_member(user_requesting_verification_id)
        # we need to check if this was a member approve / deny verification reaction from an Admin!
        if not check_roles(member_temp, admin_role_id):
            # reactions was not added by an admin? we need to delete this!
            await reaction.remove(member_temp)
            return
        # check what reaction emoji it was
        emoji_string = str(emoji_temp)
        if emoji_string == '✔':
            # verify the member
            await verify_member(user_requesting_verification, client.get_channel(general_channel_id))
            await reaction.message.delete()

        elif emoji_string == '🟢':
            # in this case we will verify them, and then add all of their original roles if they had them
            roles_id_list = retrieve_members_role_ids(user_requesting_verification, users_dict_of_dict)
            await assign_list_of_roles_to_member(user_requesting_verification, roles_id_list)
            await verify_member(user_requesting_verification, client.get_channel(general_channel_id))
            await reaction.message.delete()
        elif emoji_string == '❌':
            # kick the member from server:
            type_of_pun = 'kick'
            human_called = True
            delete_msg_after = False
            ctx = None
            channel = None
            # perhaps replace this with admin reply at some stage? TODO: Admin replies here
            reason = "Sorry but we decided not to verify you at this time."

            await punishments(member_temp, ctx, client, type_of_pun, user_requesting_verification, reason, human_called,
                              channel, delete_msg_after, member_temp.guild)
            await reaction.message.delete()
        else:
            await reaction.remove(member_temp)


#########################################################
#                                                       #
#           ON MESSAGE EDIT EVENT FUNCTION:             #
#         (need to check for swears here too!)          #
#########################################################
@client.event
async def on_message_edit(before, after):  # TODO: Check for swear words here!!!
    attachments = after.attachments
    if str(before.content) == "" and str(after.content) == "":
        # This means there was no actual EDIT, false alarm
        return
    if before.author.bot:
        # ignore bot messages
        return
    true = True
    await log_message_into_admins(after.content, before.author, before.channel, true, before.content, attachments)


#########################################################
#                                                       #
#              ON MESSAGE EVENT FUNCTION:               #
#                                                       #
#########################################################
@client.event
async def on_message(message):
    global users_dict_of_dict
    global users_list_of_dict

    global awaiting_admins_suggestion_reason
    global awaiting_admins_name_for_suggestion_reason
    # Put this stuff into memory to lower the amount of lookups and str() calls to save CPU power:

    content = str(message.content)
    content_lowered = str(content.lower())
    author_id = message.author.id
    author = message.author
    author_name = message.author.name
    channel_of_message = message.channel

    # Log message into admin logger channel:
    edited_message = False
    content_before = ""
    attachments = message.attachments

    # Check if it's a bot message from Author, TODO: Check if its other bots too....
    if message.author.bot:
        if is_startup_routine:
            return
        if message.channel == dev_progress_channel:
            print("Webhook message was sent into dev_progress_channel, adding reactions.")
            await message.add_reaction(emoji='👍')
            await message.add_reaction(emoji='👎')
        return
    # Check if message was sent in DM:
    elif isinstance(message.channel,
                    discord.abc.PrivateChannel):
        await log_message_into_admins(content, author, channel_of_message, edited_message, content_before, attachments)
        return

    # Process the message, not sure why, possibly for cogs??
    await client.process_commands(message)

    await log_message_into_admins(content, author, channel_of_message, edited_message, content_before, attachments)

    # Check if message was sent into memes channel:
    alright_emoji = get(client.emojis, name='alright')
    if message.channel.id == memes_channel_id:
        if message.attachments or "https://" in message.content or "http://" in message.content:
            await message.add_reaction(emoji='👍')
            await message.add_reaction(emoji=alright_emoji)
            await message.add_reaction(emoji='👎')

    # leveling code below:
    # users_dict_of_dict = update_member_data(author, users_dict_of_dict)  # This is resource heavy but i need to
    number = random.randint(1, 8)  # Generate random XP value...
    await try_to_add_add_experience(author, number)
    await try_to_level_up_member(author, channel_of_message)
    increase_users_total_messages(author)

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
        await send_help(message)
    elif "pls help" in content_lowered:
        await send_help(message)
    elif "help me" in content_lowered:
        await send_help(message)

    if awaiting_admins_suggestion_reason:
        if message.channel == voting_channel:
            awaiting_admins_suggestion_reason = False
            reason = message.content
            await send_suggestion_feedback(reason)
            await message.delete()
            await message_ref_remind_admin_for_suggestions_reason.delete()


#########################################################
#                                                       #
#               ON MEMBER LEAVE FUNCTION:               #
#                                                       #
#########################################################
@client.event
async def on_member_remove(member):
    global invites
    global users_dict_of_dict
    print(str(member) + " Left the Server")
    # Updates the cache when a user leaves to make sure
    # everything is up to date
    invites = await member.guild.invites()
    # Member Leave Embed
    member_leave_embed = discord.Embed(
        title=f'{member.display_name}' + " Left SkyNet",
        description="Oh No! This is so sad, can we hit 10 likes?",
        color=discord.Colour.orange()
    )
    member_leave_embed.set_footer(text="pls rejoin...")
    member_leave_embed.set_thumbnail(url=str(member.display_avatar.url))
    member_leave_embed.set_author(name="SkyNet", icon_url=image_urls['crying_emoji'])
    await member_log_channel.send(embed=member_leave_embed)

    # update_date incase the user join and left immediatly before the bot could build its record, then continue by
    # increasing the amount of times the member has left the server
    users_dict_of_dict = update_member_data(member, users_dict_of_dict)
    users_dict_of_dict[str(member.id)]["left_server"] += 1
    write_user_data(users_dict_of_dict, user_db_path)  # Update the JSON file right away for testing...
    await discord_timing_channel.send("User data has been backed up: " + str(datetime.datetime.now()))


#########################################################
#                                                       #
#             CYCLE FUNCTIONS BELOW HERE:               #
#          (Trying to keep things tidy okay)            #
#                                                       #
#########################################################
@tasks.loop(minutes=2)
async def check_jw_rss_feed():
    global news_title_list
    print("checking JW RSS feed")
    news_feed = feedparser.parse("https://www.jw.org/en/news/jw/rss/NewsSubsectionRSSFeed/feed.xml")

    for article in news_feed.entries:
        if article.title not in news_title_list:
            news_title_list.append(article.title)
            link = str(article.links[0]['href'])
            title = str(article.title)
            await theocratic_channel.send(title + "\n" + link + "\n" + "{0.mention}".format(jw_news_sub))


@tasks.loop(minutes=3)  # This function cycles the bots status automatically!
async def cycle_bot_status():
    global cycling_status_list
    # activity = discord.Game(name="SkyNet MC")
    # await client.change_presence(status=discord.Status.idle, activity=activity)
    if cycling_status_list >= 4:
        cycling_status_list = 0
        await client.change_presence(status=discord.Status.online, activity=discord.Game(name="SkyNet Servers"))
    elif cycling_status_list == 3:
        # Setting `Playing ` status
        await client.change_presence(status=discord.Status.online, activity=discord.Game(name="SkyNet MC"))
        cycling_status_list += 1
    elif cycling_status_list == 2:
        # Setting `Streaming ` status
        await client.change_presence(status=discord.Status.online,
                                     activity=discord.Game(name="SkyNet Survival", url="skynetmc.ddns.me"))
        cycling_status_list += 1
    elif cycling_status_list == 1:
        # Setting `Listening ` status
        await client.change_presence(status=discord.Status.online,
                                     activity=discord.Activity(type=discord.ActivityType.listening,
                                                               name="To Life Metal"))
        cycling_status_list += 1
    elif cycling_status_list == 0:
        # Setting `Watching ` status
        await client.change_presence(status=discord.Status.online,
                                     activity=discord.Activity(type=discord.ActivityType.watching, name="For Hackers"))
        cycling_status_list += 1


@tasks.loop(seconds=90)  # This function updates the online members placeholder voice channel
async def update_online_members_vc_placeholder():
    global is_startup_routine
    if is_startup_routine:  # Changing a channels name on startup may result in api spamming, hence getting blocked ):
        is_startup_routine = False
        return
    member_count_auto = str(sum(not member.bot for member in guild.members))
    online_member_count_auto = str(
        sum(member.status != discord.Status.offline and not member.bot for member in guild.members))
    temp = str("Online: " + online_member_count_auto + "/" + member_count_auto)
    await online_members_vc_channel.edit(name=temp)
    print("finished updating online_members_vc_placeholder channel")


@tasks.loop(minutes=3)  # This function simply writes the current user data from memory into the JSON file as a backup
async def write_user_data_loop():
    write_user_data(users_dict_of_dict, user_db_path)
    await discord_timing_channel.send("⭕ User data has been saved: " + str(datetime.datetime.now()))


@tasks.loop(hours=12)  # This function simply writes the current user data from memory into the JSON file as a backup
async def backup_user_data_loop():
    current_time = get_dashed_time_format()
    current_date = get_pretty_date_format()
    write_user_data(users_dict_of_dict, str(global_configuration_dict['general_info']['user_db_path']) +
                    " backup " + current_date + " " + current_time + '.json')
    await discord_timing_channel.send(
        f"🧾 User data has been backed up: {current_date} {current_time}")


#########################################################
#                                                       #
#            LEVELING FUNCTIONS BELOW HERE:             #
#          (Trying to keep things tidy okay)            #
#                                                       #
#########################################################

# Simple adds a specific amount of XP to the user
async def manual_add_experience(user, exp, channel):
    # Here we need to get the current user database into function:
    user_id = str(user.id)
    users_dict_of_dict[user_id]["experience"] += exp
    await manual_level_up(user, channel)


# Used to check if player can level up or level up MULTIPLE levels, and then it does so and announces it to user.
async def manual_level_up(user, channel):
    user_id = str(user.id)
    user_finished_leveling_up = False

    initial_lvl = users_dict_of_dict[user_id]["level"]  # We will compare against this at break of loop
    while not user_finished_leveling_up:
        experience = users_dict_of_dict[user_id]["experience"]
        level = users_dict_of_dict[user_id]["level"]
        xp_needed = level ** 4
        if experience > xp_needed:
            # user has leveled up, hooray! (don't announce it yet because they may level up even more!)
            users_dict_of_dict[user_id]["level"] += 1
        else:
            user_finished_leveling_up = True
            if int(initial_lvl) < int(users_dict_of_dict[user_id]["level"]):
                await channel.send(
                    f":tada: Congrats {user.mention}, you levelled up from {initial_lvl} to level " + str(
                        users_dict_of_dict[user_id]["level"]))
            else:
                # I'll keep this for now, but if it gets annoying it will be removed...
                await channel.send(
                    f"😢 Sorry {user.mention}, you did not get enough XP to level up! Maybe next time...")

    # DEPRECATED FOR NOW: We don't run this because I moved the function back into main.py
    # VERY IMPORTANT: We need to give the user db back to the main.py, only here for reference
    # update_users_dict_of_dict_from_elsewhere(user_db_dict_of_dict)


async def try_to_add_add_experience(user, exp):  # Test if user is permitted to have XP added to them
    user_id = str(user.id)
    current_time = round(time.time(), 1)
    if current_time - users_dict_of_dict[user_id]["last_message"] > 8:
        # sufficient time has passed since last message, we will now add the XP into user_db
        users_dict_of_dict[user_id]["experience"] += exp
        users_dict_of_dict[user_id]["last_message"] = current_time
    else:
        return


async def try_to_level_up_member(user, channel):  # Used to check if player can level up
    user_id = str(user.id)
    experience = users_dict_of_dict[user_id]["experience"]
    level = users_dict_of_dict[user_id]["level"]
    xp_needed = level ** 4
    if experience > xp_needed:
        # user was able to level up, hooray!
        users_dict_of_dict[user_id]["level"] += 1
        await bot_channel.send(
            f":tada: Congrats {user.mention}, you leveled up to level: " + str(users_dict_of_dict[user_id]["level"]))


def increase_users_total_messages(user):
    user_id = str(user.id)
    users_dict_of_dict[user_id]["total_messages"] += 1


#########################################################
#                                                       #
#            COMMAND FUNCTIONS BELOW HERE:              #
#                                                       #
#########################################################

@client.command()  # Make a suggestion
async def auto_check_all_roles(ctx):
    print("Check all member roles command executing")
    members_roles = ctx.message.author.roles
    if admin_role in members_roles:
        print("Sufficient role!")

        for i in guild.members:
            if subscriptions_banner_role in members_roles:
                members_roles = i.roles
                print("User has banner role, pass")
            else:
                print("Adding banner role...")
                await i.add_roles(subscriptions_banner_role)
    else:
        await ctx.message.channel.send("Oh, so you're am Admin r u??")


@client.command()  # Make a suggestion
async def post_rules(ctx):
    print("Rules command executing")
    members_roles = ctx.message.author.roles
    if admin_role in members_roles:
        print("Sufficient role!")
        await ctx.message.channel.send(rules_msg_list[0])
        await ctx.message.channel.send(rules_msg_list[1])
        await ctx.message.channel.send(rules_msg_list[2])
        await ctx.message.delete()
    else:
        await ctx.message.channel.send("Oh, so you're am Admin r u??")


@client.command(pass_context=True)  # Make a suggestion
async def suggest(ctx, *sugg):
    print("Suggestion command executing")
    global skynet_lab_role
    members_roles = ctx.message.author.roles
    # print(str(roles))
    if skynet_lab_role in members_roles:
        print("Suffecient role!")
        if ctx.channel == bugs_and_suggestions_channel:

            suggestion_temp = str(" ".join(sugg[:]))

            suggestion_confirm_embed = discord.Embed(
                title="Confirm Suggestion?",
                description="",
                color=discord.Colour.orange()
            )
            suggestion_confirm_embed.set_footer(text="React with color to confirm, ✖ to cancel")
            suggestion_confirm_embed.set_thumbnail(
                url="https://i.imgur.com/VTQvbGc.png")  # https://i.imgur.com/Iw4o4JF.png"
            suggestion_confirm_embed.set_author(name=ctx.message.author.nick,
                                                icon_url=ctx.message.author.display_avatar.url)
            suggestion_confirm_embed.add_field(name="** **",
                                               value="🟢 - Low Priority \n 🟠 - Medium Priority \n 🔴 - High Priority",
                                               inline=False)
            suggestion_confirm_embed.add_field(name="Suggestion:", value=suggestion_temp,
                                               inline=False)
            skynetlab_assign_embed_ref = await ctx.send(embed=suggestion_confirm_embed)
            await skynetlab_assign_embed_ref.add_reaction(emoji='🟢')
            await skynetlab_assign_embed_ref.add_reaction(emoji='🟠')
            await skynetlab_assign_embed_ref.add_reaction(emoji='🔴')
            await skynetlab_assign_embed_ref.add_reaction(emoji='✖')

        else:
            await ctx.send("Please use the {0.mention} channel for suggestions!".format(bugs_and_suggestions_channel))
    else:
        await ctx.message.channel.send(
            "You need the **SkyNet LAB** role to do that! You can get it in the {0.mention} Channel".format(
                role_assign_channel))


@client.command()  # Ping command to receive the latency of bot to Discord server
async def ping(ctx):
    ping_ = client.latency
    ping = round(ping_ * 1000)
    await ctx.send(f"my ping is {ping}ms")


@client.command()  # Use this to send the role assignment embeds!
async def send_role_embed_jw_new(ctx):
    global admin_role
    global mc_server_updates_channel
    members_roles = ctx.message.author.roles
    # print(str(roles))
    if admin_role in members_roles:
        print("Sending role assign embed")
        # Get emoji in memory
        skynetlab_assign_embed = discord.Embed(
            title="JW News Notifications",
            description="",
            color=discord.Colour.orange()
        )
        skynetlab_assign_embed.set_footer(text="Subscribe for JW News RSS Feed")
        skynetlab_assign_embed.set_thumbnail(
            url="https://i.imgur.com/pO17eio.png")  # https://i.imgur.com/Iw4o4JF.png"
        skynetlab_assign_embed.set_author(name="Role Assign",
                                          icon_url="https://i.imgur.com/BQLKiEh.png")
        skynetlab_assign_embed.add_field(name="Get automatically pinged with a link to any new items on JW.org!",
                                         value="Notifications sent in {0.mention}".format(theocratic_channel),
                                         inline=False)
        skynetlab_assign_embed_ref = await role_assign_channel.send(embed=skynetlab_assign_embed)
        await skynetlab_assign_embed_ref.add_reaction(emoji='📚')
    else:
        await ctx.message.channel.send("no permision")


@client.command()  # Use this to send the role assignment embeds!
async def send_role_embed(ctx):
    global admin_role
    global mc_server_updates_channel
    members_roles = ctx.message.author.roles
    # print(str(roles))
    if admin_role in members_roles:
        print("Sending role assign embed")
        # Get emoji in memory
        bw_emoji = get(client.emojis, name='bedwars')
        tw_emoji = get(client.emojis, name='grass')
        ma_emoji = get(client.emojis, name='creeper')

        other_roles_embed = discord.Embed(
            title="Other Roles?",
            description="",
            color=discord.Colour.orange()
        )
        other_roles_embed.set_footer(text="Contact an Admin about joining out Staff / Developers team!")
        other_roles_embed.set_thumbnail(
            url="https://i.imgur.com/K92EoLg.png")  # https://i.imgur.com/Iw4o4JF.png"
        other_roles_embed.set_author(name="Role Assign",
                                     icon_url="https://i.imgur.com/BQLKiEh.png")
        other_roles_embed.add_field(name="MC Linked Role Info",
                                    value='{0.mention} This is a really easy role to get, and it comes with heaps of cool features! Join our MC Server and type `/discord link`. Then you will be able to connect your Discord account to our Minecraft Server!'.format(
                                        mc_linked_role),
                                    inline=False)
        other_roles_embed.add_field(name="Donor Role Info",
                                    value="{0.mention} Running the Minecraft Server costs us money, if you want, you can donate to help us keep it running and improving, see {1.mention}".format(
                                        donor_role, donation_info_channel),
                                    inline=False)
        other_roles_embed.add_field(name="Developer Role Info",
                                    value="{0.mention} Help us develop the Minecraft Server by programming plugins in Java and setting up other plugins. If you think you have what it takes to help develop the MC Server or Discord Server Bots (Python) send an application to an Admin!".format(
                                        developers_role),
                                    inline=False)
        other_roles_embed.add_field(name="Builder Role Info",
                                    value="{0.mention} Builders create things such as BedWars Maps, Lobbies, and other Minecraft buildings that we use for our Minecraft Server. If you think you are a capable Builder and would like to contribute, start building things in our Creative Server and contact an Admin and show them what you have done! Also, people with Builder rank have access to a Private Builder Server and special WorldEdit Functions.".format(
                                        builders_role),
                                    inline=False)
        other_roles_embed_ref = await role_assign_channel.send(embed=other_roles_embed)

        skynetlab_assign_embed = discord.Embed(
            title="SkyNet LAB",
            description="",
            color=discord.Colour.orange()
        )
        skynetlab_assign_embed.set_footer(text="Subscribe for SkyNet LAB")
        skynetlab_assign_embed.set_thumbnail(
            url="https://i.imgur.com/EVqByQz.png")  # https://i.imgur.com/Iw4o4JF.png"
        skynetlab_assign_embed.set_author(name="Role Assign",
                                          icon_url="https://i.imgur.com/BQLKiEh.png")
        skynetlab_assign_embed.add_field(name="Gives you access to SkyNet LAB channels!", value="** **", inline=False)
        skynetlab_assign_embed_ref = await role_assign_channel.send(embed=skynetlab_assign_embed)
        await skynetlab_assign_embed_ref.add_reaction(emoji='🧪')

        skynetlab_assign_embed = discord.Embed(
            title="WatchTower Notifications",
            description="",
            color=discord.Colour.orange()
        )
        skynetlab_assign_embed.set_footer(text="Subscribe for WatchTower Notifications")
        skynetlab_assign_embed.set_thumbnail(
            url="https://i.imgur.com/TqlTjMY.png")  # https://i.imgur.com/Iw4o4JF.png"
        skynetlab_assign_embed.set_author(name="Role Assign",
                                          icon_url="https://i.imgur.com/BQLKiEh.png")
        skynetlab_assign_embed.add_field(name="Get pinged every Friday as a reminder for WT Study!", value="** **",
                                         inline=False)
        skynetlab_assign_embed_ref = await role_assign_channel.send(embed=skynetlab_assign_embed)
        await skynetlab_assign_embed_ref.add_reaction(emoji='📖')

        general_mc_updates_msg = '{0.mention}'.format(announcements_channel)
        skynetlab_assign_embed = discord.Embed(
            title="Minecraft Server Notifications",
            description="",
            color=discord.Colour.orange()
        )
        skynetlab_assign_embed.set_footer(text="Subscribe for Minecraft Server Updates")
        skynetlab_assign_embed.set_thumbnail(
            url="https://i.imgur.com/K92EoLg.png")  # https://i.imgur.com/Iw4o4JF.png"
        skynetlab_assign_embed.set_author(name="Role Assign",
                                          icon_url="https://i.imgur.com/BQLKiEh.png")
        skynetlab_assign_embed.add_field(name="🕹 General MC Server Updates in", value=general_mc_updates_msg,
                                         inline=True)
        skynetlab_assign_embed.add_field(name="🎉 MC Giveaways in",
                                         value='{0.mention}'.format(mc_server_updates_channel),
                                         inline=True)
        skynetlab_assign_embed.add_field(name=f"{bw_emoji} BedWars Game Notifications in",
                                         value='{0.mention}'.format(mc_server_updates_channel),
                                         inline=False)
        skynetlab_assign_embed.add_field(name=f"{tw_emoji} TurfWars Game Notifications in",
                                         value='{0.mention}'.format(mc_server_updates_channel),
                                         inline=False)
        skynetlab_assign_embed.add_field(name=f"{ma_emoji} MobArena Game Notifications in",
                                         value='{0.mention}'.format(mc_server_updates_channel),
                                         inline=False)
        skynetlab_assign_embed_ref = await role_assign_channel.send(embed=skynetlab_assign_embed)
        await skynetlab_assign_embed_ref.add_reaction(emoji='🕹')
        await skynetlab_assign_embed_ref.add_reaction(emoji='🎉')
        await skynetlab_assign_embed_ref.add_reaction(emoji=bw_emoji)
        await skynetlab_assign_embed_ref.add_reaction(emoji=tw_emoji)
        await skynetlab_assign_embed_ref.add_reaction(emoji=ma_emoji)

        tech_channel = client.get_channel(784976527447293962)
        msg = '{0.mention}'.format(tech_channel)
        skynetlab_assign_embed = discord.Embed(
            title="Programmer Role",
            description="",
            color=discord.Colour.orange()
        )
        skynetlab_assign_embed.set_footer(text="Think you're good at programming?")
        skynetlab_assign_embed.set_thumbnail(
            url="https://i.imgur.com/6oc8cfe.png")  # https://i.imgur.com/Iw4o4JF.png"
        skynetlab_assign_embed.set_author(name="Role Assign",
                                          icon_url="https://i.imgur.com/BQLKiEh.png")
        skynetlab_assign_embed.add_field(name="Let us know what languages you know or are learning!", value=msg,
                                         inline=False)
        skynetlab_assign_embed_ref = await role_assign_channel.send(embed=skynetlab_assign_embed)
        my_sql_emoji = get(client.emojis, name='mysql')
        python_emoji = get(client.emojis, name='python')
        javascript_emoji = get(client.emojis, name='javascript')
        java_emoji = get(client.emojis, name='java')
        cplusplus_emoji = get(client.emojis, name='cplusplus')
        await skynetlab_assign_embed_ref.add_reaction(emoji=python_emoji)
        await skynetlab_assign_embed_ref.add_reaction(emoji=javascript_emoji)
        await skynetlab_assign_embed_ref.add_reaction(emoji=java_emoji)
        await skynetlab_assign_embed_ref.add_reaction(emoji=cplusplus_emoji)
        await skynetlab_assign_embed_ref.add_reaction(emoji=my_sql_emoji)

        # Delete command to make life easier 4 me:
        await ctx.message.delete()

    else:
        await ctx.message.channel.send("no permission")


# @client.event  # comment this out when we want to see full excepetion log of errors
async def on_command_error(ctx, error):
    global command_list
    print("ERROR: " + str(error))
    unknown_command = str(ctx.message.content)
    # await ctx.send("Unknown command: " + unknown_command)
    # print("Command error similarity: " + str(round(SequenceMatcher(a=s_1, b=s_2).ratio(), 2)))
    for i in command_list:
        # print("Checking against: " + i)
        val = round(SequenceMatcher(a=unknown_command, b=i).ratio(), 2)
        # print(str(val))
        if val > .6:
            print("Ooh a similar command!")
            await ctx.send("Unknown command: " + "`" + unknown_command + "`" + ", Did you mean " + "`" + i + "`" + "?")
            return
    await ctx.send("Unknown command, try using !help")


#########################################################
#                                                       #
#               MISC FUNCTIONS BELOW HERE:              #
#                                                       #
#########################################################
async def send_suggestion_feedback(reason):
    global vote_message_embed
    global awaiting_admins_name_for_suggestion_reason
    global suggestion_state

    admin = awaiting_admins_name_for_suggestion_reason
    embed_dict = vote_message_embed.embeds[0].to_dict()
    user_that_suggested_it = client.get_user(int(str(embed_dict['author']['icon_url'])[35:53]))
    suggestion_message = str(embed_dict['fields'][1]['value'])

    if suggestion_state == "declined":
        suggestion_removed_embed = discord.Embed(
            title="Suggestion Declined By " + str(admin.nick),
            description="",
            color=discord.Colour.red()
        )
        suggestion_removed_embed.set_footer(text="Sorry about that!")
        suggestion_removed_embed.set_thumbnail(
            url="https://i.imgur.com/VTQvbGc.png")  # https://i.imgur.com/Iw4o4JF.png"
        suggestion_removed_embed.set_author(name="{0}'s Suggestion Was Deleted".format(user_that_suggested_it.name),
                                            icon_url=user_that_suggested_it.display_avatar.url)
        suggestion_removed_embed.add_field(name="Suggestion:",
                                           value=suggestion_message + " *from* {0.mention}".format(
                                               user_that_suggested_it),
                                           inline=False)
        suggestion_removed_embed.add_field(name="Reason:", value=reason, inline=False)
        await bugs_and_suggestions_channel.send(embed=suggestion_removed_embed)
        await vote_message_embed.delete()
    else:
        suggestion_message = str(embed_dict['fields'][1]['value'])

        suggestion_removed_embed = discord.Embed(
            title="Suggestion Approved By " + str(admin.nick),
            description="",
            color=discord.Colour.green()
        )
        suggestion_removed_embed.set_footer(text="Thanks so much for your suggestions!")
        suggestion_removed_embed.set_thumbnail(url="https://i.imgur.com/VTQvbGc.png")
        suggestion_removed_embed.set_author(name="{0}'s Suggestion Was Approved".format(user_that_suggested_it.name),
                                            icon_url=user_that_suggested_it.display_avatar.url)
        suggestion_removed_embed.add_field(name="Suggestion:", value=suggestion_message + " *from* {0.mention}".format(
            user_that_suggested_it), inline=False)
        suggestion_removed_embed.add_field(name="Reason:", value=reason, inline=False)
        await bugs_and_suggestions_channel.send("GG {0.mention}!".format(user_that_suggested_it))
        await bugs_and_suggestions_channel.send(embed=suggestion_removed_embed)
        await to_do_list_channel.send(embed=vote_message_embed.embeds[0])
        await vote_message_embed.delete()


async def send_help(message):  # Asks if member needs help in channel...
    print("Sending Help...")
    embed = discord.Embed(
        title="Need Help?",
        # description="or use !help",
        color=discord.Colour.orange()
    )
    embed.add_field(name="React with 👍 for help", value="** **", inline=False)
    # embed.add_field(name="React with 👎 to go away", value="** **", inline=False)
    # embed.set_footer(text='')
    # embed.set_author(name="")
    return_msg = await message.channel.send(embed=embed)
    await return_msg.add_reaction(emoji='👍')
    await return_msg.add_reaction(emoji='👎')


async def send_restart_notification():
    # send a restart notification embed:
    now = datetime.datetime.now()
    restart_embed = discord.Embed(
        title="RESTARTED: SkyNet Bot",
        description="Why did I restart? I have no idea!",
        color=discord.Colour.orange())
    restart_embed.set_footer(text="Well if you managed to read this far, gg wp")
    restart_embed.set_thumbnail(url="https://i.imgur.com/Iw4o4JF.png")
    restart_embed.set_author(name="SkyNet Servers", icon_url="https://i.imgur.com/BQLKiEh.png")
    restart_embed.add_field(name="Restart Time (AEST):", value=str(now.strftime('%H:%M:%S on %A, %B the %dth, %Y')),
                            inline=False)
    await bot_channel.send(embed=restart_embed)
    update_online_members_vc_placeholder.start()


async def log_message_into_admins(content, author, channel_of_message, edited_message, content_before, attachments):
    # Logger for admins:
    global all_message_log_channel
    content = str(content)
    content_before = str(content_before)
    if str(content) == "":
        # print("Empty content? How tho?")
        content = "Null"
    if author.bot:
        # print("Bot message detected, not logging...")
        return
    if str(content) == "Null":
        print("Member may have uploaded a file only, checking...")
        if len(attachments) != 0:
            for i in attachments:
                await all_message_log_channel.send("User uploaded the following attachment: " + str(i))

    if edited_message:
        now = datetime.datetime.now()
        embed = discord.Embed(
            title=str(author),
            description=str(channel_of_message),
            color=discord.Colour.orange()
        )
        embed.set_footer(text=str(now.strftime('%H:%M:%S on %A, %B the %dth, %Y')))
        embed.set_thumbnail(url=author.display_avatar.url)  # https://i.imgur.com/Iw4o4JF.png"
        embed.set_author(name=author, icon_url="https://i.imgur.com/Iw4o4JF.png")
        embed.add_field(name="Before", value=str(content_before).replace('@', 'AT'))
        embed.add_field(name="After", value=str(content).replace('@', 'AT'))
        await all_message_log_channel.send(embed=embed)
    else:
        now = datetime.datetime.now()
        embed = discord.Embed(
            title=str(author),
            description=str(channel_of_message),
            color=discord.Colour.orange()
        )
        embed.set_footer(text=str(now.strftime('%H:%M:%S on %A, %B the %dth, %Y')))
        embed.set_thumbnail(url=author.display_avatar.url)  # https://i.imgur.com/Iw4o4JF.png"
        embed.set_author(name=author, icon_url="https://i.imgur.com/Iw4o4JF.png")
        embed.add_field(name="Message", value=content.replace('@', 'AT'))

    if str(channel_of_message.type) == "private":
        await dm_log_channel.send(embed=embed)
    else:
        await all_message_log_channel.send(embed=embed)


# Last statement to run the actual bot and connect to Discord server API:
# client.run(str(input("Enter client ID: ")))
client.run(str(global_configuration_dict['general_info']['client_id_secret']))
