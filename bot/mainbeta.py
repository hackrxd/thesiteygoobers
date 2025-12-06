token = None
with open('bot/config/credentials/token', 'r') as f:
    token = f.read()
import discord
from discord.ext import commands
import bot.functions.writeToLog as logUtil
import datetime
import os
import asyncio
import requests
import aiohttp
import ollama
import random
import server
from discord import app_commands

if not os.path.exists('bot/logs'):
    os.makedirs('bot/logs')


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
    if message.author == bot.user:
        return
    if isinstance(message.channel, discord.DMChannel):
        author = message.author.display_name
        content = message.content
        server.updateQuote(content, author)
    if message.channel.id == 1444158624380358757 and message.guild:
        try:
            await message.delete()
        except discord.RateLimited:
            logUtil.log(f"Bot was ratelimited while trying to delete a message.")
        if message.content.lower() == 'goobr':
            role = message.guild.get_role(1444078313177092171)
            logUtil.log(f'User {message.author} was granted the member role.')
            await message.author.add_roles(role)
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
            async with session.get('http://localhost:3000/api/cat') as response:
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
        with open(f"bot/cmdsuggestions/{command}.md", 'w') as f:
            f.write(f"# {command}\n\n{description}\n\n##### Requested by {interaction.user.name}")
            await interaction.response.send_message(content="Your suggestion has been saved.", ephemeral=True)
            logUtil.log(f"{interaction.user.name} suggested a command: {command}")
    except Exception as e:
        await interaction.response.send_message(content=f"Suggestion failed to save: {e}", ephemeral=True)
        logUtil.log(f"{interaction.user.name} tried suggesting a command, but an exception occured! {e}")

@bot.command()
@commands.is_owner()
async def sync(ctx: commands.Context):
    # Syncs only to the current guild where the command is used
    if ctx.guild:
        bot.tree.copy_global_to(guild=ctx.guild) # Optional: copies global commands to the test guild
        synced = await bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"Synced {len(synced)} commands to **{ctx.guild.name}** instantly.")
    else:
        await ctx.send("This command must be used in a guild to sync instantly.")


def start():
    try:
        bot.run(token)
    except discord.RateLimited:
        logUtil.log(f"Bot was ratelimited at {datetime.datetime.now}")