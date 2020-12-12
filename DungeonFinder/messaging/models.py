import sass
from django.core.cache import cache
from django.db import models
from jinja2 import Template as JinjaTemplate
from markdown import markdown

from DungeonFinder.messaging.email_definitions import get_email_definition


def cached_jinja_content():
    cache_key = 'file_email_template'
    content = cache.get(cache_key)
    if content:
        return content
    with open('DungeonFinder/messaging/email_templates/email_base.jinja') as f:
        content = f.read()
    cache.set(cache_key, content, 86400)
    return content


def cached_email_styles():
    cache_key = 'file_email_css'
    content = cache.get(cache_key)
    if content:
        return content
    css = sass.compile(filename='static/scss/emails.scss')
    cache.set(cache_key, css, 86400)
    return css


class EmailTemplate(models.Model):
    TEMPLATE_SIGNUP = 'signup_confirmation'  # Sent to confirm someone's signed up
    TEMPLATE_WELCOME = 'welcome_user'  # Sent when someone has confirmed signup
    TEMPLATE_JOINED_GAME = 'joined_game'  # Sent to player when they join a game
    TEMPLATE_PLAYER_JOINED = 'player_joined'  # Sent to GM when a player joins their game

    TEMPLATE_TYPES = [TEMPLATE_SIGNUP, TEMPLATE_WELCOME, TEMPLATE_JOINED_GAME, TEMPLATE_PLAYER_JOINED]
    template_type = models.CharField(max_length=40, unique=True)

    def email_definition(self):
        return get_email_definition(self.template_type)

    def rendered_content(self, content: str, context: dict) -> (str, str):
        text = JinjaTemplate(content).render(context)
        rendered_text = markdown(text)
        rendered_html = JinjaTemplate(cached_jinja_content()).render(
            {'content': rendered_text, 'styles': cached_email_styles()}
        )
        return rendered_text, rendered_html
