# Generated by Django 4.2.6 on 2023-10-28 18:37

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('description', models.TextField(blank=True, verbose_name='Description')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='CategoryWeight',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('weight', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Weight')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.category', verbose_name='Category')),
            ],
            options={
                'verbose_name': 'Category Weight',
                'verbose_name_plural': 'Category Weights',
            },
        ),
        migrations.CreateModel(
            name='Couple',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': 'Couple',
                'verbose_name_plural': 'Couples',
            },
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('score', models.PositiveSmallIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=3, verbose_name='Score')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.category', verbose_name='Category')),
            ],
            options={
                'verbose_name': 'Grade',
                'verbose_name_plural': 'Grades',
            },
        ),
        migrations.CreateModel(
            name='Realtor',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Realtor',
                'verbose_name_plural': 'Realtors',
            },
        ),
        migrations.CreateModel(
            name='House',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nickname', models.CharField(max_length=128, verbose_name='Nickname')),
                ('address', models.TextField(blank=True, verbose_name='Address')),
                ('categories', models.ManyToManyField(through='core.Grade', to='core.category', verbose_name='Categories')),
                ('couple', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.couple', verbose_name='Couple')),
            ],
            options={
                'verbose_name': 'House',
                'verbose_name_plural': 'Houses',
            },
        ),
        migrations.CreateModel(
            name='Homebuyer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('categories', models.ManyToManyField(through='core.CategoryWeight', to='core.category', verbose_name='Categories')),
                ('partner', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.homebuyer', verbose_name='Partner')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Homebuyer',
                'verbose_name_plural': 'Homebuyers',
            },
        ),
        migrations.AddField(
            model_name='grade',
            name='homebuyer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.homebuyer', verbose_name='Homebuyer'),
        ),
        migrations.AddField(
            model_name='grade',
            name='house',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.house', verbose_name='House'),
        ),
        migrations.AddField(
            model_name='couple',
            name='realtor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.realtor', verbose_name='Realtor'),
        ),
        migrations.AddField(
            model_name='categoryweight',
            name='homebuyer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.homebuyer', verbose_name='Homebuyer'),
        ),
        migrations.AddField(
            model_name='category',
            name='couple',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.couple', verbose_name='Couple'),
        ),
    ]
