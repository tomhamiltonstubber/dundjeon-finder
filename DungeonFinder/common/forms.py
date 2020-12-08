from django import forms


class DFForm(forms.Form):
    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)
        for f in self.fields:
            self.fields[f].widget.attrs = {'class': 'dk-field'}
