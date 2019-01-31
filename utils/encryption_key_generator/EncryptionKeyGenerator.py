import json
import secrets


class EncryptionKeyGenerator(object):

    def __init__(self):
        self.encryption_key = ''

    def generate_encryption_key(self, length=32):
        self.encryption_key = secrets.token_urlsafe(length)[:32]

    def save_encryption_key(self):
        with open('temp.json', 'r') as file:
            data = json.load(file)

        data['encryption_key'] = self.encryption_key

        with open('temp.json', 'w') as file:
            json.dump(data, file)

    def load_encryption_key(self):
        with open('temp.json', 'r') as file:
            data = json.load(file)

        self.encryption_key = data['encryption_key']

    @staticmethod
    def get_encryption_key():
        with open('temp.json', 'r') as file:
            data = json.load(file)
        return data['encryption_key']

    def generate_and_save(self):
        self.generate_encryption_key()
        self.save_encryption_key()
