import os
import json
import base64

from Crypto.Cipher import AES, PKCS1_OAEP
from data_share.Pad import Pad
from utils.user_validation.UserValidation import UserValidation

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random

from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA


class DataShare(object):
    """
    This class is responsible for data encryption and validating signature.
    """

    @staticmethod
    def decrypt_data(data, encryption_key):
        """
        The function takes data argument and decrypts it using ENCRYPTION_KEY. It also unpads the data to be prepared
        for saving
        :param data: (str) data to be decrypted
        :param encryption_key: (str) 32 character random encryption key
        :return: (str) decrypted information
        """
        assert isinstance(data, str)
        obj = AES.new(encryption_key, AES.MODE_CBC, 'This is an IV456')
        bytes_data = bytes.fromhex(data)
        return Pad.unpad(obj.decrypt(bytes_data)).decode()

    @staticmethod
    def encrypt_data(data, encryption_key):
        """
        This function encrypts data and prepares it for sending.
        :param data: (str) holds unprocessed data to be send
        :param encryption_key: (str) 32 character random encryption key
        :return: (str) data ready to be send
        """
        assert isinstance(data, str)
        obj = AES.new(encryption_key, AES.MODE_CBC, 'This is an IV456')
        padded = Pad.pad(data.encode())
        ciphertext = obj.encrypt(padded)
        return ciphertext.hex()

    @staticmethod
    def validate_signature_from_message(message, signature=None, public_key=None):
        """
        This function checks if incoming message is valid for this machine.

        By default this function will use signature privided in a message argument.
        If not you can specify your own sugnature by passing signature argument.

        :param message: (obj) json incoming message
        :param signature: (str) signature for the message (None by default)
        :param public_key: (str) holds public key string information (None by default)
        :return: (bool) True if message is signed correctly, False otherwise
        """
        if signature is None:
            signature = message.pop('signature')

        signature = (int(base64.b64decode(signature).decode()),)

        message = json.dumps(message)

        if public_key is None:
            public_key_path = os.path.join('keys', 'public.key')
            with open(public_key_path, 'rb') as file:
                public_key = RSA.importKey(file.read())
        else:
            public_key = RSA.importKey(public_key)

        h = SHA.new(message.encode()).digest()

        return public_key.verify(h, signature)

    @staticmethod
    def validate_signature_using_user_id(message, signature=None):
        """
        This function checks if incoming message is valid for this machine.
        :param message: (obj) json incoming message
        :param signature:
        :return:
        """
        if signature is None:
            signature = message.pop('signature')

        signature = (int(base64.b64decode(signature).decode()),)

        user_id = message['user_id']

        message = json.dumps(message)
        public_key_path = os.path.join('public_keys', f'public.{user_id}.key')
        with open(public_key_path, 'rb') as file:
            public_key = RSA.importKey(file.read())

        h = SHA.new(message.encode()).digest()

        return public_key.verify(h, signature)

    @staticmethod
    def get_signature_for_message(message):
        """
        This function prepares signature for the message.
        :param message: (obj) json message that needs to be signed
        :return: (str) b64encoded signature for given message
        """
        message = json.dumps(message)

        private_key_path = os.path.join('keys', 'private.key')
        with open(private_key_path, 'rb') as file:
            private_key = RSA.importKey(file.read())

        h = SHA.new(message.encode()).digest()
        signature = private_key.sign(h, '')

        return base64.b64encode(bytes(str(signature[0]).encode()))

    @staticmethod
    def encrypt_using_public_key(message, user_id, public_key=None):
        """
        This function perform encryption with given public key.
        If public key not supplied the one provided for the user_id will be used.
        :param message: (str) message to be encrypted
        :param user_id: (str) user identification string
        :param public_key: (str)
        :return: (str) encrypted intormation
        """
        if public_key:
            public_key_path = os.path.join('public_keys', f'public.{user_id}.key')
            with open(public_key_path, 'rb') as file:
                public_key = RSA.importKey(file.read())
        else:
            public_key = RSA.importKey(public_key)

        cipher = PKCS1_OAEP.new(public_key)
        encrypted = cipher.encrypt(message.encode())
        return encrypted.hex()

    @staticmethod
    def decrypt_using_private_key(message):
        """
        This function decrypts information using default private key for the machine.
        :param message: (str) message to be decrypted
        :return: (str) unencrypted message
        """
        public_key_path = os.path.join('keys', 'private.key')
        with open(public_key_path, 'rb') as file:
            private_key = RSA.importKey(file.read())

        cipher = PKCS1_OAEP.new(private_key)
        encrypted = cipher.decrypt(message)
        return encrypted.hex()

    @staticmethod
    def validate_signature(message):
        """
        This function takes message as an agrument and checks if user is authorized for performing such operation.
        :param message: (dict) holds whole request json information
        :return: (tuple) True, <public_key> if user is authorized and False, None if not
        """
        user_validation = UserValidation.validate_user(message['user_id'])
        if user_validation:
            return DataShare.validate_signature_from_message(message, public_key=user_validation['result']), user_validation['result']
        return False, None


