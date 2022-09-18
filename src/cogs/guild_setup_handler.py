from discord.ext import commands
import src.configuration as configuration
import src.database as database


class GuildSetupHandler(commands.Cog):
    # ----- __init__ function runs on reload ----- #
    def __init__(self, bot):
        self.bot = bot
        self.guild = self.bot.get_guild(configuration.ConfigFile.root_conf['general_info']['guild_id'])

    # ----- on_ready function runs on startup ----- #
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.command(
        name='save_all_member_roles', description="Save all users roles into DB"
    )
    @commands.is_owner()
    async def save_all_member_roles(self, ctx):
        print("save_all_member_roles")
        for member in self.guild.members:
            role_ids = []
            for role in member.roles:
                role_ids.append(role.id)
            database.update_user_roles(member, role_ids)


async def setup(bot):
    await bot.add_cog(GuildSetupHandler(bot))
