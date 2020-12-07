from django.db import models


class Game(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    creator = models.ForeignKey('users.GameMaster', on_delete=models.CASCADE)
    players = models.ManyToManyField('users.User', related_name='games', blank=True)

    def __str__(self):
        return self.name
