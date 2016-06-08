"""
    Code taken from https://www.fullstackpython.com/blog/build-first-slack-bot-python.html
"""
import time
from staar_score_parser import convertSTAARscores
from slackclient import SlackClient

# constants
SLACK_BOT_TOKEN = 'xoxb-49123767253-UDGsdyimhRQP6OAsxjbVfLu4'
BOT_ID = 'U1F3MNK7F'
AT_BOT = "<@" + BOT_ID + ">:"
EXAMPLE_COMMAND = "do"
UPTIME_COMMAND = "uptime"
start_time = int(round(time.time() * 1000))

# instantiate Slack & Twilio clients
slack_client = SlackClient(SLACK_BOT_TOKEN)

# scoresDB = convertSTAARscores('data/staar a and l.pdf', 'data/stateid.csv')

TEST_ID = '1847662'

def get_scores(id):
    try:
        student_data = scoresDB[id]
        response = id + ' | ' + student_data[0][0] + " | " + student_data[0][1] + "\n"
        i = 1
        while i < len(student_data):
            for thing in student_data[i]:
                response += thing + " | "
            response += '\n'
            i += 1
        return response
    except KeyError:

        return "I have no data for this student. Logging and notifying Kucek."


def uptime():
    current_time = int(round(time.time() * 1000))
    dif = int((current_time - start_time)/1000)
    t = round(dif)
    d = round(t / 86400)
    t -= 86400*d
    h = round(t / 3600)
    t -= 3600*h
    m = round(t / 60)
    t -= 60*m
    return "Uptime: " + str(d) + "d:" + str(h) + "h:" + str(m) + "m:" + str(t) + "s"

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + "* command with numbers, delimited by spaces."
    if command.startswith(EXAMPLE_COMMAND):
        response = get_scores(TEST_ID)
    if command.startswith(UPTIME_COMMAND):
        response = uptime()
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
                return output['text'].split(AT_BOT)[1].strip().lower(), output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")

