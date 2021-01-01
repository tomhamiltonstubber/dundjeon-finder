from html import escape

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, QuerySet
from django.urls import reverse


class CampaignQueryset(QuerySet):
    def request_joined_qs(self, request, as_player=False):
        if not request.user.is_authenticated:
            return self.none()
        elif request.user.is_admin:
            return self.all()
        else:
            query = Q(players=request.user)
            if not as_player and request.user.is_gm:
                query |= Q(creator=request.user.is_gm)
            return self.filter(query).distinct()


class Campaign(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_COLD = 'cold'
    STATUS_IN_PROGRESS = 'in-progress'
    STATUS_FINISHED = 'finished'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Not started yet'),
        (STATUS_COLD, 'Gone cold'),
        (STATUS_IN_PROGRESS, 'In progress'),
        (STATUS_FINISHED, 'Finished'),
    )
    STATUS_JOINABLE = [STATUS_PENDING, STATUS_IN_PROGRESS]
    TYPE_HOMEBREW = 'homebrew'
    TYPE_MODULAR = 'modular'
    TYPE_SOURCE_BOOK = 'source-book'
    TYPE_CHOICES = (
        (TYPE_HOMEBREW, 'Homebrew'),
        (TYPE_MODULAR, 'Modular'),
        (TYPE_SOURCE_BOOK, 'Campaign Source Book'),
    )
    RP_ANY = 'any'
    RP_HEAVY = 'heavy'
    RP_LIGHT = 'light'
    RP_CHOICES = ((RP_ANY, 'Any'), (RP_LIGHT, 'light'), (RP_HEAVY, 'heavy'))

    objects = CampaignQueryset.as_manager()

    name = models.CharField(max_length=255)

    accepting_players = models.BooleanField(default=True)
    beginners_welcome = models.BooleanField(default=True)
    campaign_type = models.CharField(choices=TYPE_CHOICES, default=TYPE_HOMEBREW, max_length=20)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    creator = models.ForeignKey('users.GameMaster', on_delete=models.CASCADE, editable=False)
    description = models.TextField(null=True, blank=True)
    players = models.ManyToManyField('users.User', related_name='campaigns', blank=True, editable=False)
    mature_content = models.BooleanField('Contains mature content', default=False)
    max_players = models.IntegerField(default=5, validators=[MinValueValidator(1)])
    next_game_dt = models.DateTimeField(null=True, blank=True)
    price_per_session = models.DecimalField(
        help_text='The price per player per session.', decimal_places=2, max_digits=4, null=True, blank=True
    )
    role_play_level = models.CharField(choices=RP_CHOICES, default=RP_ANY, max_length=20)
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default=STATUS_PENDING, editable=False)

    def __str__(self):
        return self.name

    def game_full(self):
        return self.players.count() >= self.max_players

    def get_absolute_url(self):
        return reverse('campaign-details', kwargs={'pk': self.pk})

    def get_list_data(self):
        return {
            'name': escape(self.name),
            'link': self.get_absolute_url(),
            'free_spaces': self.free_spaces,  # This has been annotated onto the queryset
            'description': escape(self.description),
            'price_per_session': self.price_per_session,
        }
