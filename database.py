import logging

from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config


def create_tables():
    db_config = read_db_config()
    conn = MySQLConnection(**db_config)
    c = conn.cursor()

    # user_management table
    c.execute("""create table if not exists user_management(discord_uuid BIGINT NOT NULL, 
    original_inviter_uuid BIGINT, 
    invited_user_uuids BIGINT, 
    giveaways_won BIGINT, 
    total_messages_sent BIGINT, 
    total_media_sent BIGINT, 
    total_message_edits BIGINT, 
    total_message_deletes BIGINT, 
    last_message_sent_time DATE, 
    experience BIGINT, 
    level INT, 
    first_server_join DATE, 
    full_name VARCHAR(150), 
    nick VARCHAR(150), 
    profile_picture_history LONGBLOB)""")

    # join_log table
    c.execute("""create table if not exists join_log(discord_uuid BIGINT NOT NULL, 
    inviter_uuid BIGINT, 
    join_date DATE)""")

    # leave_log table
    c.execute("""create table if not exists leave_log(discord_uuid BIGINT NOT NULL, 
    leave_date DATE)""")

    # send_message_log table
    c.execute("""create table if not exists send_message_log(discord_uuid BIGINT NOT NULL, 
    content BIGINT NOT NULL, 
    message_id BIGINT NOT NULL, 
    link BIGINT NOT NULL, 
    channel BIGINT NOT NULL,
     sent_date DATE)""")

    # edit_message_log table
    c.execute("""create table if not exists edit_message_log(discord_uuid BIGINT NOT NULL, 
    content BIGINT NOT NULL, 
    message_id BIGINT NOT NULL, 
    link BIGINT NOT NULL, 
    channel BIGINT NOT NULL,
     edit_date DATE)""")

    # delete_message_log table
    c.execute("""create table if not exists delete_message_log(discord_uuid BIGINT NOT NULL, 
     content BIGINT NOT NULL, 
     message_id BIGINT NOT NULL, 
     link BIGINT NOT NULL, 
     channel BIGINT NOT NULL,
      deletion_date DATE)""")

    conn.commit()
    c.close()


def insert_user(player_name, discord_tag):
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        c = conn.cursor()
        c.execute(
            "INSERT INTO 'user_management' ('discord_uuid', 'original_inviter_uuid', 'invited_user_uuids', 'total_messages_sent', 'give_aways_won', 'total_messages_sent', 'total_media_sent', 'total_message_edits', 'total_messages_sent', 'last_message_sent_time', 'experience', 'level', 'last_server_leave', 'first_server_join', 'full_name', 'nick', 'profile_picture_history') values((%s, %s);",
            player_name, discord_tag)
        conn.commit()
        c.close()
    except Error as e:
        return e


def insert_join_log(discord_uuid, inviter_uuid, date):
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        c = conn.cursor()
        c.execute(
            "INSERT INTO 'join_log' ('discord_uuid', 'inviter_uuid', 'date') values((%s, %s);",
            discord_uuid, inviter_uuid, date)
        conn.commit()
        c.close()
    except Error as e:
        return e


def insert_leave_log(discord_uuid, date):
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        c = conn.cursor()
        c.execute(
            "INSERT INTO 'leave_log' ('discord_uuid', 'date') values((%s, %s);",
            discord_uuid, date)
        conn.commit()
        c.close()
    except Error as e:
        return e


def increment_member_messages_count(message, msg_type):
    # type can be, sent, edited, or deleted message.
    userid = str(message.author.id)
    if msg_type == "total_messages_sent":
        pass
    elif msg_type == "total_message_edits":
        pass
    elif msg_type == "total_message_deletes"
        pass
    else:
        logging.log_error('severe', 'functional', 'increment_member_messages_count was fed invalid msg_type')
        return
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        c = conn.cursor()
        c.execute("""SELECT total_messages_sent, FROM user_management
                  WHERE discord_uuid = %s""", (userid,))
        user_record = c.fetchall()[0]
        message_count = int(user_record['total_messages_sent']) + 1

        c.execute("""UPDATE user_management SET total_messages_sent = %s WHERE discord_uuid = %s""",
                  (message_count, userid))
        conn.commit()
        c.close()
    except Error as e:
        return e


def insert_send_message_log(message, date):
    userid = str(message.author.id)
    content = str(message.content)
    message_id = str(message.id)
    link = str(message.jump_url)
    channel = str(message.channel.id)

    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        c = conn.cursor()
        c.execute(
            "INSERT INTO 'send_message_log' ('discord_uuid', 'content', 'message_id', 'link', 'channel', 'sent_date') values((%s, %s, %s, %s, %s, %s);",
            userid, content, message_id, link, channel, date)
        conn.commit()
        c.close()
    except Error as e:
        return e


def insert_edit_message_log(message, date):
    userid = str(message.author.id)
    content = str(message.content)
    message_id = str(message.id)
    link = str(message.jump_url)
    channel = str(message.channel.id)

    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        c = conn.cursor()
        c.execute(
            "INSERT INTO 'edit_message_log' ('discord_uuid', 'content', 'message_id', 'link', 'channel', 'edit_date') values((%s, %s, %s, %s, %s, %s);",
            userid, content, message_id, link, channel, date)
        conn.commit()
        c.close()
    except Error as e:
        return e


def insert_deleted_message_log(message, date):
    userid = str(message.author.id)
    content = str(message.content)
    message_id = str(message.id)
    link = str(message.jump_url)
    channel = str(message.channel.id)

    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
        c = conn.cursor()
        c.execute(
            "INSERT INTO 'delete_message_log' ('discord_uuid', 'content', 'message_id', 'link', 'channel', 'deletion_date') values((%s, %s, %s, %s, %s, %s);",
            userid, content, message_id, link, channel, date)
        conn.commit()
        c.close()
    except Error as e:
        return e