# Generated by Django 4.2.6 on 2023-11-09 01:54

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('summary', models.CharField(max_length=128, verbose_name='Summary')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ['summary'],
            },
        ),
        migrations.CreateModel(
            name='CategoryWeight',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('weight', models.PositiveSmallIntegerField(choices=[(1, 'Unimportant'), (2, 'Below Average'), (3, 'Average'), (4, 'Above Average'), (5, 'Important')], default=3, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='Weight')),
            ],
            options={
                'verbose_name': 'Category Weight',
                'verbose_name_plural': 'Category Weights',
                'ordering': ['category', 'homebuyer'],
            },
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('score', models.PositiveSmallIntegerField(choices=[(1, 'Poor'), (2, 'Below Average'), (3, 'Average'), (4, 'Above Average'), (5, 'Excellent')], default=3, verbose_name='Score')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='categories.category', verbose_name='Category')),
            ],
            options={
                'verbose_name': 'Grade',
                'verbose_name_plural': 'Grades',
                'ordering': ['homebuyer', 'house', 'category', 'score'],
            },
        ),
    ]
