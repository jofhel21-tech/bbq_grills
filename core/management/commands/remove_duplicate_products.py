from django.core.management.base import BaseCommand
from core.models import Product


class Command(BaseCommand):
    help = 'Remove duplicate products from the database'

    def handle(self, *args, **options):
        # Define products to keep (remove duplicates)
        products_to_remove = [
            'BBQ Chicken Feet (Adidas)',  # Keep 'Chicken Feet (Adidas)'
            'BBQ Chicken Gizzard',        # Keep 'Chicken Gizzard' 
            'BBQ Maskara',                # Keep 'Maskara (Pig Face)'
            'BBQ Pork Isaw',              # Keep 'Isaw (Chicken Intestines)'
        ]
        
        removed_count = 0
        for product_name in products_to_remove:
            try:
                product = Product.objects.get(name=product_name)
                self.stdout.write(f'Removing duplicate: {product.name}')
                product.delete()
                removed_count += 1
            except Product.DoesNotExist:
                self.stdout.write(f'Product not found: {product_name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully removed {removed_count} duplicate products')
        )
        
        # Display remaining products
        self.stdout.write('\nRemaining products:')
        for product in Product.objects.all().order_by('name'):
            self.stdout.write(f'- {product.name}')
