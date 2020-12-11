import binascii
import os

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
