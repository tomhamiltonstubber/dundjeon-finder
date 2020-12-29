import shutil
import subprocess
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles.management.commands.collectstatic import Command as CSBaseCommand


class Command(CSBaseCommand):
    help = 'Build JS and SCSS'

    def collect(self, **kwargs):
        dist_dir = (Path(settings.DJ_DIR) / 'static/dist').resolve()
        if dist_dir.exists():
            print('deleting dist dir {}'.format(dist_dir))
            shutil.rmtree(str(dist_dir))
        print('\nRunning {}...'.format('yarn run main'))
        subprocess.run(['yarn', 'run', 'main'], check=True)
        return super().collect()
