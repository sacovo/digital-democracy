"""
AppConfig

This module is used to configure the app. Usually you don't need to
change anything here. See here if you think you need to change anything:

https://docs.djangoproject.com/en/3.2/ref/applications/#configuring-applications
"""
from django.apps import AppConfig


class PapersConfig(AppConfig):
    """
    Configuration for the papers-app
    """

    name = "papers"
