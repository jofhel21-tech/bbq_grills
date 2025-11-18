from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Product, Appointment, JournalEntry, Article, Feedback, Order, OrderItem
from decimal import Decimal
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Set up comprehensive sample data for BBQ Grill website'

    def handle(self, *args, **options):
        # Create superuser if not exists
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@bbqgrill.com',
                password='admin123'
            )
            self.stdout.write(
                self.style.SUCCESS('Created superuser: admin/admin123')
            )

        # Create regular users
        users_data = [
            {'username': 'john_doe', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe'},
            {'username': 'jane_smith', 'email': 'jane@example.com', 'first_name': 'Jane', 'last_name': 'Smith'},
            {'username': 'mike_wilson', 'email': 'mike@example.com', 'first_name': 'Mike', 'last_name': 'Wilson'},
        ]
        
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Created user: {user.username}')
                )

        # Create sample articles
        articles_data = [
            {
                'title': 'The Art of Perfect BBQ: A Complete Guide',
                'body': 'Master the fundamentals of BBQ cooking with our comprehensive guide. Learn about temperature control, smoking techniques, and the best cuts of meat for different cooking methods. From beginner tips to advanced techniques, this article covers everything you need to know to become a BBQ master.',
                'published': True,
                'author': User.objects.get(username='admin')
            },
            {
                'title': 'Filipino BBQ: Traditional Recipes and Techniques',
                'body': 'Discover the rich tradition of Filipino BBQ cooking. Learn about traditional marinades, cooking methods, and the cultural significance of BBQ in Filipino cuisine. Includes recipes for classic dishes like pork BBQ, chicken inasal, and grilled seafood.',
                'published': True,
                'author': User.objects.get(username='admin')
            },
            {
                'title': 'Grilling Safety Tips for Beginners',
                'body': 'Safety should always be your top priority when grilling. This article covers essential safety tips, proper equipment handling, fire safety, and food safety guidelines. Learn how to enjoy BBQ cooking while keeping yourself and your family safe.',
                'published': True,
                'author': User.objects.get(username='admin')
            }
        ]

        for article_data in articles_data:
            article, created = Article.objects.get_or_create(
                title=article_data['title'],
                defaults=article_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created article: {article.title}')
                )

        # Create sample journal entries for users
        journal_entries_data = [
            {
                'title': 'My First BBQ Experience',
                'content': 'Today I tried grilling for the first time! I made some pork BBQ and it turned out amazing. The marinade was perfect and the meat was so tender. I can\'t wait to try more recipes and improve my skills.',
                'author': User.objects.get(username='john_doe')
            },
            {
                'title': 'BBQ Party Success',
                'content': 'Hosted a BBQ party last weekend and everyone loved it! Made chicken, pork, and some grilled vegetables. The secret was in the marinade - I used a combination of soy sauce, garlic, and brown sugar. Planning to make this a regular thing!',
                'author': User.objects.get(username='jane_smith')
            },
            {
                'title': 'New Grill Setup',
                'content': 'Finally got my new charcoal grill set up in the backyard. Spent the whole weekend seasoning it and testing different cooking techniques. The flavor difference between charcoal and gas is incredible!',
                'author': User.objects.get(username='mike_wilson')
            }
        ]

        for entry_data in journal_entries_data:
            entry, created = JournalEntry.objects.get_or_create(
                title=entry_data['title'],
                author=entry_data['author'],
                defaults={'content': entry_data['content']}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created journal entry: {entry.title}')
                )

        # Create sample appointments
        products = Product.objects.all()
        users = User.objects.filter(is_superuser=False)
        
        for i in range(5):
            appointment, created = Appointment.objects.get_or_create(
                customer=random.choice(users),
                scheduled_for=datetime.now() + timedelta(days=random.randint(1, 30)),
                defaults={
                    'product': random.choice(products) if products.exists() else None,
                    'notes': f'Sample appointment #{i+1} - Looking forward to this consultation!',
                    'status': random.choice(['pending', 'confirmed', 'completed'])
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created appointment: {appointment.id}')
                )

        # Create sample feedback
        feedback_messages = [
            'Amazing BBQ products! The quality is outstanding and delivery was fast.',
            'Great service and excellent customer support. Highly recommended!',
            'The BBQ consultation was very helpful. Learned a lot about proper grilling techniques.',
            'Love the variety of products available. Something for every BBQ enthusiast!',
            'Fast shipping and great packaging. Will definitely order again!'
        ]

        for i, message in enumerate(feedback_messages):
            feedback, created = Feedback.objects.get_or_create(
                user=random.choice(users),
                message=message,
                defaults={}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created feedback: {feedback.id}')
                )

        # Create sample orders
        for i in range(3):
            customer = random.choice(users)
            order, created = Order.objects.get_or_create(
                customer=customer,
                defaults={
                    'total_amount': Decimal(str(random.uniform(50, 200))),
                    'status': random.choice(['pending', 'processing', 'completed']),
                    'notes': f'Sample order #{i+1} - Customer requested BBQ products'
                }
            )
            if created:
                # Add order items
                selected_products = random.sample(list(products), random.randint(1, 3))
                for product in selected_products:
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=random.randint(1, 3),
                        price=product.price
                    )
                self.stdout.write(
                    self.style.SUCCESS(f'Created order: {order.id}')
                )

        self.stdout.write(
            self.style.SUCCESS('\n🎉 Sample data setup completed successfully!')
        )
        self.stdout.write(
            self.style.SUCCESS('You can now test all the website functionalities:')
        )
        self.stdout.write('• Home page with featured products and recent orders')
        self.stdout.write('• User registration and login (try: john_doe/password123)')
        self.stdout.write('• Product browsing and ordering')
        self.stdout.write('• Appointment booking and management')
        self.stdout.write('• Journal entries and personal notes')
        self.stdout.write('• Article reading and management (admin only)')
        self.stdout.write('• Feedback submission and viewing')
        self.stdout.write('• Order management and tracking')
        self.stdout.write('• User dashboard with statistics')
