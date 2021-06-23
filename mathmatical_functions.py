from datetime import datetime


def _map(x, in_min, in_max, out_min, out_max):
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


# This function will generate a top ten leaderboard based on members XP points
def generate_leader_board(users_dict_of_dict):
    print("Getting leaderboard")
    users_list_of_dict = []
    for i in users_dict_of_dict:
        users_list_of_dict.append(users_dict_of_dict[i])

    db_sorted_by_lvl = sorted(users_list_of_dict, key=lambda row: row["experience"], reverse=True)
    i = 0
    top_ten = []
    while i < 10:
        top_ten.append(db_sorted_by_lvl[i])
        i += 1
    print("TOP TEN: " + str(top_ten))

    rank_num = 1
    message_to_send = ""
    for i in top_ten:
        message_to_send = message_to_send + "\n" + i["name"] + " Is Rank #" + str(rank_num)
        rank_num += 1

    return message_to_send


###########################################################
# This function finds the members rank given a members ID #
###########################################################
def find_members_rank(members_id, users_dict_of_dict):
    users_list_of_dict = []
    for i in users_dict_of_dict:
        users_list_of_dict.append(users_dict_of_dict[i])

    db_sorted_by_lvl = sorted(users_list_of_dict, key=lambda row: row["experience"], reverse=True)
    rank = 000
    for i in db_sorted_by_lvl:
        # print("SEARCHING 4: " + str(i["ID"]))
        if str(i["ID"]) == str(members_id):
            rank = db_sorted_by_lvl.index(i) + 1
            break

    return rank


def get_pretty_date_format():
    now = datetime.now()
    day_let = str(now.strftime('%d'))
    day_let = day_let[len(day_let) - 1]
    if day_let == 3:
        current_date = str(now.strftime('%A, %B the %drd %Y'))
    elif day_let == 1 or day_let == 0:
        current_date = str(now.strftime('%A, %B the %dst %Y'))
    else:
        current_date = str(now.strftime('%A, %B the %dth %Y'))
    return current_date  # Returns a string containing date, eg, Saturday, May the 29th 2021


def get_pretty_time_format():
    now = datetime.now()
    hour = int(now.strftime('%H'))
    if hour >= 12:
        AM_PM = "PM"
    else:
        AM_PM = "AM"

    current_time = f"{now.strftime('%I:%M:%S')} {AM_PM}"
    return current_time  # Returns a string containing time, eg, 06:36:18 PM


# Usefull for saving file names with a time stamp
def get_dashed_time_format():
    now = datetime.now()
    hour = int(now.strftime('%H'))
    if hour >= 12:
        AM_PM = "PM"
    else:
        AM_PM = "AM"

    current_time = f"{now.strftime('%I-%M')} {AM_PM}"
    return current_time  # Returns a string containing time, eg, 06-36-18 PM