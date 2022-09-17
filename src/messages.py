########################################################################################################################
#                                                                                                                      #
# This file contains all functions that are called to compare strings. Moved to a separate file since there are A LOT  #
#                                           of strings to check against.                                               #
#                                                                                                                      #
########################################################################################################################

def global_check_for_swears(message):
    if message == 'swear':
        return True
    else:
        # Return with False, implying that there was no swears in the message
        return False


def check_for_help_requests(message):
    print("Checking for help?")


def member_does_not_have_permision(author):
    message = f"Sorry {author.mention}, but you do not have permission to do that!"
    return message


# This is where the kick message that gets sent to a user right before they are kicked lives:
def kick_message_to_kicked_user(reason):
    message = "🔴 You have been kicked from SkyNet Discord Server for reason: " + '\n' + '🔴 ' + str(reason)
    return message


def mute_message_to_muted_user(reason):
    message = "🔴 You have been muted on SkyNet Discord Server for reason: " + '\n' + '🔴 ' + str(reason)
    return message


def un_mute_message_to_un_muted_user(reason):
    message = "🟢 You have been un-muted on SkyNet Discord Server for reason: " + '\n' + '🟢 ' + str(reason)
    return message


def ban_message_to_banned_user(reason):
    message = "🔴 You have been banned from SkyNet Discord Server for reason: " + '\n' + '🔴 ' + str(reason)
    return message


def warn_message_to_warned_user(reason):
    message = "🔴 You have been Warned on SkyNet Discord Server: " + '\n' + '🔴 ' + str(reason)
    return message


def unban_message_to_banned_user(reason):
    message = "🟢 You have been unbanned on SkyNet Discord Server: " + '\n' + '🟢 ' + str(reason)
    return message