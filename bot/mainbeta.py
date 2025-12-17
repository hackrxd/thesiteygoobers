token = None
with open('config/credentials/token', 'r') as f:
    token = f.read()
import discord
from discord.ext import commands
import functions.writeToLog as logUtil
import datetime
import os
import asyncio
import requests
import aiohttp
import ollama
import random
from discord import app_commands

if not os.path.exists('logs'):
    os.makedirs('logs')


logUtil.log(f'\nBot started at {datetime.datetime.now()}')
intents = discord.Intents.default()
intents.message_content = True

class dbot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='.', intents=intents)
    
   # async def setup_hook(self) -> None:
        # await self.tree.sync(guild=discord.Object(id=1437612653051772981))

bot = dbot()
# bot = commands.Bot(command_prefix='.', intents=intents)

now = datetime.datetime.now()

@bot.event
async def on_ready():
    print(f'Bot logged in as {bot.user}')
    logUtil.log(f'Bot logged in as {bot.user}')
#message listener
@bot.event
async def on_message(message):
    # 1. Ignore messages sent by the bot itself
    if message.author == bot.user:
        return

    # 2. Handle Direct Messages (DM)
    if isinstance(message.channel, discord.DMChannel):
        author = message.author.display_name
        content = message.content
        
        try:
            async with aiohttp.ClientSession() as session:
                data = {
                    "author": author,
                    "message": content
                }

                # Correct usage of session.post with 'async with'
                async with session.post(url="http://192.168.1.178/api/updatewebtext", json=data) as resp:
                    # Optional: Check the status and consume the response body
                    if resp.status == 200:
                        response_text = await resp.text() # Consume the response body
                        await message.reply(f"Website quote attempted update (Status: {resp.status})")
                    else:
                        await message.reply(f"Website quote update failed (Status: {resp.status})")

        except aiohttp.ClientConnectorError as e:
            logUtil.log(f"aiohttp connection error to 192.178.1.178: {e}")
            await message.reply("Could not connect to the external website for quote update.")
        except Exception as e:
            logUtil.log(f"Unexpected error during DM handling: {e}")
            await message.reply("An unexpected error occurred during quote update.")

    # 3. Handle specific guild channel logic (assuming bot is in a guild)
    # The channel ID 1444158624380358757 is very long, make sure it's correct!
    if message.channel.id == 1444158624380358757 and message.guild:
        
        # Check for 'goobr' command before deleting messages in this channel
        if message.content.lower() == 'goobr':
            # Ensure message.guild is not None (checked above)
            role = message.guild.get_role(1444078313177092171) # The 'member' role ID
            
            if role:
                logUtil.log(f'User {message.author} was granted the member role at {datetime.datetime.now()}')
                await message.author.add_roles(role)
            else:
                logUtil.log(f"Could not find role with ID 1444078313177092171 in guild {message.guild.id}")
                
        # Attempt to delete the message
        try:
            # Delete message *after* processing its content (like 'goobr')
            await message.delete() 
        except discord.NotFound:
             # Message might have been deleted by someone else already
            pass
        except discord.Forbidden:
            logUtil.log(f"Bot lacks permissions to delete message in channel {message.channel.id}")
        except discord.HTTPException:
             # Covers RateLimited and other HTTP errors
            logUtil.log(f"Bot encountered an HTTP error while trying to delete a message at {datetime.datetime.now()}")


    # 4. Process commands registered via @bot.command()
    await bot.process_commands(message)

@bot.tree.command(name="test", description="sigh")
async def _ping(interaction: discord.Interaction) -> None:
        """Says when a member joined."""
        await interaction.response.send_message("hah, test!")

@bot.tree.command(name="cat", description="Displays an image of a cat from an extremely bad API")
async def _cat(interaction: discord.Interaction):
    await interaction.response.send_message("Searching for a cat...")  # initial reply

    # Retrieve the original message so we can edit it
    msg = await interaction.original_response()

    try:
        await asyncio.sleep(random.randint(1, 3))

        async with aiohttp.ClientSession() as session:
            async with session.get('http://192.168.1.178/api/cat') as response:
                if response.status != 200:
                    await msg.edit(content="no luck this time :(\n maybe there will be a cat next time!")
                    return

                cat_image_url = await response.text()

                if cat_image_url:
                    embed = discord.Embed(title="Found a cat!")
                    embed.set_image(url=cat_image_url)
                    await msg.edit(content="", embed=embed)
                    logUtil.log(f"Sent {interaction.user.name} an image of a cat.")
                else:
                    await msg.edit(content="no luck this time :(\n maybe there will be a cat next time!")
                    logUtil.log(f"Failed to send an image of a cat to {interaction.user.name} (no URL returned)")

    except Exception as e:
        await msg.edit(content=f"An error occurred: {str(e)}")
        print(f"Error fetching cat data: {e}")
        logUtil.log(f"Failed to send an image of a cat to {interaction.user.name}: {e}")

@bot.tree.command(name="rate", description="Gives a subject a rating from 1 to 100 of a specified unit")
async def _rate(interaction: discord.Interaction, subject: str, unit: str):
    rating = random.randint(1,100)
    await interaction.response.send_message(f"{subject} is {rating}% {unit}")
    logUtil.log(f"Rated {subject} of {unit}. Rating was {rating}.")

@bot.tree.command(name="suggest", description="Suggest a command to be added to the bot.")
@app_commands.describe(
    command="The name of the command you want added.",
    description="A description of what you want added to the bot."
)
async def _suggest(interaction: discord.Interaction, command: str, description: str):
    try:
        with open(f"cmdsuggestions/{command}.md", 'w') as f:
            f.write(f"# {command}\n\n{description}\n\n##### Requested by {interaction.user.name}")
            await interaction.response.send_message(content="Your suggestion has been saved.", ephemeral=True)
            logUtil.log(f"{interaction.user.name} suggested a command: {command}")
    except Exception as e:
        await interaction.response.send_message(content=f"Suggestion failed to save: {e}", ephemeral=True)
        logUtil.log(f"{interaction.user.name} tried suggesting a command, but an exception occured! {e}")

@bot.tree.command(name="rps", description="Play a game of Rock Paper Scissors with the bot.")
@app_commands.choices(options = [
    app_commands.Choice(name="rock", value="rock"),
    app_commands.Choice(name="paper", value="paper"),
    app_commands.Choice(name="scissors", value="scissors")
    ]
)
async def _rps(interaction: discord.Interaction, options:app_commands.Choice[str]):
    choices = [
        "rock",
        "paper",
        "scissors"
    ]
    choice = random.choice(choices)
    win = False
    message = None
    if options.value == "paper" and choice == "rock":
        win = True
    elif options.value == "scissors" and choice == "paper":
        win = True
    elif options.value == "rock" and choice == "scissors":
        win = True
    elif options.value == choice:
        win = None
    if win:
        message = f"You win!\n\nYour choice: **{options.value}**\nMy choice: **{choice}**"
        logUtil.log(f"Lost Rock Paper Scissors against {interaction.user.name}. I chose {choice}, they chose {options.value}.")
    elif win == None:
        message = f"It's a tie!\n\nYour choice: **{options.value}**\nMy choice: **{choice}**"
        logUtil.log(f"Tied in Rock Paper Scissors with {interaction.user.name}. I chose {choice}, they chose {options.value}.")
    else:
        message = f"I win!\n\nYour choice: **{options.value}**\nMy choice: **{choice}**"
        logUtil.log(f"Won Rock Paper Scissors against {interaction.user.name}. I chose {choice}, they chose {options.value}.")
    await interaction.response.send_message(content=message)

@bot.tree.command(name='togglemaintenence')
async def _mtoggle(interaction: discord.Interaction):
    if interaction.user.id == 759167810814476319:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:3000/dev/togglemaintenence') as response:
                await interaction.response.send_message("Web access toggled.")
    else:
        await interaction.response.send_message("Only <@759167810814476319> can run this command!")

@bot.tree.command(name='kick', description="Kicks a specified user from the guild")
@app_commands.checks.has_permissions(kick_members=True)
async def _kick(interaction:discord.Interaction, member: discord.Member, reason: discord.Optional[str]):
    if not reason:
        reason = "No reason provided."
    await interaction.guild.kick(member, reason=f"User {member.name} was kicked by {interaction.user} for reason:\n{reason}")
    await interaction.response.send_message(f"{member} has been kicked for reason\n\n```{reason}```")
        
@_kick.error
async def kick_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You do not have sufficient permissions to kick members.")
    elif isinstance(error, app_commands.BotMissingPermissions):
        await interaction.response.send_message("My role doesn't have the required permissions to kick members.")
    else:
        pass
@bot.command()
@commands.is_owner()
async def sync(ctx: commands.Context):
    # Syncs only to the current guild where the command is used
    if ctx.guild:
        bot.tree.copy_global_to(guild=ctx.guild) # Optional: copies global commands to the test guild
        synced = await bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"Synced {len(synced)} commands to **{ctx.guild.name}** instantly.")
        logUtil.log(f"Synced {len(synced)} commands to {ctx.guild.name}.")
    else:
        await ctx.send("This command must be used in a guild to sync instantly.")

@bot.command()
@commands.is_owner()
async def clear(ctx):
    if ctx.guild:
        bot.tree.clear_commands(guild=ctx.guild)
        await bot.tree.sync(guild=ctx.guild)
        await ctx.send("Cleared and resynced guild commands.")


def start():
    try:
        bot.run(token)
    except discord.RateLimited:
        logUtil.log(f"Bot was ratelimited at {datetime.datetime.now}")

start()