# Discord related API packages #
import discord
# internal packages #
from mathmatical_functions import get_pretty_date_format


def generate_help_menu():  # If user does need help, this function runs...
    print("Sending Help...")
    embed = discord.Embed(
        title="Help Menu!",
        description="React for more details",
        color=discord.Colour.orange()
    )
    embed.set_footer(text="Message a Staff member for more help!")
    embed.set_thumbnail(url="https://i.imgur.com/Iw4o4JF.png")
    embed.set_author(name="SkyNet")
    embed.add_field(name=":white_check_mark:", value="Show tutorial", inline=True)
    embed.add_field(name=":watermelon:", value="View stats", inline=True)
    embed.add_field(name=":envelope:", value="Check Mail", inline=True)
    return embed


def gen_punishment_embed_mod_log_embed(type_of_pun, reason, user_that_issued_pun, punished_user):
    msg_1 = ""
    # This embed is sent into the mod-log channel so we can easily see who's been punishing who
    if type_of_pun == "ban":
        msg_1 = f'{punished_user.name} was banned for'
        msg_2 = f'{reason}'
    elif type_of_pun == "kick":
        msg_1 = f'{punished_user.name} was kicked for'
        msg_2 = f'{reason}'
    elif type_of_pun == "mute":
        msg_1 = f'{punished_user.name} was muted for'
        msg_2 = f'{reason}'
    elif type_of_pun == "un_mute":
        msg_1 = f'{punished_user.name} was un muted for'
        msg_2 = f'{reason}'
    elif type_of_pun == "warn":
        msg_1 = f'{punished_user.name} was warned for'
        msg_2 = f'{reason}'
    elif type_of_pun == "unban":
        msg_1 = f'{punished_user.name} was unbanned, reason:'
        msg_2 = f'{reason}'
    else:
        msg_1 = "invalid punish type"
        msg_2 = "invalid punish type"

    embed = discord.Embed(
        title=f'❗ Punishment ❗',
        description="Let's hope this doesn't happen again",
        color=discord.Colour.orange()
    )

    embed.set_author(name="SkyNet", icon_url="https://i.imgur.com/Ke2YvAi.png")  # TODO: move all imgur links into a yml
    embed.set_thumbnail(url=user_that_issued_pun.avatar_url)

    embed.add_field(name=msg_1,  value=msg_2, inline=False)
    embed.set_image(url=punished_user.avatar_url)
    embed.set_footer(text=get_pretty_date_format())

    return embed


def gen_unban_embed(reason, user_that_issued_unban, member):
    # this embed is sent into channels to let people know about someone being unbanned
    embed = discord.Embed(
        title=f'❗ Unban ❗',
        description='hooray, I think?',
        color=discord.Colour.orange()
    )

    embed.set_author(name="SkyNet", icon_url="https://i.imgur.com/Ke2YvAi.png")  # TODO: move all imgur links into a yml
    embed.set_thumbnail(url=user_that_issued_unban.avatar_url)

    embed.add_field(name=f'{member} unbanned by {user_that_issued_unban}',  value=str(reason), inline=False)
    embed.set_image(url=member.avatar_url)
    embed.set_footer(text=get_pretty_date_format())

    return embed