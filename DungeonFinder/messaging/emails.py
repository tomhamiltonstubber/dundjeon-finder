import logging
from dataclasses import dataclass

import boto3
import sass
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.cache import cache
from django_rq import job
from jinja2 import Template as JinjaTemplate
from markdown.core import markdown

from DungeonFinder.messaging.email_definitions import get_email_definition
from DungeonFinder.users.models import User

df_logger = logging.getLogger('df.messaging')

ses_client = boto3.client(
    'ses',
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY,
    aws_secret_access_key=settings.AWS_SECRET_KEY,
)


class EmailTemplate:
    TEMPLATE_SIGNUP = 'signup_confirmation'  # Sent to confirm someone's signed up
    TEMPLATE_WELCOME = 'welcome_user'  # Sent when someone has confirmed signup
    TEMPLATE_JOINED_GAME = 'joined_game'  # Sent to player when they join a game
    TEMPLATE_PLAYER_JOINED = 'player_joined'  # Sent to GM when a player joins their game

    TEMPLATE_TYPES = [TEMPLATE_SIGNUP, TEMPLATE_WELCOME, TEMPLATE_JOINED_GAME, TEMPLATE_PLAYER_JOINED]
    template_type: str

    def __init__(self, template_type):
        self.template_type = template_type

    def email_definition(self):
        return get_email_definition(self.template_type)

    @staticmethod
    def _cached_email_styles():
        cache_key = 'file_email_css'
        content = cache.get(cache_key)
        if content:
            return content
        css = sass.compile(filename='static/scss/emails.scss')
        cache.set(cache_key, css, 86400)
        return css

    @staticmethod
    def _cached_jinja_content():
        cache_key = 'file_email_template'
        content = cache.get(cache_key)
        if content:
            return content
        with open('DungeonFinder/messaging/email_templates/email_base.jinja') as f:
            content = f.read()
        cache.set(cache_key, content, 86400)
        return content

    def rendered_content(self, content: str, context: dict) -> (str, str):
        text = JinjaTemplate(content).render(context)
        rendered_text = markdown(text)
        rendered_html = JinjaTemplate(self._cached_jinja_content()).render(
            {'content': rendered_text, 'styles': self._cached_email_styles()}
        )
        return rendered_text, rendered_html


@dataclass
class EmailRecipient:
    user: User = None
    first_name: str = ''
    last_name: str = ''
    email: str = ''

    def __str__(self):
        return f'{self.first_name} {self.last_name} <{self.email}>'

    def populate_fields(self):
        if self.user:
            self.email = self.user.email
            self.first_name = self.user.first_name
            self.last_name = self.user.last_name


@dataclass
class UserEmail:
    context: dict
    template_type: str
    recipient: EmailRecipient
    _template: EmailTemplate = None

    @property
    def template(self):
        self._template = self._template or EmailTemplate(self.template_type)
        return self._template


def aws_send_email(recipient, *, sender: EmailRecipient, subject: str, text_body: str, html_body: str):
    try:
        # Provide the contents of the email.
        response = ses_client.send_email(
            Destination={'ToAddresses': [str(recipient)]},
            Message={
                'Body': {
                    'Html': {'Charset': 'UTF-8', 'Data': html_body},
                    'Text': {'Charset': 'UTF-8', 'Data': text_body},
                },
                'Subject': {'Charset': 'UTF-8', 'Data': subject},
            },
            Source=str(sender),
        )
    except ClientError as e:
        df_logger.error(f'Error sending email: {e}')
    else:
        df_logger.info(f'Sending email {response["MessageId"]} to {recipient}')


@job
def send_email(*user_emails: UserEmail):
    from_recip = EmailRecipient(first_name='Dungeon', last_name='Finder', email=settings.FROM_EMAIL_ADDRESS)
    for user_email in user_emails:
        email_recip = user_email.recipient
        if not email_recip.user:
            email_recip.populate_fields()
        context = user_email.context
        context.update(first_name=email_recip.first_name, last_name=email_recip.last_name)
        for k, v in context.items():
            if k.endswith('_link'):
                context[k] = settings.BASE_URL + v
        email_def = user_email.template.email_definition()
        text, html = user_email.template.rendered_content(email_def['content'], context)
        if settings.SEND_EMAILS:  # noqa
            aws_send_email(
                email_recip,
                sender=from_recip,
                subject=email_def['subject'],
                text_body=text,
                html_body=html,
            )
        else:
            print(f'\n\nEmail sent to {email_recip.email}: {text}\n\n')
