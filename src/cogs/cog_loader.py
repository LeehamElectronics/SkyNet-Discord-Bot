import os
import traceback
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from discord import Interaction
from discord.app_commands import AppCommandError


class CogLoader(commands.Cog):
    # ----- __init__ function runs on reload ----- #
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        bot.tree.on_error = on_app_command_error

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @app_commands.checks.has_any_role('Owner', 'Admin')
    @app_commands.command(name="reload", description="Reload all/one of the bots cogs")
    async def reload_cogs(self, interaction: discord.Interaction, cog: str) -> None:
        """ /command-reload """
        if not cog:
            # No cog, means we reload all cogs
            print("Reloading all cogs")
            embed = discord.Embed(
                title="Reloading all cogs!",
                color=0x808080
            )
            for ext in os.listdir("./cogs/"):
                if ext.endswith(".py") and not ext.startswith("_"):
                    try:
                        await self.bot.unload_extension(f"cogs.{ext[:-3]}")
                        await self.bot.load_extension(f"cogs.{ext[:-3]}")
                        embed.add_field(
                            name=f"Reloaded: `{ext}`",
                            value='\uFEFF',
                            inline=False
                        )
                    except:
                        try:  # Run a second try method in case the cog was already unloaded.
                            await self.bot.load_extension(f"cogs.{ext[:-3]}")
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
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            # reload the specific cog
            print("Reloading specific cog")
            embed = discord.Embed(
                title=f"Reloading {cog} cog!",
                color=0x808080
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
                    await self.bot.unload_extension(f"cogs.{ext[:-3]}")
                    await self.bot.load_extension(f"cogs.{ext[:-3]}")
                    embed.add_field(
                        name=f"Reloaded: `{ext}`",
                        value='\uFEFF',
                        inline=False
                    )
                except Exception:
                    try:  # Run a second try method in case the cog was already unloaded.
                        await self.bot.load_extension(f"cogs.{ext[:-3]}")
                        embed.add_field(
                            name=f"Loaded: `{ext}`",
                            value='\uFEFF',
                            inline=False
                        )
                    except Exception as e:
                        # desired_trace = traceback.format_exc()
                        embed.add_field(
                            name=f"Failed to reload: `{ext}`",
                            value=e,
                            inline=False
                        )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @reload_cogs.autocomplete('cog')
    async def reload_cogs_autocomplete(self, interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        cogs = ['cog_loader', 'invite', 'guild_setup_handler', 'message_events']
        return [
            app_commands.Choice(name=cog, value=cog)
            for cog in cogs if current.lower() in cog.lower()
        ]


# error handler
async def on_app_command_error(interaction: Interaction, error: AppCommandError):
    print(error)
    await interaction.response.send_message('no', ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CogLoader(bot))

