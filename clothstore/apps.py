from django.apps import AppConfig

class ClothstoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clothstore'

    def ready(self):
        import clothstore.signals