from django.db import models


class Game(models.Model):
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

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    creator = models.ForeignKey('users.GameMaster', on_delete=models.CASCADE)
    players = models.ManyToManyField('users.User', related_name='games', blank=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default=STATUS_PENDING)
    max_players = models.IntegerField()

    def __str__(self):
        return self.name
