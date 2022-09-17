import os
from configparser import ConfigParser

import json
from datetime import datetime

import diagnostics
from mysql.connector import MySQLConnection, Error


path_dir = os.getcwd().replace('\\', '/').replace('src', 'conf')
mysql_conf_dir = f"/usr/app/src/src/db/config.ini"


def read_db_config(filename=mysql_conf_dir, section='mysql'):
    """ Read database configuration file and return a dictionary object
    :param filename: name of the configuration file
    :param section: section of database configuration
    :return: a dictionary of database parameters
    """
    # create parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section, filename))

    return db


def create_tables():
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        c = conn.cursor(dictionary=True)

        # user_management table
        c.execute("""create table if not exists user_management(discord_uuid BIGINT NOT NULL, 
        original_inviter_uuid BIGINT DEFAULT 0, 
        invited_user_uuids BIGINT DEFAULT 0, 
        giveaways_won BIGINT DEFAULT 0, 
        total_messages_sent BIGINT DEFAULT 0, 
        total_media_sent BIGINT DEFAULT 0, 
        total_message_edits BIGINT DEFAULT 0, 
        total_message_deletes BIGINT DEFAULT 0, 
        last_message_sent_time DATETIME, 
        experience BIGINT DEFAULT 0, 
        level BIGINT DEFAULT 0, 
        first_server_join DATETIME, 
        full_name VARCHAR(150), 
        nick VARCHAR(150), 
        roles LONGBLOB,
        profile_picture_history LONGBLOB)""")

        # join_log table
        c.execute("""create table if not exists join_log(discord_uuid BIGINT NOT NULL, 
        inviter_uuid BIGINT, 
        join_date DATETIME)""")

        # leave_log table
        c.execute("""create table if not exists leave_log(discord_uuid BIGINT NOT NULL, 
        leave_date DATETIME)""")

        # send_message_log table
        c.execute("""create table if not exists send_message_log(discord_uuid BIGINT NOT NULL, 
        content VARCHAR(2000), 
        message_id BIGINT NOT NULL, 
        link VARCHAR(2000), 
        channel BIGINT NOT NULL,
         sent_date DATETIME)""")

        # edit_message_log table
        c.execute("""create table if not exists edit_message_log(discord_uuid BIGINT NOT NULL, 
        original_content VARCHAR(2000), 
        edited_content VARCHAR(2000), 
        message_id BIGINT NOT NULL, 
        link VARCHAR(2000), 
        channel BIGINT NOT NULL,
         edit_date DATETIME)""")

        # delete_message_log table
        c.execute("""create table if not exists delete_message_log(discord_uuid BIGINT NOT NULL, 
         content VARCHAR(2000), 
         message_id BIGINT NOT NULL, 
         link VARCHAR(2000), 
         channel BIGINT NOT NULL,
          deletion_date DATETIME)""")

        conn.commit()
        c.close()
        return None, None
    except Error as e:
        return diagnostics.log_error('severe', 'database', 'confirm_user_exists_in_db() failed to read from db', e), None


def confirm_user_exists_in_db(user):
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        c = conn.cursor(dictionary=True)
        c.execute("""SELECT * FROM user_management
                        WHERE discord_uuid = %s""", (user.id, ))
        user_record = c.fetchall()
        if not len(user_record) == 1:
            # this user does not exist in db, so add them
            insert_user(user)
        conn.commit()
        c.close()
        return None, None
    except Error as e:
        return diagnostics.log_error('severe', 'database', 'confirm_user_exists_in_db() failed to read from db', e), None


def insert_user(user):
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        c = conn.cursor(dictionary=True)

        query = """ INSERT INTO user_management(discord_uuid)\
                 VALUES (%s)"""
        c.execute(
            query, (
                user.id,
            )
        )

        conn.commit()
        c.close()
        return None, None
    except Error as e:
        return  diagnostics.log_error('severe', 'database', 'insert_user() failed to write to db', e), None


def update_user_roles(member, role_ids):
    role_ids_dict = {'roles': role_ids}
    confirm_user_exists_in_db(member)
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        c = conn.cursor(dictionary=True)
        c.execute("""UPDATE user_management SET roles = %s WHERE discord_uuid = %s""",
                  (json.dumps(role_ids_dict), member.id))
        conn.commit()
        c.close()
        return None, None

    except Error as e:
        return diagnostics.log_error('severe', 'database', 'update_user_roles() failed to update db', e), None


def insert_join_log(discord_uuid, inviter_uuid, date):
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        c = conn.cursor(dictionary=True)
        c.execute(
            """ INSERT INTO join_log(discord_uuid, inviter_uuid, date)\
             values(%s, %s, %s)""",
            (discord_uuid, inviter_uuid, date))
        conn.commit()
        c.close()
        return None, None
    except Error as e:
        return diagnostics.log_error('severe', 'database', 'insert_join_log() failed to write to db', e), None


def insert_leave_log(discord_uuid, date):
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        c = conn.cursor(dictionary=True)
        c.execute(
            "INSERT INTO leave_log(discord_uuid, date)\
             values(%s, %s);",
            (discord_uuid, date))
        conn.commit()
        c.close()
        return None, None
    except Error as e:
        return diagnostics.log_error('severe', 'database', 'insert_leave_log() failed to write to db', e), None


def increment_member_messages_count(message, msg_type):
    confirm_user_exists_in_db(message.author)
    # type can be, sent, edited, or deleted message.
    userid = str(message.author.id)
    if msg_type == "total_messages_sent":
        pass
    elif msg_type == "total_message_edits":
        pass
    elif msg_type == "total_message_deletes":
        pass
    else:
        return diagnostics.log_error('severe', 'functional', 'increment_member_messages_count was fed invalid msg_type', 'Null'), None
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        c = conn.cursor(dictionary=True)

        query = f"""SELECT {msg_type} FROM user_management WHERE `discord_uuid` = %s"""
        c.execute(query, (userid, ))

        user_record = c.fetchall()[0]
        message_count = int(user_record[msg_type]) + 1

        c.execute(f"""UPDATE user_management SET {msg_type} = %s, last_message_sent_time = %s WHERE discord_uuid = %s""",
                  (message_count, datetime.now(), userid))
        conn.commit()
        c.close()
        return None, None
    except Error as e:
        return diagnostics.log_error('severe', 'database', 'increment_member_messages_count() failed to write to db', e), None


def insert_send_message_log(message, date):
    confirm_user_exists_in_db(message.author)
    userid = str(message.author.id)
    content = str(message.content)
    message_id = str(message.id)
    link = str(message.jump_url)
    channel = str(message.channel.id)

    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        c = conn.cursor(dictionary=True)

        query = """ INSERT INTO send_message_log(discord_uuid, content, message_id, link, channel, sent_date)\
                       VALUES (%s, %s, %s, %s, %s, %s)"""
        c.execute(
            query, (
                userid, content, message_id, link, channel, date
            )
        )

        conn.commit()
        c.close()
        return None, None
    except Error as e:
        return diagnostics.log_error('severe', 'database', 'insert_send_message_log() failed to write to db', e), None


def insert_edit_message_log(before, after, date):
    confirm_user_exists_in_db(after.author)
    userid = str(after.author.id)
    edited_content = str(after.content)
    original_content = str(before.content)
    message_id = str(after.id)
    link = str(after.jump_url)
    channel = str(after.channel.id)

    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        c = conn.cursor(dictionary=True)
        c.execute(
            """ INSERT INTO edit_message_log(discord_uuid, original_content, edited_content, message_id, link, channel, edit_date)\
             VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (userid, original_content, edited_content, message_id, link, channel, date))
        conn.commit()
        c.close()
        return None, None
    except Error as e:
        return diagnostics.log_error('severe', 'database', 'insert_edit_message_log() failed to write to db', e), None


def insert_deleted_message_log(message, date):
    confirm_user_exists_in_db(message.author)
    userid = str(message.author.id)
    content = str(message.content)
    message_id = str(message.id)
    link = str(message.jump_url)
    channel = str(message.channel.id)

    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        c = conn.cursor(dictionary=True)
        c.execute(
            """ INSERT INTO delete_message_log(discord_uuid, content, message_id, link, channel, deletion_date)\
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (userid, content, message_id, link, channel, date))
        conn.commit()
        c.close()
        return None, None
    except Error as e:
        return diagnostics.log_error('severe', 'database', 'insert_deleted_message_log() failed to write to db', e), None


def fetch_member_xp_level(member):
    confirm_user_exists_in_db(member)
    userid = str(member.id)
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        c = conn.cursor(dictionary=True)
        c.execute("""SELECT experience, level FROM user_management
                  WHERE discord_uuid = %s""", (userid, ))
        user_record = c.fetchall()[0]
        xp = int(user_record['experience'])
        level = int(user_record['level'])

        c.close()
        return None, (xp, level)

    except Error as e:
        return diagnostics.log_error('severe', 'database', 'fetch_member_xp_level() failed to read from db', e), None


def update_member_xp_level(member, xp, level):
    confirm_user_exists_in_db(member)
    userid = str(member.id)
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        c = conn.cursor(dictionary=True)
        c.execute("""UPDATE user_management SET experience = %s, level = %s WHERE discord_uuid = %s""",
                  (xp, level, userid))
        conn.commit()
        c.close()
        return None, None

    except Error as e:
        return diagnostics.log_error('severe', 'database', 'update_member_xp_level() failed to update db', e), None


def fetch_member_last_message_time(member):
    confirm_user_exists_in_db(member)
    userid = str(member.id)
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        c = conn.cursor(dictionary=True)
        c.execute("""SELECT last_message_sent_time FROM user_management
                    WHERE discord_uuid = %s""", (userid,))
        user_record = c.fetchall()[0]
        last_message_sent_time = user_record['last_message_sent_time']
        last_message_sent_time_obj = datetime.now()
        if last_message_sent_time is not None:
            # convert to datetime object:
            last_message_sent_time_obj = last_message_sent_time

        conn.commit()
        c.close()
        return None, last_message_sent_time_obj

    except Error as e:
        return diagnostics.log_error('severe', 'database', 'fetch_member_last_message_time() failed to read from db', e), None


