#    CASPAR - A Battletech themed Discord bot for Mechwarrior Online providing community management functions and stat scraping from official and community leaderboards.
#    Copyright (C) 2022  Kirk Stephenson (E: nisk.is.afk@gmail.com / W: https://github.com/NiskComputermans)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import discord
from discord.ext import commands
from libmwostat import MWOStat
import configparser
import re

configParser = configparser.RawConfigParser()
configFilePath = r'/conf/caspar.conf'
configParser.read(configFilePath)

token = configParser.get('discord','token')
primaryChannel = configParser.getint('discord','primaryChannel')
prefix = configParser.get('discord','prefix')

mwoUser = configParser.get('mwomercs','username')
mwoPassword = configParser.get('mwomercs','password')

stat = MWOStat()

intents = discord.Intents.default()
intents.members = True

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

@bot.command(help='Retrieve a warrior\'s overall stats from the Jarl\'s List')
async def jarls(ctx, warrior: str):
  await ctx.send('Looking up warrior in Jarl\'s List...')
  stat.ImportPilots(pilot_list = [ warrior ])
  stats = stat.GetJarlsStats()
  if type(stats) is str:
    await ctx.send('Pilot not found.')
  else:
    stats = stats[0]
    #stats["Rating"] = re.sub(r'^\[.*\]','',stats["Rating"])
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

bot.run(token)
