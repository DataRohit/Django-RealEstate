# Generated by Django 4.2.6 on 2023-10-31 02:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pending', '0002_alter_pendinghomebuyer_email_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pendinghomebuyer',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='pendinghomebuyer',
            name='last_name',
        ),
    ]