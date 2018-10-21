from mensabot_rtm import MensaBotRtm
from os import environ


pope_bot = MensaBotRtm(environ['API_TOKEN'])
pope_bot.run()
