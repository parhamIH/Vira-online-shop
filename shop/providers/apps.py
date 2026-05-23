from django.apps import AppConfig


class ProvidersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop.providers'
    def ready(self):
        import shop.providers.signals 