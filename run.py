from mensabot import MensaBot
from os import environ


pope_bot = MensaBot(environ['API_TOKEN'])
pope_bot.run()
