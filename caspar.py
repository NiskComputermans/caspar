import discord
from discord.ext import commands
import libmwostat
import configparser

configParser = configparser.RawConfigParser()
configFilePath = r'./caspar.conf'
configParser.read(configFilePath)

token = configParser.get('discord','token')
primaryChannel = configParser.getint('discord','primaryChannel')

mwoUser = configParser.get('mwomercs','username')
mwoPassword = configParser.get('mwomercs','password')

intents = discord.Intents.default()
intents.members = True

prefix='!'

bot = commands.Bot(command_prefix=prefix, activity=discord.Game(name='Use {0}help for control instructions.'.format(prefix)))

@bot.event
async def on_ready():
  channel = bot.get_channel(primaryChannel)
  print('CASPAR ready as {0}!'.format(bot.user))
  await channel.send('CASPAR online; **{0}** reporting for duty.\nAll services nominal.'.format(bot.user.display_name))

@bot.command(help='Echoes a simple reply to confirm the bot is listening.')
async def ping(ctx):
  await ctx.send('pong')

@bot.command(help='Retrieve current season\'s kill/death stats from mwomercs.com')
async def kdr(ctx, warrior: str):
  result = 'This function incomplete'
  await ctx.send(result)

@bot.command(help='Retrieve overall stat and last 5 season\'s stats from the Jarl\'s List')
async def jarls(ctx, warrior: str):
  result = 'This function incomplete'
  await ctx.send(result)

bot.run(token)
