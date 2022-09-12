import os
import traceback
import asyncio
import discord
from discord.ext import commands


class Config(commands.Cog):
    # ----- __init__ function runs on reload ----- #
    def __init__(self, bot):
        self.bot = bot

    # ----- on_ready function runs on startup ----- #
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    ##################################################
    #             Command Methods Below              #
    ##################################################
    # TODO: Move these into a reaction GUI!
    # ------------------------- reload (load / unload included) command ------------------------------ #
    @commands.command(
        name='reload', description="Reload all/one of the bots cogs!"
    )
    @commands.is_owner()
    async def reload(self, ctx, cog=None):
        if not cog:
            # No cog, means we reload all cogs
            print("Reloading all cogs")
            async with ctx.typing():
                embed = discord.Embed(
                    title="Reloading all cogs!",
                    color=0x808080,
                    timestamp=ctx.message.created_at
                )
                for ext in os.listdir("./cogs/"):
                    if ext.endswith(".py") and not ext.startswith("_"):
                        try:
                            self.bot.unload_extension(f"cogs.{ext[:-3]}")
                            self.bot.load_extension(f"cogs.{ext[:-3]}")
                            embed.add_field(
                                name=f"Reloaded: `{ext}`",
                                value='\uFEFF',
                                inline=False
                            )
                        except:
                            try:  # Run a second try method in case the cog was already unloaded.
                                self.bot.load_extension(f"cogs.{ext[:-3]}")
                                embed.add_field(
                                    name=f"Loaded: `{ext}`",
                                    value='\uFEFF',
                                    inline=False
                                )
                            except Exception as e:
                                embed.add_field(
                                    name=f"Failed to reload: `{ext}`",
                                    value=e[:1024],
                                    inline=False
                                )
                        await asyncio.sleep(0.5)
                await ctx.send(embed=embed)
        else:
            # reload the specific cog
            print("Reloading specific cog")
            async with ctx.typing():
                embed = discord.Embed(
                    title=f"Reloading {cog} cog!",
                    color=0x808080,
                    timestamp=ctx.message.created_at
                )
                ext = f"{cog.lower()}.py"
                if not os.path.exists(f"./cogs/{ext}"):
                    # if the file does not exist
                    embed.add_field(
                        name=f"Failed to reload: `{ext}`",
                        value="This cog does not exist.",
                        inline=False
                    )

                elif ext.endswith(".py") and not ext.startswith("_"):
                    try:
                        self.bot.unload_extension(f"cogs.{ext[:-3]}")
                        self.bot.load_extension(f"cogs.{ext[:-3]}")
                        embed.add_field(
                            name=f"Reloaded: `{ext}`",
                            value='\uFEFF',
                            inline=False
                        )
                    except Exception:
                        try:  # Run a second try method in case the cog was already unloaded.
                            self.bot.load_extension(f"cogs.{ext[:-3]}")
                            embed.add_field(
                                name=f"Loaded: `{ext}`",
                                value='\uFEFF',
                                inline=False
                            )
                        except Exception as e:
                            desired_trace = traceback.format_exc()
                            embed.add_field(
                                name=f"Failed to reload: `{ext}`",
                                value=desired_trace[:1024],
                                inline=False
                            )
                await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Config(bot))
