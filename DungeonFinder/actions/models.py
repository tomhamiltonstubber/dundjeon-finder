from django.conf import settings
from django.db import models
from django.db.models import JSONField
from django.dispatch import Signal
from django_rq import job

from DungeonFinder.games.models import Campaign
from DungeonFinder.users.models import User


class Action(models.Model):
    ACTION_LOGIN = 10
    ACTION_LOGOUT = 11
    ACTION_JOIN_GAME = 20
    ACTION_LEAVE_GAME = 21
    ACTION_CREATE_GAME = 30
    ACTION_DELETE_GAME = 31
    ACTION_EDIT_GAME = 32
    ACTION_KICK_PLAYER = 33
    ACTION_SEND_MESSAGE = 40
    ACTION_DELETE_MESSAGE = 41
    ACTION_EDIT_MESSAGE = 42
    ACTION_CHOICES = (
        (ACTION_LOGIN, 'Logged in'),
        (ACTION_LOGOUT, 'Logged out'),
        (ACTION_JOIN_GAME, 'Joined a game'),
        (ACTION_LEAVE_GAME, 'Left a game'),
        (ACTION_CREATE_GAME, 'Created a game'),
        (ACTION_DELETE_GAME, 'Deleted a game'),
        (ACTION_EDIT_GAME, 'Edited a game'),
        (ACTION_KICK_PLAYER, 'Kicked a player from a game'),
        (ACTION_SEND_MESSAGE, 'Sent a message'),
        (ACTION_DELETE_MESSAGE, 'Deleted a message'),
        (ACTION_EDIT_MESSAGE, 'Edited a message'),
    )

    timestamp = models.DateTimeField(auto_now=True, db_index=True)
    actor = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.IntegerField(db_index=True, choices=ACTION_CHOICES)
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='actions')
    target_campaign = models.ForeignKey(
        Campaign, on_delete=models.SET_NULL, null=True, blank=True, related_name='actions'
    )
    data = JSONField(null=True, blank=True)

    class Meta:
        verbose_name = 'Action'


action_recorded = Signal()


@job
def _record_action(action_type, **kwargs):
    Action.objects.create(action_type=action_type, **kwargs)
    action_recorded.send(sender=action_type, **kwargs)


def record_action(actor: User, action_type: int, target_user: User = None, target_campaign: Campaign = None, **data):
    kwargs = {
        'actor': actor,
        'action_type': action_type,
        'target_user': target_user or actor,
        'target_campaign': target_campaign,
        **data,
    }
    if settings.HEROKU_WEB_DYNO:  # no-cov
        _record_action.delay(**kwargs)
    else:
        _record_action(**kwargs)
