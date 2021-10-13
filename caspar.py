import discord
from discord.ext import commands
from libmwostat import MWOStat
import configparser

configParser = configparser.RawConfigParser()
configFilePath = r'./caspar.conf'
configParser.read(configFilePath)

token = configParser.get('discord','token')
primaryChannel = configParser.getint('discord','primaryChannel')

mwoUser = configParser.get('mwomercs','username')
mwoPassword = configParser.get('mwomercs','password')

stat = MWOStat()

intents = discord.Intents.default()
intents.members = True

prefix = '!'

bot = commands.Bot(command_prefix=prefix, activity=discord.Game(name='Use {0}help for control instructions.'.format(prefix)))

@bot.event
async def on_ready():
  channel = bot.get_channel(primaryChannel)
  print('CASPAR ready as {0}!'.format(bot.user))
  await channel.send('CASPAR online; **{0}** reporting for duty.\nAll services nominal.'.format(bot.user.display_name))

@bot.command(help='Echoes a simple reply to confirm the bot is listening.')
async def ping(ctx):
  await ctx.send('pong')

@bot.command(help='Retrieve a warrior\'s kill/death stats for the current month from mwomercs.com. Wrap usernames with spaces in quotes "like this".')
async def kdr(ctx, warrior: str):
  await ctx.send('Looking up warrior in MWOMercs database...')
  try:
    stat.ImportPilots(pilot_list = [ warrior ])
    stat.Login(mwo_username = mwoUser, mwo_password = mwoPassword)
    season = stat.GetLatestSeason()
    leaderboard = stat.GetLeaderboardStats(mwo_season = season)
    result = f'```python\n{leaderboard[0]["Pilot"]}:\n'
    line = leaderboard[0]['All']
    for key in line:
      whitespace = ' ' * (20 - len(key) - len(f'{line[key]}'))
      result = f'{result}  {key}:{whitespace}{line[key]}\n'
    result = f'{result}\n```'
    await ctx.send(result)
  except:
    await ctx.send('Unable to retrieve warrior data. Check CASPAR MWO service account.')

@bot.command(help='Retrieve overall stat and last 5 season\'s stats from the Jarl\'s List')
async def jarls(ctx, warrior: str):
  result = 'This function incomplete'
  await ctx.send(result)

bot.run(token)
