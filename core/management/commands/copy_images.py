import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Copy product images from static/image to media/products directory'

    def handle(self, *args, **options):
        # Source directory (static/image)
        source_dir = os.path.join(settings.BASE_DIR, 'static', 'image')
        
        # Destination directory (media/products)
        media_dir = os.path.join(settings.BASE_DIR, 'media')
        dest_dir = os.path.join(media_dir, 'products')
        
        # Create media and products directories if they don't exist
        os.makedirs(dest_dir, exist_ok=True)
        
        # Image mappings
        image_files = [
            'BBQpork.jpg',
            'bbqchicken.jpg',
            'bbqhotdog.jpg',
            'bbqporkliempo.jpg',
            'betamax.jpg',
            'chickenfeet.jpg',
            'chickengizzard.jpg',
            'isaw.jpg',
            'maskara.jpg'
        ]
        
        copied_count = 0
        
        for image_file in image_files:
            source_path = os.path.join(source_dir, image_file)
            dest_path = os.path.join(dest_dir, image_file)
            
            if os.path.exists(source_path):
                try:
                    shutil.copy2(source_path, dest_path)
                    copied_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Copied: {image_file}')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to copy {image_file}: {str(e)}')
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Source file not found: {image_file}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSummary: {copied_count} images copied to media/products/')
        )
