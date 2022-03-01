import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

# Vars
intents = discord.Intents.all()
client = commands.Bot(command_prefix='rose!', intents=intents, help_command = None)

# On Start
@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  await client.change_presence(activity = discord.Game('rose!help'))

client.run(os.environ.get('BOT'))
