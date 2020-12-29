import logging

logger = logging.getLogger('df.request')


class CommonMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        logger.info('Request made to %s', request.path)
        return self.get_response(request)
