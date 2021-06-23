#################################################################################
#                                                                               #
#        This contains basic check functions to help keep our bot clean         #
#                                                                               #
#################################################################################
import discord
from discord.utils import get


# Check if given member has a given role, returns True or False
def check_roles(member, role_id):
    members_roles = member.roles
    role = get(member.guild.roles, id=role_id)
    # print(str(roles))
    if role in members_roles:
        return True
    else:
        return False

