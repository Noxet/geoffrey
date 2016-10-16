
""" Get user ID from name """
def get_user_id(slackc, user_name):
    api_call = slackc.api_call('users.list')
    if api_call.get('ok'):
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == user_name:
                return user.get('id')
    
    return None

""" Get channel ID from name """
def get_channel_id(slackc, channel_name):
    api_call = slackc.api_call('channels.list')
    if api_call.get('ok'):
        channels = api_call.get('channels')
        for channel in channels:
            if 'name' in channel and channel.get('name') == channel_name:
                return channel.get('id')
    
    return None
