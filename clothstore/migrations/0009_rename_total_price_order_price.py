# Generated by Django 4.1.7 on 2023-03-17 08:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clothstore', '0008_rename_price_order_total_price_remove_order_date_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='total_price',
            new_name='price',
        ),
    ]