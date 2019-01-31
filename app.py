import os

from apscheduler.schedulers.background import BackgroundScheduler

from data_share.KeyGeneration import KeyGeneration
from nodes_available.NodesChecker import NodesChecker

FOLDERS = ['logs', 'data_acquisition', 'nodes', 'keys']


def check_folder(folder_name):
    """
    This function makes a folder needed for application to run correctly.
    :param folder_name: str
    :return: None
    """
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)


sched = BackgroundScheduler(daemon=True)
sched.add_job(NodesChecker.get_all_nodes_availability, 'interval', minutes=1)
sched.start()

if __name__ == '__main__':
    [check_folder(folder) for folder in FOLDERS]
    keys = KeyGeneration()
    keys.load_or_generate()

    from ngs.ngs import server

    if int(os.environ.get('FLASK_DEBUG', 0)):
        server.run(debug=True, port=8080, host='0.0.0.0')
    else:
        server.run(host='0.0.0.0', port=80)
