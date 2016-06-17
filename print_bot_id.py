import os

from slackclient import SlackClient

SLACK_BOT_TOKEN = 'xoxb-51514364678-Aq9nqq0to2DdBRtcZoriR3HU'
BOT_NAME = 'tigerbot'
BOT_ID = 'U1F3MNK7F'

slack_client = SlackClient(SLACK_BOT_TOKEN)

if __name__ == "__main__":
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            print(user.get('name'))
            if 'name' in user and user.get('name') == BOT_NAME:
                print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
    else:
        print("could not find bot user with the name " + BOT_NAME)