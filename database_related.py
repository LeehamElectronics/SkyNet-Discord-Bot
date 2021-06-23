###################################
#   Import modules into program   #
###################################
# Discord related API packages #
import discord
from discord.ext import commands
from discord.utils import get
from discord.ext import tasks  # For scheduling repeated function calls such as timers.
import asyncio  # For running asynchronous code...

import datetime
import json
from load_configs import share_global_config_dict_elsewhere
# Networking #
import mysql.connector  # For interacting with the internal MySQL Server
import urllib.request, io

########################################################################################################################
#                                                                                                                      #
#                                                initialize databases                                                  #
#                                                                                                                      #
########################################################################################################################
global_configuration_dict = share_global_config_dict_elsewhere()

#######################################
#  Database for DiscordSRV MC Plugin  #
#######################################
my_sql_discord_db_info_dict = global_configuration_dict['my_sql_dicordsrv_db']  # Get to the root!
discord_srv_data_db = mysql.connector.connect(
    host=my_sql_discord_db_info_dict['host'],
    user=my_sql_discord_db_info_dict['user'],
    password=my_sql_discord_db_info_dict['password'],
    database=my_sql_discord_db_info_dict['database'],
    autocommit=my_sql_discord_db_info_dict['autocommit']
)
discord_srv_data_cursor = discord_srv_data_db.cursor(buffered=True)  # We will reference this a lot

#######################################
#     Database for PAPI MC Plugin     #
#######################################
my_sql_placeholder_db_info_dict = global_configuration_dict['my_sql_papibridge_db']  # Get to the root!
mc_placeholder_db = mysql.connector.connect(
    host=my_sql_placeholder_db_info_dict['host'],
    user=my_sql_placeholder_db_info_dict['user'],
    password=my_sql_placeholder_db_info_dict['password'],
    database=my_sql_placeholder_db_info_dict['database'],
    autocommit=my_sql_placeholder_db_info_dict['autocommit']
)
mc_placeholder_data_cursor = mc_placeholder_db.cursor(buffered=True)  # We will reference this a lot


# This function only runs once when the bot initially starts up.
def read_users_data_into_mem(user_db_path):
    print("Trying to read all users data from JSON file...")
    users_list_of_dict = []  # Create the empty list
    begin_time = datetime.datetime.now()  # So we cna time how long it takes!
    with open(user_db_path) as f:
        users_dict_of_dict = json.load(f)
        for i in users_dict_of_dict:
            users_list_of_dict.append(users_dict_of_dict[i])
    print("Finished reading User data")
    print("Time taken to read user data into memory: " + str(datetime.datetime.now() - begin_time )+
          "  (hour:minutes:seconds:microseconds)")
    time_taken = str(datetime.datetime.now() - begin_time)
    return [users_dict_of_dict, users_list_of_dict, time_taken]


# This drops the current user database in memory into the JSON file, don't call this too many times it drains resources
def write_user_data(users_dict_of_dict, user_db_path):
    print("Appending all user data into JSON file...")
    with open(user_db_path, "w") as f:
        json.dump(users_dict_of_dict, f, indent=4)


########################################################################################################################
#                                                                                                                      #
#                          MySQL related functions, mostly related to communicating with MC server                     #
#                                                                                                                      #
########################################################################################################################
# Returns a list of time spent on MC server, this function should only be called locally for now
def get_time_on_mc_server(mc_uuid):
    # Time On All Servers:
    total_time_on_skynetmc = 0
    time_on_lobby = 0
    time_on_survival = 0
    time_on_minigames = 0
    time_on_skyblock = 0
    time_on_creative = 0

    mc_placeholder_data_cursor.execute("SELECT * FROM `total_hoursplayed`")
    for x in mc_placeholder_data_cursor:
        # print(x[0])  # Print the current UUID
        current_uuid = str(x[0])
        if current_uuid == mc_uuid:
            total_time_on_skynetmc = x[2]
            # print(total_time_on_skynetmc)  # Prints their total play time
            break

    # Time On Lobby:
    mc_placeholder_data_cursor.execute("SELECT * FROM `lobby_hoursplayed`")
    for x in mc_placeholder_data_cursor:
        # print(x[0])  # Print the current UUID
        current_uuid = str(x[0])
        if current_uuid == mc_uuid:
            time_on_lobby = x[2]
            # print(time_on_lobby)  # Prints their total play time
            break

    # Time On Survival:
    mc_placeholder_data_cursor.execute("SELECT * FROM `survival_hoursPlayed`")
    for x in mc_placeholder_data_cursor:
        # print(x[0])  # Print the current UUID
        current_uuid = str(x[0])
        if current_uuid == mc_uuid:
            time_on_survival = x[2]
            # print(time_on_survival)  # Prints their total play time
            break

    # Time On MiniGames:
    mc_placeholder_data_cursor.execute("SELECT * FROM `minigames_hoursPlayed`")
    for x in mc_placeholder_data_cursor:
        # print(x[0])  # Print the current UUID
        current_uuid = str(x[0])
        if current_uuid == mc_uuid:
            time_on_minigames = x[2]
            # print(time_on_minigames)  # Prints their total play time
            break

    # Time On SkyBlock:
    mc_placeholder_data_cursor.execute("SELECT * FROM `skyblock_hoursPlayed`")
    for x in mc_placeholder_data_cursor:
        # print(x[0])  # Print the current UUID
        current_uuid = str(x[0])
        if current_uuid == mc_uuid:
            time_on_skyblock = x[2]
            # print(time_on_skyblock)  # Prints their total play time
            break

    # Time On Creative:
    mc_placeholder_data_cursor.execute("SELECT * FROM `creative_hoursPlayed`")
    for x in mc_placeholder_data_cursor:
        # print(x[0])  # Print the current UUID
        current_uuid = str(x[0])
        if current_uuid == mc_uuid:
            time_on_creative = x[2]
            # print(time_on_creative)  # Prints their total play time
            break

    time_spent = [total_time_on_skynetmc, time_on_lobby, time_on_survival, time_on_minigames, time_on_skyblock,
                  time_on_creative]
    return time_spent


# Returns a list of balances, this function should only be called locally for now
def get_player_balance(mc_uuid):
    # print("Getting player balances")
    skycoin = 0
    minicoin = 0
    hcs_coin = 0
    player_balance_total = 0

    # SkyCoin:
    mc_placeholder_data_cursor.execute("SELECT * FROM `skyblock_balance`")
    for x in mc_placeholder_data_cursor:
        # print(x[0])  # Print the current UUID
        current_uuid = str(x[0])
        if current_uuid == mc_uuid:
            skycoin = x[2]
            # print(total_time_on_skynetmc)  # Prints their total play time
            break

    # HCS Coin:
    mc_placeholder_data_cursor.execute("SELECT * FROM `survival_balance`")
    for x in mc_placeholder_data_cursor:
        # print(x[0])  # Print the current UUID
        current_uuid = str(x[0])
        if current_uuid == mc_uuid:
            hcs_coin = x[2]
            # print(time_on_lobby)  # Prints their total play time
            break

    # MiniCoin:
    mc_placeholder_data_cursor.execute("SELECT * FROM `minigames_balance`")
    for x in mc_placeholder_data_cursor:
        # print("Checking UUID: " + x[0] + " MiniCoin val: " + x[2])  # Print the current UUID
        current_uuid = str(x[0])
        if current_uuid == mc_uuid:
            minicoin = x[2]
            # print("FOUND MINICOIN: " + str(minicoin))
            # print(time_on_survival)  # Prints their total play time
            break

    player_balance_total = int(skycoin) + int(minicoin) + int(hcs_coin)
    balance = [skycoin, minicoin, hcs_coin, player_balance_total]
    return balance


########################################################################################################################
#                                                                                                                      #
#                   Member MC statistics embed related functions, returns a simple Disdord.embed object                #
#                                                                                                                      #
########################################################################################################################
def get_mc_stats_embed(mc_uuid, user):
    # print("MC UUID: " + mc_uuid)
    time_spent = get_time_on_mc_server(mc_uuid)
    player_balance = get_player_balance(mc_uuid)
    # print("PLAYER BAL: " + str(player_balance))
    # print("TIME SPENT LIST: " + str(time_spent))
    with urllib.request.urlopen(
            f"http://tools.glowingmines.eu/convertor/uuid/{str(mc_uuid).replace('-', '')}") as url:
        data = json.loads(url.read().decode())
    mc_username = data['nick']
    embed = discord.Embed(
        title="{0}'s Stats".format(mc_username),
        description="",
        color=user.colour.value
    )
    embed.set_footer(text="Jeff?")
    embed.set_thumbnail(url="https://www.mc-heads.net/avatar/{}/100/nohelm.png".format(
        mc_uuid))  # https://i.imgur.com/Iw4o4JF.png"
    embed.set_author(name=f"{mc_username} ~ {user.nick}",
                                  icon_url="https://i.imgur.com/Iw4o4JF.png")
    embed.add_field(name="Joined MC Server",
                                 value=str(user.joined_at.year) + "-" + str(
                                     user.joined_at.month) + "-" + str(
                                     user.joined_at.day), inline=False)
    embed.add_field(name="Time spent on MC Server:", value="In hours...", inline=False)
    embed.add_field(name="Total:", value=time_spent[0], inline=True)
    embed.add_field(name="Survival:", value=time_spent[2], inline=True)
    embed.add_field(name="MiniGames:", value=time_spent[3], inline=True)
    embed.add_field(name="SkyBlock:", value=time_spent[4], inline=True)
    embed.add_field(name="Creative:", value=time_spent[5], inline=True)
    embed.add_field(name="Lobby:", value=time_spent[1], inline=True)

    #  balance = [skycoin, minicoin, hcs_coin, player_balance_total] REFERNCE ONLY
    embed.add_field(name="MC Balances:",
                                 value="$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$", inline=False)
    embed.add_field(name="SkyCoin:", value="$" + str(player_balance[0]), inline=True)
    embed.add_field(name="HCS Coin:", value="$" + str(player_balance[2]), inline=True)
    embed.add_field(name="MiniCoin:", value="$" + str(player_balance[1]), inline=True)
    embed.add_field(name="Total:", value="$" + str(player_balance[3]), inline=True)
    return embed


# returns True or False if we can find the users discord ID in the discord SRV database. Also returns MC UUID
# This could probably be replaced with DiscordSRV's built in role sync, but I need to use MySQL anyway to get UUID and
# other info like time spent on MC server. Perhaps we should experiment with DiscordSRVs role sync feature eventually?
def check_if_user_is_mc_linked(user):
    account_mc_linked = False
    mc_uuid = None
    try:
        user_id = str(user.id)
        discord_srv_data_cursor.execute("SELECT * FROM `discordsrv_accounts`")
        for table in discord_srv_data_cursor:
            if str(table[1]) == user_id:
                account_mc_linked = True
                mc_uuid = str(table[2])
                break
    except Exception as error:
        # TODO: move stuff like this into a proper logging stream...
        print("MySQL error encountered in check_if_user_is_mc_linked(): " + str(error))
        account_mc_linked = False

    return account_mc_linked, mc_uuid  # return True or False