#!/usr/bin/env python

import sys
import os
import logging
import time
import random
import yaml
import datetime
import importlib
from slackclient import SlackClient
import schedule

from slack_utils import get_user_id, get_channel_id

dir_path = os.path.dirname(os.path.realpath(__file__))

# parse configuration file for slack
with open('%s/slack_config.yaml' % dir_path, 'r') as stream:
    try:
        conf = yaml.full_load(stream)
    except yaml.YAMLError as e:
        print ('Could not parse configuration file')
        print (e)
        sys.exit(1)

# parse configuration file for geoffrey
with open('%s/geoffrey_config.yaml' % dir_path, 'r') as stream:
    try:
        gconf = yaml.full_load(stream)
    except yaml.YAMLError as e:
        print ('Could not parse geoffrey_config file')
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

# load the menu classes dynamically
menu_classes = []
for menu in gconf['MENUS']:
    full_path = 'menus.%s' % menu
    class_data = full_path.split('.')
    mod_path = '.'.join(class_data[:-1])
    class_str = class_data[-1]
    mod = importlib.import_module(mod_path)
    cls = getattr(mod, class_str)
    menu_classes.append(cls)

# set up slack connection
slackc = SlackClient(API_TOKEN)

# map the day of week numbers to the actual names, in swedish
weekdays = {0: 'måndag', 1: 'tisdag', 2: 'onsdag', 3: 'torsdag', 4: 'fredag'}

def post_lunch(dow, channel):
    """ Posts today's menu from all included restaurants """
    # don't post on weekends
    if dow > 4: return

    resp = '*Lunch of the Day (%s):*\n------------------------------------\n\n' % weekdays[dow]
    for menu in menu_classes:
        menu_obj = menu()
        # only show Avesta menu on fridays
        # TODO: this should be entered in the config file
        if dow != 4 and 'Avesta' in str(menu_obj):
            continue
        try:
            dishes = menu_obj.get_day(dow)
        except Exception:
            logging.exception('Exception in post_lunch')
            dishes = ['500 - Internal Food Poisoning']
        resp += '*%s*\n' % menu_obj
        for dish in dishes:
            resp += '- \t%s\n' % dish

    resp += '\n_Yours Truly_,\nGeoffrey'
    #print (resp)
    slackc.api_call('chat.postMessage', channel=channel, text=resp, as_user=True)

def post_today(channel):
    today = datetime.datetime.today().weekday()
    post_lunch(today, channel)

def update_lunch():
    """ Update the menu, caching it """
    for menu in menu_classes:
        # the function caches the menu
        menu().get_week()

def post_msg(msg, channel):
    slackc.api_call('chat.postMessage', channel=channel, text=msg, as_user=True)

def handle_command(command, channel, user):
    """ Handles mentions in channels """
    if user not in gconf['WHITELIST']:
        # users not in the whitelist receives a 'nice' response
        error_msg_list = gconf['WHITELIST_ERROR_MESSAGES']
        rnd_idx = random.randint(0, len(error_msg_list) - 1)
        post_msg(error_msg_list[rnd_idx], channel)
        return

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
        msg = "\"What\" ain't no country I've ever heard of. They speak English in What?"
        post_msg(msg, channel)

def parse_slack_output(slack_rtm_output):
    """ Parses slack output """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            # check if bot was mentioned in a channel
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, remove whitespace
                # also return the channel and the user sending the message
                return output['text'].split(AT_BOT)[1].strip().lower(), output['channel'], output['user']

    return None, None, None

if __name__ == '__main__':
    logging.basicConfig(level='WARNING')

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

    # seconds to sleep between reading
    READ_DELAY = 1

    UPDATE_TIME = gconf['UPDATE_TIME']
    schedule.every().day.at(UPDATE_TIME).do(update_lunch)

    # set up schedule for posting lunch
    POST_TIME = gconf['POST_TIME']
    schedule.every().day.at(POST_TIME).do(post_today, BOT_CHANNEL_ID)

    if slackc.rtm_connect():
        print ('%s is ready to serve!' % BOT_NAME)
        while True:
            cmd, chn, usr = parse_slack_output(slackc.rtm_read())
            if cmd and chn and usr:
                handle_command(cmd, chn, usr)
            schedule.run_pending()
            time.sleep(READ_DELAY)
