def get_email_definition(template_type):
    from DungeonFinder.messaging.models import EmailTemplate

    return {
        EmailTemplate.TEMPLATE_SIGNUP: {
            'subject': '',
            'content': (
                """\
Hi {{ first_name }},

Thanks for signing up to Dungeon Finder. Click [here]({{ confirm_link }}) to confirm your account:

Thanks"""
            ),
        },
        EmailTemplate.TEMPLATE_WELCOME: {
            'subject': '',
            'content': (
                """\
Hi {{ first_name }},

You've just signed up. Great."""
            ),
        },
    }[template_type]
