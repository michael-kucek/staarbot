"""
    Code taken from https://www.fullstackpython.com/blog/build-first-slack-bot-python.html
"""
import time, csv, datetime
from staar_score_parser import convertSTAARscores
from slackclient import SlackClient
from a4e_parser import read_a4e
from datetimetest import comm_school_day

def csv_writer(data, path):
    with open(path, "w", newline="\n") as f:
        writer = csv.writer(f)
        for i in data:
            writer.writerow(i)

# constants
SLACK_BOT_TOKEN = 'xoxb-49123767253-VM6ywukEcC6ejxLYsEz5zMDv'
BOT_ID = 'U1F3MNK7F'
AT_BOT = "<@" + BOT_ID + ">:"
EXAMPLE_COMMAND = "do"
UPTIME_COMMAND = "uptime"
STAAR_COMMAND = 'scores'
SCHOOL_DAY_COMMAND = 'dismissal'
HELP_COMMAND = 'help'
UPDATE_COMMAND = 'update'
LAST_DB_UPDATE = '6/8/16'
start_time = int(round(time.time() * 1000))
activity_log = []
error_log = []
log_path = datetime.datetime.now().strftime("data/logs/%Y_%m_%d %H_%M log.csv")

# instantiate Slack & Twilio clients
slack_client = SlackClient(SLACK_BOT_TOKEN)


scoresDB = read_a4e('data/staar data noheader.csv')

def log_event(event, user):
    activity_log.append([datetime.datetime.now().strftime("%Y_%m_%d %H_%M_%S"), user, event])
    csv_writer(activity_log, log_path)

def comm_get_scores(message, user):
    id = message.split(" ")[1]
    log_event(id + " score lookup", user)
    try:
        student_data = scoresDB[id]
        response = ""
        for line in student_data:
            response += line + "\n"
        return response
    except KeyError:
        error_log.append(str(id) + "searched by ")
        return "I have no data for the id " + str(id) + ". Logging and notifying Kucek."

def comm_get_help():
    return "Available commands are as follows...\n" \
           "*@staarbot: scores [id]* - Provides a student's STAAR Scores\n" \
           "*@staarbot: dismissal* - Tells you how long until school is out\n" \
           "*@staarbot: update* - Gives the date of the last database update"

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
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), output['channel'], output['user']
    return None, None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel, user = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel, user)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")

