import json


class Config:
    def __init__(self, filename):
        self.conf = json.load(open(filename))

    def get_discord_token(self):
        return self.conf['discord']['token']

    def get_instances(self):
        for name, instance in self.conf['instances'].items():
            yield name, instance

    def get_moderator_roles(self):
        return self.conf['roles']['moderators']
