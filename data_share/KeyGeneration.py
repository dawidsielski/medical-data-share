import os

import Crypto
import Crypto.Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP


class KeyGeneration(object):
    """
    This class is responsible for handling keys for data sharing.

    Attributes:
        private_key (obj):  holds private key object
        public_key  (obj): holds public key object
    """

    def __init__(self):
        self.private_key = 0
        self.public_key = 0

    def generate_keys(self, key_length):
        """
        This function only generates public and private keys.
        :param key_length: (int)
        """
        random_gen = Crypto.Random.new().read
        self.private_key = RSA.generate(key_length, random_gen)
        self.public_key = self.private_key.publickey()

    def save_keys(self):
        """
        This function saves public and private keys to `keys` folder.
        """
        with open(os.path.join('keys', 'private.key'), 'wb') as file:
            file.write(self.private_key.exportKey())

        with open(os.path.join('keys', 'public.key'), 'wb') as file:
            file.write(self.public_key.exportKey())

    def load_keys(self):
        """
        This function loads public and private key from `keys` folder.
        :return: private_key, public_key
        """
        self._load_private()
        self._load_public()

        return self.private_key, self.public_key

    def _load_private(self):
        """
        This function loads private key.
        """
        path = os.path.join('keys')
        with open(os.path.join(path, '{}.key'.format('private')), 'rb') as file:
            self.private_key = RSA.importKey(file.read())

    def _load_public(self):
        """
        This function loads public key.
        """
        path = os.path.join('keys')
        with open(os.path.join(path, '{}.key'.format('public')), 'rb') as file:
            self.public_key = RSA.importKey(file.read())

    def load_or_generate(self):
        """
        This function depending on the current state will generate or load keys.
        """
        path = os.path.join('keys')

        keys_path_content = os.listdir(path)

        if 'private.key' not in keys_path_content or 'public.key' not in keys_path_content:
            self.generate_keys(4 * 1024)
            self.save_keys()
        self.load_keys()
