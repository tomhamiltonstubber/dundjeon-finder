from html import escape

from django.db import models
from django.db.models import QuerySet

from DungeonFinder.games.models import Campaign
from DungeonFinder.users.models import User


class MessageQueryset(QuerySet):
    def request_qs(self, request):
        if not request.user.is_authenticated:
            return self.none()
        if request.user.is_admin:
            return self
        elif request.user.is_gm:
            return self.filter(campaign__creator=request.user.gamemaster)
        else:
            return self.filter(campaign__players=request.user)

    def request_editable_qs(self, request):
        qs = self.request_qs(request)
        if request.user.is_admin:
            return qs
        else:
            return self.filter(author=request.user)


class Message(models.Model):
    objects = MessageQueryset.as_manager()

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now=True, db_index=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def get_list_data(self):
        return {
            'id': self.id,
            'text': escape(self.text),
            'timestamp': self.timestamp.strftime('%Y-%m-%dT%H:%M'),
            'author': escape(self.author.screen_name),
            'gm_message': self.author.is_gm,
        }

    class Meta:
        ordering = ('-timestamp',)
