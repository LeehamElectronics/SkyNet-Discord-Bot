import datetime


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


def log_error(severity, error_type, message):
    # severity is a string such as 'severe' or 'minor'
    # error_type can be 'functional' or 'database'
    # message is a custom string describing the error
    # log to db, Discord, and local console
    now = datetime.datetime.now()
    print(f'{LoggingColors.WARNING}ERROR LOG ({severity}) {LoggingColors.OKCYAN}{now}> {LoggingColors.OKBLUE}Type: {error_type} : {LoggingColors.FAIL}{message}')
