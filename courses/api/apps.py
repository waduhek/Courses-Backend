from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class APIConfig(AppConfig):
    name = 'api'
    verbose_name = gettext_lazy("API")
