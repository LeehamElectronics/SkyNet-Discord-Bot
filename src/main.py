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

# misc #
import os  # Interact with OS through Python for listing dir's and the like
from difflib import SequenceMatcher  # For checking how similar a string is to another string, like auto correct!
import yaml
import datetime
import feedparser  # for RSS Feeds!

# These imports are from local .py files:
import configuration as configuration
import database as database
from load_configs import read_rules_into_mem

import discord
from discord.utils import get
import asyncio  # For running asynchronous code...
import re
import requests
import PIL
import json
import mysql.connector  # For interacting with the internal MySQL Server
import urllib.request


print("Loading Configuration...")
global_configuration_dict = configuration.ConfigFile.root_conf  # Load our configuration file into memory
image_urls = global_configuration_dict['image_links']  # keeps code cleaner when referencing image urls

##########################################
# Setup code for bot command and intents #
##########################################
intents = discord.Intents.all()
intents.message_content = True
intents.members = True

client = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)
tree = client.tree

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

########################
#         db           #
########################
database.create_tables()


########################
#       Cogs           #
########################
async def load_cogs():
    for filename in os.listdir('cogs'):
        if filename.endswith('.py'):
            print('Loading cog: ' + str(filename))
            await client.load_extension(f'cogs.{filename[:-3]}')


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

###############################
#    General Configuration    #
###############################
server_id = global_configuration_dict['general_info']['guild_id']  # Unique guild ID of the Discord Server.
path_dir = os.getcwd().replace('\\', '/').replace('src', 'conf')
rules_yml_location = f"{path_dir}/rules.yml"

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
    bot_channel = client.get_channel(configuration.ChannelObjects.bot_channel_id)  # Channel for bot-spam
    announcements_channel = client.get_channel(configuration.ChannelObjects.announcements_channel_id)
    general_channel = client.get_channel(configuration.ChannelObjects.general_channel_id)
    member_log_channel = client.get_channel(configuration.ChannelObjects.member_log_channel_id)
    all_message_log_channel = client.get_channel(configuration.ChannelObjects.all_message_log_channel_id)
    memes_channel = client.get_channel(configuration.ChannelObjects.memes_channel_id)
    role_assign_channel = client.get_channel(configuration.ChannelObjects.role_assign_channel_id)
    mc_server_updates_channel = client.get_channel(configuration.ChannelObjects.mc_server_updates_channel_id)
    bugs_and_suggestions_channel = client.get_channel(configuration.ChannelObjects.bugs_and_suggestions_channel_id)
    voting_channel = client.get_channel(configuration.ChannelObjects.voting_channel_id)
    to_do_list_channel = client.get_channel(configuration.ChannelObjects.to_do_list_channel_id)
    sky_block_console_channel = client.get_channel(configuration.ChannelObjects.sky_block_console_channel_id)
    lobby_console_channel = client.get_channel(configuration.ChannelObjects.lobby_console_channel_id)
    minigames_console_channel = client.get_channel(configuration.ChannelObjects.minigames_console_channel_id)
    survival_console_channel = client.get_channel(configuration.ChannelObjects.survival_console_channel_id)
    creative_console_channel = client.get_channel(configuration.ChannelObjects.creative_console_channel_id)
    rules_channel = client.get_channel(configuration.ChannelObjects.rules_channel_id)
    admin_member_join_logger_channel = client.get_channel(configuration.ChannelObjects.admin_member_join_logger_channel_id)
    discord_timing_channel = client.get_channel(configuration.ChannelObjects.discord_timing_channel_id)
    dm_log_channel = client.get_channel(configuration.ChannelObjects.dm_log_channel_id)
    dev_progress_channel = client.get_channel(configuration.ChannelObjects.dev_progress_channel_id)
    online_members_vc_channel = client.get_channel(configuration.ChannelObjects.online_members_vc_channel_id)
    theocratic_channel = client.get_channel(configuration.ChannelObjects.theocratic_channel_id)
    donation_info_channel = client.get_channel(configuration.ChannelObjects.donation_info_channel_id)

    # send a restart notification embed:
    await load_cogs()
    await send_restart_notification()

    # Begin cycle operations below:
    cycle_bot_status.start()  # Change status of bot:
    check_jw_rss_feed.start()  # Checks if there is anything new on JW.org


#########################################################
#                                                       #
#             CYCLE FUNCTIONS BELOW HERE:               #
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


@tasks.loop(seconds=3000)  # This function updates the online members placeholder voice channel
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


#########################################################
#                                                       #
#            COMMAND FUNCTIONS BELOW HERE:              #
#                                                       #
#########################################################

@client.command()
@commands.guild_only()
@commands.is_owner()
async def sync_tree(ctx):
    print("syncing tree")
    members_roles = ctx.message.author.roles
    if admin_role in members_roles:
        client.tree.copy_global_to(guild=guild)
        await ctx.bot.tree.sync(guild=ctx.guild)
        await ctx.send(
            f"Synced bot commands"
        )
    else:
        await ctx.message.channel.send("Oh, so you're am Admin r u??")


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
            await skynetlab_assign_embed_ref.add_reaction('🟢')
            await skynetlab_assign_embed_ref.add_reaction('🟠')
            await skynetlab_assign_embed_ref.add_reaction('🔴')
            await skynetlab_assign_embed_ref.add_reaction('✖')

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
        await skynetlab_assign_embed_ref.add_reaction('🧪')

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
        await skynetlab_assign_embed_ref.add_reaction('📖')

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
        await skynetlab_assign_embed_ref.add_reaction('🕹')
        await skynetlab_assign_embed_ref.add_reaction('🎉')
        await skynetlab_assign_embed_ref.add_reaction(bw_emoji)
        await skynetlab_assign_embed_ref.add_reaction(tw_emoji)
        await skynetlab_assign_embed_ref.add_reaction(ma_emoji)

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
        await skynetlab_assign_embed_ref.add_reaction(python_emoji)
        await skynetlab_assign_embed_ref.add_reaction(javascript_emoji)
        await skynetlab_assign_embed_ref.add_reaction(java_emoji)
        await skynetlab_assign_embed_ref.add_reaction(cplusplus_emoji)
        await skynetlab_assign_embed_ref.add_reaction(my_sql_emoji)

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
client.run(str(global_configuration_dict['general_info']['client_id_secret']))
