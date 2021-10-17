import discord
from discord.ext import commands
from libmwostat import MWOStat
import configparser
import re
import logging

configParser = configparser.RawConfigParser()
configFilePath = r'/conf/caspar.conf'
configParser.read(configFilePath)

token = configParser.get('discord','token')
primaryChannel = configParser.getint('discord','primaryChannel')
prefix = configParser.get('discord','prefix')
onJoinRole = configParser.get('discord','newUserRole')

mwoUser = configParser.get('mwomercs','username')
mwoPassword = configParser.get('mwomercs','password')

stat = MWOStat()

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=prefix, activity=discord.Game(name='Use {0}help for control instructions.'.format(prefix)))

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='/log/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

@bot.event
async def on_ready():
  channel = bot.get_channel(primaryChannel)
  print('CASPAR ready as {0}!'.format(bot.user))
  logger.info('Logged on as {0}'.format(bot.user))
  await channel.send('CASPAR online; **{0}** reporting for duty.\nAll services nominal.'.format(bot.user.display_name))

@bot.event
async def on_member_join(member):
    if onJoinRole != "":
      try:
        role = discord.utils.get(member.guild.roles, name=onJoinRole)
        await member.add_roles(role)
      except:
        print(f'ERR: Unable to assign on-join role to new member {member.display_name}!')
        logger.warning(f'WARN: Was unable to assign {onJoinRole} to {member.display_name}.')
    else:
      logger.warning('onJoinRole was empty')

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

@bot.command(help='Retrieve a warrior\'s overall stats from the Jarl\'s List')
async def jarls(ctx, warrior: str):
  await ctx.send('Looking up warrior in Jarl\'s List...')
  stat.ImportPilots(pilot_list = [ warrior ])
  stats = stat.GetJarlsStats()
  if type(stats) is str:
    await ctx.send('Pilot not found.')
  else:
    stats = stats[0]
    result = f'```python\n{stats["Pilot"]}:\n'
    stats.pop('Pilot')
    for key in stats:
        whitespace = ' ' * (20 - len(key) - len(f'{stats[key]}'))
        result = f'{result}  {key}:{whitespace}{stats[key]}\n'
    result = f'{result}\n```'
    await ctx.send(result)

@bot.command(pass_context=True, help='Add a role or rank to a warrior.')
@commands.has_any_role("Unit Commander", "Staff Officer","Section Officer")
async def addrole(ctx, warrior: discord.Member, role: str):
  try:
    role = discord.utils.get(warrior.guild.roles, name=role)
    await warrior.add_roles(role)
    await ctx.send(f'Aff. Added {role} role to {warrior.display_name}.')
  except:
    await ctx.send('Unable to assign role to warrior. Please check role name and permissions.')

@bot.command(pass_context=True, help='Remove a role or rank from a warrior.')
@commands.has_any_role("Unit Commander", "Staff Officer","Section Officer")
async def rmrole(ctx, warrior: discord.Member, role: str):
  try:
    role = discord.utils.get(warrior.guild.roles, name=role)
    await warrior.remove_roles(role)
    await ctx.send(f'Aff. Removed {role} role from {warrior.display_name}.')
  except:
    await ctx.send('Unable to remove role from warrior. Please check role name and permissions.')

@bot.commands(help='Look up a mech by chassis or variant on GrimMechs. Queries are case insensitive.')
async def grim(ctx, mech: str):
  if re.match('[!@#$%^&*()|\;:\'",.\[\]<>?/`~_=+]*', '', mech):
    await ctx.send('Query does not accept special characters other than dash. Queries are case insensitive.')
  else:
    # results = stat.GetGrimMechsBuilds(mech)
    # TODO: Cook and return results
    await ctx.send('Function not yet implemented.')

bot.run(token)
