# Generated by Django 4.2.6 on 2023-10-31 02:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pending', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pendinghomebuyer',
            name='email',
            field=models.EmailField(error_messages={'unique': 'A user with this email already exists.'}, max_length=254, unique=True, verbose_name='Email Address'),
        ),
        migrations.AlterField(
            model_name='pendinghomebuyer',
            name='first_name',
            field=models.CharField(default='First', max_length=30, verbose_name='First Name'),
        ),
        migrations.AlterField(
            model_name='pendinghomebuyer',
            name='last_name',
            field=models.CharField(default='Last', max_length=30, verbose_name='Last Name'),
        ),
    ]
