from django.db.models.signals import post_delete
from django.dispatch import receiver
from cloudinary.uploader import destroy
from .models import Post


@receiver(post_delete, sender=Post)
def delete_post_image(sender, instance, **kwargs):
    if hasattr(instance, 'featured_image') and instance.featured_image:
        public_id = instance.featured_image.public_id
        if public_id:
            destroy(public_id)
