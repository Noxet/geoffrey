#!/usr/bin/env python

import sys
import time
import yaml
import datetime
from slackclient import SlackClient
import schedule

from slack_utils import get_user_id, get_channel_id

# TODO: load the classes dynamically
from menus.mop import MOP
from menus.finnut import FinnUt
from menus.finnin import FinnIn

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

# map the day of week numbers to the actual names, in swedish
weekdays = {0: 'måndag', 1: 'tisdag', 2: 'onsdag', 3: 'torsdag', 4: 'fredag'}

def post_lunch(dow, channel):
    """ Posts today's menu from all included restaurants """
    # don't post on weekends
    if dow > 4: return

    resp = '*Lunch of the Day (%s):*\n------------------------------------\n\n' % weekdays[dow]
    dishes = MOP().get_day(dow)
    resp += '*%s*\n' % MOP()
    for dish in dishes:
        resp += '- \t%s\n' % dish

    dishes = FinnUt().get_day(dow)
    resp += '*%s*\n' % FinnUt()
    for dish in dishes:
        resp += '- \t%s\n' % dish

    dishes = FinnIn().get_day(dow)
    resp += '*%s*\n' % FinnIn()
    for dish in dishes:
        resp += '- \t%s\n' % dish

    resp += '\n_Yours Truely_,\nGeoffrey'
    #print (resp)
    slackc.api_call('chat.postMessage', channel=channel, text=resp, as_user=True)

def post_what(channel):
    resp = "\"What\" ain't no country I've ever heard of. They speak English in What?"
    slackc.api_call('chat.postMessage', channel=channel, text=resp, as_user=True)

def handle_command(command, channel):
    """ Handles mentions in channels """
    if command.startswith('today'):
        today = datetime.datetime.today().weekday()
        post_lunch(today, channel)
    elif command.startswith('monday'):
        post_lunch(0, channel)
    elif command.startswith('tuesday'):
        post_lunch(1, channel)
    elif command.startswith('wednesday'):
        post_lunch(2, channel)
    elif command.startswith('thursday'):
        post_lunch(3, channel)
    elif command.startswith('friday'):
        post_lunch(4, channel)
    elif command.startswith('what'):
        post_what(channel)

    #resp = 'I am here and ready to serve!'
    #slackc.api_call('chat.postMessage', channel=channel, text=resp, as_user=True)

def parse_slack_output(slack_rtm_output):
    """ Parses slack output """
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
    if BOT_CHANNEL_ID == '':
        BOT_CHANNEL_ID = get_channel_id(slackc, BOT_CHANNEL)
        if BOT_CHANNEL_ID == None:
            print ('Error: Could not get the bot channel ID')
            sys.exit(1)

    # the tag when the bot is mentioned
    AT_BOT = '<@%s>' % BOT_ID

    #print ('BOT_ID:', get_user_id(slackc, BOT_NAME))
    #print ('CHANNEL_ID:', get_channel_id(slackc, BOT_CHANNEL))

    with open('geoffrey_config.yaml', 'r') as stream:
        try:
            gconf = yaml.load(stream)
        except yaml.YAMLError as e:
            print ('Could not parse geoffrey_config file')
            print (e)
            sys.exit(1)

    # seconds to sleep between reading
    READ_DELAY = 1

    # set up schedule for posting lunch
    POST_TIME = gconf['POST_TIME']
    today = datetime.datetime.today().weekday()
    schedule.every().day.at(POST_TIME).do(post_lunch, today, BOT_CHANNEL_ID)

    if slackc.rtm_connect():
        print ('%s is ready to serve!' % BOT_NAME)
        while True:
            cmd, chn = parse_slack_output(slackc.rtm_read())
            if cmd and chn:
                handle_command(cmd, chn)
            schedule.run_pending()
            time.sleep(READ_DELAY)
