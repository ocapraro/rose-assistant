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
                (course_id INTEGER PRIMARY KEY, name TEXT, channel TEXT)''')
              
cursor.execute('''CREATE TABLE IF NOT EXISTS  class_times
                (class_time_id INTEGER PRIMARY KEY, name TEXT, time TEXT, day TEXT)''')

# Vars
intents = discord.Intents.all()
client = commands.Bot(command_prefix='rose!', intents=intents)
slash = SlashCommand(client, sync_commands=True)
guild_ids = [685164560948527164, 696195534632910947]
embed_color = 0xb00b0b

# Functions

def create_event(name:str, channel:int, date:str, description:str, parent_id:int = -1, repeating:int = 0):
  events = [i for i in cursor.execute('SELECT * FROM events')]
  cursor.execute(f"INSERT INTO events VALUES ({0 if not len(events) else events[-1][0]+1},\"{name}\",{channel},'{date}',\"{description}\",{repeating},{parent_id})")
  connection.commit()

# On Start
@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  await client.change_presence(activity = discord.Game(''))

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
  class_times = [i for i in cursor.execute('SELECT * FROM class_times')]
  cursor.execute(f"INSERT INTO class_times VALUES ({0 if not len(class_times) else class_times[-1][0]+1},'{name}','{time}','{day}')")
  connection.commit()
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

@slash.slash(
  name="createcourse",
  description="Creates a new course.",
  guild_ids=guild_ids,
  options=[
    create_option(
      name="name",
      description="The name of the course",
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
      name="classes",
      description="The classes in the course (Seperate with a pipe ie, class 1|class 2|class 3)",
      required=True,
      option_type=3
    )
  ]
)
async def _createcourse(ctx:SlashContext,name:str, channel, classes:str):
  courses = [i for i in cursor.execute('SELECT * FROM courses')]
  class_times = [i for i in cursor.execute('SELECT * FROM class_times')]
  days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
  onDay = lambda dt, day, offset=0: (dt + datetime.timedelta(days=(day-dt.weekday()+7*(offset+1))%7)).strftime("%Y-%m-%d")
  # Create course
  course_id = 0 if not len(courses) else courses[-1][0]+1
  cursor.execute(f"INSERT INTO courses VALUES ({course_id},\"{name}\",{channel.id})")
  connection.commit()
  # Create class events
  for i, _class in enumerate(classes.split("|")):
    for time in class_times:
      date = f"{time[2]} {onDay(datetime.datetime.utcnow(), days.index(time[3]), i)}"
      create_event(f"{name} {_class} ({time[1]})", channel.id, date, "The class starts in an hour. Join the general discord voice channel to access it.", parent_id=course_id)

  embed = discord.Embed(title="Success!", description=f"'{name}' was successfully created.", color=embed_color)
  await ctx.send(embed=embed)

@slash.slash(
  name="deleteevent",
  description="Deletes an event.",
  guild_ids=guild_ids,
  options=[
    create_option(
      name="eventid",
      description="The ID of the event you wish to delete",
      required=True,
      option_type=4
    ),
  ]
)
async def _deleteevent(ctx:SlashContext, eventid:int):
  cursor.execute(f"DELETE FROM events WHERE event_id={eventid}")
  connection.commit()
  embed = discord.Embed(title="Success!", description="The event was successfully deleted.", color=embed_color)
  await ctx.send(embed=embed)

@slash.slash(
  name="deletecourse",
  description="Deletes a course.",
  guild_ids=guild_ids,
  options=[
    create_option(
      name="courseid",
      description="The ID of the course you wish to delete",
      required=True,
      option_type=4
    ),
  ]
)
async def _deletecourse(ctx:SlashContext, courseid:int):
  cursor.execute(f"DELETE FROM courses WHERE course_id={courseid}")
  cursor.execute(f"DELETE FROM events WHERE parent_id={courseid}")
  connection.commit()
  embed = discord.Embed(title="Success!", description="The course was successfully deleted.", color=embed_color)
  await ctx.send(embed=embed)

@slash.slash(
  name="listevents",
  description="Lists all current events.",
  guild_ids=guild_ids,
)
async def _listevents(ctx:SlashContext):
  courses = [i for i in cursor.execute('SELECT * FROM courses')]
  events = [i for i in cursor.execute('SELECT * FROM events WHERE parent_id = -1')]
  description = "\n".join([f"{e[1]} - ID: {e[0]}" for e in events])
  embed = discord.Embed(title="Events", description=description if description else "There are no current events.", color=embed_color)
  for course in courses:
    embed.add_field(name=f"{course[1]} - CourseID: {course[0]}", value="\n".join([f"{e[1]} - ID: {e[0]}" for e in cursor.execute(f'SELECT * FROM events WHERE parent_id = {course[0]}')]), inline=False)
  await ctx.send(embed=embed)

@slash.slash(
  name="addclass",
  description="Adds a class to an existing course.",
  guild_ids=guild_ids,
  options=[
    create_option(
      name="courseid",
      description="The ID of the course you're adding the class to.",
      required=True,
      option_type=4
    ),
    create_option(
      name="name",
      description="The name of the class.",
      required=True,
      option_type=3
    ),
  ]
)
async def _addclass(ctx:SlashContext, courseid:int, name:str):
  class_times = [i for i in cursor.execute('SELECT * FROM class_times')]
  days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
  onDay = lambda dt, day: (dt + datetime.timedelta(days=(day-dt.weekday()-1)%7+1)).strftime("%Y-%m-%d")
  course = [i for i in cursor.execute(f'SELECT * FROM courses WHERE course_id = {courseid}')][0]
  events = [i for i in cursor.execute(f'SELECT * FROM events WHERE parent_id = {courseid}')]
  for time in class_times:
    date = f"{time[2]} {onDay(datetime.datetime.strptime(events[-1][3], '%I:%M%p %Y-%m-%d'), days.index(time[3]))}"
    create_event(f"{course[1]} {name} ({time[1]})", course[2], date, "The class starts in an hour. Join the general discord voice channel to access it.", parent_id=courseid)
    embed = discord.Embed(title="Success!", description="The class was successfully added.", color=embed_color)
  await ctx.send(embed=embed)


# Time loop
@tasks.loop(seconds=5)
async def every_minute():
  events = [i for i in cursor.execute('SELECT * FROM events')]

  for e in events:
    if (datetime.datetime.utcnow() + datetime.timedelta(hours=1, minutes=0)).strftime("%I:%M%p %Y-%m-%d") == e[3]:
      channel = client.get_channel(e[2])
      embed = discord.Embed(title=f"{e[1]} 1 Hour Reminder", description=e[4], color=embed_color)
      cursor.execute(f"DELETE FROM events WHERE event_id={e[0]}")
      connection.commit()
      await channel.send(embed=embed)

# Start Time Loop
every_minute.start()

# Run
client.run(os.environ.get('BOT_TOKEN'))
