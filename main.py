import os
from dotenv import load_dotenv
import sqlite3
import datetime
from datetime import timezone
import discord
from discord.ext import commands, tasks
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option

# Take environment variables from .env
load_dotenv()  

# Connect to database
connection = sqlite3.connect("events.db")
cursor = connection.cursor()

# Create tables
cursor.execute('''CREATE TABLE IF NOT EXISTS events
                (event_id INTEGER PRIMARY KEY, name TEXT, channel INTEGER, date TEXT, description TEXT, repeating INTEGER, parent_id INTEGER)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS courses
                (course_id INTEGER PRIMARY KEY, name TEXT, channel TEXT, class_times BLOB)''')
              
cursor.execute('''CREATE TABLE IF NOT EXISTS  class_times
                (class_time_id INTEGER PRIMARY KEY, name TEXT, time TEXT)''')

# Vars
intents = discord.Intents.all()
client = commands.Bot(command_prefix='rose!', intents=intents)
slash = SlashCommand(client, sync_commands=True)
guild_ids = [685164560948527164]
embed_color = 0xb00b0b

# SQL Tables
class_times = [i for i in cursor.execute('SELECT * FROM class_times')]
events = [i for i in cursor.execute('SELECT * FROM events')]

# Functions

def create_event(name:str, channel:int, date:str, description:str, parent_id:int = -1, repeating:int = 0):
  global events

  cursor.execute(f"INSERT INTO events VALUES ({0 if not len(events) else events[-1][0]+1},'{name}',{channel},'{date}','{description}',{repeating},{parent_id})")
  connection.commit()
  events = [i for i in cursor.execute('SELECT * FROM events')]

# On Start
@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  await client.change_presence(activity = discord.Game('rose!help'))

# Slash Commands
@slash.slash(
  name="addclasstime",
  description="Adds a new class time (ie, Weekday, Weekend)",
  guild_ids=guild_ids,
  options=[
    create_option(
      name="name",
      description="The name of the class time",
      required=True,
      option_type=3
    ),
    create_option(
      name="day",
      description="The day of the week(UTC) the class time would happen on",
      required=True,
      option_type=3
    ),
    create_option(
      name="time",
      description="The time(UTC) the class time would happen on (ie, 02:00AM)",
      required=True,
      option_type=3
    )
  ]
)
async def _addclasstime(ctx:SlashContext, name:str, day:str, time:str):
  global class_times
  cursor.execute(f"INSERT INTO class_times VALUES ({0 if not len(class_times) else class_times[-1][0]+1},'{name}','{time} {day}')")
  connection.commit()
  class_times = [i for i in cursor.execute('SELECT * FROM class_times')]
  embed = discord.Embed(title="Success!", description=f"'{name}' was successfully added as a class time.", color=embed_color)
  await ctx.send(embed=embed)

@slash.slash(
  name="createevent",
  description="Creates a new event.",
  guild_ids=guild_ids,
  options=[
    create_option(
      name="name",
      description="The name of the event",
      required=True,
      option_type=3
    ),
    create_option(
      name="channel",
      description="The channel where the reminder notification will be sent",
      required=True,
      option_type=7
    ),
    create_option(
      name="date",
      description="The date(UTC) of the event (format: YYYY-MM-DD)",
      required=True,
      option_type=3
    ),
    create_option(
      name="time",
      description="The time(UTC) the event will start (format: HH:MM ie, 02:00AM)",
      required=True,
      option_type=3
    ),
    create_option(
      name="description",
      description="The event alert description",
      required=True,
      option_type=3
    )
  ]
)
async def _createevent(ctx:SlashContext,name:str, channel, date:str, description:str, time:str):
  create_event(name, channel.id, f"{time} {date}", description)
  embed = discord.Embed(title="Success!", description=f"'{name}' was successfully created.", color=embed_color)
  await ctx.send(embed=embed)

# Time loop
@tasks.loop(seconds=5)
async def every_minute():
  global events

  for e in events:
    if (datetime.datetime.utcnow() + datetime.timedelta(hours=1, minutes=0)).strftime("%I:%M%p %Y-%m-%d") == e[3]:
      channel = client.get_channel(e[2])
      embed = discord.Embed(title=f"{e[1]} Will Start in 1 Hour", description=e[4], color=embed_color)
      cursor.execute(f"DELETE FROM events WHERE event_id={e[0]}")
      connection.commit()
      events = [i for i in cursor.execute('SELECT * FROM events')]
      await channel.send(embed=embed)

# Start Time Loop
every_minute.start()

# Run
client.run(os.environ.get('BOT_TOKEN'))
