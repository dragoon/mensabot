import os

from pymongo import MongoClient

from .repository import TeamsRepository

client = MongoClient()
db = client['mensabot']
authed_teams_repo = TeamsRepository(db['authed_teams'])

# read properties
_MONGO_URI = os.environ.get('MONGODB_URI')

if _MONGO_URI:
    client = MongoClient(_MONGO_URI)
    _remote_db = client[_MONGO_URI.split('/')[-1].split('?')[0]]
    authed_teams_repo = TeamsRepository(_remote_db['authed_teams'])
