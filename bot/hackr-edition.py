credentials_folder = "config/credentials"
import os
import discord
import datetime
import functions.writeToLog as logUtil
from discord.ext import commands

with open('config/credentials/token', 'r') as f:
    bot_token = f.read()

if not os.path.exists('logs'):
    os.makedirs('logs')

logUtil.log(f'\nBot started at {datetime.datetime.now()}')

intents = discord.Intents.default()

intents.message_content = True
bot = commands.Bot(command_prefix='.', intents=intents)

@bot.event
async def on_ready():
    print(f'okie so like {bot.user} has logged in or whatever')
    logUtil.log(f'Bot logged in as {bot.user} at {datetime.datetime.now()}')
    await bot.load_extension('commands.say')

"""
@bot.command()
async def say(ctx, *, message):
    try:
        
        
        await ctx.send(message)
        logUtil.log(f'Said message "{message}" for {ctx.author} at {datetime.datetime.now()}')
    except Exception as e:
        await ctx.send('An error occurred while trying to send your message.')
        logUtil.log(f'Error sending message for {ctx.author} at {datetime.datetime.now()}: {e}')
"""
bot.run(bot_token)