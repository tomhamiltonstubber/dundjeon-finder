import os
import shutil

os.environ['ASYNC_RQ'] = 'FALSE'

from DungeonFinder.settings import *

MEDIA_ROOT = '/tmp/tc2/media_main/'

try:
    os.makedirs(MEDIA_ROOT)
except OSError:
    shutil.rmtree(MEDIA_ROOT)


SEND_EMAILS = False
TESTING = True
