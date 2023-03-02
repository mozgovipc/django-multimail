"""django-multimail

.. moduleauthor:: Scott B. Bradley <scott@scott2b.com>, Twitter <@scott2b>
"""
from django.apps import AppConfig

__version__ = '0.1.5'
__license__ = 'OSI Approved :: MIT License'

__author__ = 'scott2b <Scott B. Bradley>'
__email__ = 'scott@scott2b.com'
__url__ = 'http://django-multimail.com'
default_app_config = 'multimail.MultimailConfig'


class MultimailConfig(AppConfig):
    name = 'multimail'

    def ready(self):
        from . import signals
