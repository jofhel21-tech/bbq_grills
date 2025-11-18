# Generated migration for adding delivery location fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_userhistory'),
    ]

    operations = [
        # Add delivery location fields to Order model
        migrations.AddField(
            model_name='order',
            name='delivery_address',
            field=models.TextField(blank=True, help_text='Full delivery address'),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_latitude',
            field=models.FloatField(blank=True, help_text='Delivery location latitude', null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_longitude',
            field=models.FloatField(blank=True, help_text='Delivery location longitude', null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_barangay',
            field=models.CharField(blank=True, help_text='Barangay/District in Naval', max_length=100),
        ),
        
        # Add customer location fields to OrderTracking model
        migrations.AddField(
            model_name='ordertracking',
            name='customer_latitude',
            field=models.FloatField(blank=True, help_text='Customer location latitude', null=True),
        ),
        migrations.AddField(
            model_name='ordertracking',
            name='customer_longitude',
            field=models.FloatField(blank=True, help_text='Customer location longitude', null=True),
        ),
        migrations.AddField(
            model_name='ordertracking',
            name='customer_location_name',
            field=models.CharField(blank=True, help_text='Customer location name', max_length=255),
        ),
        
        # Update existing fields with help text
        migrations.AlterField(
            model_name='ordertracking',
            name='latitude',
            field=models.FloatField(blank=True, help_text='Current delivery person latitude', null=True),
        ),
        migrations.AlterField(
            model_name='ordertracking',
            name='longitude',
            field=models.FloatField(blank=True, help_text='Current delivery person longitude', null=True),
        ),
        migrations.AlterField(
            model_name='ordertracking',
            name='location_name',
            field=models.CharField(blank=True, help_text='Current location name', max_length=255),
        ),
    ]
