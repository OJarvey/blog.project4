import os
from django.core.management.base import BaseCommand
from django.conf import settings
from cloudinary.uploader import upload as cloudinary_upload
from blog.models import Post

class Command(BaseCommand):
    help = "Migrate local featured images to Cloudinary."

    def handle(self, *args, **options):
        posts = Post.objects.all()
        for post in posts:
            # Check if the instance has a 'featured_image' attribute
            if hasattr(post, 'featured_image') and post.featured_image:
                # Check if the object has a local file path
                if not hasattr(post.featured_image, 'path'):
                    self.stdout.write(f"Post {post.id} image is already migrated (no local path). Skipping.")
                    continue

                try:
                    local_file = post.featured_image.path
                    # If the field value is already a URL, skip migration
                    if str(post.featured_image).startswith("http"):
                        self.stdout.write(f"Post {post.id} image already on Cloudinary.")
                        continue

                    if os.path.exists(local_file):
                        self.stdout.write(f"Uploading {local_file} for Post {post.id}...")
                        result = cloudinary_upload(local_file)
                        # Update the featured_image field with the new Cloudinary public_id.
                        post.featured_image = result['public_id']
                        post.save()
                        self.stdout.write(self.style.SUCCESS(
                            f"Successfully uploaded {local_file} as {result['public_id']} for Post {post.id}"
                        ))
                    else:
                        self.stdout.write(self.style.WARNING(f"File not found: {local_file}"))
                except Exception as e:
                    self.stderr.write(f"Error uploading file for Post {post.id}: {e}")
            else:
                self.stdout.write(f"Post {post.id} does not have a featured_image field; skipping.")