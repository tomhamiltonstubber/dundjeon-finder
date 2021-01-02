import factory

from DungeonFinder.messaging.models import Message


class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message
