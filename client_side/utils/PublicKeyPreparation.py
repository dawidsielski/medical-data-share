import os

from .RandomIdGenerator import RandomIdGenerator


class PublicKeyPreparation(object):

    @staticmethod
    def prepare_public_key():
        public_key_path = os.path.join('keys', 'public.key')
        user_id = RandomIdGenerator.generate_random_id(64)
        new_public_key_path = os.path.join('keys', f'public.{user_id}.key')
        os.rename(public_key_path, new_public_key_path)
        PublicKeyPreparation.save_user_id(user_id)
        return user_id

    @staticmethod
    def save_user_id(uid):
        with open(os.path.join('keys', 'user_id'), 'w') as file:
            file.write(uid)

    @staticmethod
    def get_user_id():
        with open(os.path.join('keys', 'user_id'), 'r') as file:
            uid = file.readline()
        return uid
