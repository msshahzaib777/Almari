# Generated by Django 2.1.7 on 2019-05-11 08:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0004_profile'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='Firstname',
            new_name='firstname',
        ),
    ]
