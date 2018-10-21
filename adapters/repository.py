from typing import Optional, Dict


class TeamsRepository(object):
    collection = None

    def __init__(self, collection):
        self.collection = collection

    def get_by_team_id(self, team_id: str) -> Optional[Dict]:
        team_doc = self.collection.find_one({"team_id": team_id})
        if team_doc:
            return team_doc
        return None

    def get_all_teams(self):
        return [doc for doc in self.collection.find()]

    def save_team_data(self, team_id: str, doc: Dict) -> None:
        doc['team_id'] = team_id
        self.collection.insert_one(doc)
