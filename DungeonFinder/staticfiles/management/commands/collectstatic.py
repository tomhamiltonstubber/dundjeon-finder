import shutil
import subprocess
from pathlib import Path

from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'run rollup to build js files'

    def handle(self, **kwargs):
        dist_dir = (Path(settings.DJ_DIR) / 'static/dist').resolve()
        if dist_dir.exists():
            print('deleting dist dir {}'.format(dist_dir))
            shutil.rmtree(str(dist_dir))
        self.run('yarn', 'run', 'main')

    @staticmethod
    def run(*args):
        print('\nRunning {}...'.format(' '.join(args)))
        subprocess.run(args, check=True)
