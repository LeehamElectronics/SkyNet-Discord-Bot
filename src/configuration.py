import load_configs


class ConfigFile:
    root_conf = load_configs.load_main_config()


class ChannelObjects:
    general_channel_id_dict = ConfigFile.root_conf['discord_channel_ids']['general_channels']  # Get to the root!
    bot_channel_id = general_channel_id_dict['bot_channel_id']
    announcements_channel_id = general_channel_id_dict['announcements_channel_id']
    memes_channel_id = general_channel_id_dict['memes_channel_id']
    bugs_and_suggestions_channel_id = general_channel_id_dict['bugs_and_suggestions_channel_id']
    general_channel_id = general_channel_id_dict['general_channel_id']
    member_log_channel_id = general_channel_id_dict['member_log_channel_id']
    mc_server_updates_channel_id = general_channel_id_dict['mc_server_updates_channel_id']
    voting_channel_id = general_channel_id_dict['voting_channel_id']
    rules_channel_id = general_channel_id_dict['rules_channel_id']
    dev_progress_channel_id = general_channel_id_dict['dev_progress_channel_id']
    theocratic_channel_id = general_channel_id_dict['theocratic_channel_id']
    donation_info_channel_id = general_channel_id_dict['donation_info_channel_id']
    #############################
    #      Misc Channel ID's    #
    #############################
    misc_channel_id_dict = ConfigFile.root_conf['discord_channel_ids']['misc_channel_ids']  # Get to the root!
    online_members_vc_channel_id = misc_channel_id_dict['online_members_vc_channel_id']
    role_assign_channel_id = misc_channel_id_dict['role_assign_channel_id']
    ##############################################
    #          Bungee Console Channel ID's       #
    ##############################################
    bungee_console_channel_id_dict = ConfigFile.root_conf['discord_channel_ids'][
        'bungee_network_console_channel_ids']  # Get to the root!
    sky_block_console_channel_id = bungee_console_channel_id_dict['sky_block_console_channel_id']
    creative_console_channel_id = bungee_console_channel_id_dict['creative_console_channel_id']
    survival_console_channel_id = bungee_console_channel_id_dict['survival_console_channel_id']
    minigames_console_channel_id = bungee_console_channel_id_dict['minigames_console_channel_id']
    lobby_console_channel_id = bungee_console_channel_id_dict['lobby_console_channel_id']
    ##############################################
    #           Administration Channel ID's      #
    ##############################################
    administration_channel_id_dict = ConfigFile.root_conf['discord_channel_ids'][
        'admin_channel_ids']  # Get to the root!
    all_message_log_channel_id = administration_channel_id_dict['all_message_log_channel_id']
    to_do_list_channel_id = administration_channel_id_dict['to_do_list_channel_id']
    admin_member_join_logger_channel_id = administration_channel_id_dict['admin_member_join_logger_channel_id']
    discord_timing_channel_id = administration_channel_id_dict['discord_timing_channel_id']
    mod_log_channel_id = administration_channel_id_dict['mod_log']
    dm_log_channel_id = administration_channel_id_dict['dm_log']
    # log channels
    log_channel_id_dict = ConfigFile.root_conf['discord_channel_ids']['log_channels']
    rule_breaker_log_channel_id = log_channel_id_dict['rule_breaker_log']
    commands_logger_channel_id = log_channel_id_dict['commands_logger_channel']


class RoleIDObjects:
    general_role_id_dict = ConfigFile.root_conf['discord_role_ids']  # Get to the root!
    chat_muted_role_id = general_role_id_dict['general_roles']['chat_muted']
    owner_role_id = general_role_id_dict['general_roles']['owner']
    admin_role_id = general_role_id_dict['general_roles']['admin']
    mod_role_id = general_role_id_dict['general_roles']['mod']
    member_role_id = general_role_id_dict['general_roles']['member']