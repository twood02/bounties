####################################################
## A Python-based Slack bot to log messages sent
## in monitored channels and output that data 
## through a series of commands.
####################################################
## Function Descriptions:
## message_sent - Logs each message into db
## stats - Initial function on /stats command
## user_function - User is tagged
## help_function - Displays help message
## channel_function - Channel is tagged
## channel_parameters - Channel is tagged with dates
## channel_parameters_admin - Shows full channel table
## channel_parameters_not_admin - Returns one row of table
## channel_no_parameters - Channel is tagged without dates
## stats_function - No user or channel tagged
## generate_dates - Caluculate dates for db lookup
## line_function - Builds each line of table
## generate_csv - Generates csv file for admin users
## file_upload - Uploads and dm's csv files
####################################################
## Author: Gavin Blanchette
## Copyright: Copyright 2022
## License: MIT License
## Version: 1.0
## Email: gblanchette@gwu.edu
####################################################
## Directions:
## Database must be generated using commented code
## at bottom or use the empty main.db database
## A Slack Bot must be created by end user and tokens set
## Execute by running "python main.py"
####################################################
## TODO:
## - Setup Flask server for endpoint connection rather
## than socket connection.
## - Enable public distribution
## - Improve documentation and redesign command flow
## - Host files on Flask Server rather than Slack
####################################################

import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import sqlite3
import datetime
from datetime import timedelta
from tabulate import tabulate
import csv

# Initializes app with bot token and socket mode handler
app = App(token=os.environ.get("SLACK_TOKEN"))
connection = sqlite3.connect("main.db", check_same_thread=False)

@app.event("message")
def message_sent(message, say):
  ts = round(float(message['ts']))  ##round to nearest minute
  formattedtime = datetime.datetime.fromtimestamp(ts)  ##convert to workable datetime format
  cursor = connection.cursor()
  user = str(message['user'])
  id = str(message['client_msg_id'])
  text = str(message['text']).replace("'", "''")  ##handle apostrophe in message
  channel = str(message['channel'])
  cursor.execute(f"""INSERT INTO messages VALUES ('{user}', '{id}', '{text}', '{channel}', '{formattedtime}');""")
  connection.commit()


@app.command("/stats")
def stats(body, ack, respond, command):
  ack()
  try:
    cursor = connection.cursor()
    parameters = body['text'].split()  ##get a list of parameters
    if parameters:
      if parameters[0][0] == "#":  ##if user enters a channel
        channel_function(respond, cursor, command, parameters)
      elif parameters[0][0] == "@":  ##if user enters a user
        user_function(respond, cursor, command, parameters)
      elif parameters[0] == "help":  ##if user enters help
        help_function(respond, command)
      else:  ##if user enters wrong parameter
        respond(f"The first parameter must be a user or channel! Please use /stats help for more information.")
    else:  ##if user has no parameters
      stats_function(respond, cursor, command)
  except:
    respond("There was an error! Error Code: SM3")

def user_function(respond, cursor, command, parameters):
  username = parameters[0].replace("@", "")
  result = app.client.users_info(user=command['user_id'])
  if result['user']['is_admin'] == True:
    users = app.client.users_list()
    for user in users['members']:
      if user['name'] == username:
        id = user['id']
    try:
      user = app.client.users_info(user=id)
    except:
      respond("That user was not found!")
    try:
      if len(parameters) > 1:
        try:
          start_date = datetime.datetime.strptime(parameters[1], '%m-%d-%Y')
          end_date = datetime.datetime.strptime(parameters[2], '%m-%d-%Y')
          cursor.execute(f"""SELECT * FROM messages WHERE user='{id}' AND time BETWEEN '{start_date}' AND '{end_date}'""")
        except:
          respond(f"The dates must be in MM-DD-YYYY! Please use /stats help for more information.")
      else:
        cursor.execute(f"""SELECT * FROM messages WHERE user='{id}'""")
      messages = cursor.fetchall()
      table = []
      if messages:
        for message in messages:
          channels = app.client.conversations_list()
          for channel in channels['channels']:
            if channel['id'] == message[3]:
              name = channel['name']
              table.append([name, message[4], message[2]])
        respond(f"Here is a list of messages that {username} has sent\n```" + tabulate(table, ["Channel", "Date", "Message"], tablefmt="simple") + "```")
      else:
        respond("There were no messages found with your selected parameters!")
    except:
      respond("There was an error! Error Code: UF4")
  else:
    respond("You must be an admin to tag a user!")
    
def help_function(respond, command):
  result = app.client.users_info(user=command['user_id'])
  if result['user']['is_admin'] == True:
    respond(""":wave: Need some help with /stats?\n>Use `/stats` to see stats for yourself, someone else, or for a channel. Some examples include:\n>• `/stats`\n>• `/stats #example`\n>• `/stats #example 06-22-2022 07-08-2022`\n>• `/stats @user`\n>• `/stats @user 06-22-2022 07-08-2022`""")
  else:
    respond(""":wave: Need some help with /stats?\n>Use `/stats` to see stats for yourself or for a channel. Some examples include:\n>• `/stats`\n>• `/stats #example`\n>• `/stats #example 06-22-2022 07-08-2022`""")

def channel_function(respond, cursor, command, parameters):  ##function when user tags a channel
  parameter = parameters[0].replace("#", "")  ##get the channel name from parameter
  try:
    channels = app.client.conversations_list()  ##list of channels to compare channel name to
    for channel in channels['channels']:
      if channel['name'] == parameter:
        id = channel['id']
        if len(parameters) > 1:  ##check if we have date parameters
          channel_parameters(respond, cursor, command, parameters,id, channel)
        else:
          channel_no_parameters(respond, cursor, command, id,channel)
  except:
    respond("There was an error! Error Code: CF0")


def channel_parameters(respond, cursor, command, parameters, id, channel):
  try:
    start_date = datetime.datetime.strptime(parameters[1], '%m-%d-%Y')  ##check if start date is in correct format
    start_weekday = start_date.weekday()  ##convert to weekday so we can find the last sunday
    if start_weekday != 6:  ##if the weekday is not sunday, subtract to hit sunday
      start_sunday = start_date - timedelta(days=start_weekday + 1)
    else:  ##if the weekday is sunday, set it as our start date
      start_sunday = start_date
      end_date = datetime.datetime.strptime(parameters[2], '%m-%d-%Y') + timedelta(days=1)  ##check if end date is in correct format and add one to catch any messages on the last day
      end_weekday = end_date.weekday()  ##convert to weekday so we can find the last sunday
      if end_weekday != 6:  ##if the weekday is not sunday, add to hit sunday
        end_sunday = end_date + timedelta(days=6 - end_weekday)
      else:  ##if the weekday is sunday, it is the beginning of our current week so add 7
        end_sunday = end_date + timedelta(days=7)
  except:
    respond(f"The dates must be in MM-DD-YYYY! Please use /stats help for more information.")
  if (end_date - start_date).days < 7 and end_weekday < 6:  ##if the days are in the same week, we need to use original dates
    cursor.execute(f"""SELECT user FROM messages WHERE channel='{id}' AND time BETWEEN '{start_date}' AND '{end_date}'""")
    weeks = 1
    same = True
  else:
    cursor.execute(f"""SELECT user FROM messages WHERE channel='{id}' AND time BETWEEN '{start_sunday}' AND '{end_sunday}'""")
    weeks = int(((end_sunday - start_sunday).days) / 7)  ##count the number of weeks we will be showing and iterate through
    same = False
  users = cursor.fetchall()
  result = app.client.users_info(user=command['user_id'])
  if result['user']['is_admin'] == True:  ##check if the user is an admin for permissions
    if users:
      channel_parameters_admin(respond, cursor, command, id, channel, users, start_sunday, end_sunday,start_date, end_date, weeks, same)
    else:
      respond("No messages were found during your selected timeframe.")
  else:
    channel_parameters_not_admin(respond, cursor, command, id, channel, users, start_sunday, end_sunday, start_date, end_date,weeks, same)


def channel_parameters_admin(respond, cursor, command, id, channel, users, start_sunday, end_sunday, start_date, end_date,weeks, same):
  user_list = []
  week_list = []
  for user in users:
    try:
      result = app.client.users_info(user=user[0])  ##send call to api with user id
      name = result['user']['name']  ##get name from api response
    except:
      respond("That user does not exist!")
    if name not in user_list:  ##if user is not already in the list, add them
      user_list.append(name)  ##Step 1, add user name to pull from
      user_week_list = generate_dates(cursor, start_date, end_date,start_sunday, weeks, same, user,id)
      week_list.append(user_week_list)  ##big user list
  headers = ["Name"]
  csv_headers = ["Name"]
  table = []
  csv_table = []
  for name in user_list:
    index = user_list.index(name)
    weeks = week_list[index]
    if index == 0:
      for week in weeks:
        if weeks.index(week) < 4:
          headers.append(week[0])
        csv_headers.append(week[0])
    line, csv_line = line_function(name, weeks)
    table.append(line)  ##append the line to our master table list
    csv_table.append(csv_line)
  try:
    generate_csv(csv_headers, csv_table)
  except:
    respond("No weeks found!")
  intro = f"Here is a breakdown of messages sent in #{channel['name']}\n```"
  tabtable = tabulate(table, headers, tablefmt="simple")
  file_upload(command, respond, intro, tabtable)


##Function used when user is not an admin but dates are specified
def channel_parameters_not_admin(respond, cursor, command, id, channel, users, start_sunday, end_sunday, start_date, end_date, weeks, same):
  if weeks > 4:
    respond("The maximum number of weeks you may see at a time is 4! Please narrow your search.")
  try:
    result = app.client.users_info(user=command['user_id'])
    name = result['user']['name']
    user = command['user_id']
  except:
    respond("That user does not exist!")
  week_list = generate_dates(cursor, start_date, end_date, start_sunday, weeks, same, user, id)
  headers = ["Name"]
  csv_headers = ["Name"]
  table = []
  csv_table = []
  weeks = week_list[0]
  for week in weeks:
    if weeks.index(week) < 4:
      headers.append(week[0])
    csv_headers.append(week[0])
  line, csv_line = line_function(name, weeks)
  table.append(line)
  csv_table.append(csv_line)
  try:
    generate_csv(csv_headers, csv_table)
  except:
    respond("No weeks found!")
  intro = f"Here is a breakdown of messages sent in #{channel['name']}\n```"
  tabtable = tabulate(table, headers, tablefmt="simple")
  respond(intro + tabtable)

##Function used when a channel is specified but no dates
def channel_no_parameters(respond, cursor, command, id, channel):
  try:
    result = app.client.users_info(user=command['user_id'])
    name = result['user']['name']
  except:
    respond("That user does not exist!")
  if result['user']['is_admin'] == True:
    cursor.execute(f"""SELECT * FROM messages WHERE channel='{id}'""")
  else:
    cursor.execute(f"""SELECT * FROM messages WHERE channel='{id}' AND user='{command['user_id']}'""")
  messages = cursor.fetchall()
  table = []
  user_dict = {}
  if messages:
    for message in messages:
      try:
        result = app.client.users_info(user=message[0])
        name = result['user']['name']
      except:
        respond("That user does not exist!")
      if not name in user_dict:
        user_dict[name] = 1
      else:
        user_dict[name] += 1
    for key in user_dict:
      table.append([key, user_dict[key]])
  else:
    respond("There were no messages found with your selected parameters!")
  generate_csv(["Name", "Count"], table)
  intro = f"Here is a breakdown of your messages sent in #{channel['name']}\n```"
  tabtable = tabulate(table, ["Name", "Count"], tablefmt="simple")
  if result['user']['is_admin'] == True:
    try:
      dm = app.client.conversations_open(users=command['user_id'])
      response = app.client.files_upload(file='table.csv', channels=dm['channel']['id'], initial_comment="Here is the report you requested")
      file = f"```\nYour file is located here: {response['file']['url_private']}"
      respond(intro + tabtable + file)
    except:
      file = f"```\nYour file could not be uploaded."
      respond(intro + tabtable + file)
  else:
    respond(intro + tabtable + "```")


def stats_function(respond, cursor, command):
    id = command['user_id']
    try:
      cursor.execute(f"""SELECT * FROM messages WHERE user='{id}'""")
      messages = cursor.fetchall()
      table = []
      if messages:
        for message in messages:
          channels = app.client.conversations_list()
          for channel in channels['channels']:
            if channel['id'] == message[3]:
              name = channel['name']
              table.append([name, message[4], message[2]])
      else:
        respond("There were no messages found with your selected parameters!")
      respond("Here is a list of messages you have sent\n```" + tabulate(table, ["Channel", "Date", "Message"], tablefmt="simple") + "```")
    except:
        respond("There was an error! Error Code: SF1")

def generate_dates(cursor, start_date, end_date, start_sunday, weeks, same, user, id):
  user_week_list = []
  for x in range(weeks):
    if same == False:
      start_date = (start_sunday + timedelta(days=7 * x)).strftime("%Y-%m-%d")
      end_date = (start_sunday + timedelta(days=7 + 7 * x)).strftime("%Y-%m-%d")
      cursor.execute(f"""SELECT * FROM messages WHERE channel='{id}' AND user='{user[0]}' AND time BETWEEN '{start_date}' AND '{end_date}'""")
    else:
      cursor.execute(f"""SELECT * FROM messages WHERE channel='{id}' AND user='{user[0]}' AND time BETWEEN '{start_date}' AND '{end_date}'""")
    messages = cursor.fetchall()
    if same == False:
      user_week_list.append([start_date, len(messages)])  ##small week list
    else:
      user_week_list.append([start_date.strftime("%Y-%m-%d") + " - " +end_date.strftime("%Y-%m-%d"), len(messages)])
  return user_week_list

def line_function(name, weeks):
  line = []  ##used to keep track of each line
  csv_line = []
  line.append(name)  ##line always starts with name
  csv_line.append(name)
  for week in weeks:
    if weeks.index(week) < 4:
      line.append(week[1])
    csv_line.append(week[1])
  return line, csv_line

def generate_csv(headers, table):
  with open('table.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(headers)
    for row in table:
      writer.writerow(row)

def file_upload(command, respond, intro, tabtable):
  try:
    dm = app.client.conversations_open(users=command['user_id'])
    response = app.client.files_upload(
      file='table.csv',
      channels=dm['channel']['id'],
      initial_comment="Here is the report you requested")
    file = f"```\nYour file is located here: {response['file']['url_private']}"
    respond(intro + tabtable + file)
  except:
    file = f"```\nYour file could not be uploaded."
    respond(intro + tabtable + file)

if __name__ == "__main__":
  #c = connection.cursor()
  #SQL_STATEMENT = """CREATE TABLE messages (user STRING, id GUID PRIMARY KEY, text STRING, channel STRING, time DATE);"""
  #c.execute(SQL_STATEMENT)
  SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
