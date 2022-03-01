import os
from dotenv import load_dotenv
import sqlite3
import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option

# Take environment variables from .env
load_dotenv()  




# Vars
intents = discord.Intents.all()
client = commands.Bot(command_prefix='rose!', intents=intents)
slash = SlashCommand(client, sync_commands=True)

# On Start
@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  await client.change_presence(activity = discord.Game('rose!help'))

# Slash Commands
@slash.slash(
  name="getuser",
  description="Get user ID",
  guild_ids=[685164560948527164],
  options=[
    create_option(
      name="user",
      description="Select a user",
      required=True,
      option_type=6
    )
  ]
)
async def _getuser(ctx:SlashContext, user:str):
  await ctx.send(user.id)

# Run
client.run(os.environ.get('BOT_TOKEN'))
