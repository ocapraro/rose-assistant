# R.O.S.E. Assistant
[![](https://img.shields.io/badge/-Add_to_Discord-blue.svg?logo=discord&labelColor=363636)](https://discord.com/api/oauth2/authorize?client_id=889624315308437526&permissions=8&scope=bot%20applications.commands)

R.O.S.E. Assistant is a bot for the Guild of the ROSE Discord server.

## Command List
- `/addclasstime` -> Adds a new class time (ie, Weekday, Weekend)
- `/createevent` -> Creates a new event given a date and time, and sends out an alert 1 hour prior to the event in the specified channel.
- `/createcourse` -> Creates a new course, and creates an event for each of its classes to happen on each of the class times.
- `/deleteevent` -> Deletes an event.
- `/deletecourse` -> Deletes a course along with all of its classes.
- `/listevents` -> Lists all current events, courses, classes, and class times.
- `/addclass` -> Adds a class to an existing course.
- `/deleteclasstime` -> Deletes a class time.

## Installing

Install requirements:

```bash
pip3 install -r requirements.txt
```

Run app:
```bash
python3 main.py
```
## .env file template
```
BOT_TOKEN = YOUR_TOKEN_HERE
```
