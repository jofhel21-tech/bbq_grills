from django.core.management.base import BaseCommand
from core.models import Product


class Command(BaseCommand):
    help = 'Remove old Chicken Gizzard product from the database'

    def handle(self, *args, **options):
        try:
            # Find and delete the old "Chicken Gizzard" product
            old_product = Product.objects.get(name='Chicken Gizzard')
            old_product.delete()
            self.stdout.write(
                self.style.SUCCESS('Successfully removed "Chicken Gizzard" product')
            )
        except Product.DoesNotExist:
            self.stdout.write(
                self.style.WARNING('Product "Chicken Gizzard" not found in database')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error removing product: {str(e)}')
            )
