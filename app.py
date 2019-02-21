import os

from apscheduler.schedulers.background import BackgroundScheduler
from configparser import ConfigParser

from data_share.KeyGeneration import KeyGeneration
from nodes_available.NodesChecker import NodesChecker
from utils.public_variants_handler.PublicVariantsHandler import PublicVariantsHandler
from utils.nodes_key_pair_updator.NodesKeyPairUpdator import NodeKeyPairUpdator
from utils.user_validation.UserValidation import UserValidation

config = ConfigParser()
config.read(os.path.join(os.getcwd(), 'config.ini'), encoding='utf-8')

FOLDERS = ['logs', 'data_acquisition', 'nodes', 'keys', 'logs/data_sharing', 'logs/website', 'public_keys']


def check_folder(folder_name):
    """
    This function makes a folder needed for application to run correctly.
    :param folder_name: str
    """
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)


sched = BackgroundScheduler(daemon=True, timezone=config.get('NODE', 'TIMEZONE'))
sched.add_job(NodesChecker.get_all_nodes_availability, 'interval', minutes=1)
sched.add_job(PublicVariantsHandler.reset_limit, 'cron', day='*')
sched.add_job(NodeKeyPairUpdator.update_keys, 'cron', hour='*')
sched.add_job(UserValidation.check_key_expiration_date, 'cron', minute='*')
sched.start()


if __name__ == '__main__':
    [check_folder(folder) for folder in FOLDERS]
    keys = KeyGeneration()
    keys.load_or_generate()

    PublicVariantsHandler.create_temp_file()

    from data_share_website.data_share_website import server

    if int(os.environ.get('FLASK_DEBUG', 0)):
        # app.run(use_reloader=False)
        server.run(debug=True, port=8080, host='0.0.0.0', use_reloader=False)
    else:
        server.run(host='0.0.0.0', port=80)
