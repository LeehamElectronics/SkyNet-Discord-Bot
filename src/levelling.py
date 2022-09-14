# Simple adds a specific amount of XP to the user
import datetime
import src.db.database as database


# Used to check if player can level up or level up MULTIPLE levels, and then it does so and announces it to user.
async def manual_level_up(user, channel):
    user_finished_leveling_up = False
    experience, original_level = database.fetch_member_xp_level(user)
    new_level = original_level
    while not user_finished_leveling_up:
        xp_needed = new_level ** 4
        if experience > xp_needed:
            # user has levelled up, keep checking to see if they levelled up multiple times.
            new_level += 1
        else:
            user_finished_leveling_up = True
            database.update_member_xp_level(user, experience, new_level)
    if int(original_level) < int(new_level):
        await channel.send(
            f":tada: Congrats {user.mention}, you levelled up from level {original_level} to level {new_level}")
    else:
        pass


def try_to_add_add_experience(user, added_exp):  # Test if user is permitted to have XP added to them
    if database.fetch_member_last_message_time(user) is not None:
        now_time = datetime.datetime.now()
        difference = now_time - database.fetch_member_last_message_time(user)
        datetime.timedelta(0, 8, 562000)

        if difference.seconds > 8:
            # sufficient time has passed since last message, we will now add the XP into user_db
            current_xp, current_level = database.fetch_member_xp_level(user)
            new_exp = current_xp + added_exp
            database.update_member_xp_level(user, new_exp, current_level)
        else:
            return


# is this even used? idk...
def try_to_level_up_member(user):  # Used to check if player can level up
    current_xp, current_level = database.fetch_member_xp_level(user)
    xp_needed = current_level ** 4
    if current_xp > xp_needed:
        database.update_member_xp_level(user, current_xp, current_level + 1)
        return True
    else:
        return False
