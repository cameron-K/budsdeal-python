from django.forms import ModelForm

from . import models


class MessageForm(ModelForm):
    class Meta:
        model = models.Conversations
        exclude = ['from_user', 'to_user', 'regard_item', 'timestamp', 'read']

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'