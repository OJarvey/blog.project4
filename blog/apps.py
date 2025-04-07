from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'

    def ready(self):
        import blog.signals  # noqa F401
        from django.contrib.sites.models import Site
        Site.objects.filter(id=1).update(
            name="My Blog",
            domain="127.0.0.1:8000"
        )
