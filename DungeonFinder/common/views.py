import binascii
import os
import random

from django.shortcuts import render
from django.views.generic import CreateView, FormView, TemplateView, UpdateView

from DungeonFinder.actions.models import record_action


class DFView:
    meta_title = None
    meta_description = None

    def get_meta_title(self):
        return self.meta_title

    def get_meta_description(self):
        return self.meta_description

    def get_context_data(self, **kwargs):
        kwargs.update(meta_title=self.get_meta_title(), meta_description=self.get_meta_description())
        return super().get_context_data(**kwargs)


class FormRequestMixin:
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(request=self.request)
        return kwargs


class _DFModelFormView(FormRequestMixin, DFView):
    action = None
    request = None

    def record_action(self):
        if self.action:
            record_action(self.request.user, self.action)

    def form_valid(self, form):
        r = super().form_valid(form)
        self.record_action()
        return r


class DFCreateView(_DFModelFormView, CreateView):
    pass


class DFEditView(_DFModelFormView, UpdateView):
    pass


class DFFormView(FormRequestMixin, DFView, FormView):
    pass


def generate_random_key(length=50):
    # + 5 makes sure the original string is as long as (or longer than) length
    return binascii.hexlify(os.urandom(int(length / 2 + 5))).decode()[:length]


class Dashboard(DFView, TemplateView):
    meta_title = 'Find Dungeons & Dragons Games'
    meta_description = 'The online dungeons and dragons search engine'

    def get_template_names(self):
        if self.request.user.is_authenticated:
            return ['users/dashboard.jinja']
        else:
            return ['index.jinja']


index = Dashboard.as_view()


def handle_404(request, exception=None):
    options = [['You took a wrong turn', 1], ['You rolled a natural one', 2], ['You are not a wise wizard', 3]]

    title, img = random.choice(options)
    return render(request, '404.jinja', {'title': title, 'image': img}, status=404)
