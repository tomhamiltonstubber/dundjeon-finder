import factory
from django.db import IntegrityError

from DungeonFinder.users.models import User, GameMaster


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    password = 'testing'
    first_name = 'Hystera'
    last_name = factory.Sequence(lambda n: 'Died %d' % n)

    @factory.LazyAttribute
    def email(self):
        fn = getattr(self, 'first_name', 'Jane')
        ln = self.last_name
        em = f'{fn}_{ln}@example.com'
        return em.lower().replace(' ', '_')

    @classmethod
    def _create(cls, model_class, n=0, *args, **kwargs):
        """
        Override the default ``_create`` with our custom call.
        The default would use ``manager.create(*args, **kwargs)``
        """
        manager = cls._get_manager(model_class)

        try:
            user = manager.create_user(*args, **kwargs)
        except IntegrityError:
            kwargs.update(email=f"{kwargs['email']}{n}")
            n += 1
            cls._create(model_class, n, *args, **kwargs)
        else:
            return user


class GameMasterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GameMaster

    user = factory.SubFactory(UserFactory)
