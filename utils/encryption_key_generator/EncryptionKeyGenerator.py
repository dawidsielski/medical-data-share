import secrets


class EncryptionKeyGenerator(object):

    @staticmethod
    def generate_encryption_key(length=32):
        return secrets.token_urlsafe(length)[:length]
