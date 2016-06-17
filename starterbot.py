"""
    Code taken from https://www.fullstackpython.com/blog/build-first-slack-bot-python.html
"""
import time, csv, datetime, os
from slackclient import SlackClient
from a4e_parser import read_a4e
from datetimetest import comm_school_day, comm_period
from h_student_parser import get_dicts, student_search
from tables import create_table

def csv_writer(data, path):
    with open(path, "w", newline="\n") as f:
        writer = csv.writer(f)
        for i in data:
            writer.writerow(i)

# constants
DELETE_BOT_TOKEN = "xoxp-49123306933-49119366320-50916637381-44698e870c"
# tigerbot
SLACK_BOT_TOKEN = 'xoxb-51514364678-sJ3kmB6WfefrIRBPGq9RH6u4'
BOT_ID = 'U1HF4AQKY'
# Kucekbot
# SLACK_BOT_TOKEN = 'xoxb-49123767253-M31bkBoABlm33J6vKYHsaCbp'
# BOT_ID = 'U1F3MNK7F'

AT_BOT = "<@" + BOT_ID + ">:"
EXAMPLE_COMMAND = "do"
UPTIME_COMMAND = "uptime"
STAAR_COMMAND = 'scores'
SCHOOL_DAY_COMMAND = 'dismissal'
HELP_COMMAND = 'help'
UPDATE_COMMAND = 'update'
PERIOD_COMMAND = 'period'
CLEAR_COMMAND = 'clear'
SEARCH_COMMAND = 'search'
FIND_COMMAND = 'find'
TEST_DATES_COMMAND = 'test dates'
TEACHER_SCHEDULE_COMMAND = 'teacher'
STUDENT_SCHEDULE_COMMAND = 'schedule'
GRADES_COMMAND = 'grades'
DELETE_COMMAND = 'delete'
LAST_DB_UPDATE = '6/16/16'
start_time = int(round(time.time() * 1000))
activity_log = []
error_log = []
log_path = datetime.datetime.now().strftime("data/logs/%Y_%m_%d %H_%M log.csv")

# instantiate Slack & Twilio clients
slack_client = SlackClient(SLACK_BOT_TOKEN)
# delete_bot = SlackClient(DELETE_BOT_TOKEN)

scoresDB = read_a4e('data/staar data noheader.csv')
teacher_dict, student_dict, student_list = get_dicts()

def log_event(event, user):
    activity_log.append([datetime.datetime.now().strftime("%Y_%m_%d %H_%M_%S"), user, event])
    csv_writer(activity_log, log_path)

def comm_get_teacher_schedule(message):
    teacher = message.split(" ")[1]
    reply = '`'
    try:
        teacher_schedule = teacher_dict[teacher]
    except KeyError:
        return "I can't find classes for that teacher."
    reply += teacher_schedule[0] + ' in room ' + teacher_schedule[1] + '`\n'
    table_array = [["PD", "Class", "Stds"]]
    for i in range(3):
        table_array.append([str(i + 1), teacher_schedule[2][i][0].title().replace(' ',""), str(teacher_schedule[2][i][1])])
        i += 1
    reply += create_table(table_array)
    return reply

def comm_get_student_schedule(message):
    student = int(message.split(" ")[1])
    reply = '`'
    try:
        student_schedule = student_dict[student]
    except KeyError:
        return "I can't find classes for that student."
    table_array = [["P", "R", "T", "C", "G"]]
    reply += student_schedule[1] + ' (' + str(student_schedule[0]) + ')`\n'
    for i in range(3):
        table_array.append([str(i + 1), student_schedule[2][i][0], str(student_schedule[2][i][1]), str(student_schedule[2][i][2]), student_schedule[2][i][3]])
        # reply += str(i + 1) + '|' + student_schedule[2][i][0] + ' '*(3-len(student_schedule[2][i][0])) + "| " + str(student_schedule[2][i][1]) + ' '*(9-len(student_schedule[2][i][1])) +\
        #          '| ' + str(student_schedule[2][i][2]) + '\n'
        i += 1
    # reply += '```'
    reply += create_table(table_array)
    return reply


def comm_get_scores(message, user):
    try:
        id = message.split(" ")[1]
        student_data = scoresDB[id]
        response = ""
        for line in student_data:
            response += line + "\n"
        return response
    except KeyError:
        error_log.append(str(id) + "searched by ")
        return "I have no data for the id " + str(id) + "."
    except IndexError:
        return "It looks like you may have forgotten to type an ID number."

def comm_delete():
    imlist = slack_client.api_call("im.history", channel=channel, count=2)
    for thing in imlist['messages']:
        slack_client.api_call("chat.delete", channel=channel, ts=thing['ts'])

def comm_get_help():
    return "Available commands are listed below...\n" \
           "*find [id]* or *search [id]* - Finds all matchinig students\n" \
           "*scores [id]* - Provides a student's STAAR Scores\n" \
           "*schedule [id]* or *grades [id]* - Provides a student's schedule\n" \
           "*teacher [last name]* - Provides a teacher's schedule" \
           "*period* - Tells you how long until the end of the current period\n" \
           "*dismissal* - Tells you how long until school is out\n" \
           "*update* - Gives the date of the last database update\n" \
           "*test dates* - Shows the upcoming STAAR dates\n" \
           "" \
           "If you find any bugs or if the bot goes offline, " \
           "send a direct message to Kucek, and he'll fix it as soon as he can!"

def comm_uptime():
    current_time = int(round(time.time() * 1000))
    dif = int((current_time - start_time)/1000)
    t = round(dif)
    d = t // 86400
    t -= 86400*d
    h = t // 3600
    t -= 3600*h
    m = t // 60
    t -= 60*m
    return "Uptime: " + str(d) + "d:" + str(h) + "h:" + str(m) + "m:" + str(t) + "s"

def comm_update():
    return "Databases were last updated on *" + LAST_DB_UPDATE + "*."

def comm_student_search(q):
    s = q.split(" ")[1]
    matches = student_search(student_list, s)
    if len(matches) > 0:
        reply = "The students below match part or all of your query.```"
        for m in matches:
            reply += m + "\n"
        reply += '```'
        return reply
    return "No students were found. You can search by ID, Last Name, or First Name one at a time. You cannot combine these fields."

def comm_test_dates():
    return "Summer STAAR Test Dates\n```Mon Jul 11 | Eng 1\nTue Jul 12 | Alg 1\n" \
           "Wed Jul 13 | Eng 2\nThu Jul 14 | USH and Bio\nFri Jul 15 | MakeUps```"


def handle_command(command, channel, user):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "I'm not sure what you mean. Type *@staarbot help* to see all of the available commands."
    if command.startswith(STAAR_COMMAND):
        print('looking up staar scores')
        response = comm_get_scores(command, user)
    if command.startswith(UPTIME_COMMAND):
        print('calculating uptime...')
        response = comm_uptime()
    if command.startswith(SCHOOL_DAY_COMMAND):
        response = comm_school_day()
    if command.startswith(HELP_COMMAND):
        response = comm_get_help()
    if command.startswith(UPDATE_COMMAND):
        response = comm_update()
    if command.startswith(PERIOD_COMMAND):
        response = comm_period()
    if command.startswith(TEST_DATES_COMMAND):
        response = comm_test_dates()
    if command.startswith(TEACHER_SCHEDULE_COMMAND):
        response = comm_get_teacher_schedule(command)
    if command.startswith(STUDENT_SCHEDULE_COMMAND):
        response = comm_get_student_schedule(command)
    if command.startswith(GRADES_COMMAND):
        response = comm_get_student_schedule(command)
    if command.startswith(SEARCH_COMMAND):
        response = comm_student_search(command)
    if command.startswith(FIND_COMMAND):
        response = comm_student_search(command)
    if command.startswith(DELETE_COMMAND):
        response = comm_delete()
    slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            # if output and 'text' in output and AT_BOT in output['text']:
            #     # return text after the @ mention, whitespace removed
            #     return output['text'].split(AT_BOT)[1].strip().lower(), output['channel'], output['user']
            if output and 'text' in output and output['user'] != BOT_ID:
                return output['text'].lower(), output['channel'], output['user']
    return None, None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("Connected!")
        while True:
            command, channel, user = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                log_event(command, user)
                imlist = slack_client.api_call("im.history", channel=channel, count=2)
                for thing in imlist['messages']:
                    slack_client.api_call("chat.delete", channel=channel, ts=thing['ts'])
                handle_command(command, channel, user)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")

