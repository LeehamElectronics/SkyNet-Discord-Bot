###################################
#   Import modules into program   #
###################################
import discord
from discord.ext import commands
from discord.utils import get
from misc_functions import convert_variable_to_mem_obj, send_dm, _unban, punishments, \
    generate_level_picture, manual_add_experience, find_invite_by_code, update_member_data
from mathmatical_functions import _map, find_members_rank, get_pretty_date_format
from load_configs import share_global_config_dict_elsewhere  # Use this to find role ID's from config.yml
from datetime import date
from datetime import datetime


class Events(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.config = share_global_config_dict_elsewhere()
        self.user_db_path = self.config['general_info']['user_db_path'] + '.json'
        self.channel_ids = self.config['discord_channel_ids']
        self.admin_member_join_logger_channel = self.client.get_channel(
            self.channel_ids['admin_channel_ids']['admin_member_join_logger_channel_id'])
        self.rules_channel = self.client.get_channel(self.channel_ids['general_channels']['rules_channel_id'])
        self.bot_channel = self.client.get_channel(self.channel_ids['general_channels']['bot_channel_id'])
        self.role_assign_channel = self.client.get_channel(self.channel_ids['misc_channel_ids']['role_assign_channel_id'])

    @commands.Cog.listener()
    async def on_ready(self):
        print("🟢 reaction_events.py loaded successfully.\n-----")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        global awaiting_admins_suggestion_reason
        global awaiting_admins_name_for_suggestion_reason
        global message_ref_remind_admin_for_suggestions_reason
        global admin_role
        global suggestion_state
        global to_do_list_channel
        global vote_message_embed
        if user.bot:
            # ignore reactions from bots
            return
        # Reacted message channel and content info:
        reacted_channel = reaction.message.channel
        reacted_message = reaction.message.content
        # Reacted message info:
        reacted_message_embeds = reaction.message.embeds
        reacted_message_id = reaction.message.id
        if str(reacted_message_embeds[0].title) == "Confirm Suggestion?":
            print(str(user.nick) + " Reacted to Suggestion Confirmation from " + str(
                reacted_message_embeds[0].author.name))
            if str(user.nick) == str(reacted_message_embeds[0].author.name):
                print("Original author...")
                # Send suggestion to voting channel...
                if reaction.emoji == "✖":
                    await reaction.message.delete()
                    return
                else:
                    # send to voting channel with priority attached:
                    if reaction.emoji == "✖":
                        await reaction.message.delete()
                    elif reaction.emoji == "🟢":
                        priority = "Low"
                        await reaction.message.delete()
                    elif reaction.emoji == "🟠":
                        priority = "Medium"
                        await reaction.message.delete()
                    elif reaction.emoji == "🔴":
                        priority = "High"
                        await reaction.message.delete()
                    else:
                        # unknown emoji, remove it...
                        await reaction.remove(user)
                        return
                    embed_dict = reaction.message.embeds[0].to_dict()
                    suggestion_message = str(embed_dict['fields'][1]['value'])
                    voting_embed = discord.Embed(
                        title="Voting Poll",
                        description="",
                        color=discord.Colour.orange()
                    )
                    voting_embed.set_footer(text="React with 👍 or 👎")
                    voting_embed.set_thumbnail(
                        url="https://i.imgur.com/VTQvbGc.png")  # https://i.imgur.com/Iw4o4JF.png"
                    voting_embed.set_author(name=str(user.nick) + "'s Suggestion",
                                            icon_url=user.display_avatar.url)
                    voting_embed.add_field(name="** **",
                                           value=str(reaction.emoji) + " " + str(priority) + " Priority",
                                           inline=False)
                    voting_embed.add_field(name="Suggestion:", value=suggestion_message,
                                           inline=False)
                    await reaction.message.channel.send(
                        "Suggestion added in {0.mention}! Thank you.".format(voting_channel))
                    voting_embed_ref = await voting_channel.send(embed=voting_embed)
                    await voting_embed_ref.add_reaction(emoji="👍")
                    await voting_embed_ref.add_reaction(emoji="👎")
                    await voting_embed_ref.add_reaction(emoji="✅")
                    await voting_embed_ref.add_reaction(emoji="✖")
            else:
                print("No permission")
                await reaction.message.remove_reaction(reaction, user)

        elif str(reacted_message_embeds[0].title) == "Voting Poll":
            if str(reaction.emoji) == "✖":
                members_roles = user.roles
                # print(str(roles))
                if admin_role in members_roles:
                    print("Suffecient perms!")
                    vote_message_embed = reaction.message
                    message_ref_remind_admin_for_suggestions_reason = await reaction.message.channel.send(
                        f"{user.mention} "
                        f"Please type a reason for removing this suggestion / bug report")
                    awaiting_admins_suggestion_reason = True
                    awaiting_admins_name_for_suggestion_reason = user
                    suggestion_state = "declined"

                else:
                    await reaction.message.remove_reaction(reaction, user)
            elif str(reaction.emoji) == "✅":
                members_roles = user.roles
                if admin_role in members_roles:
                    print("Suffecient perms!")
                    vote_message_embed = reaction.message
                    message_ref_remind_admin_for_suggestions_reason = await reaction.message.channel.send(
                        f"{user.mention} Please type a reason for approving this suggestion / bug report")
                    awaiting_admins_suggestion_reason = True
                    awaiting_admins_name_for_suggestion_reason = user
                    suggestion_state = "approved"

                else:
                    await reaction.message.remove_reaction(reaction, user)

        elif str(reacted_message_embeds[0].title) == "Your Stats!":
            # Need to check to make sure reacted user is the user that sent !stat because we need cool downs!
            if str(reaction.emoji) == "🎮":
                is_mc_linked, mc_uuid = check_if_user_is_mc_linked(user)
                if is_mc_linked:
                    await reaction.message.channel.send(embed=get_mc_stats_embed(mc_uuid, user))
        elif str(reacted_message_embeds[0].title) == "Need Help?":
            if str(reaction.emoji) == "👍":
                print("THEY WANT HELP")
                await reaction.message.channel.send(embed=generate_help_menu())
            elif str(reaction.emoji) == "👎":
                print("DELETING HELP")
                await reaction.message.delete()

        else:
            print("IGNORING REACTION")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Adds a role based on a reaction emoji."""
        # Make sure that the message the user is reacting to is the one we care about
        emoji_temp = payload.emoji
        reacted_channel_id = payload.channel_id
        reacted_channel_obj = client.get_channel(reacted_channel_id)
        member_temp = payload.member
        message_id_temp = str(payload.message_id)
        message_object = await reacted_channel_obj.fetch_message(payload.message_id)
        reaction = get(message_object.reactions, emoji=payload.emoji.name)

        if member_temp.bot:
            # reactions added by bot are ignored
            return

        try:
            print(reaction.custom_emoji)
        except:
            reaction = get(message_object.reactions, emoji=payload.emoji)
            print("WAS not CUSTOM, EMOJI IS: " + str(reaction))

        if reacted_channel_id == role_assign_channel_id:
            print(member_temp.name + " has reacted to a role assign embed!")
            members_roles = member_temp.roles
            if subscriptions_banner_role in members_roles:
                print("User has banner role, pass")
            else:
                print("Adding banner role...")
                await member_temp.add_roles(subscriptions_banner_role)
            if other_roles_banner_role not in members_roles:
                print("Adding other roles banner:")
                await member_temp.add_roles(other_roles_banner_role)
            if message_id_temp == skynet_lab_role_assign_msg_id:
                if str(emoji_temp) != "🧪":
                    print("WRONG EMOJI")
                    print("EMOJI: " + str(emoji_temp))
                    print(str(type(emoji_temp)))
                    if reaction.custom_emoji:
                        print("This is a custom emoji from SkyNet!")
                    else:
                        print("This is not a custom Emoji")

                    await message_object.remove_reaction(reaction, member_temp)
                    return
                print("User Added LAB role!!")
                members_roles = member_temp.roles
                if skynet_lab_role in members_roles:
                    print("User already has LAB role")
                    await bot_channel.send(("You already have the LAB role {0.mention}!!".format(member_temp)))

                else:
                    print("Adding LAB role!")
                    await member_temp.add_roles(skynet_lab_role)
                    await bot_channel.send((
                        "Good job {0.mention}, you now have the SkyNet LAB Role giving you access to cool channels like {1.mention}".format(
                            member_temp, dev_progress_channel)))

            elif message_id_temp == wt_not_role_assign_msg_id:
                print("User Added WT Study role!!")
                if str(emoji_temp) != "📖":
                    print("WRONG EMOJI")
                    print("EMOJI: " + str(emoji_temp))
                    print(str(type(emoji_temp)))
                    if reaction.custom_emoji:
                        print("This is a custom emoji from SkyNet!")
                    else:
                        print("This is not a custom Emoji")

                    await message_object.remove_reaction(reaction, member_temp)
                    return
                print("User Added WT role!!")
                members_roles = member_temp.roles
                if wt_study_sub_role in members_roles:
                    print("User already has WT role")
                    await bot_channel.send(
                        ("You already have the Watchtower Study Notifications role {0.mention}!!".format(member_temp)))

                else:
                    print("Adding WT role!")
                    await member_temp.add_roles(wt_study_sub_role)
                    await bot_channel.send((
                        "Good job {0.mention}, you now have the Watchtower Study Notifications Role, you will now be automatically notified about Watchtower Study groups".format(
                            member_temp)))

            elif message_id_temp == jw_news_role_assign_id:
                print("User Added JW News role!!")
                if str(emoji_temp) != "📚":
                    print("WRONG EMOJI")
                    print("EMOJI: " + str(emoji_temp))
                    print(str(type(emoji_temp)))
                    if reaction.custom_emoji:
                        print("This is a custom emoji from SkyNet!")
                    else:
                        print("This is not a custom Emoji")

                    await message_object.remove_reaction(reaction, member_temp)
                    return
                members_roles = member_temp.roles
                if jw_news_sub in members_roles:
                    print("User already has JW News role")
                    await bot_channel.send(
                        ("You already have the JW News Notifications role {0.mention}!!".format(member_temp)))

                else:
                    print("Adding JW News role!")
                    await member_temp.add_roles(jw_news_sub)
                    await bot_channel.send((
                        "Good job {0.mention}, you now have the JW News Notifications Role, you will now be automatically notified about new items on JW.org".format(
                            member_temp)))

            elif message_id_temp == mc_updates_role_assign_msg_id:
                print("User Added MC updates role!!")
                # Get emojis into memory
                bw_emoji = get(client.emojis, name='bedwars')
                tw_emoji = get(client.emojis, name='grass')
                ma_emoji = get(client.emojis, name='creeper')
                if str(emoji_temp) == "🕹":
                    print("🕹 EMOJI")
                    print(str(type(emoji_temp)))
                    if reaction.custom_emoji:
                        print("This is a custom emoji from SkyNet!")
                    else:
                        print("This is not a custom Emoji")

                    members_roles = member_temp.roles
                    if mc_server_updates_sub_role in members_roles:
                        print("User already has MC Updates role")
                        await bot_channel.send(
                            ("You already have the MC Updates role {0.mention}!!".format(member_temp)))

                    else:
                        print("Adding MC Updates role!")
                        await member_temp.add_roles(mc_server_updates_sub_role)
                        await bot_channel.send((
                            "Good job {0.mention}, you now have the MC Updates Role, notifications are sent in {1.mention}".format(
                                member_temp, announcements_channel)))
                elif str(emoji_temp) == "🎉":
                    print("🎉 EMOJI")
                    print(str(type(emoji_temp)))
                    if reaction.custom_emoji:
                        print("This is a custom emoji from SkyNet!")
                    else:
                        print("This is not a custom Emoji")

                elif emoji_temp == bw_emoji:
                    print("BW EMOJI")
                    print(str(type(emoji_temp)))
                    if reaction.custom_emoji:
                        print("This is a custom emoji from SkyNet!")
                    else:
                        print("This is not a custom Emoji")

                    members_roles = member_temp.roles
                    if bedwars_notifications_role in members_roles:
                        print("User already has bedwars_notifications_role role")
                        await bot_channel.send(
                            ("You already have the BedWars Game Notifications role {0.mention}!!".format(member_temp)))

                    else:
                        print("Adding bedwars_notifications_role role!")
                        await member_temp.add_roles(bedwars_notifications_role)
                        await bot_channel.send((
                            "Good job {0.mention}, you now have the BedWars Game Notifications Role, notifications are sent in {1.mention}".format(
                                member_temp, mc_server_updates_channel)))
                elif emoji_temp == tw_emoji:
                    print("tw_emoji EMOJI")
                    print(str(type(emoji_temp)))
                    if reaction.custom_emoji:
                        print("This is a custom emoji from SkyNet!")
                    else:
                        print("This is not a custom Emoji")

                    members_roles = member_temp.roles
                    if turfwars_notifications_role in members_roles:
                        print("User already has turfwars_notifications_role")
                        await bot_channel.send(
                            ("You already have the TurfWars Game Notifications role {0.mention}!!".format(member_temp)))

                    else:
                        print("Adding turfwars_notifications_role!")
                        await member_temp.add_roles(turfwars_notifications_role)
                        await bot_channel.send((
                            "Good job {0.mention}, you now have the TurfWars Game Notifications Role, notifications are sent in {1.mention}".format(
                                member_temp, mc_server_updates_channel)))
                elif emoji_temp == ma_emoji:
                    print("ma_emoji EMOJI")
                    print(str(type(emoji_temp)))
                    if reaction.custom_emoji:
                        print("This is a custom emoji from SkyNet!")
                    else:
                        print("This is not a custom Emoji")

                    members_roles = member_temp.roles
                    if mobarena_notifications_role in members_roles:
                        print("User already has mobarena_notifications_role")
                        await bot_channel.send(
                            ("You already have the MobArena Game Notifications role {0.mention}!!".format(member_temp)))

                    else:
                        print("Adding mobarena_notifications_role!")
                        await member_temp.add_roles(mobarena_notifications_role)
                        await bot_channel.send((
                            "Good job {0.mention}, you now have the MobArena Game Notifications Role, notifications are sent in {1.mention}".format(
                                member_temp, mc_server_updates_channel)))

            elif message_id_temp == programmer_role_assign_msg_id:
                print("User Added Programmer role!!")
                cplusplus_emoji = get(client.emojis, name='cplusplus')
                my_sql_emoji = get(client.emojis, name='mysql')
                python_emoji = get(client.emojis, name='python')
                javascript_emoji = get(client.emojis, name='javascript')
                java_emoji = get(client.emojis, name='java')

                if emoji_temp == cplusplus_emoji:
                    print("cplusplus_emoji EMOJI")
                    print("EMOJI: " + str(emoji_temp))
                    print(str(type(emoji_temp)))
                    if reaction.custom_emoji:
                        print("This is a custom emoji from SkyNet!")
                    else:
                        print("This is not a custom Emoji")
                    members_roles = member_temp.roles
                    if cplusplus_role in members_roles:
                        print("User already has cplusplus_emoji role")
                        await bot_channel.send(("You already have the C++ role {0.mention}!!".format(member_temp)))

                    else:
                        print("Adding cplusplus_role role!")
                        await member_temp.add_roles(cplusplus_role)
                        await bot_channel.send((
                            "Good job {0.mention}, you now have the C++ Role".format(
                                member_temp)))
                elif emoji_temp == my_sql_emoji:
                    print("my_sql_emoji EMOJI")
                    print("EMOJI: " + str(emoji_temp))
                    print(str(type(emoji_temp)))
                    if reaction.custom_emoji:
                        print("This is a custom emoji from SkyNet!")
                    else:
                        print("This is not a custom Emoji")
                    members_roles = member_temp.roles
                    if mysql_role in members_roles:
                        print("User already has mysql_role role")
                        await bot_channel.send(("You already have the MySQL role {0.mention}!!".format(member_temp)))

                    else:
                        print("Adding mysql_role role!")
                        await member_temp.add_roles(mysql_role)
                        await bot_channel.send((
                            "Good job {0.mention}, you now have the MySQL".format(
                                member_temp)))
                elif emoji_temp == python_emoji:
                    print("python_emoji EMOJI")
                    print("EMOJI: " + str(emoji_temp))
                    print(str(type(emoji_temp)))
                    if reaction.custom_emoji:
                        print("This is a custom emoji from SkyNet!")
                    else:
                        print("This is not a custom Emoji")
                    members_roles = member_temp.roles
                    if python_role in members_roles:
                        print("User already has python_emoji role")
                        await bot_channel.send(("You already have the Python role {0.mention}!!".format(member_temp)))

                    else:
                        print("Adding python_emoji role!")
                        await member_temp.add_roles(python_role)
                        await bot_channel.send((
                            "Good job {0.mention}, you now have the Python Role".format(
                                member_temp)))
                elif emoji_temp == javascript_emoji:
                    print("javascript_emoji EMOJI")
                    print("EMOJI: " + str(emoji_temp))
                    print(str(type(emoji_temp)))
                    if reaction.custom_emoji:
                        print("This is a custom emoji from SkyNet!")
                    else:
                        print("This is not a custom Emoji")
                    members_roles = member_temp.roles
                    if javascript_role in members_roles:
                        print("User already has javascript_emoji role")
                        await bot_channel.send(
                            ("You already have the JavaScript role {0.mention}!!".format(member_temp)))

                    else:
                        print("Adding python_emoji role!")
                        await member_temp.add_roles(javascript_role)
                        await bot_channel.send((
                            "Good job {0.mention}, you now have the JavaScript Role".format(
                                member_temp)))
                elif emoji_temp == java_emoji:
                    print("java_emoji EMOJI")
                    print("EMOJI: " + str(emoji_temp))
                    print(str(type(emoji_temp)))
                    if reaction.custom_emoji:
                        print("This is a custom emoji from SkyNet!")
                    else:
                        print("This is not a custom Emoji")
                    members_roles = member_temp.roles
                    if java_role in members_roles:
                        print("User already has java_role role")
                        await bot_channel.send(("You already have the Java role {0.mention}!!".format(member_temp)))

                    else:
                        print("Adding java_role role!")
                        await member_temp.add_roles(java_role)
                        await bot_channel.send((
                            "Good job {0.mention}, you now have the Java Role".format(
                                member_temp)))
                else:
                    print("Wrong emoji!")
                    await message_object.remove_reaction(reaction, member_temp)
                    return

            elif message_id_temp == "795095361198096384":
                print("User Added TBA role!!")
            else:
                print("Unkown role message id??")
                print("Msg ID: " + message_id_temp)
        elif reacted_channel_id == admin_member_join_logger_channel_id:
            # first we check if the reaction was on a verification embed or not!

            if reaction.message.embeds:
                # this was indeed a message containing an embed
                reacted_message_embed = reaction.message.embeds[0]
            else:
                # message does not contain a embed, return
                return

            if str(reacted_message_embed.title) != "Verification Needed":
                # reacted message was not a verification embed, return
                return
            # this was indeed a verification message, continue by getting the member object to be verified:
            user_requesting_verification_id = int(reacted_message_embed.footer.text)
            user_requesting_verification = message_object.guild.get_member(user_requesting_verification_id)
            # we need to check if this was a member approve / deny verification reaction from an Admin!
            if not check_roles(member_temp, admin_role_id):
                # reactions was not added by an admin? we need to delete this!
                await reaction.remove(member_temp)
                return
            # check what reaction emoji it was
            emoji_string = str(emoji_temp)
            if emoji_string == '✔':
                # verify the member
                await verify_member(user_requesting_verification, client.get_channel(general_channel_id))
                await reaction.message.delete()

            elif emoji_string == '🟢':
                # in this case we will verify them, and then add all of their original roles if they had them
                roles_id_list = retrieve_members_role_ids(user_requesting_verification, users_dict_of_dict)
                await assign_list_of_roles_to_member(user_requesting_verification, roles_id_list)
                await verify_member(user_requesting_verification, client.get_channel(general_channel_id))
                await reaction.message.delete()
            elif emoji_string == '❌':
                # kick the member from server:
                type_of_pun = 'kick'
                human_called = True
                delete_msg_after = False
                ctx = None
                channel = None
                # perhaps replace this with admin reply at some stage? TODO: Admin replies here
                reason = "Sorry but we decided not to verify you at this time."

                await punishments(member_temp, ctx, client, type_of_pun, user_requesting_verification, reason,
                                  human_called,
                                  channel, delete_msg_after, member_temp.guild)
                await reaction.message.delete()
            else:
                await reaction.remove(member_temp)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Removes a role based on a reaction emoji."""
        # Make sure that the message the user is reacting to is the one we care about
        emoji_temp = payload.emoji
        reacted_channel_id = payload.channel_id
        reacted_channel_obj = client.get_channel(reacted_channel_id)
        member_temp = get(guild.members, id=payload.user_id)
        message_id_temp = str(payload.message_id)
        message_object = await reacted_channel_obj.fetch_message(payload.message_id)
        reaction = get(message_object.reactions, emoji=payload.emoji.name)

        try:
            print(reaction.custom_emoji)
        except:
            # This must be a custom emoji
            reaction = get(message_object.reactions, emoji=payload.emoji)

        if reacted_channel_id == role_assign_channel_id:
            print(member_temp.name + " has reacted to a role assign embed!")
            members_roles = member_temp.roles
            if message_id_temp == skynet_lab_role_assign_msg_id:
                print("User reacted to a LAB embed")
                print("EMOJI = " + str(emoji_temp))
                if str(emoji_temp) != "🧪":
                    print("WRONG EMOJI")
                    print("EMOJI: " + str(emoji_temp))
                    print(str(type(emoji_temp)))
                    if reaction.custom_emoji:
                        print("This is a custom emoji from SkyNet!")
                    else:
                        print("This is not a custom Emoji")

                    await message_object.remove_reaction(reaction, member_temp)
                    return
                print("User Removed LAB role!!")

                if skynet_lab_role in members_roles:
                    print("User already has LAB role")
                    await bot_channel.send(("We have removed your LAB role {0.mention}!!".format(member_temp)))
                    await member_temp.remove_roles(skynet_lab_role)

                else:
                    print("They already didnt have the LAB role!")
                    await bot_channel.send(
                        ("You did not have the LAB role in the first place?? {0.mention}".format(member_temp)))

            elif message_id_temp == wt_not_role_assign_msg_id:
                print("USER REMOVED WT ROLE")
                if str(emoji_temp) != "📖":
                    print("WRONG EMOJI")
                    print("EMOJI: " + str(emoji_temp))
                    print(str(type(emoji_temp)))
                    if reaction.custom_emoji:
                        print("This is a custom emoji from SkyNet!")
                    else:
                        print("This is not a custom Emoji")

                    await message_object.remove_reaction(reaction, member_temp)
                    return
                print("User Removed WT role!!")
                members_roles = member_temp.roles
                if wt_study_sub_role in members_roles:
                    print("User already has WT role")
                    await bot_channel.send(
                        ("We have removed your Watchtower Notifications role {0.mention}!!".format(member_temp)))
                    await member_temp.remove_roles(wt_study_sub_role)

                else:
                    print("They already didnt have the LAB role!")
                    await bot_channel.send(
                        ("You did not have the Watchtower Notifications role in the first place?? {0.mention}".format(
                            member_temp)))

            elif message_id_temp == jw_news_role_assign_id:
                print("USER REMOVED JW NEWS ROLE")
                if str(emoji_temp) != "📚":
                    print("WRONG EMOJI")
                    print("EMOJI: " + str(emoji_temp))
                    print(str(type(emoji_temp)))
                    if reaction.custom_emoji:
                        print("This is a custom emoji from SkyNet!")
                    else:
                        print("This is not a custom Emoji")

                    await message_object.remove_reaction(reaction, member_temp)
                    return
                print("User Removed JW NEWS role!!")
                members_roles = member_temp.roles
                if jw_news_sub in members_roles:
                    print("User already has JW NEWS role")
                    await bot_channel.send(
                        ("We have removed your JW News Notifications role {0.mention}!!".format(member_temp)))
                    await member_temp.remove_roles(jw_news_sub)

                else:
                    print("They already didnt have the JW News role!")
                    await bot_channel.send(
                        ("You did not have the JW News Notifications role in the first place?? {0.mention}".format(
                            member_temp)))

            elif message_id_temp == mc_updates_role_assign_msg_id:
                print("User Removed MC updates role!!")
                # Get emojis into memory
                bw_emoji = get(client.emojis, name='bedwars')
                tw_emoji = get(client.emojis, name='grass')
                ma_emoji = get(client.emojis, name='creeper')
                if str(emoji_temp) == "🕹":
                    print("🕹 EMOJI")
                    print("EMOJI: " + str(emoji_temp))
                    print(str(type(emoji_temp)))
                    if reaction.custom_emoji:
                        print("This is a custom emoji from SkyNet!")
                    else:
                        print("This is not a custom Emoji")

                    print("User Removed MC Updates role!!")
                    members_roles = member_temp.roles
                    if mc_server_updates_sub_role in members_roles:
                        print("User already has MC Updates role")
                        await bot_channel.send(
                            ("We have removed your MC Updates Notifications role {0.mention}!!".format(member_temp)))
                        await member_temp.remove_roles(mc_server_updates_sub_role)

                    else:
                        print("They already didnt have the MC Updates role!")
                        await bot_channel.send(
                            ("You did not have the MC Updates Notifications role in the first place?? {0.mention}".format(
                                member_temp)))
                elif emoji_temp == bw_emoji:
                    print("BW EMOJI")
                    print("EMOJI: " + str(emoji_temp))
                    print(str(type(emoji_temp)))
                    if reaction.custom_emoji:
                        print("This is a custom emoji from SkyNet!")
                    else:
                        print("This is not a custom Emoji")

                    print("User Removed MC BW role!!")
                    members_roles = member_temp.roles
                    if bedwars_notifications_role in members_roles:
                        print("User already has bedwars_notifications_role role")
                        await bot_channel.send(
                            ("We have removed your BedWars Games Notifications role {0.mention}!!".format(member_temp)))
                        await member_temp.remove_roles(bedwars_notifications_role)

                    else:
                        print("They already didnt have the bedwars_notifications_role role!")
                        await bot_channel.send(
                            (
                                "You did not have the BedWars Games Notifications role in the first place?? {0.mention}".format(
                                    member_temp)))
                elif emoji_temp == tw_emoji:
                    print("TW EMOJI")
                    print("EMOJI: " + str(emoji_temp))
                    print(str(type(emoji_temp)))
                    if reaction.custom_emoji:
                        print("This is a custom emoji from SkyNet!")
                    else:
                        print("This is not a custom Emoji")

                    print("User Removed MC TW role!!")
                    members_roles = member_temp.roles
                    if turfwars_notifications_role in members_roles:
                        print("User already has turfwars_notifications_role role")
                        await bot_channel.send(
                            ("We have removed your TurfWars Games Notifications role {0.mention}!!".format(member_temp)))
                        await member_temp.remove_roles(turfwars_notifications_role)

                    else:
                        print("They already didnt have the turfwars_notifications_role role!")
                        await bot_channel.send(
                            (
                                "You did not have the TurfWars Games Notifications role in the first place?? {0.mention}".format(
                                    member_temp)))
                elif emoji_temp == ma_emoji:
                    print("MA EMOJI")
                    print("EMOJI: " + str(emoji_temp))
                    print(str(type(emoji_temp)))
                    if reaction.custom_emoji:
                        print("This is a custom emoji from SkyNet!")
                    else:
                        print("This is not a custom Emoji")

                    print("User Removed MC MA role!!")
                    members_roles = member_temp.roles
                    if mobarena_notifications_role in members_roles:
                        print("User already has mobarena_notifications_role role")
                        await bot_channel.send(
                            ("We have removed your MobArena Games Notifications role {0.mention}!!".format(member_temp)))
                        await member_temp.remove_roles(mobarena_notifications_role)

                    else:
                        print("They already didnt have the mobarena_notifications_role role!")
                        await bot_channel.send(
                            (
                                "You did not have the MobArena Games Notifications role in the first place?? {0.mention}".format(
                                    member_temp)))

            elif message_id_temp == programmer_role_assign_msg_id:
                print("User Removed Programmer role!!")
                cplusplus_emoji = get(client.emojis, name='cplusplus')
                my_sql_emoji = get(client.emojis, name='mysql')
                python_emoji = get(client.emojis, name='python')
                javascript_emoji = get(client.emojis, name='javascript')
                java_emoji = get(client.emojis, name='java')
                if emoji_temp == cplusplus_emoji:
                    print("cplusplus_emoji EMOJI")
                    print("EMOJI: " + str(emoji_temp))
                    print(str(type(emoji_temp)))
                    if reaction.custom_emoji:
                        print("This is a custom emoji from SkyNet!")
                    else:
                        print("This is not a custom Emoji")

                    print("User Removed cplusplus_emoji role!!")
                    members_roles = member_temp.roles
                    if cplusplus_role in members_roles:
                        print("User has cplusplus_emoji role")
                        await bot_channel.send(
                            ("We have removed your C++ role {0.mention}!!".format(member_temp)))
                        await member_temp.remove_roles(cplusplus_role)

                    else:
                        print("They already didnt have the cplusplus_emoji role!")
                        await bot_channel.send(
                            ("You did not have the C++ role in the first place?? {0.mention}".format(
                                member_temp)))
                elif emoji_temp == my_sql_emoji:
                    print("my_sql_emoji EMOJI")
                    print("EMOJI: " + str(emoji_temp))
                    print(str(type(emoji_temp)))
                    if reaction.custom_emoji:
                        print("This is a custom emoji from SkyNet!")
                    else:
                        print("This is not a custom Emoji")

                    print("User Removed my_sql_emoji role!!")
                    members_roles = member_temp.roles
                    if mysql_role in members_roles:
                        print("User has mysql_role role")
                        await bot_channel.send(
                            ("We have removed your MySQL role {0.mention}!!".format(member_temp)))
                        await member_temp.remove_roles(mysql_role)

                    else:
                        print("They already didnt have the mysql_role role!")
                        await bot_channel.send(
                            ("You did not have the MySQL role in the first place?? {0.mention}".format(
                                member_temp)))
                elif emoji_temp == python_emoji:
                    print("python_emoji EMOJI")
                    print("EMOJI: " + str(emoji_temp))
                    print(str(type(emoji_temp)))
                    if reaction.custom_emoji:
                        print("This is a custom emoji from SkyNet!")
                    else:
                        print("This is not a custom Emoji")

                    print("User Removed python_emoji role!!")
                    members_roles = member_temp.roles
                    if python_role in members_roles:
                        print("User has python_role role")
                        await bot_channel.send(
                            ("We have removed your Python role {0.mention}!!".format(member_temp)))
                        await member_temp.remove_roles(python_role)

                    else:
                        print("They already didnt have the python_role role!")
                        await bot_channel.send(
                            ("You did not have the Python role in the first place?? {0.mention}".format(
                                member_temp)))
                elif emoji_temp == javascript_emoji:
                    print("javascript_emoji EMOJI")
                    print("EMOJI: " + str(emoji_temp))
                    print(str(type(emoji_temp)))
                    if reaction.custom_emoji:
                        print("This is a custom emoji from SkyNet!")
                    else:
                        print("This is not a custom Emoji")

                    print("User Removed javascript_emoji role!!")
                    members_roles = member_temp.roles
                    if javascript_role in members_roles:
                        print("User has javascript_role role")
                        await bot_channel.send(
                            ("We have removed your JavaScript role {0.mention}!!".format(member_temp)))
                        await member_temp.remove_roles(javascript_role)

                    else:
                        print("They already didnt have the mysql_role role!")
                        await bot_channel.send(
                            ("You did not have the JavaScript role in the first place?? {0.mention}".format(
                                member_temp)))
                elif emoji_temp == java_emoji:
                    print("java_emoji EMOJI")
                    print("EMOJI: " + str(emoji_temp))
                    print(str(type(emoji_temp)))
                    if reaction.custom_emoji:
                        print("This is a custom emoji from SkyNet!")
                    else:
                        print("This is not a custom Emoji")

                    print("User Removed java_emoji role!!")
                    members_roles = member_temp.roles
                    if java_role in members_roles:
                        print("User has java_role role")
                        await bot_channel.send(
                            ("We have removed your Java role {0.mention}!!".format(member_temp)))
                        await member_temp.remove_roles(java_role)

                    else:
                        print("They already didnt have the java_role role!")
                        await bot_channel.send(
                            ("You did not have the Java role in the first place?? {0.mention}".format(
                                member_temp)))

            elif message_id_temp == "795095361198096384":
                print("User Removed TBA role!!")
            else:
                print("Unkown role message id??")
                print("Msg ID: " + message_id_temp)


async def setup(client):
    await client.add_cog(Events(client))
