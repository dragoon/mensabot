"""
Based on the code from
https://www.fullstackpython.com/blog/build-first-slack-bot-python.html (https://github.com/mattmakai/slack-starterbot/)
https://github.com/ianhillmedia/slackbot-for-heroku
"""
import random
import time
import os
import re
from typing import List, Dict, Optional
from datetime import datetime

from slackclient import SlackClient

# constants
from menu_parsers import MenuParser
from menu_parsers.barenhofli_parser import HofliParser
from menu_parsers.schanze_parser import SchanzeParser

RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"


class MensaBot(object):
    MENU_COMMAND = "menus"
    RANDOM_QUOTES = ["Updates should happen in the email -- Greg Skoot",
                     "Load forks and knives face down in a dishwasher -- Baron Geddon"]
    mensas: List[MenuParser] = None
    name: str = None
    emoji: str = None
    client = None
    bot_id = None
    username = None

    """ Instantiates a Bot object."""
    def __init__(self):
        super(MensaBot, self).__init__()
        self.name = "mensabot"
        self.emoji = ":knife_fork_plate:"

        # NOTE: Python-slack requires a client connection to generate
        # an oauth token. We can connect to the client without authenticating
        # by passing an empty string as a token and then re-instantiating the
        # client with a valid OAuth token once we have one.
        self.client = SlackClient("")
        # We'll use this dictionary to store the state of each message object.
        # In a production environment you'll likely want to store this more
        # persistently in  a database.
        self.messages = {}
        self.mensas = [SchanzeParser(), HofliParser()]

    def run(self):
        """RTM way to run a bot"""
        if self.client.rtm_connect(with_team_state=False):
            try:
                print("Mensa Bot connected and running!")
                self.bot_id = self.client.api_call("auth.test")["user_id"]
                self.username = self.client.api_call("auth.test")['user']
                self._log(self.username + ": " + self.bot_id)
            except Exception as e:
                self._log(e)
                print("Connection failed. Exception traceback printed above.")
            while True:
                command, orig_event = self.parse_bot_commands(self.client.rtm_read())
                if command:
                    timestamp = datetime.fromtimestamp(float(orig_event['ts']))
                    self.handle_command(command, orig_event['channel'], timestamp)
                time.sleep(RTM_READ_DELAY)
        else:
            self._log("Connection failed.")

    def _log(self, message):
        print(message)

    def parse_bot_commands(self, slack_events):
        """
            Parses a list of events coming from the Slack RTM API to find bot commands.
            If a bot command is found, this function returns a tuple of command and channel.
            If its not found, then this function returns None.
        """
        for event in slack_events:
            if event["type"] == "message" and "subtype" not in event:
                user_id, command = self.parse_direct_mention(event.get('text', ''))
                if user_id == self.bot_id:
                    print('Bot id matches')
                    return command, event
        return None, None

    def parse_direct_mention(self, message_text):
        """
            Finds a direct mention (a mention that is at the beginning) in message text
            and returns the user ID which was mentioned. If there is no direct mention, returns None
        """
        matches = re.search(MENTION_REGEX, message_text)
        # the first group contains the username, the second group contains the remaining message
        return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

    def handle_command(self, command: str, channel: str, event_time: datetime):
        """
            Executes bot command if the command is known
        """
        # Default response is help text for the user
        default_response = "Not sure what you mean. Try *{}*.".format(self.MENU_COMMAND)

        # Finds and executes the given command, filling in response
        response = None
        # This is where you start to implement more commands!
        if self.MENU_COMMAND in command:
            response = '\n\n'.join([m.get_menu_string(event_time) for m in self.mensas])

        # Sends the response back to the channel
        response = self.client.api_call(
            "chat.postMessage",
            icon_emoji=self.emoji,
            channel=channel,
            username=self.name,
            text=response or default_response
        )
        print(response)

