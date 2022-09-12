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
from main import share_users_dict_of_dict_elsewhere
from main import import_users_dict_of_dict_db
from datetime import date
from datetime import datetime
import yaml


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
        print("🟢 Events.py loaded successfully.\n-----")
        self.config = share_global_config_dict_elsewhere()
        self.user_db_path = self.config['general_info']['user_db_path'] + '.json'
        self.channel_ids = self.config['discord_channel_ids']
        self.admin_member_join_logger_channel = self.client.get_channel(
            self.channel_ids['admin_channel_ids']['admin_member_join_logger_channel_id'])
        self.rules_channel = self.client.get_channel(self.channel_ids['general_channels']['rules_channel_id'])
        self.bot_channel = self.client.get_channel(self.channel_ids['general_channels']['bot_channel_id'])
        self.role_assign_channel = self.client.get_channel(
            self.channel_ids['misc_channel_ids']['role_assign_channel_id'])

    # We need to send a small message into the public member join channel saying that someone has joined, awaiting
    # verification. Don't send username or profile pic in case it is not PG. Then once the user has been verified, send
    # a message into the channel saying that they have been verified!
    @commands.Cog.listener()
    async def on_member_join(self, member):
        # A way to make the following code run just before on_member_join occurs? I need to do this in order to keep
        # track of who invited who on my server. Thanks
        invites_after_join = await member.guild.invites()

        print(str(member.name) + " joined discord server")
        await self.client.wait_until_ready()  # Stops code from running when the Bot has not yet fully loaded up.
        user_db_path = self.user_db_path  # At end of function we will backup user db

        the_people_channel = discord.utils.get(member.guild.text_channels, name="the-people")  # Change this back to ID
        admin_role = get(member.guild.roles, id=self.config['discord_role_ids']['general_roles']['admin'])

        total_bot_count = 5  # Need to make this automatic
        total_member_count_val = member.guild.member_count - total_bot_count  # Will use this in embeds

        user_db = share_users_dict_of_dict_elsewhere()  # get current user_db

        # Getting the invites before the user joining
        # from our cache for this specific guild
        with open(str(self.config['general_info']['invites_db_path'])) as file:
            invites_before_join = yaml.load(file, Loader=yaml.FullLoader)

        # Getting the invites after the user joining so we can compare it with the first one, and see which invite uses
        # number increased
        invites_after_join = await member.guild.invites()
        print("INVITE OBJ TYPE:")
        print(str(type(invites_after_join)))
        print(invites_after_join)
        print("LENGTHS:")
        print(str(len(invites_before_join)))
        print(str(len(invites_after_join)))
        # Now we will update the invites JSON so it's ready for next time!
        simplified_invites = {}
        for invite in invites_after_join:
            # create temp dict obj
            invite_dict = {'name': str(invite.inviter.name), 'code': str(invite.code), 'uses': str(invite.uses)}
            # append the dict into a list
            simplified_invites[str(invite.code)] = invite_dict

        with open(str(self.config['general_info']['invites_db_path']), 'w') as file:
            yaml.dump(simplified_invites, file)
        # Loops for each invite we have for the guild the user joined.
        found = False

        if simplified_invites == invites_before_join:
            print("THERE EXACTLY THE SAME HECKKKK")

        if len(invites_after_join) != len(invites_before_join):
            print("Amount of invites before is not the same as after, hence a new invite was created...")
            for invite in invites_after_join:
                if str(invite.code) not in invites_before_join:
                    print("CONFIRMED THE INIVTE IS NEW WOOOOW HERE IT IS BOIIS")

        if invites_after_join not in invites_before_join:
            print("This was a NEW invite:")
            for invite_obj_temp in invites_before_join:
                # Now, we're using the function we created just before to check which invite count is bigger than it was
                # before the user joined.
                invite_code = invites_before_join[invite_obj_temp]['code']
                invite_uses = int(invites_before_join[invite_obj_temp]['uses'])
                # TODO: Does this account for BRAND new invite codes????

                new_invite_obj = find_invite_by_code(invites_after_join, invite_code)

                if invite_uses < new_invite_obj.uses:
                    found = True
                    # Now that we found which link was used, we will print a couple things in our console; the name, invite
                    # code used, and the person who created the invite code, or the inviter.
                    print(f"Member {member.name} Joined")
                    print(f"Invite Code: {invite_code}")
                    print(f"Inviter: {new_invite_obj.inviter}")
                    # We will now update our cache so it's ready
                    # for the next user that joins the guild
                    # We break here since we already found which
                    # one was used and there is no point in
                    # looping when we already got what we wanted
                    break
            if not found:
                # Somehow we did not find the associated invite, lets report this and return a None object
                new_invite_obj = None  # Perhaps turn this into a default invite obj?
                print("INIVTE NOT FOUND")

        member_id_temp = str(member.id)
        inviter_id_temp = str(new_invite_obj.inviter.id)
        inviter_user = new_invite_obj.inviter

        current_date = get_pretty_date_format()

        if member_id_temp in user_db:
            # This code runs if the user that has joined the server was ALREADY a member in the past... (they rejoined)
            # We will need to add their original roles back...
            print('This user has already been invited to this server before, they must be REJOINING!')

            # update user db in case there has been a new change to db format, they will need to be updated.
            user_db = update_member_data(member, user_db)
            user_db = update_member_data(inviter_user, user_db)

            if user_db[member_id_temp]["invited_by"] == "Unknown":
                # This code runs when a user rejoins the server, but we do not know who the original inviter was
                # Rejoined embed but without the "Originally invited part in it"!
                user_db[member_id_temp]["invited_by"] = inviter_id_temp
                user_db[inviter_id_temp]["invites"] += 1
                user_db[inviter_id_temp]["invited"].append(int(member_id_temp))
                inviter_count_temp = str(user_db[inviter_id_temp]["invites"])

                member_join_embed = discord.Embed(
                    title=f'{member.name}' + " Re-Joined!",
                    description='For a total of ' + f'{total_member_count_val} Members',
                    color=discord.Colour.orange()
                )
                member_join_embed.set_footer(text=current_date)
                member_join_embed.set_thumbnail(url=str(member.avatar_url))
                member_join_embed.set_author(name="SkyNet", icon_url="https://i.imgur.com/BQLKiEh.png")
                member_join_embed.add_field(
                    name="Invited by " + str(new_invite_obj.inviter.name),
                    value=str(inviter_user.name) + "'s  total invitations: " +
                          inviter_count_temp, inline=False)
                await the_people_channel.send(embed=member_join_embed)

            else:
                # This code runs if a user rejoins the server, and we know for sure who the original inviter was:
                original_inviter = self.client.get_user(int(user_db[member_id_temp]["invited_by"]))
                inviter_count_temp = str(user_db[inviter_id_temp]["invites"])

                # Member Join Embed
                member_join_embed = discord.Embed(
                    title=f'{member.name}' + " Re-Joined!",
                    description='For a total of ' + f'{total_member_count_val} Members',
                    color=discord.Colour.orange()
                )
                member_join_embed.set_footer(text=current_date)
                member_join_embed.set_thumbnail(url=str(member.avatar_url))
                member_join_embed.set_author(name="SkyNet", icon_url="https://i.imgur.com/BQLKiEh.png")
                member_join_embed.add_field(
                    name="Invited by: " + str(inviter_user.name) + " (originally invited by: " + str(
                        original_inviter.name) + ")",
                    value=str(inviter_user.name) + "'s  total invitations: " + inviter_count_temp, inline=False)
                # member_join_embed.add_field(name="", value="", inline=False)
                await the_people_channel.send(embed=member_join_embed)
        else:
            #  This code runs when a new user that has never joined SkyNet has just joined

            # update user db with NEW member
            user_db = update_member_data(member, user_db)
            user_db = update_member_data(inviter_user, user_db)

            print("NEW member, adding to invite_count...")
            user_db[member_id_temp]["invited_by"] = inviter_id_temp
            user_db[inviter_id_temp]["invites"] += 1
            user_db[inviter_id_temp]["invited"].append(int(member_id_temp))
            inviter_count_temp = str(user_db[inviter_id_temp]["invites"])
            xp_reward = (int(inviter_count_temp) * 50) + 500

            # Member Join Embed
            member_join_embed = discord.Embed(
                title=f'{member.name}' + " Joined!",
                description='For a total of ' + f'{total_member_count_val} Members',
                color=discord.Colour.orange()
            )
            member_join_embed.add_field(name="Invited by: " + str(new_invite_obj.inviter.name),
                                        value=new_invite_obj.inviter.name + "'s  total invitations: " + inviter_count_temp,
                                        inline=False)
            member_join_embed.add_field(name="Please Read Our Rules!", value="{0.mention}".format(self.rules_channel),
                                        inline=False)
            member_join_embed.add_field(name="(IMPORTANT) Subscribe to your Roles!",
                                        value="{0.mention}".format(self.role_assign_channel),
                                        inline=False)
            member_join_embed.set_footer(text=current_date)
            member_join_embed.set_thumbnail(url=str(member.avatar_url))
            member_join_embed.set_author(name="SkyNet", icon_url="https://i.imgur.com/BQLKiEh.png")
            await the_people_channel.send("Welcome {0.mention}".format(member))
            await the_people_channel.send(embed=member_join_embed)

            join_reward_embed = discord.Embed(
                title=f'{new_invite_obj.inviter.name}' + " Invited Someone New!",
                description='For a total of ' + f'{total_member_count_val} Members',
                color=discord.Colour.orange()
            )
            join_reward_embed.set_footer(text=current_date)
            join_reward_embed.set_thumbnail(url=str(new_invite_obj.inviter.avatar_url))
            join_reward_embed.set_author(name="SkyNet Rewards", icon_url="https://i.imgur.com/BQLKiEh.png")
            join_reward_embed.add_field(name="Member Invite Reward",
                                        value="Good Job {0.mention} for inviting {1}, You have now invited a total of {2} "
                                              "people and as a reward received {3} XP".format(new_invite_obj.inviter,
                                                                                              member.name,
                                                                                              inviter_count_temp,
                                                                                              xp_reward), inline=False)
            join_reward_embed.set_image(url="https://i.imgur.com/MejZgaS.png")

            await self.bot_channel.send("Great Job {0.mention}!".format(new_invite_obj.inviter))
            await self.bot_channel.send(embed=join_reward_embed)
            user_db = await manual_add_experience(new_invite_obj.inviter, xp_reward, self.bot_channel, user_db)

        ########################################
        # Find how many days old an account is #
        ########################################

        # date the account was created
        account_created = member.created_at
        year = int(account_created.strftime("%Y"))
        month = int(account_created.strftime("%m"))
        day = int(account_created.strftime("%d"))
        created_date = date(year, month, day)

        # today's date
        now = datetime.now()
        year = int(now.strftime("%Y"))
        month = int(now.strftime("%m"))
        day = int(now.strftime("%d"))
        today = date(year, month, day)

        # Calculate gap
        gap = (today - created_date).days

        new_line = '\n'

        original_inviter = self.client.get_user(int(user_db[member_id_temp]["invited_by"]))
        logger_embed = discord.Embed(
            title="Verification Needed",
            description=f"New User: {member.mention}",
            color=discord.Colour.orange()
        )
        logger_embed.add_field(
            name=f"Account is {gap} days old.",
            value=f"They were invited by: {str(new_invite_obj.inviter.name)} and originally invited by: {str(original_inviter.name)}", inline=False)
        logger_embed.add_field(name="Controls", value=f"✔ Verify {new_line}🟢 Verify + Add Original Roles {new_line}❌ Deny + Kick user", inline=False)
        logger_embed.set_footer(text=str(member.id))
        logger_embed.set_thumbnail(url=str(member.avatar_url))
        logger_embed.set_author(name="SkyNet", icon_url="https://i.imgur.com/BQLKiEh.png")

        await self.admin_member_join_logger_channel.send("{0.mention} Verification is needed!".format(admin_role))
        message_ref = await self.admin_member_join_logger_channel.send(embed=logger_embed)
        # Added reactions to message to approve / deny, also add a shortcut into verification channel!!!
        await message_ref.add_reaction(emoji='✔')
        await message_ref.add_reaction(emoji='🟢')
        await message_ref.add_reaction(emoji='❌')

        # Finally we need to pass back the user db into main.py
        import_users_dict_of_dict_db(user_db)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if len(before.roles) != len(after.roles):
            print("ROLE CHANCE")
            # add this new role list into the members db
            role_id_list = []
            for role in after.roles:
                role_id_list.append(role.id)
            db = share_users_dict_of_dict_elsewhere()
            db[str(after.id)]['member_roles'] = role_id_list
            import_users_dict_of_dict_db(db)
            print(str(db[str(after.id)]))


def setup(client):
    client.add_cog(Events(client))
