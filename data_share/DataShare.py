import os
import json
import base64

from Crypto.Cipher import AES
from data_share.Pad import Pad

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
    def decrypt_data(data):
        """
        The function takes data argument and decrypts it using ENCRYPTION_KEY. It also unpads the data to be prepared
        for saving
        :param data: (str)
        :return: (str)
        """
        assert isinstance(data, str)
        obj = AES.new(os.environ.get('ENCRYPTION_KEY'), AES.MODE_CBC, 'This is an IV456')
        bytes_data = bytes.fromhex(data)
        return Pad.unpad(obj.decrypt(bytes_data)).decode()

    @staticmethod
    def encrypt_data(data):
        """
        This function encrypts data and prepares it for sending.
        :param data: (str) holds unprocessed data to be send
        :return: (str) data ready to be send
        """
        assert isinstance(data, str)
        obj = AES.new(os.environ.get('ENCRYPTION_KEY'), AES.MODE_CBC, 'This is an IV456')
        padded = Pad.pad(data.encode())
        ciphertext = obj.encrypt(padded)
        return ciphertext.hex()

    @staticmethod
    def validate_signature(message, signature=None):
        """
        This function checks if incoming message is valid for this machine.
        :param message: (obj) json incoming message
        :param signature:
        :return:
        """
        if signature is None:
            signature = message.pop('signature')

        signature = (int(base64.b64decode(signature).decode()),)

        message = json.dumps(message)

        public_key_path = os.path.join('keys', 'public.key')
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
    def prepare_data_for_sending(data):
        return json.dumps(data)


if __name__ == '__main__':
    ds = DataShare()
    d = {
        "data": "9cef4a8384657fb6f2f7b66218251734",
        "name": "Laboratory-Warsaw",
    }
    signature = ds.get_signature_for_message(d)

    print(signature)

    x = ds.validate_signature(d, signature)
    print(x)
