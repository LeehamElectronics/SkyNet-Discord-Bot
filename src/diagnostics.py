import datetime

# logging level:
import discord

logging_level = 1


class LoggingColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


async def log_error(severity, error_type, message, trace_message):
    # severity is a string such as 'severe' or 'minor'
    # error_type can be 'functional' or 'database'
    # message is a custom string describing the error
    # log to db, Discord, and local console
    now = datetime.datetime.now()
    if logging_level == 0:
        print(f'{LoggingColors.WARNING}ERROR LOG ({severity}) {LoggingColors.OKCYAN}{now}> {LoggingColors.OKBLUE}Type: {error_type} : {LoggingColors.FAIL}{message}')
    else:
        print(
            f'{LoggingColors.WARNING}ERROR LOG ({severity}) {LoggingColors.OKCYAN}{now}> {LoggingColors.OKBLUE}Type: {error_type} : {LoggingColors.FAIL}{message} : {LoggingColors.ENDC}{trace_message}')
        # send error into Discord channel:
        embed = discord.Embed(
            title=f'ERROR LOG ({severity})',
            description=f'{error_type}',
            color=discord.Colour.red())
        embed.set_footer(text=now)
        embed.set_thumbnail(url=author.display_avatar.url)  # https://i.imgur.com/Iw4o4JF.png"
        embed.set_author(name=author, icon_url="https://i.imgur.com/Iw4o4JF.png")
        embed.add_field(name="Trace", value=f'{trace_message}')
        await dm_log_channel.send(embed=embed)