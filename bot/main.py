token = None
with open('config/credentials/token', 'r') as f:
    token = f.read()
import discord
from discord.ext import commands
import functions.writeToLog as logUtil
import datetime
import os
if not os.path.exists('logs'):
    os.makedirs('logs')


logUtil.log(f'\nBot started at {datetime.datetime.now()}')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='.', intents=intents)
@bot.event
async def on_ready():
    print(f'Bot logged in as {bot.user}')
    logUtil.log(f'Bot logged in as {bot.user} at {datetime.datetime.now()}')
    await bot.load_extension('commands.say')

#message listener
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.channel.id == 1438339555190116502 and message.guild:
        await message.delete()
        if message.content.lower() == 'goobr':
            role = message.guild.get_role(1444078313177092171)
            logUtil.log(f'User {message.author} was granted the member role at {datetime.datetime.now()}')
            await message.author.add_roles(role)

@bot.command
async def mute(ctx, member: discord.Member, duration:int, *, reason=None):
    try:
        duration = int(duration)
    except ValueError:
        await ctx.send("Duration must be an integer representing minutes.")
        return
    if not ctx.author.guild_permissions.moderate_members:
        await ctx.send("You do not have permission to use this command.")
        return
    member.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=duration), reason=reason)
    embed = discord.Embed(title="User Muted", description=f"{member} has been muted for {duration} minutes.", color=0xff0000)
    await ctx.send(embed=embed)

bot.run(token)