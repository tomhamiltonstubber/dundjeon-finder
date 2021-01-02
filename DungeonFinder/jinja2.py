import logging
import os
import re

from django.conf import settings
from django.templatetags.static import static
from django.urls import reverse
from jinja2 import Environment


def _js_path(name, dev=False):  # pragma: no cover
    if dev and os.path.exists(settings.BASE_DIR + f'/static/dist/{name}.js'):
        _js_file = name + '.js'
    else:
        try:
            path = name + r'\..+\.js'
            _js_file = next(f for f in os.listdir(settings.BASE_DIR + '/static/dist') if re.fullmatch(path, f))
        except (StopIteration, FileNotFoundError) as e:  # pragma: no cover
            _js_file = f'__{name}_js_missing__'
            logging.warning(f'unable to find {name}.[chunkhash].js %s', e)
    return '/static/dist/{}'.format(_js_file)


def js_path(name):  # pragma: no cover
    if settings.DEBUG:
        return _js_path(name, dev=True)
    else:
        return _js_path(name)


def _reverse(rurl, **kwargs):
    return reverse(rurl, kwargs=kwargs)


def environment(**options):
    env = Environment(**options)
    env.globals.update({'static': static, 'url': _reverse, 'js_path': js_path})
    return env
