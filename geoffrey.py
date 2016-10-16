#!/usr/bin/env python

import sys
import time
import yaml
from slackclient import SlackClient
import schedule

from slack_utils import get_user_id, get_channel_id

with open('slack_config.yaml', 'r') as stream:
    try:
        conf = yaml.load(stream)
    except yaml.YAMLError as e:
        print ('Could not parse configuration file')
        print (e)
        sys.exit(1)

# declare globals
BOT_NAME = conf['BOT_NAME']
BOT_ID = ''
AT_BOT = ''
BOT_CHANNEL = conf['BOT_CHANNEL']
BOT_CHANNEL_ID = ''
API_TOKEN = conf['API_TOKEN']
if 'BOT_ID' in conf:
    BOT_ID = conf['BOT_ID']
if 'BOT_CHANNEL_ID' in conf:
    BOT_CHANNEL_ID = conf['BOT_CHANNEL_ID']

# set up slack connection
slackc = SlackClient(API_TOKEN)


""" Posts today's menu from all included restaurant """
def post_daily_lunch():
    resp = 'Sorry, no lunch for you!'
    slackc.api_call('chat.postMessage', channel=BOT_CHANNEL_ID, text=resp, as_user=True)

""" Handles mentions in channels """
def handle_command(command, channel):
    if command.startswith('lunch'):
        post_daily_lunch()
        return
    resp = 'I am here and ready to serve!'
    print (channel)
    slackc.api_call('chat.postMessage', channel=channel, text=resp, as_user=True)

""" Parses slack output """
def parse_slack_output(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, remove whitespace
                return output['text'].split(AT_BOT)[1].strip().lower(), output['channel']

    return None, None

if __name__ == '__main__':
    if BOT_ID == '':
        BOT_ID = get_user_id(slackc, BOT_NAME)
    if BOT_ID == None:
        print ('Error: Could not get the bot ID')
        sys.exit(1)

    # the tag when the bot is mentioned
    AT_BOT = '<@%s>' % BOT_ID

    print ('BOT_ID:', get_user_id(slackc, BOT_NAME))
    print ('CHANNEL_ID:', get_channel_id(slackc, BOT_CHANNEL))

    # seconds to sleep between reading
    READ_DELAY = 1

    # set up schedule for posting lunch
    POST_TIME = conf['POST_TIME']
    schedule.every().day.at(POST_TIME).do(post_daily_lunch)

    if slackc.rtm_connect():
        print ('%s is ready to serve!' % BOT_NAME)
        while True:
            cmd, chn = parse_slack_output(slackc.rtm_read())
            if cmd and chn:
                handle_command(cmd, chn)
            schedule.run_pending()
            time.sleep(READ_DELAY)
