from django.core.management.base import BaseCommand
from core.models import Product


class Command(BaseCommand):
    help = 'Add maskara and chicken feet products to the database'

    def handle(self, *args, **options):
        # Create Maskara product
        maskara_product, created = Product.objects.get_or_create(
            name='BBQ Maskara',
            defaults={
                'description': 'Grilled pork face mask, a Filipino BBQ delicacy with crispy skin and tender meat. Marinated in our special BBQ sauce for authentic flavor.',
                'price': 25.00,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created product: {maskara_product.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Product already exists: {maskara_product.name}')
            )

        # Create Chicken Feet product
        chicken_feet_product, created = Product.objects.get_or_create(
            name='BBQ Chicken Feet (Adidas)',
            defaults={
                'description': 'Grilled chicken feet, locally known as "Adidas". A popular Filipino street food with chewy texture and savory BBQ flavor.',
                'price': 15.00,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created product: {chicken_feet_product.name}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Product already exists: {chicken_feet_product.name}')
            )

        # Create additional popular BBQ products
        additional_products = [
            {
                'name': 'BBQ Pork Liempo',
                'description': 'Premium pork belly strips grilled to perfection with our signature BBQ marinade. Juicy, flavorful, and tender.',
                'price': 35.00
            },
            {
                'name': 'BBQ Chicken Wings',
                'description': 'Succulent chicken wings marinated in our special blend of spices and grilled over charcoal for that authentic smoky flavor.',
                'price': 20.00
            },
            {
                'name': 'BBQ Pork Isaw',
                'description': 'Grilled pork intestines, a beloved Filipino street food. Cleaned thoroughly and grilled with our signature sauce.',
                'price': 18.00
            },
            {
                'name': 'BBQ Chicken Gizzard',
                'description': 'Tender chicken gizzards marinated and grilled to perfection. A protein-rich and flavorful BBQ option.',
                'price': 22.00
            }
        ]

        for product_data in additional_products:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'description': product_data['description'],
                    'price': product_data['price'],
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created product: {product.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Product already exists: {product.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Finished adding featured BBQ products!')
        )
