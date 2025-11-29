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

if not os.path.exists('bot/logs'):
    os.makedirs('bot/logs')


logUtil.log(f'\nBot started at {datetime.datetime.now()}')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='.', intents=intents)
@bot.event
async def on_ready():
    print(f'Bot logged in as {bot.user}')
    logUtil.log(f'Bot logged in as {bot.user} at {datetime.datetime.now()}')

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
        await message.delete()
        if message.content.lower() == 'goobr':
            role = message.guild.get_role(1444078313177092171)
            logUtil.log(f'User {message.author} was granted the member role at {datetime.datetime.now()}')
            await message.author.add_roles(role)
    await bot.process_commands(message)

@bot.command()
async def mute(ctx, member: discord.Member, duration:int, *, reason=None):
    try:
        duration = int(duration)
    except ValueError:
        await ctx.send("Duration must be an integer representing minutes.")
        return
    if not ctx.author.guild_permissions.moderate_members:
        await ctx.send("You do not have permission to use this command.")
        return
    await member.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=duration), reason=reason)
    embed = discord.Embed(title="User Muted", description=f"{member} has been muted for {duration} minutes.", color=0xff0000)
    await ctx.send(embed=embed)

@bot.command()
async def cat(ctx):
    # Send an initial "Searching for a cat..." message
    msg = await ctx.send("Searching for a cat...")

    try:
        # Send request to the API
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:3000/api/cat') as response:
                if response.status != 200:
                    # If the request fails, update the message to indicate failure
                    await msg.edit(content=f"Failed to fetch cat image. HTTP Status: {response.status}")
                    return
                
                # Get the text (URL of the cat image)
                cat_image_url = await response.text()

                if cat_image_url:
                    # Edit the message to show the cat image URL
                    embed = discord.Embed(title="Found a cat!")
                    embed.set_image(url=cat_image_url)
                    await msg.edit(content="", embed=embed)
                else:
                    # If there's no image URL in the response
                    await msg.edit(content="No image found in the API response.")
    
    except Exception as e:
        # Handle any other exceptions (e.g., connection issues)
        await msg.edit(f"An error occurred: {str(e)}")
        print(f"Error fetching cat data: {e}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member:discord.Member, *, reason=None):
    try:
        if not reason == None:
            await member.ban(reason=f"By {ctx.author}\nReason: {reason}")
            return
        await member.ban(reason=f"By {ctx.author}\nReason: No reason provided.")
    except AttributeError:
        await ctx.send("i fucked up")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        try:
            response = ollama.generate('mistral', f'A user just tried banning someone from the Discord server without sufficient permissions. Make a message that brutally calls them out for it. You\'re directly sending this message, so don\'t act like you\'re talking to me, instead, send ONLY the message. Keep it short. They didn\'t successfully ban them, the bot didn\'t let them.')
            message = response['response']
            await ctx.send(message)
        except:
            messages = ["you disgust me.",
                        "check your permissions first",
                        "try getting... i dunno, an admin to do that?",
                        "soo, when are you giving up?,"
                        "announcing your stupidity to the entire server",
                        "when do i get a pay raise?",
                        "why should i even have to deal with people like you?"]
            message = random.choice(messages)
            await ctx.send(message)
                        

@bot.command()
async def test(ctx):
    await ctx.send("The bot is working!")

def start():
    bot.run(token)