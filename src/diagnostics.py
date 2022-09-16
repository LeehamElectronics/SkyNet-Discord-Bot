import datetime
import discord
import src.db.configuration as configuration

image_links = configuration.ConfigFile.root_conf['image_links']
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


def log_error(severity: str, error_type: str, message: str, trace_message: str, *args):
    # severity is a string such as 'severe' or 'minor'
    # error_type can be 'functional' or 'database'
    # message is a custom string describing the error
    # log to db, Discord, and local console
    if args is not None:
        cog_name = args[0]
    else:
        cog_name = "general"
    now = datetime.datetime.now()
    if logging_level == 0:
        print(f'{LoggingColors.WARNING}ERROR LOG ({severity}) {LoggingColors.OKCYAN}{now}> {LoggingColors.OKBLUE}Type: {error_type} : {LoggingColors.FAIL}{message}')
    else:
        print(
            f'{LoggingColors.WARNING}ERROR LOG ({severity}) {LoggingColors.OKCYAN}{now}> {LoggingColors.OKBLUE}Type: {error_type} : {LoggingColors.FAIL}{message} : {LoggingColors.ENDC}{trace_message}')
        # send error into Discord channel:
        embed = discord.Embed(
            title=f'ERROR LOG ({severity})',
            description=f'{error_type}: {message}',
            color=discord.Colour.red())
        embed.set_footer(text=now)
        embed.set_thumbnail(url=image_links['skynet_s_logo_broken'])  # https://i.imgur.com/Iw4o4JF.png"
        embed.set_author(name='Skynet Logging', icon_url=image_links['skynet_s_logo_broken'])
        embed.add_field(name="Cog", value=f'{cog_name}')
        embed.add_field(name="Trace", value=f'{trace_message}')
        return embed
