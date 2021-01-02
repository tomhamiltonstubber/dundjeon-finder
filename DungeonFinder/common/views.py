import binascii
import os
import random

from django.shortcuts import render
from django.views.generic import CreateView, FormView, UpdateView


class FormRequestMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(request=self.request)
        return kwargs


class DFCreateView(FormRequestMixin, CreateView):
    pass


class DFEditView(FormRequestMixin, UpdateView):
    pass


class DFFormView(FormRequestMixin, FormView):
    pass


def generate_random_key(length=50):
    # + 5 makes sure the original string is as long as (or longer than) length
    return binascii.hexlify(os.urandom(int(length / 2 + 5))).decode()[:length]


def index(request):
    meta_data = {
        'meta_title': 'Find Dungeons & Dragons Games',
        'meta_description': 'The online dungeons and dragons search engine',
    }

    if request.user.is_authenticated:
        return render(request, 'users/dashboard.jinja', meta_data)
    return render(request, 'index.jinja', meta_data)


def handle_404(request, exception=None):
    options = [['You took a wrong turn', 1], ['You rolled a natural one', 2], ['You are not a wise wizard', 3]]

    title, img = random.choice(options)
    return render(request, '404.jinja', {'title': title, 'image': img}, status=404)
