"""
Based on the code from
https://www.fullstackpython.com/blog/build-first-slack-bot-python.html (https://github.com/mattmakai/slack-starterbot/)
https://github.com/ianhillmedia/slackbot-for-heroku
"""
import random
import os
import re
from typing import List, Dict, Optional
from datetime import datetime

from slackclient import SlackClient

# constants
from adapters import authed_teams_repo
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
    oauth: Dict = None
    verification: str = None
    clients = {}
    default_client = None

    """ Instantiates a Bot object."""
    def __init__(self):
        super(MensaBot, self).__init__()
        self.name = "mensabot"
        self.emoji = ":knife_fork_plate:"
        # When we instantiate a new bot object, we can access the app
        # credentials we set earlier in our local development environment.
        self.oauth = {"client_id": os.environ.get("CLIENT_ID"),
                      "client_secret": os.environ.get("CLIENT_SECRET"),
                      # Scopes provide and limit permissions to what our app
                      # can access. It's important to use the most restricted
                      # scope that your app will need.
                      "scope": "bot"}
        self.verification = os.environ.get("VERIFICATION_TOKEN")

        # NOTE: Python-slack requires a client connection to generate
        # an oauth token. We can connect to the client without authenticating
        # by passing an empty string as a token and then re-instantiating the
        # client with a valid OAuth token once we have one.
        self.default_client = SlackClient("")
        self.mensas = [SchanzeParser(), HofliParser()]

        for team_doc in authed_teams_repo.get_all_teams():
            self.clients[team_doc['team_id']] = SlackClient(team_doc['bot_token'])

    def auth(self, code):
        """
        Authenticate with OAuth and assign correct scopes.
        Save a dictionary of authed team information in memory on the bot
        object.
        Parameters
        ----------
        code : str
            temporary authorization code sent by Slack to be exchanged for an
            OAuth token
        """
        # After the user has authorized this app for use in their Slack team,
        # Slack returns a temporary authorization code that we'll exchange for
        # an OAuth token using the oauth.access endpoint
        auth_response = self.default_client.api_call(
                                "oauth.access",
                                client_id=self.oauth["client_id"],
                                client_secret=self.oauth["client_secret"],
                                code=code
                                )
        # To keep track of authorized teams and their associated OAuth tokens,
        # we will save the team ID and bot tokens to the global
        # authed_teams object
        team_id = auth_response["team_id"]
        # Then we'll reconnect to the Slack Client with the correct team's
        # bot token
        self.clients[team_id] = SlackClient(auth_response["bot"]["bot_access_token"])
        authed_teams_repo.save_team_data(team_id, {"bot_token": auth_response["bot"]["bot_access_token"]})
        print("Mensa Bot connected and running!")

    def parse_bot_command(self, event: Dict) -> Optional[str]:
        """
            Parses a list of events coming from the Slack RTM API to find bot commands.
            If a bot command is found, this function returns a tuple of command and channel.
            If its not found, then this function returns None.
        """
        user_id, command = self.parse_direct_mention(event.get('text', ''))
        # if user_id == self.bot_id:
        #     print('Bot id matches')
        return command

    def parse_direct_mention(self, message_text):
        """
            Finds a direct mention (a mention that is at the beginning) in message text
            and returns the user ID which was mentioned. If there is no direct mention, returns None
        """
        matches = re.search(MENTION_REGEX, message_text)
        # the first group contains the username, the second group contains the remaining message
        return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

    def handle_command(self, command: str, channel: str, team_id: str, event_time: datetime):
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
        response = self.clients[team_id].api_call(
            "chat.postMessage",
            icon_emoji=self.emoji,
            channel=channel,
            username=self.name,
            text=response or default_response
        )
        print(response)

