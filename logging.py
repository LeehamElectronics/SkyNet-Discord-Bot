import datetime


def log_error(severity, error_type, message):
    # severity is a string such as 'severe' or 'minor'
    # error_type can be 'functional' or 'database'
    # message is a custom string describing the error
    # log to db, Discord, and local console
    now = datetime.datetime.now()
    print(f'ERROR LOG ({severity}) {now}> Type: {error_type} : {message}')