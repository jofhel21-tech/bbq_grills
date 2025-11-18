from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Make a user staff and superuser for admin access'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to make staff')

    def handle(self, *args, **options):
        username = options['username']

        try:
            user = User.objects.get(username=username)
            user.is_staff = True
            user.is_superuser = True
            user.save()

            self.stdout.write(
                self.style.SUCCESS(f'Successfully made "{username}" a staff member and superuser!')
            )
            self.stdout.write(f'User "{username}" can now:')
            self.stdout.write('• Access admin order management')
            self.stdout.write('• Edit order status and tracking')
            self.stdout.write('• Manage all user orders')
            self.stdout.write('• Access Django admin panel')

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" does not exist!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {e}')
            )
