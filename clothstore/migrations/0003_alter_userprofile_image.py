# Generated by Django 4.1.7 on 2023-03-15 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clothstore', '0002_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='image',
            field=models.ImageField(default='profile.png', upload_to='profile_images/'),
        ),
    ]