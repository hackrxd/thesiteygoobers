from discord.ext import commands
import datetime

class SayCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def say(self, ctx, *, message):
        """Makes the bot say a specified message."""
        try:
            await ctx.send(message)
            # Assuming logUtil is properly imported and configured
            import functions.writeToLog as logUtil
            logUtil.log(f'Said message "{message}" for {ctx.author} at {datetime.datetime.now()}')
        except Exception as e:
            await ctx.send('An error occurred while trying to send your message.')
            logUtil.log(f'Error sending message for {ctx.author} at {datetime.datetime.now()}: {e}')

async def setup(bot):
    await bot.add_cog(SayCommand(bot))