# import #
import os.path
import yaml


def load_main_config():
    print("Loading main configuration file")
    # Procedure one is to check if the configuration file exists, it should be in root:
    path_dir = os.getcwd().replace('\\', '/')
    print(path_dir)
    conf_dir = f"/usr/app/src/src/db/config.yml"

    # If folder doesn't exist, then create it.
    if not os.path.isdir(path_dir):
        # os.makedirs(path_dir)
        pass
    if os.path.isfile(conf_dir):
        print("configuration file exists")

    else:
        print("configuration file does not exist")
        dict_file = {
            'general_info': {
                "guild_id": 123,
                "user_db_path": "//192.168.1.1/file.json",
                "invites_db_path": "//192.168.1.1/invites.yml",
                "rules_message_path": "rules.yml",
                "something": 1964
            },

            # Discord Channel ID fields:
            'discord_channel_ids': {
                'general_channels': {
                    "general_channel_id": 123,
                    "rules_channel_id": 123,
                    "bot_channel_id": 123,
                    "member_log_channel_id": 123,
                    "memes_channel_id": 123,
                    "announcements_channel_id": 123,
                    "bugs_and_suggestions_channel_id": 123,
                    "mc_server_updates_channel_id": 123,
                    "voting_channel_id": 123,
                    "dev_progress_channel_id": 123,
                    "theocratic_channel_id": 123,
                    "donation_info_channel_id": 123,
                },

                # Admin tool channels:
                'admin_channel_ids': {
                    "to_do_list_channel_id": 123,
                    "admin_member_join_logger_channel_id": 123,
                    "all_message_log_channel_id": 123,
                    "discord_timing_channel_id": 123,
                    "mod_log": 123,
                    "dm_log": 123
                },

                # Bungee network channel ID's:
                'bungee_network_console_channel_ids': {
                    "creative_console_channel_id": 123,
                    "survival_console_channel_id": 123,
                    "minigames_console_channel_id": 123,
                    "sky_block_console_channel_id": 123,
                    "lobby_console_channel_id": 123
                },

                # Misc channel ID's:
                'misc_channel_ids': {
                    "online_members_vc_channel_id": 123,
                    "role_assign_channel_id": 123,
                }

            },

            # Discord Role ID fields:
            'discord_role_ids': {
                'general_roles': {
                "admin": 123,
                "mc_linked": 123,
                "skynet_lab": 123,
                "developer": 123,
                "donor": 123,
                "builders": 123,
                "member": 123
                },
                # Subscription roles (such as Watchtower notifications):
                'subscription_roles': {
                "wt_study_sub": 123,
                "mc_giveaway_sub": 123,
                "mc_server_updates_sub": 123,
                "bedwars_notifications_sub": 123,
                "mobarena_notifications_sub": 123,
                "turf_wars_notifications_sub": 123,
                "jw_news_sub": 123,
                },
                # Misc roles (such as banners):
                'misc_role_ids': {
                "subscription_banner": 123,
                "other_roles_banner": 123,
                "mysql_role": 123,
                "javascript_role": 123,
                "java_role": 123,
                "python_role": 123,
                "cplusplus_role": 123
                }
            },

            # Role assign embed message ID's (so the bot knows what message to check for self role assigning):
            'role_assign_message_embed_ids': {
                "skynet_lab_role_assign_msg_id": 123,
                "wt_not_role_assign_msg_id": 123,
                "mc_updates_role_assign_msg_id": 123,
                "programmer_role_assign_msg_id": 123,
                "jw_news_role_assign_id": 123
            },

            # MySQL Server details:
            # This is for the DiscordSRV Database:
            'my_sql_dicordsrv_db': {
                "host": "192.168.1.1",
                "user": "username",
                "password": "bigPassword",
                "database": "discord_srv_data",
                "autocommit": True
            },

            # This database is for MC Placeholders stored in MySQL (papi_bridge):
            'my_sql_papibridge_db': {
                "host": "192.168.1.1",
                "user": "username",
                "password": "bigPassword",
                "database": "papi_bridge",
                "autocommit": True
            },

            'image_links': {
                "skynet_s_logo": "https://i.imgur.com/abc.png",
                "icon_url_orange_play_button": "https://i.imgur.com/abc.png",
                "crying_emoji": "https://i.imgur.com/abc.png",
                "skynet_s_logo_broken": "https://i.imgur.com/abc.png"
            },

        }

        with open(conf_dir, 'w') as file:
            documents = yaml.dump(dict_file, file)

    # Now we will read the configuration file into a Python dictionary variable
    with open(conf_dir) as file:
        dict_file = yaml.load(file, Loader=yaml.FullLoader)

    # Return the dictionary to our main.py file
    return dict_file


def read_rules_into_mem(path):
    with open(path) as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python the dictionary format
        list_file = yaml.load(file, Loader=yaml.FullLoader)
        return list_file


