# Generated by Django 4.2.6 on 2023-10-30 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appauth', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'A user with this username already exists.'}, max_length=30, unique=True, verbose_name='Username'),
        ),
    ]
