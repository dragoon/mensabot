"""
Based on the code from
https://www.fullstackpython.com/blog/build-first-slack-bot-python.html (https://github.com/mattmakai/slack-starterbot/)
https://github.com/ianhillmedia/slackbot-for-heroku
"""
import time
import re
from typing import List
from datetime import datetime

from slackclient import SlackClient

# constants
from menu_parsers import MenuParser
from menu_parsers.barenhofli_parser import HofliParser
from menu_parsers.schanze_parser import SchanzeParser

RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"


class MensaBot:
    MENU_COMMAND = "menus"
    mensas: List[MenuParser] = None
    username: str = None
    bot_id: str = None

    def __init__(self, token):
        self.client = SlackClient(token)
        self.mensas = [SchanzeParser(), HofliParser()]

    def run(self):
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
            If its not found, then this function returns None, None.
        """
        for event in slack_events:
            if event["type"] == "message" and "subtype" not in event:
                user_id, command = self.parse_direct_mention(event.get('text', ''))
                if user_id == self.bot_id:
                    print('Message received')
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
        self.client.api_call(
            "chat.postMessage",
            channel=channel,
            text=response or default_response
        )
