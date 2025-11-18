from django.core.management.base import BaseCommand
from core.models import Product
from decimal import Decimal


class Command(BaseCommand):
    help = 'Add Filipino BBQ products to the database'

    def handle(self, *args, **options):
        products_data = [
            {
                'name': 'BBQ Pork',
                'description': 'Tender grilled pork marinated in our signature BBQ sauce. A Filipino favorite with sweet and savory flavors.',
                'price': Decimal('25.00'),
                'image': 'products/BBQpork.jpg',
            },
            {
                'name': 'BBQ Chicken',
                'description': 'Juicy grilled chicken pieces with our special marinade. Perfectly charred and full of flavor.',
                'price': Decimal('40.00'),
                'image': 'products/bbqchicken.jpg',
            },
            {
                'name': 'Isaw (Chicken Intestines)',
                'description': 'Grilled chicken intestines, a popular Filipino street food. Crispy outside, tender inside.',
                'price': Decimal('10.00'),
                'image': 'products/isaw.jpg',
            },
            {
                'name': 'Betamax (Chicken Blood)',
                'description': 'Grilled cubed chicken blood, named after the old video format. A unique Filipino delicacy.',
                'price': Decimal('10.00'),
                'image': 'products/betamax.jpg',
            },
            {
                'name': 'BBQ Hotdog',
                'description': 'Grilled hotdogs with a sweet glaze. A crowd favorite for all ages.',
                'price': Decimal('15.00'),
                'image': 'products/bbqhotdog.jpg',
            },
            {
                'name': 'Gizzard',
                'description': 'Tender grilled chicken gizzards marinated in soy sauce and spices. Chewy and flavorful.',
                'price': Decimal('30.00'),
                'image': 'products/chickengizzard.jpg',
            },
            {
                'name': 'Maskara (Pig Face)',
                'description': 'Grilled pig face, crispy skin with tender meat. A traditional Filipino BBQ specialty.',
                'price': Decimal('15.00'),
                'image': 'products/maskara.jpg',
            },
            {
                'name': 'Chicken Feet (Adidas)',
                'description': 'Grilled chicken feet, locally called "Adidas". Collagen-rich and full of flavor.',
                'price': Decimal('15.00'),
                'image': 'products/chickenfeet.jpg',
            },
            {
                'name': 'BBQ Pork Liempo',
                'description': 'Premium grilled pork belly with crispy skin and tender meat. A Filipino BBQ favorite.',
                'price': Decimal('100.00'),
                'image': 'products/bbqporkliempo.jpg',
            },
        ]

        created_count = 0
        updated_count = 0

        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'description': product_data['description'],
                    'price': product_data['price'],
                    'image': product_data.get('image', ''),
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created product: {product.name}')
                )
            else:
                # Update existing product
                product.description = product_data['description']
                product.price = product_data['price']
                product.image = product_data.get('image', '')
                product.is_active = True
                product.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated product: {product.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSummary: {created_count} products created, {updated_count} products updated'
            )
        )
