# Generated by Django 3.2 on 2021-05-07 10:53

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0036_alter_purchasedorder_date_ordered'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchasedorder',
            name='date_ordered',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]