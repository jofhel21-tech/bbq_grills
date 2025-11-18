from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import IntegrityError


class Command(BaseCommand):
    help = 'Create an admin user for BBQ Grill order management'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin', help='Admin username (default: admin)')
        parser.add_argument('--email', type=str, default='admin@bbqgrill.com', help='Admin email')
        parser.add_argument('--password', type=str, default='admin123', help='Admin password (default: admin123)')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        try:
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'User "{username}" already exists!')
                )
                return

            # Create superuser
            admin_user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )

            self.stdout.write(
                self.style.SUCCESS(f'Successfully created admin user: "{username}"')
            )
            self.stdout.write(f'Email: {email}')
            self.stdout.write(f'Password: {password}')
            self.stdout.write('')
            self.stdout.write(
                self.style.SUCCESS('Admin user can now:')
            )
            self.stdout.write('• Manage all user orders')
            self.stdout.write('• Update order status')
            self.stdout.write('• Track order delivery')
            self.stdout.write('• Access admin panel at /admin/')
            self.stdout.write('')
            self.stdout.write(
                self.style.WARNING('IMPORTANT: Change the default password after first login!')
            )

        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating admin user: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error: {e}')
            )
