from datetime import datetime

from django.dispatch import receiver
from pytz import utc

from DungeonFinder.actions.models import Action, action_recorded
from DungeonFinder.users.models import User


@receiver(action_recorded, sender=Action.ACTION_LOGIN)
def update_login(actor: User, **kwargs):
    actor.last_logged_in = datetime.now().replace(tzinfo=utc)
    actor.save(update_fields=['last_logged_in'])
